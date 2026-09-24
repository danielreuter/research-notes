#!/usr/bin/env bash
# agkr-table: where t_open_acc goes -- the top device kernels inside add_lookup_claim / add_input_claim / add_chain
# (torch.profiler/CUPTI, after two warm-up proves, gc frozen), per phase: kernel name, device ms, count.  13_busy.sh
# showed these phases are ~100% GPU-busy, so the kernels (not the host) are the cost.
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

from gpu import prover
from gpu.run import load_instance

dev = torch.device("cuda")
inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
prover.prove(inst, True)
prover.prove(inst, True)
torch.cuda.synchronize()
gc.collect()
gc.freeze()

PH = ["add_lookup_claim", "add_input_claim", "add_chain"]
for name in PH:
    f = getattr(prover, name)

    def g(*a, _f=f, _n=name, **k):
        with record_function(f"PH::{_n}"):
            return _f(*a, **k)

    setattr(prover, name, functools.wraps(f)(g))

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
ranges = collections.defaultdict(list)
kern = []
for e in prof.events():
    if e.device_type == DeviceType.CPU and e.name.startswith("PH::"):
        ranges[e.name].append((e.time_range.start, e.time_range.end))
    elif e.device_type == DeviceType.CUDA and not e.name.startswith("PH::"):
        kern.append((e.time_range.start, e.time_range.end, e.name))
print(f"t_open_acc {st.t_open_acc:.3f}s (profiled)")
for ph in PH:
    rs = ranges.get(f"PH::{ph}", [])
    cnt, dur = collections.Counter(), collections.Counter()
    for s, e, nm in kern:
        if any(a <= s < b for a, b in rs):
            cnt[nm] += 1
            dur[nm] += (e - s) / 1e3
    print(f"== {ph}: {len(rs)} calls, host {sum(b - a for a, b in rs) / 1e3:.1f} ms, kernels {sum(dur.values()):.1f} ms")
    for nm, d in dur.most_common(12):
        print(f"  {nm[:96]:96s} {d:8.2f} {cnt[nm]:6d}")
EOF
