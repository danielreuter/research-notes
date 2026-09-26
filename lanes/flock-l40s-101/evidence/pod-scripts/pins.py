"""flock-l40s-101 (reopened): per-parameter lowerings of the #73 / #60 elementwise subcircuits -- pin, rows vs the granted
parameter's rows, units, and the laid-out units against the IR evaluator on bench-spine's per-workload set."""
import hashlib, json, subprocess, sys, time
from pathlib import Path
import numpy as np
from verity_flock import ir_lower as IL
from verity_numerical.bench import lowerings, templates as TM
from verity_numerical.bench.input_sets import InputSet

REG = lowerings.registry("C-Flock")
CELLS = [("rope-head", {"D": 128}, "art:8ac2449fc02d46c56ffd54544b566383d2b4cc0e43d8f6c363f8829038367faa", {"D": 64}),
         ("silu-mul", {"I": 9728}, "art:049bedba5b608a4da9885296f869f0ad8559a5a92152e9574a82047ea976d1e0", {"I": 8192}),
         ("silu-mul", {"I": 14336}, "art:1a98fa49aac00195a0f9c5ad8522d25be074866020943ca253cec40594011a46", {"I": 8192}),
         ("rmsnorm-fused-cuda", {"N": 4096, "EPS": 1e-05}, "art:7092d6b2612df598f3afe50aa91695d6369bad3315cbca95df2fa8fe74107786", {"N": 2048, "EPS": 1e-05}),
         ("rmsnorm-triton", {"N": 4096, "EPS": 1e-05}, "art:d14afda2f946eb8a0d2762fbea11f031f9bbfdeac033c19686ff703dddb92edb", {"N": 2048, "EPS": 1e-05})]
only = sys.argv[1:] 

def rows(text):
    return [l for l in text.splitlines() if not l.startswith(("LEAVES ", "CUT "))]

def fetch(art):
    r = subprocess.run(["research", "data", "fetch", art], capture_output=True, text=True, check=True)
    return Path(r.stdout.strip().splitlines()[-1])

out = []
for tpl, params, art, granted in CELLS:
    if only and tpl not in only:
        continue
    mod = REG.module(tpl)
    s = InputSet.open(fetch(art))
    sub = s.subcircuit
    t0 = time.time()
    low = mod.lowering(sub)
    frame = mod.frame_lowering(sub)
    g = mod.lowering(TM.subcircuit(tpl, **granted))
    gframe = mod.frame_lowering(TM.subcircuit(tpl, **granted))
    fin, want = IL.flat_ports(s, sub.inputs, 0, s.n), IL.flat_ports(s, sub.outputs, 0, s.n)
    cuts = IL.cut_words(low, fin) if low.units.cut else None
    got, cut_out, ok = low.evaluate(fin, cuts)
    unsat = int(s.n * low.units.n - bin(ok).count("1")) if isinstance(ok, int) else None
    bad = (got != want).any(axis=1)
    if cuts is not None:
        bad |= (cut_out != cuts).any(axis=1)
    rec = {"subcircuit": sub.id, "set": art[:12], "n": s.n, "source": s.source, "content_digest": s.content_digest,
           "pin": low.sha256, "frame_pin": frame.sha256, "units_per_instance": low.units.n,
           "rows_equal_granted": rows(low.text) == rows(g.text), "frame_rows_equal_granted": rows(frame.text) == rows(gframe.text),
           "granted_pin": g.sha256, "granted_frame_pin": gframe.sha256,
           "mismatched_instances": int(bad.sum()), "unsatisfied_units": unsat, "seconds": round(time.time() - t0, 1)}
    print(json.dumps(rec), flush=True)
    out.append(rec)
