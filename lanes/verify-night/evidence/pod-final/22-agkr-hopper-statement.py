"""verify-night: an A-GKR bf16-hopper statement (agkr-table handoff 20260924T0830Z) regenerated from MY tree and compared with a dump.

    cd /workspace/src/backends/gkr && PYTHONPATH=.:$PYTHONPATH python 22-agkr-hopper-statement.py DUMP/statement OUT

circuit.txt / epilogue.txt / chain.txt: my tree's builders (gkr_export.v2, gpu.v2.epilogue_limbs; identical to agkr-table
5b3a4646's) at Params.from_model(MODELS["hopper_bf16_m16n8k16"]) of my tree, limb epilogue: the body of 5b3a4646's
gpu.v2.export.circuits(), which my tree lacks (glue only). public.bin against the frozen bf16-hopper set's published y, drawn
here by my tree's loaders (instance_equiv.frozen_relation + relchain.instances, no cache): y_public(last FP32 accumulator),
the BF16 cast (the same y whose sha256 15-sp1f-statements.py found, ab8c8067...)."""
import dataclasses
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
from gpu.v2 import epilogue_limbs as EL
from gpu.v2.export import P, manifest_for
from verity.ml.tc.models import MODELS
from verity_numerical.checker import Params
from verity_numerical.gkr_export import v2 as V2

MODEL, TARGET, N = "hopper_bf16_m16n8k16", "bf16-hopper-mma-draft/2026-09-22", 4096
st, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
p = Params.from_model(MODELS[MODEL])
uctx, _ = V2.build_unit_circuit_v2(p)
ectx, _ = EL.build_epilogue_circuit_limbs(p)
V2.export_circuit_v2(uctx, out / "circuit.txt", modulus=P, p=p)
V2.export_circuit_v2(ectx, out / "epilogue.txt", modulus=P, p=p)
V2.write_chain(V2.chain_spec(uctx, ectx, p), out / "chain.txt", P)
mine = json.loads(json.dumps(manifest_for(uctx, ectx, out, model=MODEL, params=dataclasses.asdict(p), steps=1536 // 16,
                                          epilogue="limbs"), default=str))
res = {"params": dataclasses.asdict(p)}
for f in ("circuit.txt", "epilogue.txt", "chain.txt"):
    res[f] = {"identical": (st / f).read_bytes() == (out / f).read_bytes(), "sha256": hashlib.sha256((out / f).read_bytes()).hexdigest()}
theirs = json.loads((st / "manifest.json").read_text())
keys = ["field", "variant", "modulus", "unit_columns", "epilogue_columns", "chain_sha256", "epilogue", "model", "params", "steps"]
res["manifest_params_differ"] = [k for k in keys if theirs.get(k) != mine.get(k)]
res["dump_manifest_other"] = {k: v for k, v in theirs.items() if k not in keys and k != "chain_file"}

from backends.direct.ligero import relchain  # noqa: E402
from verity_numerical.bench.instance_equiv import frozen_relation  # noqa: E402

rel, _ = frozen_relation(TARGET, N)
vus = relchain.instances(rel, N, procs=12)
y_fp32 = np.asarray([int(v[3]) for v in vus], dtype=np.int64)
y_bf16 = np.asarray([int(rel.y_public(int(v[3]))) for v in vus], dtype=np.int64)
pb = (st / "public.bin").read_bytes()
n, c = struct.unpack("<QQ", pb[:16])
pub = np.frombuffer(pb[16:], dtype="<u4").astype(np.int64)
res["frozen_relation"] = rel.name
res["y_bf16_sha256_u16"] = hashlib.sha256(y_bf16.astype("<u2").tobytes()).hexdigest()
res["public_bin"] = {"header": [n, c], "words": int(pub.size), "sha256": hashlib.sha256(pb).hexdigest(),
                     "equals_frozen_y_bf16": bool(n == N and c == 1 and np.array_equal(pub, y_bf16)),
                     "equals_frozen_y_fp32": bool(pub.size == N and np.array_equal(pub, y_fp32))}
res["ok"] = (all(res[f]["identical"] for f in ("circuit.txt", "epilogue.txt", "chain.txt")) and not res["manifest_params_differ"]
             and res["public_bin"]["equals_frozen_y_bf16"])
(out / "statement-check.json").write_text(json.dumps(res, indent=1, default=str))
print(json.dumps(res, indent=1, default=str))
