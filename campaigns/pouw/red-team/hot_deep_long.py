"""Clause (b) at long tails for k up to 65,536 (the assessor, bc-d7d4b0d1; ratings.md 2:48 PM PDT, condition 1): one
family per run, the chain of `hot_deep.py` to k/32 atoms. Per-step exactness by atom band, and for windows of L atoms at
the given starts, the words exact over the whole window and the rows-first common columns of the r most-exact rows.
usage: hot_deep_long.py --family F [--k 65536] [--rows 64] [--cols 128] [--lens 253,1024] [--starts ...] --out FILE
"""
import argparse
import json
import time

import numpy as np

import hot_deep as HD
from pearlc_hot_start import chain, hot_words
from pearlc_promotion_fusion import f32
from verity_pouw.schemes import pearl_c as C
from verity_pouw.schemes import pearl_c_device as D
from verity_pouw.schemes import pearl_kw as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--k", type=int, default=65536)
    ap.add_argument("--rows", type=int, default=64)
    ap.add_argument("--cols", type=int, default=128)
    ap.add_argument("--lens", default="253,1024")
    ap.add_argument("--starts", default="4,128,255,512,1024,1536,1790")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    k, nrows, ncol, name = a.k, a.rows, a.cols, a.family
    natoms = k // 32
    rng = np.random.default_rng(abs(hash((name, k, "deep"))) % 2 ** 32)
    Ax, Bx = HD.family(name, nrows, ncol, k, rng)
    salt = f"{name}/{k}/deep".encode()
    seed_b = C._labelled(salt + b"B", "seed-B")
    seed_a = C._labelled(salt + b"A", "seed-A")
    dev = D.SM120_UNPROMOTED
    cols = [[f32(float(v)) for v in row] for row in Bx]
    rows = [[f32(float(v)) for v in row] for row in Ax]
    live = [sum(bool(C.live_row(r)) for r in rows), sum(bool(C.live_row(c)) for c in cols)]
    FB = C.form_v1(cols, [P.sample_line(seed_b, 1, 0, j) for j in range(ncol)], C._basis(seed_b, 1, k, C.LINE_NORM_V1), dev)
    FA = C.form_v1(rows, [P.sample_line(seed_a, 0, 0, i) for i in range(nrows)], C._basis(seed_b, 0, k, C.LINE_NORM_V1), dev)
    A, B = FA.codes, FB.codes
    H, _ = hot_words(seed_a, FA, FB, "const")
    EX = [[chain(A[i], B[j], dev, H[i], natoms)[0] for j in range(ncol)] for i in range(nrows)]
    edges = [0, 8, 64, 256, 512, 1024, 2048]
    bands = {f"{lo}-{hi}": round(sum(sum(EX[i][j][lo:hi]) for i in range(nrows) for j in range(ncol)) / (nrows * ncol * (hi - lo)), 4)
             for lo, hi in zip(edges, edges[1:]) if hi <= natoms}
    windows = {}
    for L in (int(x) for x in a.lens.split(",")):
        for t in (int(x) for x in a.starts.split(",")):
            if t < 4 or t + L > natoms:
                continue
            masks = [sum(1 << j for j in range(ncol) if all(EX[i][j][t:t + L])) for i in range(nrows)]
            order = sorted(range(nrows), key=lambda i: -bin(masks[i]).count("1"))
            acc, rf = (1 << ncol) - 1, {}
            for r in range(1, nrows + 1):
                acc &= masks[order[r - 1]]
                if r in (1, 2, 4, 8, 16):
                    rf[str(r)] = bin(acc).count("1")
            windows[f"{L}@{t}"] = {"words_exact": sum(bin(m).count("1") for m in masks), "of": nrows * ncol,
                                   "rows_first_common_cols": rf}
    json.dump({"family": name, "k": k, "rows": nrows, "cols": ncol, "live": live, "steps_exact_by_band": bands,
               "windows": windows, "secs": round(time.time() - t0)}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
