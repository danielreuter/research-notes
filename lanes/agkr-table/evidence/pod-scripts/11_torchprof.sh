#!/usr/bin/env bash
# agkr-table: per prover phase, host wall vs device kernel time (torch.profiler, CUPTI) on the exported 4096-VU
# instance after a warm-up prove: a phase whose kernel time is far below its wall is bound by the host (Python,
# launches, D2H syncs of the Fiat-Shamir sponge), not by the GPU.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import functools, gc
from pathlib import Path

import torch
from torch.profiler import ProfilerActivity, profile, record_function

from gpu import ligero, logup_packed, prover
from gpu.run import load_instance

dev = torch.device("cuda")
inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
prover.prove(inst, True)
torch.cuda.synchronize()
gc.collect()
gc.freeze()

PH = [(prover, "prove_segment"), (prover, "add_lookup_claim"), (prover, "add_input_claim"), (prover, "add_chain"),
      (prover, "start_transcript"), (ligero, "commit"), (ligero, "open_w_qc_eval"), (logup_packed, "prove_range_table_graphed"),
      (logup_packed, "prove_ext_table_graphed")]
for mod, name in PH:
    f = getattr(mod, name)

    def g(*a, _f=f, _n=name, **k):
        with record_function(f"PH::{_n}"):
            return _f(*a, **k)

    setattr(mod, name, functools.wraps(f)(g))

with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    with record_function("PH::prove"):
        proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
rows = [e for e in prof.key_averages() if e.key.startswith("PH::")]
print(f"{'phase':36s} {'calls':>5s} {'host wall ms':>12s} {'device ms':>10s}")
for e in sorted(rows, key=lambda e: -e.cpu_time_total):
    dev_us = getattr(e, "device_time_total", None)
    if dev_us is None:
        dev_us = e.cuda_time_total
    print(f"{e.key:36s} {e.count:5d} {e.cpu_time_total / 1e3:12.1f} {dev_us / 1e3:10.1f}")
kern = [e for e in prof.key_averages() if getattr(e, "device_type", None) is not None and str(e.device_type).endswith("CUDA")]
top = sorted(prof.key_averages(), key=lambda e: -(getattr(e, "self_device_time_total", 0) or 0))[:15]
print("top kernels by self device time:")
for e in top:
    print(f"  {e.key[:80]:80s} x{e.count:6d} {(getattr(e, 'self_device_time_total', 0) or 0) / 1e3:8.1f} ms")
EOF
