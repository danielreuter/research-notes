"""The assessor's late-start search for v2-hot's clause (b) (bc-d7d4b0d1; ratings.md 17:00Z condition 3, and
bc-b58c6093's cancelling-sum case in ttout-restatements.md §8 17:30Z).

Clause (b) of the restated `no-aligned-exact-region/sm120-unpromoted-hot` says no wide exact block starts at atom 6 or
later. Its support is that the accumulator leaves H_i's binade within about 5 atoms, after which the dropped bits are
per word. This asks whether a family can keep it in the binade longer:
- **cancelling families:** clean atom sums of exactly 0 on every column, so only the forming noise moves the accumulator:
  `cancel-pair` (A[2l+1] = −A[2l], B[2l+1] = B[2l]) and `cancel-atom` (A's atoms alternate in sign, B repeats per atom);
- **H/acc swept by the columns' shape** (forming normalises each column, so only shape moves the code RMS against the
  constant 64): `t4` (Student-t(4), the census's), `spiky` (one spike per column, small code RMS, H/acc large) and
  `flat` (signs, code RMS near 448, H/acc small);
- the census's `saturated` and `rank1` as controls.
Everything goes through `pearl_c.form_v1` (both sides noisy) and `pearlc_hot_start.chain` from H_i by the `const` rule,
on the `SM120_UNPROMOTED` atom. Per window [t, t + w): the share of steps exact, each row's share of columns exact over
the window, and the rows-first greedy: the columns on which the r most-exact rows are all exact. Liveness (`live_row`)
is reported for rows and columns, since a family outside the domain doesn't count.
Usage: PYTHONPATH=<tree>/packages/verity/src:<tree>/protocols/pouw:. python3 hot_late_start.py [--rows R] [--cols N]
       [--k K] [--atoms A] [--fams a,b] [--procs P] --out FILE
"""
import argparse
import json
import sys
import time
from multiprocessing import Pool

import numpy as np

from pearlc_hot_start import chain, hot_words
from pearlc_promotion_fusion import f32
from verity_pouw.schemes import pearl_c as C
from verity_pouw.schemes import pearl_c_device as D
from verity_pouw.schemes import pearl_kw as P

STARTS = [0, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40]
WS = [4, 6, 8]
RS = [2, 4, 8, 16, 32, 64]
FAMS = ["saturated@t4", "rank1@t4", "cancel-pair@t4", "cancel-pair@spiky", "cancel-pair@flat", "cancel-atom@t4",
        "cancel-atom@spiky", "saturated@spiky", "saturated@flat"]


def trailing_zeros(mant):
    if mant == 0:
        return 23
    t = 0
    while not (mant >> t) & 1:
        t += 1
    return t


def columns(kind, cols, k, rng):
    if kind == "t4":
        return rng.standard_t(4, (cols, k))
    if kind == "spiky":
        b = rng.standard_normal((cols, k)) * 0.05
        b[np.arange(cols), rng.integers(0, k, cols)] = 1.0
        return b
    if kind == "flat":
        return np.sign(rng.standard_normal((cols, k)))
    raise ValueError(kind)


def sat_values(rng, rows, n):
    v = rng.standard_normal((rows, n)) * 0.1
    v[:, : n // 2] = np.sign(rng.standard_normal((rows, n // 2)))
    return v


def family(name, rows, cols, k, rng):
    base, _, ck = name.partition("@")
    B = columns(ck or "t4", cols, k, rng)
    if base == "saturated":
        return sat_values(rng, rows, k), B
    if base == "rank1":
        v = rng.standard_normal(k)
        return np.outer(rng.standard_normal(rows), v), B
    if base == "cancel-pair":
        v = sat_values(rng, rows, k // 2)
        A = np.empty((rows, k))
        A[:, 0::2], A[:, 1::2] = v, -v
        B[:, 1::2] = B[:, 0::2]
        return A, B
    if base == "cancel-atom":
        a = sat_values(rng, rows, 32)
        sign = np.where((np.arange(k) // 32) % 2 == 0, 1.0, -1.0)
        return np.tile(a, k // 32) * sign, np.tile(B[:, :32], k // 32)
    raise ValueError(base)


def run(job):
    name, k, nrows, ncol, natoms = job
    t0 = time.time()
    rng = np.random.default_rng(abs(hash((name, k, "late-start"))) % 2 ** 32)
    Ax, Bx = family(name, nrows, ncol, k, rng)
    salt = f"{name}/{k}/late-start".encode()
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
    H, c = hot_words(seed_a, FA, FB, "const")
    EX = [[chain(A[i][:32 * natoms], B[j][:32 * natoms], dev, H[i], natoms)[0] for j in range(ncol)] for i in range(nrows)]
    code_rms = float(np.sqrt(np.mean([[P.fp8_to_f32(x) ** 2 for x in col] for col in B[: min(64, ncol)]])))
    out = []
    for w in WS:
        for t in STARTS:
            if t + w > natoms:
                continue
            masks = [sum(1 << j for j in range(ncol) if all(EX[i][j][t:t + w])) for i in range(nrows)]
            step = sum(sum(EX[i][j][t:t + w]) for i in range(nrows) for j in range(ncol)) / (nrows * ncol * w)
            share = [bin(m).count("1") / ncol for m in masks]
            order = sorted(range(nrows), key=lambda i: -share[i])
            acc, rf = (1 << ncol) - 1, {}
            for r in range(1, nrows + 1):
                acc &= masks[order[r - 1]]
                if r in RS:
                    rf[r] = round(bin(acc).count("1") / ncol, 4)
            by = {}
            for s_, h in zip(share, H):
                by.setdefault(min(trailing_zeros(h & 0x7FFFFF), 3), []).append(s_)
            tzc = {str(z): [len(v), round(float(np.mean(v)), 4)] for z, v in sorted(by.items())}
            out.append({"t": t, "w": w, "steps_exact": round(step, 4), "row_share_mean": round(float(np.mean(share)), 4),
                        "row_share_max": round(max(share), 4), "rows_first_common_cols": rf, "share_by_h_tz": tzc})
    return {"family": name, "k": k, "rows": nrows, "cols": ncol, "atoms": natoms, "live_rows": live_a,
            "live_cols": live_b, "col_code_rms": round(code_rms, 1), "secs": round(time.time() - t0),
            "windows": out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=64)
    ap.add_argument("--cols", type=int, default=512)
    ap.add_argument("--k", type=int, default=2048)
    ap.add_argument("--atoms", type=int, default=48)
    ap.add_argument("--fams", default=",".join(FAMS))
    ap.add_argument("--procs", type=int, default=9)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = [(f, a.k, a.rows, a.cols, a.atoms) for f in a.fams.split(",")]
    res = []
    with Pool(a.procs) as pool:
        for r in pool.imap_unordered(run, jobs):
            res.append(r)
            late = [w for w in r["windows"] if w["t"] >= 6 and w["w"] == 6]
            print(json.dumps({"family": r["family"], "live": [r["live_rows"], r["live_cols"]], "col_code_rms": r["col_code_rms"],
                              "secs": r["secs"],
                              "w6": {w["t"]: [w["steps_exact"], w["row_share_mean"], w["rows_first_common_cols"].get(16),
                                              w["rows_first_common_cols"].get(64)] for w in r["windows"] if w["w"] == 6}}),
                  flush=True)
            json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
