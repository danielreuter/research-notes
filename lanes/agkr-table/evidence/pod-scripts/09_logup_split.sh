#!/usr/bin/env bash
# agkr-table: is the graphed LogUp bound by the GPU or by the per-round host round trip?  CUDA events around every
# CUDAGraph.replay give the GPU time inside the round graphs; per table it is compared with the wall time of the walk
# (the difference = D2H syncs + host SHA-256 sponge + H2D of the coins + launch gaps).
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import functools, time
from pathlib import Path

import torch

from gpu import logup_packed, prover
from gpu.run import load_instance

dev = torch.device("cuda")
inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
prover.prove(inst, True)
torch.cuda.synchronize()

EV = []
orig_replay = torch.cuda.CUDAGraph.replay


def replay(self):
    s, e = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    s.record()
    orig_replay(self)
    e.record()
    EV.append((s, e))


torch.cuda.CUDAGraph.replay = replay
tables = []


def wrap(name):
    f = getattr(logup_packed, name)

    @functools.wraps(f)
    def g(*a, **k):
        torch.cuda.synchronize()
        i0, t = len(EV), time.perf_counter()
        r = f(*a, **k)
        torch.cuda.synchronize()
        tables.append((name.split("_")[1], a[-3] if name.endswith("ext_table_graphed") else a[-3], i0, len(EV), time.perf_counter() - t))
        return r

    setattr(logup_packed, name, g)


for n in ("prove_range_table_graphed", "prove_ext_table_graphed"):
    wrap(n)
t0 = time.perf_counter()
proof, st = prover.prove(inst, True)
torch.cuda.synchronize()
print(f"prove {time.perf_counter() - t0:.3f}s t_lookup {st.t_lookup:.3f}s  lookup_dims {st.lookup_dims}")
tot_wall = tot_gpu = 0.0
for kind, n, i0, i1, wall in tables:
    gpu = sum(s.elapsed_time(e) for s, e in EV[i0:i1]) / 1e3
    tot_wall += wall
    tot_gpu += gpu
    print(f"  {kind:6s} n={n:>3} replays {i1 - i0:4d}  wall {wall * 1e3:7.1f} ms  gpu-in-graphs {gpu * 1e3:7.1f} ms  per-replay host+gap {(wall - gpu) / max(1, i1 - i0) * 1e6:6.1f} us")
print(f"total walls {tot_wall:.3f}s gpu-in-graphs {tot_gpu:.3f}s host+gaps {tot_wall - tot_gpu:.3f}s replays {sum(t[3] - t[2] for t in tables)}")
EOF
