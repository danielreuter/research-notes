#!/usr/bin/env bash
# agkr-fp8: where Proof.to_bytes spends its time on an FP8 statement ($H/stmt): the ext lists (msgs, w, qc) and the column +
# Merkle-path loop, timed separately after 3 warm proves; types and sizes of the opening fields.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=${H:-/workspace/agkr-fp8/$REL} $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import json, os, time
from pathlib import Path

import numpy as np

import bench_result as br
from gpu import field as F, prover
from gpu.circuit import layers, load_circuit
from gpu.run import read_chain
from gpu.v2.fp8 import relation_params
from gpu.v2.witness import Generator, Ops

REL, N, H = os.environ["REL"], int(os.environ["N"]), Path(os.environ["H"])
d = H / "stmt"
man = json.loads((d / "manifest.json").read_text())
x, w, y, rel = br.load_relation(REL, Path("/workspace/src"), 0, N, 16)
p, _ = relation_params(rel)
ops = Ops("cuda")
gen = Generator(ops, p)
uc, ec = load_circuit(d / "circuit.txt"), load_circuit(d / "epilogue.txt")
ul, el = layers(uc), layers(ec)
rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                        prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)],
                       read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in y]))
for _ in range(3):
    proof, st = prover.prove(inst, True)
op = proof.opening
print("msgs", type(proof.msgs), len(proof.msgs), "w", type(op.w), len(op.w), "qc", type(op.qc), len(op.qc),
      "columns", type(op.columns), getattr(op.columns, "shape", None), "paths", type(op.paths), len(op.paths),
      type(op.paths[0]), len(op.paths[0]), type(op.paths[0][0]), flush=True)
for i in range(3):
    t0 = time.perf_counter(); F.exts_to_bytes(proof.msgs)
    t1 = time.perf_counter(); F.exts_to_bytes(op.w); F.exts_to_bytes(op.qc)
    t2 = time.perf_counter(); c = np.asarray(op.columns, dtype="<u4")
    t3 = time.perf_counter(); parts = [np.ascontiguousarray(c[oi]).tobytes() + b"".join(op.paths[oi]) for oi in range(c.shape[0])]
    t4 = time.perf_counter(); b = proof.to_bytes()
    t5 = time.perf_counter()
    print(f"msgs {t1 - t0:.4f} w+qc {t2 - t1:.4f} asarray {t3 - t2:.4f} cols+paths {t4 - t3:.4f} to_bytes {t5 - t4:.4f} bytes {len(b)}", flush=True)
EOF
