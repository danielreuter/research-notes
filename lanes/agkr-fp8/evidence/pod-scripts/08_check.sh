#!/usr/bin/env bash
# agkr-fp8: exactness checks for host-overhead changes, then 06_ab.sh ($1 = relation, $2 = VUs).
#  eq_table (one-launch kernel) == the doubling loop for random points, n = 0..20, int64 and int32 outputs;
#  total bytes of every table's query values (what caching them across the mults and lookup passes would hold).
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=/workspace/agkr-fp8/$REL $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import json, os, random
from pathlib import Path

import torch

from gpu import field, prover

dev = torch.device("cuda")
rng = random.Random(7)
bad = 0
for n in list(range(0, 21)) + [16, 16, 12, 12]:
    pt = [tuple(rng.randrange(field.P) for _ in range(field.DEG)) for _ in range(n)]
    if n and rng.random() < 0.3:
        pt[0] = tuple([field.P - 1] * field.DEG)
    ref = field._eq_table_doubling(pt, dev) if n <= 16 else None
    for dt in (torch.int64, torch.int32):
        got = field.eq_table(pt, dev, out_dtype=dt)
        if ref is not None and not torch.equal(got.to(torch.int64), ref):
            bad += 1
            print("MISMATCH n", n, dt)
        if n > 16:
            lo = field._eq_table_doubling(pt, dev)
            if not torch.equal(got.to(torch.int64), lo):
                bad += 1
                print("MISMATCH (outer) n", n, dt)
print("eq_table kernel resolved:", field._fast_eq_vars is not None, " mismatches:", bad)
EOF
REL=$REL N=$N H=/workspace/agkr-fp8/$REL $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import json, os
from pathlib import Path

import torch

import bench_result as br
from gpu import prover
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
tot = 0
for t in inst.tables:
    vs = [v for v in prover.seg_query_values(inst, t.name) if v is not None]
    b = sum(v.numel() * v.element_size() for v in vs)
    tot += b
    print(f"{t.name:10s} cols {t.cols} rows {sum(v.shape[0] for v in vs):10d} dtype {vs[0].dtype} {b / 2**20:8.1f} MiB")
print(f"all query values {tot / 2**30:.2f} GiB")
EOF
bash /workspace/agkr-fp8/scripts/06_ab.sh $REL $N
