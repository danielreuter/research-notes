"""`FragDraw Λ` (bc-3006c44a, `a-commit-latency.md` "The fragment argument, made rigorous"): the per-draw count
  Y_i = #{(J, t) : t lies in an undebited skippable set of every word (i, j), j ∈ J},
measured directly, and its named falsifier: rows built from B̃'s columns (the prover sees B̃ before it fixes a row).

Per word, `U_j` = the atoms in some jointly skippable pair of that word (skipping both leaves its final value; neither alone
does, as the census's greedy defines the hole), minus the atoms the replayed debit flags (v2: lone skips; rev1: every atom
of a one-group joint set). Pairs lower-bound the skippable sets, so |∩_j U_j| lower-bounds Y's term for the group J. Each
row is measured against one fixed group of 8 B̃ columns.

Constructions (each row in the domain, fresh s5 noise per row):
  fresh         the family's own row (aligned-spikes-r64: +R at 128g + 1 and 128g + 9)
  sign-spikes   the family's spike budget (k/64 entries, off the every-8th positions) placed where the 8 columns' codes
                agree in sign and are largest, each spike signed to make all 8 products positive
  early-spike   one spike in atom 0 at the position whose 8 column codes best agree, signed likewise, of the largest size
                the domain allows; the rest Gaussian
  correlated    a dense row: the sign-aligned mean of the 8 columns' values plus Gaussian, so every word's partial sums grow
"""
import argparse
import importlib.util
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
C.set_atom(os.environ.get("CENSUS_ATOM", "sm120-e4m3-k32"))


def dec_table():
    v = np.zeros(256)
    for c in range(256):
        e, m = (c >> 3) & 15, c & 7
        x = (1 + m / 8) * 2.0 ** (e - 7) if e else m * 2.0 ** -9
        v[c] = -x if c & 0x80 else x
    v[0x7F] = v[0xFF] = 0.0
    return v


DEC = dec_table()


def advance(A, B, t, X, tot, G, skip):
    T = A.shape[1] // 32
    if not skip:
        X, _ = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
    if G and (t % G == G - 1 or t == T - 1):
        tot = (tot + X.astype(np.float32)).astype(np.float32)
        X = np.zeros_like(X)
    return X, tot


def run_from(A, B, t0, X, tot, G, skip=frozenset()):
    for t in range(t0, A.shape[1] // 32):
        X, tot = advance(A, B, t, X, tot, G, t in skip)
    return tot if G else X


def pair_members(A, B, G):
    """Per word (row of A, B): the atoms in some skippable pair, neither atom of which skips alone. Returns (P, T) bools."""
    P, k = A.shape
    T = k // 32
    start = (np.zeros(P), np.zeros(P, np.float32) if G else None)
    final = run_from(A, B, 0, *start, G)
    states, (X, tot) = [], start
    for t in range(T):
        states.append((X.copy(), None if tot is None else tot.copy()))
        X, tot = advance(A, B, t, X, tot, G, False)
    alone = np.zeros((P, T), bool)
    for t in range(T):
        Xs, ts = advance(A, B, t, *states[t], G, True)
        alone[:, t] = run_from(A, B, t + 1, Xs, ts, G) == final
    member = np.zeros((P, T), bool)
    for t1 in range(T - 1):
        nb = T - t1 - 1
        X0, t0 = advance(A, B, t1, *states[t1], G, True)
        X = np.tile(X0, nb)
        tt = None if t0 is None else np.tile(t0, nb)
        Ab, Bb = np.tile(A, (nb, 1)), np.tile(B, (nb, 1))
        for h in range(t1 + 1, T):
            live = np.repeat(np.arange(nb) != h - t1 - 1, P)
            D, _ = C.step(X, Ab[:, 32 * h:32 * h + 32], Bb[:, 32 * h:32 * h + 32])
            X = np.where(live, D, X)
            if G and (h % G == G - 1 or h == T - 1):
                tt = (tt + X.astype(np.float32)).astype(np.float32)
                X = np.zeros_like(X)
        ok = ((tt if G else X).reshape(nb, P) == final).T          # (P, nb): word p, second atom t1 + 1 + b
        for p in range(P):
            for bi in np.flatnonzero(ok[p]):
                t2 = t1 + 1 + int(bi)
                if not alone[p, t1] and not alone[p, t2]:
                    member[p, t1] = member[p, t2] = True
    return member


def build(kind, k, b, rng, R):
    """One row of x (FP64) for a construction, given B̃'s 8 columns' codes b (8, k)."""
    x = rng.standard_normal(k)
    vb = DEC[b]                                                     # (8, k) values
    off = np.array([l for l in range(k) if l % 8])
    if kind == "fresh":
        x[np.array([l for g in range(k // 128) for l in (128 * g + 1, 128 * g + 9)])] = R
    elif kind == "sign-spikes":
        agree = np.abs(np.sign(vb).sum(0))                          # 8 when all 8 columns agree in sign
        score = np.where(agree[off] == 8, np.abs(vb[:, off]).min(0), -1.0)
        pos = off[np.argsort(-score)[:k // 64]]
        x[pos] = R * np.sign(vb[:, pos].sum(0))
    elif kind == "early-spike":
        cand = off[off < 32]
        agree = np.abs(np.sign(vb[:, cand]).sum(0))
        score = np.where(agree == 8, np.abs(vb[:, cand]).min(0), -1.0)
        p = cand[int(np.argmax(score))]
        x[p] = 400.0 * np.sign(vb[:, p].sum())                      # s + 4ρ ≤ 448 ρ keeps ρα ≥ 1 (ρ ≈ 1)
    elif kind == "correlated":
        s = np.sign(vb.sum(0))
        x = s * np.abs(vb).mean(0) / (np.abs(vb).mean() + 1e-12) + 0.5 * rng.standard_normal(k)
    return x


def job(args):
    kind, k, G, n0, n1, R = args
    T = k // 32
    _, XB, _, _ = C.family_rows("aligned-spikes-r64", k, 1.0, 1, 8, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, "fragdraw", k, "B"))[0]
    rng = np.random.default_rng(abs(hash((kind, k, G, n0))) % 2 ** 32)
    out = []
    for r in range(n0, n1):
        x = build(kind, k, b, rng, R)[None, :]
        a, _, _, fa, la = C.form_s5(x, FcA, 1.0, 16.0, C._rng(1, "fragdraw", k, kind, G, r))
        A, B = np.repeat(a, 8, 0), b
        flags = C.debit_pure(A, B) if G == 0 else C.debit(A, B, G)[0]
        U = pair_members(A, B, G) & ~flags
        out.append({"in_domain": bool(fa and la), "Y": int(U.all(0).sum()), "U_mean": float(U.sum(1).mean()),
                    "U_max": int(U.sum(1).max()), "flagged_mean": float(flags.sum(1).mean())})
    return kind, G, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=48)
    ap.add_argument("--kinds", default="fresh,sign-spikes,early-spike,correlated")
    ap.add_argument("--layouts", default="0,4")
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    R = 64.0
    step = 4
    jobs = [(kd, args.k, int(G), lo, min(lo + step, args.rows), R) for kd in args.kinds.split(",")
            for G in args.layouts.split(",") for lo in range(0, args.rows, step)]
    agg = {}
    with Pool(args.procs) as pool:
        for kind, G, out in pool.imap_unordered(job, jobs):
            agg.setdefault((kind, G), []).extend(out)
    for (kind, G), rows in sorted(agg.items()):
        Y = np.array([r["Y"] for r in rows])
        print(json.dumps({"construction": kind, "k": args.k, "layout": "pure" if G == 0 else f"G{G}", "rows": len(rows),
                          "in_domain": all(r["in_domain"] for r in rows), "Y_max": int(Y.max()), "Y_mean": float(Y.mean()),
                          "rows_with_Y": int((Y > 0).sum()), "Y_hist": {int(v): int((Y == v).sum()) for v in np.unique(Y)},
                          "U_mean": float(np.mean([r["U_mean"] for r in rows])), "U_max": max(r["U_max"] for r in rows),
                          "flagged_mean": float(np.mean([r["flagged_mean"] for r in rows]))}), flush=True)


if __name__ == "__main__":
    main()
