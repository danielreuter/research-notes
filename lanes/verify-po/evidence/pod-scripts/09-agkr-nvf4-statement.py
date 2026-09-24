"""verify-po: the A-GKR fp4-nvf4 statement (agkr-nvf4 handoff 20260924T2200Z) checked two ways.

    python 09-agkr-nvf4-statement.py DUMP/statement REGEN_DIR

1. circuit.txt / epilogue.txt / chain.txt / manifest params vs REGEN_DIR, the output of the PRODUCER'S NAMED SOURCE
   (lane/agkr-nvf4 @ 3c769c6d, `python -m gpu.nvf4.circuit export --out`, run on my pod from a git archive; main has no
   NVFP4 A-GKR circuit).
2. public.bin (4096 x 3, VU-major) vs the frozen NVFP4 set drawn by MY tree (main ab9573fd:
   backends/direct/ligero/fp4/chain.instances_fp4(4096), final FP32 word Y = v[3]): row i == ((Y>>31)&1, (Y>>23)&0xFF, Y&(2^23-1)).
Run from main's tree (part 2 imports only main's modules)."""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np

st, regen = Path(sys.argv[1]), Path(sys.argv[2])
N = 4096
res = {}
for f in ("circuit.txt", "epilogue.txt", "chain.txt"):
    a, b = (st / f).read_bytes(), (regen / f).read_bytes()
    res[f] = {"identical": a == b, "sha256": hashlib.sha256(a).hexdigest()}
res["chain_public_line"] = [ln for ln in (st / "chain.txt").read_text().splitlines() if ln.startswith("public")]
theirs = json.loads((st / "manifest.json").read_text())
mine = json.loads((regen / "manifest.json").read_text())
res["manifest_keys_differ"] = sorted(k for k in set(theirs) | set(mine) if theirs.get(k) != mine.get(k))
res["manifest_steps"] = theirs.get("steps")
res["manifest_relation"] = theirs.get("relation")

from backends.direct.ligero.fp4.chain import instances_digest, instances_fp4  # noqa: E402

vus = instances_fp4(N)
Y = np.asarray([int(v[3]) for v in vus], dtype=np.int64)
want = np.stack([(Y >> 31) & 1, (Y >> 23) & 0xFF, Y & (2**23 - 1)], axis=1)
pb = (st / "public.bin").read_bytes()
n, c = struct.unpack("<QQ", pb[:16])
pub = np.frombuffer(pb[16:], dtype="<u4").astype(np.int64)
res["instances_digest_main"] = instances_digest(N)
res["public_bin"] = {"header": [int(n), int(c)], "words": int(pub.size), "sha256": hashlib.sha256(pb).hexdigest()}
ok_shape = n == N and c == 3 and pub.size == 3 * N
res["public_bin"]["equals_frozen_stf"] = bool(ok_shape and np.array_equal(pub.reshape(N, 3), want))
res["public_bin"]["rows_mismatched"] = int((pub.reshape(N, 3) != want).any(1).sum()) if ok_shape else None
res["ok"] = (all(res[f]["identical"] for f in ("circuit.txt", "epilogue.txt", "chain.txt")) and not res["manifest_keys_differ"]
             and res["public_bin"]["equals_frozen_stf"])
print(json.dumps(res, indent=1, default=str))
