import json
import sys
import time
from collections import defaultdict

import numpy as np

from verity_flock import ir_lower as IL
from verity_numerical.bench import templates as TM
from verity_numerical.bench.input_sets import InputSet

path = sys.argv[1]
only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else None
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
s = InputSet.open(path)
ix = s.index()
cols = ix["columns"] if isinstance(ix, dict) else None
rows = ix["rows"] if isinstance(ix, dict) else ix
sub = TM.subcircuit("attention-head", D=64, BN=128)
q, k, v, out = s.port("q"), s.port("k"), s.port("v"), s.port("out")
byT = defaultdict(list)
for i in range(s.n):
    byT[len(k[i]) // 64].append(i)
summary = {}
for T in sorted(byT):
    if only and T not in only:
        continue
    ids = byT[T][:limit] if limit else byT[T]
    t0 = time.time()
    low = IL.lowering(sub.definition(T), f"attention-head/tc-step/t{T}", unit_fn=IL.tc_units)
    fin = np.stack([np.concatenate([q[i], k[i], v[i]]).astype(np.uint64) for i in ids])
    cuts = IL.cut_words(low, fin)
    t1 = time.time()
    _res, cut_out, ok = low.evaluate(fin, cuts)
    tc_slots = sorted({p for u in low.units.out_src for _, p in u})
    diff = int((cut_out[:, tc_slots] != cuts[:, tc_slots]).any(axis=1).sum())
    unsat = bin(((1 << (len(ids) * low.units.n)) - 1) & ~ok).count("1")
    # the IR's outputs against the captured ones (the tail computes them from the cut words)
    from verity.ir.evaluate import evaluate_call
    prog, call = IL.standalone(low.definition)
    bad_out = 0
    for r, i in enumerate(ids):
        t = {}
        evaluate_call(prog.circuit, call, [int(x) for x in fin[r]], t)
        if [t[g] for g in call.returns] != [int(x) for x in out[i]]:
            bad_out += 1
    summary[T] = {"heads": len(ids), "units": low.units.n, "tail": len(low.units.tail), "unit_mismatch_heads": diff, "unsat_lanes": unsat,
                  "ir_vs_captured_out": bad_out, "ir_s": round(t1 - t0, 1), "eval_s": round(time.time() - t1, 1)}
    print(T, json.dumps(summary[T]), flush=True)
print("SUMMARY", json.dumps(summary))
