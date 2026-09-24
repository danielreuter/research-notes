#!/usr/bin/env bash
# agkr-table: where the prover's time goes after warm-up -- the exported 4096-VU instance (bb/pos4096, CPU export),
# one warm-up prove, then one prove with the opening-phase and LogUp entry points wrapped in synchronising timers
# (the extra syncs cost a little; the totals are for ranking, not for the table).  Prints Stats, the per-function
# totals and the LogUp host round trips (tr.logup_syncs).
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - "$@" <<'EOF'
import dataclasses, functools, hashlib, sys, time
from collections import defaultdict
from pathlib import Path

import torch

from gpu import ligero, logup_packed, prover
from gpu.run import load_instance

dev = torch.device("cuda")
inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
t0 = time.perf_counter()
proof, st = prover.prove(inst, True)
torch.cuda.synchronize()
print(f"warm-up prove {time.perf_counter() - t0:.2f}s", flush=True)

tot, cnt = defaultdict(float), defaultdict(int)


def wrap(mod, name):
    f = getattr(mod, name)

    @functools.wraps(f)
    def g(*a, **k):
        torch.cuda.synchronize()
        t = time.perf_counter()
        r = f(*a, **k)
        torch.cuda.synchronize()
        tot[f"{mod.__name__.split('.')[-1]}.{name}"] += time.perf_counter() - t
        cnt[f"{mod.__name__.split('.')[-1]}.{name}"] += 1
        return r

    setattr(mod, name, g)


import gc, os
if os.environ.get("GC_FREEZE"):
    gc.collect()
    gc.freeze()
    print(f"gc.freeze(): {gc.get_freeze_count()} objects frozen", flush=True)
gc.callbacks.append(lambda phase, info: phase == "start" and info["generation"] == 2 and cnt.__setitem__("gc.gen2", cnt["gc.gen2"] + 1))

for mod, names in ((prover, ["add_input_claim", "add_lookup_claim", "add_chain", "prove_segment"]),
                   (ligero, ["open_w_qc_eval", "open_w_qc", "row_coeffs", "open_set", "py_exts"]),
                   (logup_packed, ["prove_range_table_graphed", "prove_ext_table_graphed", "prove_range_table",
                                   "prove_ext_table"])):
    for n in names:
        if hasattr(mod, n):
            wrap(mod, n)

for rep in range(2):
    tot.clear(); cnt.clear()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
    wall = time.perf_counter() - t0
    sha = hashlib.sha256(proof.to_bytes()).hexdigest()
    print(f"rep {rep}: prove {wall:.3f}s proof_sha256 {sha}", flush=True)
s = dataclasses.asdict(st)
print({k: round(v, 4) if isinstance(v, float) else v for k, v in s.items() if k.startswith("t_") or "sync" in k})
for k in sorted(tot, key=lambda k: -tot[k]):
    print(f"  {k:48s} {tot[k]:8.4f}s  x{cnt[k]}")
EOF
