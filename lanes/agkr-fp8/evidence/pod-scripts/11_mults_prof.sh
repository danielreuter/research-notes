#!/usr/bin/env bash
# agkr-fp8: split t_mults on an FP8 statement ($H/stmt): seg_query_values vs logup.multiplicities, 5 timed passes per table.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-ada}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=${H:-/workspace/agkr-fp8/$REL} $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import json, os, time
from pathlib import Path

import torch

import bench_result as br
from gpu import logup, prover
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
dev = inst.device
for t in inst.tables:
    tr = logup.table_rows(t, dev)
    for i in range(6):
        torch.cuda.synchronize(); a = time.perf_counter()
        vals = [v for v in prover.seg_query_values(inst, t.name) if v is not None]
        torch.cuda.synchronize(); b = time.perf_counter()
        m = logup.multiplicities(t, tr, vals)
        torch.cuda.synchronize(); c = time.perf_counter()
        if i:
            print(f"{t.name} rows={t.nrows} vals={[tuple(v.shape) for v in vals]} {vals[0].dtype} qv={b - a:.4f}s mult={c - b:.4f}s", flush=True)
        del vals, m
print("peak GiB", torch.cuda.max_memory_allocated() / 2**30, "total GiB", torch.cuda.get_device_properties(dev).total_memory / 2**30)
EOF
