#!/usr/bin/env python3
"""red-team-flock-3: the attention unit netlist (fp.tc_dot16, the pinned flock-ir-unit/v2 text) against the IR primitive
AmpereBF16TcDot16_v1 (verity_vllm prims -> verity.ml.tc.total.tc_dot_total on AMPERE_BF16_M16N8K16), bit for bit, on adversarial
vectors, with my own netlist evaluator (netlist.py). Every lane must also satisfy every row.

Families (per vector): moderate (finite, exponents around 1), uniform (every field uniform bits), special / special_dense (operands from a special set with p 0.03 / 0.3: signed zeros, both
infinities, quiet / signalling NaNs of both signs, the extreme subnormals, min normal, max finite, 1), overflow (bf16 exponents
near the top: group saturation of either sign, and a later group's infinity or opposite-sign saturation), cancel (exact
cancellation of product pairs and of the accumulator), tiny (products and accumulators near the 2^-132 floor and the f32
subnormal range), scale (a huge accumulator with small products and the reverse: alignment and truncation), one_inf (one
infinite operand against zero, subnormal or finite partners, accumulators of either sign), nan (NaN payloads in a, b, acc).

  tc_diff.py NETLIST N SEED [procs]
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402

FAMILIES = ("moderate", "uniform", "special", "special_dense", "overflow", "cancel", "tiny", "scale", "one_inf", "nan")
SP16 = np.array([0x0000, 0x8000, 0x7F80, 0xFF80, 0x7FC0, 0xFFC0, 0x7F81, 0xFF81, 0x7FFF, 0xFFFF, 0x0001, 0x8001, 0x007F, 0x807F,
                 0x0080, 0x8080, 0x7F7F, 0xFF7F, 0x3F80, 0xBF80], dtype=np.uint64)
SP32 = np.array([0, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000, 0x7F800001, 0xFFFFFFFF, 0x7FFFFFFF, 1, 0x80000001,
                 0x007FFFFF, 0x807FFFFF, 0x00800000, 0x80800000, 0x7F7FFFFF, 0xFF7FFFFF, 0x3F800000, 0xBF800000], dtype=np.uint64)


def w16(rng, shape, lo, hi):
    return (rng.integers(0, 2, shape, dtype=np.uint64) << 15) | (rng.integers(lo, hi + 1, shape, dtype=np.uint64) << 7) | rng.integers(0, 128, shape, dtype=np.uint64)


def w32(rng, shape, lo, hi):
    return (rng.integers(0, 2, shape, dtype=np.uint64) << 31) | (rng.integers(lo, hi + 1, shape, dtype=np.uint64) << 23) | rng.integers(0, 1 << 23, shape, dtype=np.uint64)


def vectors(fam, L, seed):
    rng = np.random.default_rng([seed, FAMILIES.index(fam)])
    a, b, acc = w16(rng, (L, 16), 110, 144), w16(rng, (L, 16), 110, 144), w32(rng, L, 100, 160)
    if fam == "uniform":
        a, b, acc = rng.integers(0, 1 << 16, (L, 16), dtype=np.uint64), rng.integers(0, 1 << 16, (L, 16), dtype=np.uint64), rng.integers(0, 1 << 32, L, dtype=np.uint64)
    elif fam in ("special", "special_dense"):
        for x in (a, b):
            m = rng.random(x.shape) < (0.3 if fam == "special_dense" else 0.03)
            x[m] = rng.choice(SP16, int(m.sum()))
        m = rng.random(L) < (0.4 if fam == "special_dense" else 0.1)
        acc[m] = rng.choice(SP32, int(m.sum()))
    elif fam == "overflow":
        a, b = w16(rng, (L, 16), 180, 254), w16(rng, (L, 16), 180, 254)
        acc = np.where(rng.random(L) < 0.5, w32(rng, L, 240, 254), acc)
        g1 = rng.random(L) < 0.5                          # group 1 all one sign (saturates), group 2 the other sign
        s = rng.integers(0, 2, L, dtype=np.uint64) << 15
        a[g1, :8] = (a[g1, :8] & 0x7FFF) | s[g1, None]; b[g1, :8] &= 0x7FFF
        a[g1, 8:] = (a[g1, 8:] & 0x7FFF) | (s[g1, None] ^ 0x8000); b[g1, 8:] &= 0x7FFF
        m = rng.random(L) < 0.25                          # an infinity in group 2
        j = rng.integers(8, 16, L)
        a[m, j[m]] = rng.choice(np.array([0x7F80, 0xFF80], dtype=np.uint64), int(m.sum()))
    elif fam == "cancel":
        for p in range(0, 16, 2):
            m = rng.random(L) < 0.7
            a[m, p + 1] = a[m, p] ^ 0x8000; b[m, p + 1] = b[m, p]
        acc = np.where(rng.random(L) < 0.5, np.uint64(0), np.where(rng.random(L) < 0.5, np.uint64(0x80000000), acc))
        m = rng.random(L) < 0.3                           # a nearly-cancelled pair: one ulp apart
        a[m, 1] ^= 1
    elif fam == "tiny":
        a, b = w16(rng, (L, 16), 0, 70), w16(rng, (L, 16), 0, 70)
        acc = np.where(rng.random(L) < 0.5, w32(rng, L, 0, 3), w32(rng, L, 0, 0))
    elif fam == "scale":
        big = rng.random(L) < 0.5
        acc = np.where(big, w32(rng, L, 170, 250), w32(rng, L, 1, 60))
        a = np.where(big[:, None], w16(rng, (L, 16), 60, 110), w16(rng, (L, 16), 150, 200))
        b = np.where(big[:, None], w16(rng, (L, 16), 60, 110), w16(rng, (L, 16), 150, 200))
    elif fam == "one_inf":
        j = rng.integers(0, 16, L)
        a[np.arange(L), j] = rng.choice(np.array([0x7F80, 0xFF80], dtype=np.uint64), L)
        b[np.arange(L), j] = rng.choice(np.array([0x0000, 0x8000, 0x0001, 0x8001, 0x007F, 0x3F80, 0xBF80, 0x7F7F], dtype=np.uint64), L)
        acc = np.where(rng.random(L) < 0.4, rng.choice(SP32, L), acc)
    elif fam == "nan":
        for x in (a, b):
            m = rng.random(x.shape) < 0.05
            x[m] = (rng.integers(0, 2, int(m.sum()), dtype=np.uint64) << 15) | 0x7F80 | rng.integers(1, 128, int(m.sum()), dtype=np.uint64)
        m = rng.random(L) < 0.2
        acc[m] = (rng.integers(0, 2, int(m.sum()), dtype=np.uint64) << 31) | 0x7F800000 | rng.integers(1, 1 << 23, int(m.sum()), dtype=np.uint64)
    return acc & 0xFFFFFFFF, a & 0xFFFF, b & 0xFFFF


def job(args):
    netp, fam, L, seed = args
    from verity_vllm.program.registry import prims as P
    net = NL.Net(open(netp).read()); tc = NL.TcUnit(net)
    acc, a, b = vectors(fam, L, seed)
    res, sat = tc(acc, a, b)
    ir = np.array([P.AmpereBF16TcDot16.evaluate(int(acc[i]), *map(int, a[i]), *map(int, b[i])) & 0xFFFFFFFF for i in range(L)], dtype=np.uint64)
    bad = np.nonzero(res != ir)[0]
    e = (ir >> 23) & 0xFF; m = ir & 0x7FFFFF
    cls = {"nan": int(((e == 0xFF) & (m != 0)).sum()), "inf": int(((e == 0xFF) & (m == 0)).sum()), "zero": int((ir == 0).sum()),
           "subnormal": int(((e == 0) & (m != 0)).sum())}
    ex = [{"acc": f"{int(acc[i]):08x}", "a": [f"{int(x):04x}" for x in a[i]], "b": [f"{int(x):04x}" for x in b[i]],
           "net": f"{int(res[i]):08x}", "ir": f"{int(ir[i]):08x}"} for i in bad[:3]]
    return fam, seed, L, len(bad), int((~sat).sum()), cls, ex


def main():
    netp, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    chunk = 32768
    jobs = [(netp, fam, chunk, seed * 1000 + c) for fam in FAMILIES for c in range(max(1, N // chunk // len(FAMILIES)))]
    t0 = time.time()
    tot = {}
    with Pool(procs) as pool:
        for fam, s, L, bad, unsat, cls, ex in pool.imap_unordered(job, jobs):
            t = tot.setdefault(fam, {"vectors": 0, "mismatches": 0, "unsat": 0, "nan": 0, "inf": 0, "zero": 0, "subnormal": 0, "examples": []})
            t["vectors"] += L; t["mismatches"] += bad; t["unsat"] += unsat
            for k, v in cls.items():
                t[k] += v
            t["examples"] += ex[:max(0, 3 - len(t["examples"]))]
    for fam, t in tot.items():
        print("TC", fam, json.dumps(t), flush=True)
    print("TC_SUMMARY", json.dumps({"netlist_sha256": NL.Net(open(netp).read()).sha256, "vectors": sum(t["vectors"] for t in tot.values()),
                                    "mismatches": sum(t["mismatches"] for t in tot.values()), "unsat": sum(t["unsat"] for t in tot.values()),
                                    "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
