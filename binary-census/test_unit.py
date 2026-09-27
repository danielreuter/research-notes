"""Bit-exact test of the GF(2) unit circuit against verity.ml.tc (read-only import from the repo), plus counts."""
from __future__ import annotations

import json
import random
import sys
import time

sys.path.insert(0, "/workspace/packages/verity/src")
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

from verity.ml.tc.models import ADA_E4M3_M16N8K32, AMPERE_BF16_M16N8K16, HOPPER_BF16_M16N8K16, HOPPER_E4M3_K32  # noqa: E402

import unit as U  # noqa: E402


def rand_bf16(rng):
    s = rng.getrandbits(1)
    r = rng.random()
    if r < 0.30:
        e = rng.randint(120, 134)
    elif r < 0.45:
        e = rng.randint(0, 254)
    elif r < 0.55:
        e = 0  # subnormal / zero
    elif r < 0.62:
        e = rng.randint(240, 254)  # near overflow
    elif r < 0.70:
        e = rng.randint(1, 12)  # tiny
    else:
        e = rng.randint(100, 150)
    m = rng.getrandbits(7) if rng.random() > 0.08 else 0
    return (s << 15) | (e << 7) | m


def rand_e4m3(rng):
    while True:
        w = rng.getrandbits(8)
        if rng.random() < 0.1:
            w &= 0x87  # subnormal / zero
        if (w & 0x7F) != 0x7F:
            return w


def rand_acc(rng):
    s = rng.getrandbits(1)
    r = rng.random()
    if r < 0.15:
        return 0 if rng.random() < 0.5 else 0x80000000
    if r < 0.30:
        e = 0
    elif r < 0.60:
        e = rng.randint(110, 145)
    elif r < 0.70:
        e = rng.randint(230, 254)
    else:
        e = rng.randint(0, 254)
    return (s << 31) | (e << 23) | rng.getrandbits(23)


def cancel_case(rng, k, rand_op, bits):
    xs = [rand_op(rng) for _ in range(k)]
    ws = [rand_op(rng) for _ in range(k)]
    for i in range(0, k - 1, 2):
        xs[i + 1] = xs[i] ^ (1 << (bits - 1))  # same magnitude, opposite sign
        ws[i + 1] = ws[i]
    return xs, ws


def run(name, pipeline, fmt, T=3000, seed=1):
    C = U.unit(fmt, pipeline.groups, pipeline.width, pipeline.zero_exponent)
    cnt = C.counts()
    rng = random.Random(seed)
    k = pipeline.k
    rand_op = U_rand = rand_bf16 if fmt is U.BF16 else rand_e4m3
    cases = []
    while len(cases) < T:
        if rng.random() < 0.15:
            xs, ws = cancel_case(rng, k, rand_op, fmt.bits)
        else:
            xs = [rand_op(rng) for _ in range(k)]
            ws = [rand_op(rng) for _ in range(k)]
        c = rand_acc(rng)
        try:
            ref = pipeline.step(c, xs, ws)
        except Exception:
            continue
        cases.append((xs, ws, c, ref))
    # bit-slice
    nb = fmt.bits
    xin = [0] * (k * nb)
    win = [0] * (k * nb)
    cin = [0] * 32
    for t, (xs, ws, c, _) in enumerate(cases):
        for i in range(k):
            for b in range(nb):
                if xs[i] >> b & 1:
                    xin[i * nb + b] |= 1 << t
                if ws[i] >> b & 1:
                    win[i * nb + b] |= 1 << t
        for b in range(32):
            if c >> b & 1:
                cin[b] |= 1 << t
    t0 = time.time()
    outs, fail = C.evaluate({"x": xin, "w": win, "c": cin}, len(cases))
    dt = time.time() - t0
    got = [0] * len(cases)
    for b, v in enumerate(outs["c_out"]):
        for t in range(len(cases)):
            if v >> t & 1:
                got[t] |= 1 << b
    bad = [(t, hex(cases[t][3]), hex(got[t])) for t in range(len(cases)) if got[t] != cases[t][3]]
    nsat = sum(1 for cs in cases if (cs[3] & 0x7F800000) == 0x7F800000)
    return {"pipeline": name, "cases": len(cases), "saturating_cases": nsat, "mismatches": len(bad),
            "first_mismatches": bad[:5], "assert_failures_on_valid": bin(fail).count("1"), "eval_s": round(dt, 2),
            **cnt}


def negatives(pipeline, fmt, seed=7):
    """Non-finite operands / accumulators must fire an assertion."""
    C = U.unit(fmt, pipeline.groups, pipeline.width, pipeline.zero_exponent)
    rng = random.Random(seed)
    k = pipeline.k
    rand_op = rand_bf16 if fmt is U.BF16 else rand_e4m3
    nb = fmt.bits
    cases = []
    for t in range(64):
        xs = [rand_op(rng) for _ in range(k)]
        ws = [rand_op(rng) for _ in range(k)]
        c = rand_acc(rng)
        kind = t % 3
        if kind == 0:  # non-finite operand
            i = rng.randrange(k)
            if fmt is U.BF16:
                xs[i] = (rng.getrandbits(1) << 15) | (0xFF << 7) | rng.getrandbits(7)
            else:
                xs[i] = 0x7F | (rng.getrandbits(1) << 7)
        elif kind == 1:  # non-finite accumulator
            c = (rng.getrandbits(1) << 31) | (0xFF << 23) | rng.getrandbits(23)
        else:
            if fmt is U.BF16:
                ws[rng.randrange(k)] = 0x7F80 | (rng.getrandbits(1) << 15)
            else:
                ws[rng.randrange(k)] = 0xFF
        cases.append((xs, ws, c))
    xin = [0] * (k * nb)
    win = [0] * (k * nb)
    cin = [0] * 32
    for t, (xs, ws, c) in enumerate(cases):
        for i in range(k):
            for b in range(nb):
                if xs[i] >> b & 1:
                    xin[i * nb + b] |= 1 << t
                if ws[i] >> b & 1:
                    win[i * nb + b] |= 1 << t
        for b in range(32):
            if c >> b & 1:
                cin[b] |= 1 << t
    _, fail = C.evaluate({"x": xin, "w": win, "c": cin}, len(cases))
    return {"negatives": len(cases), "rejected": bin(fail).count("1")}


if __name__ == "__main__":
    which = sys.argv[1:] or ["ampere_bf16"]
    table = {
        "ampere_bf16": (AMPERE_BF16_M16N8K16, U.BF16),
        "hopper_bf16": (HOPPER_BF16_M16N8K16, U.BF16),
        "ada_e4m3": (ADA_E4M3_M16N8K32, U.E4M3),
        "hopper_e4m3": (HOPPER_E4M3_K32, U.E4M3),
    }
    res = []
    for name in which:
        p, f = table[name]
        r = run(name, p, f)
        r.update(negatives(p, f))
        res.append(r)
        print(json.dumps(r), flush=True)
    ep = U.epilogue_only().counts()
    print(json.dumps({"epilogue_f32_to_bf16": ep}))
