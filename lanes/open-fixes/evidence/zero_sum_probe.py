"""Lane open-fixes task 2: does a v2 / v2x4 relation accept the honest witness of an exactly cancelling sum with a large
group maximum?  Unit 92536 (relmin-private's find, fp8-hopper) + constructed units of the same class for every v2 / v2x4 /
v3 relation: two live products that cancel exactly at the group maximum, every other product dead (shifted out), c = +-0.
Run from a tree root (PYTHONPATH = packages/verity/src:backends/numerical/python:.).  Prints per relation / mode the number
of honest units rejected (must be 0) and the number of wrong claims accepted (must be 0)."""
import json
import sys

import numpy as np
import torch
from verity.ml.tc.silicon import tc_dot

from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.pubsel.relation import plan
from backends.direct.ligero.pubsel.relation_test import _accepts
from backends.direct.ligero.witness import build_witness, tables

UNIT = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
NAMES = [n for n in ("fp8-hopper-v2", "fp8-ada-v2", "bf16-hopper-v2", "bf16-ampere-v2",
                     "fp8-hopper-v2x4", "fp8-ada-v2x4", "bf16-hopper-v2x4", "bf16-ampere-v2x4",
                     "fp8-hopper-v3", "fp8-ada-v3", "bf16-hopper-v3", "bf16-ampere-v3") if n in RELATIONS]


def constructed(rel, n, seed):
    """c = +-0; a[0] b[0] and a[1] b[1] = -a[0] b[0] with the largest exponents of the unit; every other product tiny
    (dead at that maximum) or zero."""
    pl = plan(rel.params)
    rng = np.random.default_rng(seed)
    k = rel.k
    sign = 1 << (pl.op_word_bits - 1)
    ef = pl.op_frac
    top = 2**pl.op_exp - 2                             # the largest finite biased exponent field (E4M3: 14 keeps f != 7 free)
    a = np.zeros((n, k), dtype=np.int64)
    b = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        ta, tb_ = int(rng.integers(top - 3, top + 1)), int(rng.integers(top - 3, top + 1))
        fa, fb = int(rng.integers(0, 2**ef)), int(rng.integers(0, 2**ef))
        a[i, 0] = (ta << ef) | fa
        b[i, 0] = (tb_ << ef) | fb
        # the cancelling partner: same magnitude, opposite sign, placed at a random position (group 0 or a later step)
        j = int(rng.integers(1, k))
        a[i, j], b[i, j] = a[i, 0], b[i, 0] ^ sign
        for q in range(1, k):
            if q == j:
                continue
            if rng.random() < 0.7:                        # tiny live products: subnormal / smallest normal operands
                a[i, q] = (int(rng.integers(0, 2)) << (pl.op_word_bits - 1)) | int(rng.integers(0, 2 * 2**ef))
                b[i, q] = int(rng.integers(0, 2 * 2**ef))
    c = np.where(rng.integers(0, 2, size=n) == 1, 1 << 31, 0).astype(np.int64)
    return c, a, b


def check(rel, c, a, b, tag):
    y = np.array([tc_dot(rel.model, int(c[i]), a[i].tolist(), b[i].tolist()) for i in range(len(c))], dtype=np.int64)
    fin = ((y >> 23) & 0xFF) != 0xFF
    c, a, b, y = c[fin], a[fin], b[fin], y[fin]
    zeros = int(((y & 0x7FFFFFFF) == 0).sum())
    p = rel.params
    pl = plan(p)
    out = {}
    for chain in (False, True):
        sys_ = rel.compile(p, chain)
        tb = tables(sys_, "cpu")
        pub = rel.public_vectors(p, c, a, b, y, device="cpu")
        W = build_witness(sys_, pub, rel.hints(p, sys_, c, a, b, y if chain else None, "cpu"), "cpu")
        ok = _accepts(sys_, tb, W, pub)
        rej = torch.nonzero(~ok).flatten().tolist()
        wrong = 0
        if not chain:
            lo = pl.drop if pl.fp8 else 0
            yb = y ^ (1 << np.random.default_rng(1).integers(lo, 31, size=len(y)))
            finb = ((yb >> 23) & 0xFF) != 0xFF
            pubb = rel.public_vectors(p, c[finb], a[finb], b[finb], yb[finb], device="cpu")
            Wb = build_witness(sys_, pubb, rel.hints(p, sys_, c[finb], a[finb], b[finb], None, "cpu"), "cpu")
            wrong = int(_accepts(sys_, tb, Wb, pubb).sum())
        out["chain" if chain else "unit"] = (len(rej), rej[:5], wrong)
    print(f"{rel.name:18s} {tag:12s} units={len(c):4d} zero_words={zeros:4d}  unit: rejected={out['unit'][0]} {out['unit'][1]} "
          f"wrong_accepted={out['unit'][2]}  chain: rejected={out['chain'][0]} {out['chain'][1]}", flush=True)
    return out["unit"][0] + out["chain"][0] + out["unit"][2]


bad = 0
for name in NAMES:
    rel = RELATIONS[name]
    if UNIT is not None and rel.k == len(UNIT["a"]) and plan(rel.params).fp8:
        c = np.array([UNIT["c"]], dtype=np.int64)
        a = np.array([UNIT["a"]], dtype=np.int64)
        b = np.array([UNIT["b"]], dtype=np.int64)
        bad += check(rel, c, a, b, "unit92536")
    c, a, b = constructed(rel, 256, seed=92536)
    bad += check(rel, c, a, b, "constructed")
print("PROBE_BAD", bad)
