"""router_eq.py N_RANDOM: MoeRouterTopKRounds[_Norm] == MoeRouterTopK[_Norm] on the reference evaluator, bit for bit, over edge-case and
randomized bf16 logit rows at (E, TOPK, VPT) = (64, 8, 8) and (128, 8, 8)."""
import json
import sys
import time

import numpy as np

from verity.evaluation import evaluate
from verity.ir.defs import bind
from verity_vllm.program.registry import moe

NAN, PINF, NINF, PZ, NZ = 0x7FC0, 0x7F80, 0xFF80, 0x0000, 0x8000


def bf16(a):
    return (np.asarray(a, np.float32).view(np.uint32) >> 16).astype(np.int64).tolist()


def cases(E, rng, n_random):
    out = {}
    out["all +0"] = [PZ] * E
    out["all -0"] = [NZ] * E
    out["mixed +-0"] = [PZ if i % 2 else NZ for i in range(E)]
    out["all -inf"] = [NINF] * E
    out["all NaN"] = [NAN] * E
    out["all +inf"] = [PINF] * E
    out["one +inf"] = [PZ] * E
    out["one +inf"][E // 3] = PINF
    out["two +inf"] = bf16(rng.standard_normal(E))
    out["two +inf"][3] = out["two +inf"][E - 2] = PINF
    out["one NaN"] = bf16(rng.standard_normal(E))
    out["one NaN"][5] = NAN
    out["NaN first"] = bf16(rng.standard_normal(E))
    out["NaN first"][0] = NAN
    out["some -inf"] = bf16(rng.standard_normal(E))
    for i in range(0, E, 3):
        out["some -inf"][i] = NINF
    out["-inf and one finite"] = [NINF] * E
    out["-inf and one finite"][E - 1] = bf16([1.5])[0]
    out["all equal"] = bf16([2.0] * E)
    out["ties of 3"] = bf16(np.repeat(rng.standard_normal(E // 3 + 1), 3)[:E])
    out["huge (expf overflow)"] = bf16(rng.standard_normal(E) * 1e4)
    out["tiny spread (p ties after rounding)"] = bf16(10.0 + rng.standard_normal(E) * 1e-3)
    out["underflow to 0 but one"] = bf16([-200.0] * (E - 1) + [100.0])
    out["subnormal logits"] = [int(x) for x in rng.integers(1, 0x7F, E)]
    out["neg subnormal"] = [0x8000 | int(x) for x in rng.integers(1, 0x7F, E)]
    out["max finite"] = [0x7F7F] * (E // 2) + [0xFF7F] * (E - E // 2)
    for r in range(n_random):
        kind = r % 4
        if kind == 0:
            v = rng.standard_normal(E) * rng.choice([0.5, 2, 8])
        elif kind == 1:
            v = rng.choice(rng.standard_normal(4) * 3, E)                     # few distinct values: heavy ties
        elif kind == 2:
            v = rng.integers(-3, 4, E).astype(np.float32)                      # small integers: exact ties
        else:
            v = rng.standard_normal(E) * 4
        row = bf16(v)
        if kind == 3:                                                          # sprinkle specials
            for i in rng.choice(E, rng.integers(1, 6), replace=False):
                row[int(i)] = int(rng.choice([NAN, PINF, NINF, PZ, NZ, 0x7F7F, 0xFF7F, 0x0001, 0x8001]))
        out[f"random {r} kind {kind}"] = row
    return out


def main():
    n_random = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    rng = np.random.default_rng(20260926)
    report = {}
    for E, TOPK, VPT in ((64, 8, 8), (128, 8, 8)):
        for old, new in ((moe.MoeRouterTopK, moe.MoeRouterTopKRounds), (moe.MoeRouterTopKNorm, moe.MoeRouterTopKRoundsNorm)):
            a, b = bind(old, E=E, TOPK=TOPK, VPT=VPT), bind(new, E=E, TOPK=TOPK, VPT=VPT)
            t = time.time()
            n = bad = 0
            first = None
            for name, row in cases(E, rng, n_random).items():
                ra, rb = evaluate(a, row), evaluate(b, row)
                n += 1
                if tuple(ra) != tuple(rb):
                    bad += 1
                    first = first or {"case": name, "old": list(ra), "new": list(rb)}
            key = f"{new.name}{{E={E},TOPK={TOPK},VPT={VPT}}} vs {old.name}"
            report[key] = {"cases": n, "unequal": bad, "first_unequal": first, "seconds": round(time.time() - t, 1)}
            print(key, report[key]["cases"], "cases,", bad, "unequal", report[key]["seconds"], "s", flush=True)
    json.dump(report, open("/tmp/vux/router_eq.json", "w"), indent=1)


if __name__ == "__main__":
    main()
