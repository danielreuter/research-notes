"""verify-night: the A-GKR statement's Params-only files regenerated from MY tree and compared with a dump's statement/.

    cd /workspace/src/backends/gkr && PYTHONPATH=.:$PYTHONPATH python 11-agkr-statement.py DUMP/statement OUT

circuit.txt / epilogue.txt / chain.txt through gpu.v2.export's own API (limb epilogue, the export default), without the operand
arrays (they do not enter these files); public.bin against the frozen vu-k1536.y.u16 [0, 4096) of my tree's fixture."""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
from gpu.v2.export import API, manifest_for
from verity_numerical.bench.tables import FROZEN_INSTANCES

st, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
uctx, _ = API.build_unit()
ectx, _ = API.build_epilogue()
API.export_circuit(uctx, out / "circuit.txt")
API.export_circuit(ectx, out / "epilogue.txt")
API.export_extra(uctx, ectx, out)
mine = manifest_for(uctx, ectx, out, epilogue=API.epilogue)
res = {}
for f in ("circuit.txt", "epilogue.txt", "chain.txt"):
    res[f] = {"identical": (st / f).read_bytes() == (out / f).read_bytes(), "sha256": hashlib.sha256((out / f).read_bytes()).hexdigest()}
theirs = json.loads((st / "manifest.json").read_text())
keys = ["field", "variant", "modulus", "unit_columns", "epilogue_columns", "chain_sha256", "epilogue"]
res["manifest_params_differ"] = [k for k in keys if theirs.get(k) != mine.get(k)]
fz = Path("/workspace/src/fixtures/bench-instances/v1")
want = FROZEN_INSTANCES["first-campaign-target/2026-09-21"]
res["manifest_sha256_frozen"] = hashlib.sha256((fz / "manifest.json").read_bytes()).hexdigest() == want["manifest_sha256"]
res["dump_manifest"] = {k: theirs.get(k) for k in ("tier", "range", "steps", "root_manifest_sha256", "cross_check")}
res["dump_manifest_root_is_frozen"] = theirs.get("root_manifest_sha256") in (None, want["manifest_sha256"])
lo, hi = want["range"]
y = np.frombuffer((fz / "vu-k1536.y.u16").read_bytes(), dtype="<u2")[lo:hi]
pb = (st / "public.bin").read_bytes()
n, c = struct.unpack("<QQ", pb[:16])
pub = np.frombuffer(pb[16:], dtype="<u4")
res["public_bin"] = {"header": [n, c], "words": int(pub.size), "sha256": hashlib.sha256(pb).hexdigest(),
                     "equals_frozen_y": bool(n == hi - lo and c == 1 and np.array_equal(pub, y.astype(np.uint32)))}
res["ok"] = (all(res[f]["identical"] for f in ("circuit.txt", "epilogue.txt", "chain.txt")) and not res["manifest_params_differ"]
             and res["manifest_sha256_frozen"] and res["public_bin"]["equals_frozen_y"] and res["dump_manifest_root_is_frozen"])
(out / "statement-check.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
