#!/usr/bin/env bash
# agkr-fp8: planned query values (prover._query_values_planned) == the per-form logup.query_values stack for every
# (segment, table) of $1 at $2 VUs, depth-batched prover._eval_wires == circuit.eval_wires per segment; then 06_ab.sh.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=/workspace/agkr-fp8/$REL $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
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
rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
inst = prover.Instance([prover.Segment("unit", uc, layers(uc), rows.units, uc.hash),
                        prover.Segment("epilogue", ec, layers(ec), rows.epilogue, ec.hash)],
                       read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in y]))
bad = 0
for t in inst.tables:
    for s in inst.segs:
        qs = prover.table_queries(s.circ, t.name)
        if not qs:
            continue
        ref = torch.stack([logup.query_values(q, s.cols) for q in qs], dim=1).reshape(-1, len(qs[0].cols))
        new = prover._query_values_planned(s.circ, t.name, qs, s.cols).reshape(-1, len(qs[0].cols))
        ok = ref.dtype == new.dtype and ref.shape == new.shape and bool(torch.equal(ref, new))
        bad += not ok
        print(f"{t.name:10s} {s.name:9s} q_t {len(qs):3d} steps {len(prover._query_plan(s.circ, t.name, qs, s.cols.device)[1]):2d} equal {ok}")
for _ in range(3):
    torch.cuda.synchronize(); t0 = time.perf_counter()
    for t in inst.tables:
        prover.seg_query_values(inst, t.name)
    torch.cuda.synchronize()
    print(f"seg_query_values all tables {time.perf_counter() - t0:.4f}s")
print(f"query-value mismatches: {bad}")
from gpu.circuit import eval_wires
for s in inst.segs:
    ref, new = eval_wires(s.circ, s.cols), prover._eval_wires(s.circ, s.cols)
    planned = prover._wire_plan(s.circ, s.cols.device) is not None
    print(f"wires {s.name:9s} planned {planned} levels {len(prover._wire_plan(s.circ, s.cols.device)[2]) if planned else 0} "
          f"equal {ref.dtype == new.dtype and bool(torch.equal(ref, new))}")
    for _ in range(2):
        torch.cuda.synchronize(); t0 = time.perf_counter(); eval_wires(s.circ, s.cols); torch.cuda.synchronize(); t1 = time.perf_counter()
        prover._eval_wires(s.circ, s.cols); torch.cuda.synchronize(); t2 = time.perf_counter()
        print(f"  eval_wires {t1 - t0:.4f}s  planned {t2 - t1:.4f}s")
EOF
bash /workspace/agkr-fp8/scripts/06_ab.sh "$REL" "$N"
