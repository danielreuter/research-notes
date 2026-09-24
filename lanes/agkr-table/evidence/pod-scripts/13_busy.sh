#!/usr/bin/env bash
# agkr-table: per prover phase, host wall vs GPU BUSY time (union of kernel intervals inside the phase's host range,
# torch.profiler/CUPTI device timestamps) and the kernel count, after a warm-up prove; plus the top kernels inside
# prove_segment.  busy << wall  =>  the phase is bound by the host (Python, launches, syncs), not by the GPU.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import collections, functools, gc
from pathlib import Path

import torch
from torch.autograd import DeviceType
from torch.profiler import ProfilerActivity, profile, record_function

from gpu import gkr, ligero, logup_packed, prover
from gpu.run import load_instance

dev = torch.device("cuda")
inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
prover.prove(inst, True)
prover.prove(inst, True)
torch.cuda.synchronize()
gc.collect()
gc.freeze()

PH = [(prover, "prove_segment"), (prover, "add_lookup_claim"), (prover, "add_input_claim"), (prover, "add_chain"),
      (ligero, "commit"), (ligero, "open_w_qc_eval"), (ligero, "prove_open"), (logup_packed, "prove_range_table_graphed"),
      (logup_packed, "prove_ext_table_graphed"), (gkr, "prove_layer"), (prover, "eval_wires")]
for mod, name in PH:
    if not hasattr(mod, name):
        continue
    f = getattr(mod, name)

    def g(*a, _f=f, _n=name, **k):
        with record_function(f"PH::{_n}"):
            return _f(*a, **k)

    setattr(mod, name, functools.wraps(f)(g))

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
ev = prof.events()
ranges = collections.defaultdict(list)
kern = []
for e in ev:
    if e.device_type == DeviceType.CPU and e.name.startswith("PH::"):
        ranges[e.name].append((e.time_range.start, e.time_range.end))
    elif e.device_type == DeviceType.CUDA:
        kern.append((e.time_range.start, e.time_range.end, e.name))
kern.sort()
print(f"{len(kern)} device events; prove t_total-ish: commit {st.t_commit:.3f} lookup {st.t_lookup:.3f} arith {st.t_arith:.3f} open {st.t_open:.3f}")


def busy(lo, hi):
    tot, cur_s, cur_e, n = 0.0, None, None, 0
    for s, e, _ in kern:
        if e <= lo or s >= hi:
            continue
        n += 1
        s, e = max(s, lo), min(e, hi)
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                tot += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        tot += cur_e - cur_s
    return tot, n


print(f"{'phase':34s} {'calls':>5s} {'wall ms':>9s} {'busy ms':>9s} {'busy %':>7s} {'kernels':>8s}")
for name, rs in sorted(ranges.items(), key=lambda kv: -sum(b - a for a, b in kv[1])):
    wall = sum(b - a for a, b in rs) / 1e3
    bz, nk = 0.0, 0
    for a, b in rs:
        x, n = busy(a, b)
        bz += x / 1e3
        nk += n
    print(f"{name:34s} {len(rs):5d} {wall:9.1f} {bz:9.1f} {100 * bz / max(wall, 1e-9):6.0f}% {nk:8d}")
seg = ranges.get("PH::prove_segment", [])
cnt = collections.Counter()
dur = collections.Counter()
for s, e, nm in kern:
    if any(a <= s < b for a, b in seg):
        cnt[nm] += 1
        dur[nm] += (e - s) / 1e3
print("top kernels inside prove_segment (device ms, count):")
for nm, d in dur.most_common(14):
    print(f"  {nm[:90]:90s} {d:8.1f} {cnt[nm]:7d}")
EOF
