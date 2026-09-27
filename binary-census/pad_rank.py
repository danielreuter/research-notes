"""Empirical redraw rates for the link's zero-knowledge pad (GF(2^128), GHASH polynomial x^128 + x^7 + x^2 + x + 1).

y_k = zhat(r_k) includes the pad contribution sum_j s_j eq(r_k, j) over the pad positions j. y is uniform iff the
GF(2)-linear map s -> (pad contributions) is onto. We measure how often it is not (the redraw event).
"""
from __future__ import annotations

import random
import sys

POLY = (1 << 128) | 0x87  # x^128 + x^7 + x^2 + x + 1
MASK = (1 << 128) - 1


def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a ^= POLY
    return r


def eq_table(r):
    """eq(r, j) for j in {0,1}^len(r), j's bit k <-> coordinate k (little-endian)."""
    t = [1]
    for rk in r:
        one_plus = rk ^ 1
        nt = [0] * (2 * len(t))
        for j, v in enumerate(t):
            nt[j] = gmul(v, one_plus)          # bit k = 0 -> factor (1 + r_k)
            nt[j + len(t)] = gmul(v, rk)       # bit k = 1 -> factor r_k
        t = nt
    return t


def rank_gf2(rows):
    rows = [r for r in rows if r]
    rank = 0
    pivots = {}
    for r in rows:
        while r:
            p = r.bit_length() - 1
            if p in pivots:
                r ^= pivots[p]
            else:
                pivots[p] = r
                rank += 1
                break
    return rank


def matrix_rows(columns, nbits):
    """columns: list of K elements (each a 128-bit int) -> 128 row bitmasks over the columns (GF(2) matrix rows)."""
    rows = [0] * nbits
    for c, v in enumerate(columns):
        for t in range(nbits):
            if v >> t & 1:
                rows[t] |= 1 << c
    return rows


def trial_single(rng, d, m=24):
    r = [rng.getrandbits(128) for _ in range(m)]
    lo, hi = r[:d], r[d:]
    h = [1] * (m - d)  # pad at the all-ones high index (any fixed index works)
    e = 1
    for rk, hk in zip(hi, h):
        e = gmul(e, rk if hk else rk ^ 1)
    cols = [gmul(e, v) for v in eq_table(lo)]
    return rank_gf2(matrix_rows(cols, 128)) == 128 and e != 0


def trial_two_points(rng, d, blocks, m=24):
    """Two independent points; `blocks` pad sub-cubes of dimension d at distinct high indices."""
    pts = [[rng.getrandbits(128) for _ in range(m)] for _ in range(2)]
    highs = [[(b >> k) & 1 for k in range(m - d)] for b in range(1, blocks + 1)]
    rows = [0] * 256
    col = 0
    for h in highs:
        per_point = []
        for p, r in enumerate(pts):
            lo, hi = r[:d], r[d:]
            e = 1
            for rk, hk in zip(hi, h):
                e = gmul(e, rk if hk else rk ^ 1)
            if e == 0:
                return False
            per_point.append([gmul(e, v) for v in eq_table(lo)])
        for j in range(1 << d):
            for p in range(2):
                v = per_point[p][j]
                for t in range(128):
                    if v >> t & 1:
                        rows[128 * p + t] |= 1 << col
            col += 1
    return rank_gf2(rows) == 256


if __name__ == "__main__":
    rng = random.Random(2026)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    res = {}
    for d in (7, 8, 9):
        ok = sum(trial_single(rng, d) for _ in range(n))
        res[f"one point, one pad sub-cube of 2^{d} bits"] = f"{n - ok}/{n} redraws"
    for d, blocks in ((8, 1), (8, 2), (9, 1), (8, 4)):
        ok = sum(trial_two_points(rng, d, blocks) for _ in range(n))
        res[f"two points, {blocks} pad sub-cube(s) of 2^{d} bits ({blocks << d} pad bits)"] = f"{n - ok}/{n} redraws"
    for k, v in res.items():
        print(f"{k}: {v}")
