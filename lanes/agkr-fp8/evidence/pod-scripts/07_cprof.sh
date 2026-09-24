#!/usr/bin/env bash
# agkr-fp8: host-side hotspots of one warm A-GKR prove ($1 = relation, $2 = VUs): cProfile sorted by tottime and cumtime.
# Device waits show up in the syncing calls (tolist / item / int() of a device tensor); the rest is Python + launch cost.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=/workspace/agkr-fp8/$REL $PY - <<'EOF' 2>&1 | grep -v -i -E "warn|searchsorted"
import cProfile, gc, io, json, os, pstats, time
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
ul, el = layers(uc), layers(ec)
rows = gen.run(ops.asarray(x), ops.asarray(w), ops.asarray(y))
inst = prover.Instance([prover.Segment("unit", uc, ul, rows.units, uc.hash),
                        prover.Segment("epilogue", ec, el, rows.epilogue, ec.hash)],
                       read_chain(d / "chain.txt", uc, ec, man["steps"], [int(v) for v in y]))
for i in range(3):
    prover.prove(inst, True)
torch.cuda.synchronize()
gc.collect()
gc.freeze()
pr = cProfile.Profile()
t0 = time.perf_counter()
pr.enable()
proof, st = prover.prove(inst, True)
torch.cuda.synchronize()
pr.disable()
print(f"profiled prove {time.perf_counter() - t0:.4f}s (lookup {st.t_lookup:.4f} arith {st.t_arith:.4f} open_acc {st.t_open_acc:.4f})")
for key in ("tottime", "cumtime"):
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats(key).print_stats(40)
    print("\n".join(l[:170] for l in s.getvalue().splitlines()[:60]))
EOF
