#!/usr/bin/env bash
# agkr-table: the device witness generator's phases (chain / unit_rows / epilogue, synchronised) on the frozen
# vu-k1536 operands, cold and then after a full prove of the same rows -- bench_result.py's rep measured 0.88 s where
# gpu/v2/witness.py compare measured 0.34 s; this separates the phases and the allocator state.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import json, time
from pathlib import Path

import torch

import bench_result as br
from gpu import prover
from gpu.circuit import layers, load_circuit
from gpu.run import read_chain
from gpu.v2.witness import Generator, Ops

dev = torch.device("cuda")
d = Path("/workspace/agkr-table/bb/stmt")
man = json.loads((d / "manifest.json").read_text())
x, w, y, _ = br.load_frozen(Path("/workspace/bench-instances/v1"), Path("/workspace/src/fixtures/bench-instances/v1/manifest.json"),
                            br.TIER, 0, 4096)
ops = Ops(str(dev))
gen = Generator(ops)
sync = lambda: torch.cuda.synchronize(dev)


def gen_once(tag):
    sync()
    t0 = time.perf_counter()
    A, B, Y = ops.asarray(x), ops.asarray(w), ops.asarray(y)
    sync()
    t_h2d = time.perf_counter() - t0
    rows = gen.run(A, B, Y, sync=sync)
    bad = int(rows.bad.sum())
    t = time.perf_counter() - t0
    print(f"{tag}: total {t:.3f}s h2d {t_h2d:.3f}s " + " ".join(f"{k} {v:.3f}" for k, v in rows.seconds.items()) + f" bad {bad}", flush=True)
    return rows


for i in range(3):
    rows = gen_once(f"cold{i}")
ucirc, ecirc = load_circuit(d / "circuit.txt"), load_circuit(d / "epilogue.txt")
inst = prover.Instance([prover.Segment("unit", ucirc, layers(ucirc), rows.units, ucirc.hash),
                        prover.Segment("epilogue", ecirc, layers(ecirc), rows.epilogue, ecirc.hash)],
                       read_chain(d / man.get("chain_file", "chain.txt"), ucirc, ecirc, man["steps"], [int(v) for v in y]))
del rows
for i in range(2):
    proof, st = prover.prove(inst, True)
    sync()
    del proof, st
    gen_once(f"after_prove{i}")
EOF
