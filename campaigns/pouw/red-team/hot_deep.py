"""Clause (b) at long tails for k > 8,192 (the assessor, bc-d7d4b0d1): does any word stay exact over a 253-atom window
starting at atom 4 or later, on the hot chain at k = 16,384? Same forming and chain as `hot_late_start.py`.
Per family: per-step exactness by atom band, and for windows [t, t + 253) at t = 4, 128, 255, the share of words exact over
the whole window and the rows-first common columns of the r most-exact rows.
Families: the census controls, `cancel-pair` (half ±1 pairs, half 0.1·N pairs, as before), and `cancel-full` (every entry a
±1 pair, all products coarse), the likeliest to keep every step exact deep into the chain.
"""
import argparse
import json
import time
from multiprocessing import Pool

import numpy as np

import hot_late_start as H
from pearlc_hot_start import chain, hot_words
from pearlc_promotion_fusion import f32
from verity_pouw.schemes import pearl_c as C
from verity_pouw.schemes import pearl_c_device as D
from verity_pouw.schemes import pearl_kw as P

L_LONG = 253
STARTS = [4, 128, 255]
BANDS = [(0, 8), (8, 64), (64, 256), (256, 512)]


def family(name, rows, cols, k, rng):
    base, _, ck = name.partition("@")
    if base == "cancel-full":
        B = H.columns(ck or "t4", cols, k, rng)
        v = np.sign(rng.standard_normal((rows, k // 2)))
        A = np.empty((rows, k))
        A[:, 0::2], A[:, 1::2] = v, -v
        B[:, 1::2] = B[:, 0::2]
        return A, B
    if base == "saturated-full":
        return np.sign(rng.standard_normal((rows, k))), H.columns(ck or "t4", cols, k, rng)
    return H.family(name, rows, cols, k, rng)


def run(job):
    name, k, nrows, ncol = job
    t0 = time.time()
    natoms = k // 32
    rng = np.random.default_rng(abs(hash((name, k, "deep"))) % 2 ** 32)
    Ax, Bx = family(name, nrows, ncol, k, rng)
    salt = f"{name}/{k}/deep".encode()
    seed_b = C._labelled(salt + b"B", "seed-B")
    seed_a = C._labelled(salt + b"A", "seed-A")
    dev = D.SM120_UNPROMOTED
    cols = [[f32(float(v)) for v in row] for row in Bx]
    rows = [[f32(float(v)) for v in row] for row in Ax]
    live_a = sum(bool(C.live_row(r)) for r in rows)
    live_b = sum(bool(C.live_row(c)) for c in cols)
    FB = C.form_v1(cols, [P.sample_line(seed_b, 1, 0, j) for j in range(ncol)], C._basis(seed_b, 1, k, C.LINE_NORM_V1), dev)
    FA = C.form_v1(rows, [P.sample_line(seed_a, 0, 0, i) for i in range(nrows)], C._basis(seed_b, 0, k, C.LINE_NORM_V1), dev)
    A, B = FA.codes, FB.codes
    Hh, _ = hot_words(seed_a, FA, FB, "const")
    EX = [[chain(A[i], B[j], dev, Hh[i], natoms)[0] for j in range(ncol)] for i in range(nrows)]
    bands = {f"{a}-{b}": round(sum(sum(EX[i][j][a:b]) for i in range(nrows) for j in range(ncol)) / (nrows * ncol * (b - a)), 4)
             for a, b in BANDS}
    longw = {}
    for t in STARTS:
        masks = [sum(1 << j for j in range(ncol) if all(EX[i][j][t:t + L_LONG])) for i in range(nrows)]
        words = sum(bin(m).count("1") for m in masks)
        order = sorted(range(nrows), key=lambda i: -bin(masks[i]).count("1"))
        acc, rf = (1 << ncol) - 1, {}
        for r in range(1, nrows + 1):
            acc &= masks[order[r - 1]]
            if r in (1, 2, 4, 8, 16):
                rf[str(r)] = bin(acc).count("1")
        longw[str(t)] = {"words_exact": words, "of": nrows * ncol, "rows_first_common_cols": rf}
    return {"family": name, "k": k, "rows": nrows, "cols": ncol, "live": [live_a, live_b], "steps_exact_by_band": bands,
            "long_windows_253": longw, "secs": round(time.time() - t0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=64)
    ap.add_argument("--cols", type=int, default=128)
    ap.add_argument("--k", type=int, default=16384)
    ap.add_argument("--fams", default="saturated@t4,rank1@t4,cancel-pair@t4,cancel-full@t4,cancel-full@spiky,saturated-full@t4")
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = []
    with Pool(a.procs) as pool:
        for r in pool.imap_unordered(run, [(f, a.k, a.rows, a.cols) for f in a.fams.split(",")]):
            res.append(r)
            print(json.dumps(r), flush=True)
            json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
