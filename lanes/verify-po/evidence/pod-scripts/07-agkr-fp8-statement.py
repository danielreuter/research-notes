"""verify-po: an A-GKR E4M3 statement (agkr-fp8 handoff 20260924T2129Z) checked two ways.

    python 07-agkr-fp8-statement.py DUMP/statement REGEN_DIR TARGET MODEL

1. circuit.txt / epilogue.txt / chain.txt / manifest params vs REGEN_DIR, the output of the PRODUCER'S NAMED SOURCE
   (lane/agkr-fp8 @ 07a8edd6, `python -m gpu.v2.export circuits --model MODEL`, run on my pod from a git archive; main has
   no E4M3 A-GKR builder): shows the dump is exactly what that source builds.
2. public.bin vs the frozen TARGET set drawn by MY tree (main ab9573fd: instance_equiv.frozen_relation + relchain.instances,
   no cache): word i == fp8.relation.pack_public(final FP32 accumulator of VU i) (low 10 bits zero, then >> 10).
Run with main's tree first on PYTHONPATH (part 2 imports only main's modules; part 1 only compares files)."""
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

import numpy as np

st, regen, target, model = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
N = 4096
res = {"target": target, "model": model}
for f in ("circuit.txt", "epilogue.txt", "chain.txt"):
    a, b = (st / f).read_bytes(), (regen / f).read_bytes()
    res[f] = {"identical": a == b, "sha256": hashlib.sha256(a).hexdigest()}
theirs = json.loads((st / "manifest.json").read_text())
mine = json.loads((regen / "manifest.json").read_text()) if (regen / "manifest.json").is_file() else json.loads((regen / "circuits.json").read_text())
keys = ["field", "variant", "modulus", "unit_columns", "epilogue_columns", "chain_sha256", "epilogue", "model", "params", "steps"]
res["manifest_params_differ"] = [k for k in keys if theirs.get(k) != mine.get(k)]
res["manifest_steps"] = theirs.get("steps")

from backends.direct.ligero import relchain  # noqa: E402
from backends.direct.ligero.fp8.relation import pack_public  # noqa: E402
from verity_numerical.bench.instance_equiv import frozen_relation  # noqa: E402

rel, ref = frozen_relation(target, N)
vus = relchain.instances(rel, N, procs=int(os.environ.get("VY_CPU_THREADS", "12")))
y_fp32 = [int(v[3]) for v in vus]
y_pack = np.asarray([pack_public(y) for y in y_fp32], dtype=np.int64)
y_rel = np.asarray([int(rel.y_public(y)) for y in y_fp32], dtype=np.int64)
pb = (st / "public.bin").read_bytes()
n, c = struct.unpack("<QQ", pb[:16])
pub = np.frombuffer(pb[16:], dtype="<u4").astype(np.int64)
res["frozen_relation"] = rel.name
res["frozen_ref"] = ref
res["y_rel_equals_pack"] = bool(np.array_equal(y_rel, y_pack))
res["public_bin"] = {"header": [int(n), int(c)], "words": int(pub.size), "sha256": hashlib.sha256(pb).hexdigest(),
                     "equals_frozen_y_packed": bool(n == N and c == 1 and pub.size == N and np.array_equal(pub, y_pack)),
                     "mismatched": int((pub != y_pack).sum()) if pub.size == N else None}
res["ok"] = (all(res[f]["identical"] for f in ("circuit.txt", "epilogue.txt", "chain.txt")) and not res["manifest_params_differ"]
             and res["public_bin"]["equals_frozen_y_packed"])
print(json.dumps(res, indent=1, default=str))
