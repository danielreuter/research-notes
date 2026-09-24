#!/usr/bin/env bash
# agkr-fp8: where the A-GKR FP8 prover's time goes ($1 = fp8-ada | fp8-hopper, $2 = VUs): Stats of 3 warm proves, then one
# torch.profiler pass with a record_function range per prover phase function: kernel name, device ms, count, per phase.
set -uo pipefail
source /workspace/env.sh
REL=${1:-fp8-hopper}; N=${2:-4096}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REL=$REL N=$N H=/workspace/agkr-fp8/$REL $PY - <<'EOF' 2>&1 | grep -v -i warn
import collections, dataclasses, functools, gc, json, os, time
from pathlib import Path

import torch
from torch.autograd import DeviceType
from torch.profiler import ProfilerActivity, profile, record_function

import bench_result as br
from gpu import ligero, logup, logup_packed, prover
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
KEYS = ("t_mults", "t_commit", "t_lookup", "t_arith", "t_witness_wires", "t_open_acc", "t_open_wq", "t_open_cols")
for i in range(4):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
    tt = time.perf_counter() - t0
    if i == 0:
        gc.collect()
        gc.freeze()
    print(f"prove {i}: {tt:.4f}s  " + "  ".join(f"{k[2:]}={getattr(st, k):.4f}" for k in KEYS), flush=True)
print("lookup_dims", st.lookup_dims)

PH = [(prover, "prove_segment"), (prover, "add_input_claim"), (prover, "add_lookup_claim"), (prover, "add_chain"),
      (ligero, "commit"), (ligero, "prove_open"), (logup, "multiplicities"), (logup, "build_leaves"),
      (logup_packed, "prove_range_table_graphed"), (logup_packed, "prove_range_table"),
      (logup_packed, "prove_ext_table_graphed"), (logup_packed, "prove_ext_table"), (prover, "start_transcript")]
for mod, name in PH:
    f = getattr(mod, name)

    def g(*a, _f=f, _n=name, **k):
        with record_function(f"PH::{_n}"):
            return _f(*a, **k)

    setattr(mod, name, functools.wraps(f)(g))

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
for _, ph in PH:
    rs = ranges.get(f"PH::{ph}", [])
    if not rs:
        continue
    cnt, dur = collections.Counter(), collections.Counter()
    for s, e, nm in kern:
        if any(a <= s < b for a, b in rs):
            cnt[nm] += 1
            dur[nm] += (e - s) / 1e3
    print(f"== {ph}: {len(rs)} calls, host {sum(b - a for a, b in rs) / 1e3:.1f} ms, kernels {sum(dur.values()):.1f} ms, "
          f"launches {sum(cnt.values())}")
    for nm, dd in dur.most_common(8):
        print(f"  {nm[:90]:90s} {dd:8.2f} {cnt[nm]:6d}")
EOF
