"""P2, per-row seeds (`tt-out/pearl-c-sm120-rowseed`): does grinding rows one at a time let a prover align a fragment?

With per-row seeds a row's noise is fixed by that row's bytes and position alone, so a prover can draw q variants of each row
(fresh noise each) and keep the one that suits the rows before it: Σ q calls buy Π q combinations. Under fragment pricing a
skip pays only when all 128 words of an `mma.sync m16n8k32` fragment (16 rows of A x 8 rows of B) agree on it, which the
unit-seeded census never saw (0 fragment-wide on passing units, `fragment-joint-skips.md`). This grinds for it:
  - rows 0 .. 15 of one fragment each get q candidate rows of the family (independent background, fresh s5 noise);
  - row 0 takes the candidate with the largest joint set S over its 8 words (pairs neither atom of which skips alone, then
    singles, packed greedily, as the census's per-word greedy but required of all 8 words);
  - each later row takes the candidate that keeps the most of S's units jointly skippable on its 8 words (greedy, in order),
    and S shrinks to what it keeps;
  - on the final 16 x 8 fragment: |S| / T, its undebited part (the replayed debit, v2's lone flags or rev1's one-group
    joint flags), and whether the fragment's debit passes the cap; then S's transfer to other column blocks (other B rows).
q = 1 is the unit-seeded baseline (no choice). Run from a tree with benchmarks/pouw/pearlc_census.py (CENSUS_TREE or the
research source tree).
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
FADD = 8.456
BLOCKS = 4


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


def start(P, G):
    return np.zeros(P), (np.zeros(P, np.float32) if G else None)


def greedy_over(A, B, G, cand):
    """Sequential greedy over the atoms in `cand` (in order): keep t if skipping it, with those kept, leaves every word."""
    P = A.shape[0]
    final = run_from(A, B, 0, *start(P, G), G)
    X, tot = start(P, G)
    kept = []
    cand = set(cand)
    for t in range(A.shape[1] // 32):
        if t in cand:
            Xs, ts = advance(A, B, t, X, tot, G, True)
            if (run_from(A, B, t + 1, Xs, ts, G) == final).all():
                kept.append(t)
                X, tot = Xs, ts
                continue
        X, tot = advance(A, B, t, X, tot, G, False)
    return kept


def pair_units(A, B, G):
    """Joint-skip units over all P words at once: atom pairs (t1, t2) whose joint skip leaves every word unchanged while
    neither atom alone does (batched over t2, as the census's per-word greedy does), then single atoms. Returns the units
    packed greedily (pairs first), each replayed on all P words."""
    P, k = A.shape
    T = k // 32
    final = run_from(A, B, 0, *start(P, G), G)
    alone = []
    X, tot = start(P, G)
    states = []
    for t in range(T):
        states.append((X.copy(), None if tot is None else tot.copy()))
        X, tot = advance(A, B, t, X, tot, G, False)
    for t in range(T):
        Xs, ts = advance(A, B, t, *states[t], G, True)
        alone.append(bool((run_from(A, B, t + 1, Xs, ts, G) == final).all()))
    pairs = []
    for t1 in range(T - 1):
        if alone[t1]:
            continue
        nb = T - t1 - 1
        X0, t0 = advance(A, B, t1, *states[t1], G, True)
        X = np.tile(X0, nb)
        tt = None if t0 is None else np.tile(t0, nb)
        Ab, Bb = np.tile(A, (nb, 1)), np.tile(B, (nb, 1))
        for h in range(t1 + 1, T):
            live = np.repeat(np.arange(nb) != h - t1 - 1, P)
            if live.any():
                D, _ = C.step(X, Ab[:, 32 * h:32 * h + 32], Bb[:, 32 * h:32 * h + 32])
                X = np.where(live, D, X)
            if G and (h % G == G - 1 or h == T - 1):
                tt = (tt + X.astype(np.float32)).astype(np.float32)
                X = np.zeros_like(X)
        got = (tt if G else X).reshape(nb, P)
        for bi in np.flatnonzero((got == final).all(1)):
            t2 = t1 + 1 + int(bi)
            if not alone[t2]:
                pairs.append((t1, t2))
    return pack(A, B, G, [p for p in pairs] + [(t,) for t in range(T)])


def pack(A, B, G, units):
    """Keep units greedily, in order, while the joint skip of everything kept leaves every word unchanged."""
    P = A.shape[0]
    final = run_from(A, B, 0, *start(P, G), G)
    kept, S = [], set()
    for u in units:
        if S & set(u):
            continue
        if (run_from(A, B, 0, *start(P, G), G, frozenset(S | set(u))) == final).all():
            kept.append(u)
            S |= set(u)
    return kept


def atoms(units):
    return sorted({t for u in units for t in u})


def pair(a_rows, b_rows):
    """Words w = 8 i + j of rows a_rows x b_rows (8 of them), as the chain's row-aligned operand pairs."""
    return np.repeat(a_rows, b_rows.shape[0], 0), np.tile(b_rows, (a_rows.shape[0], 1))


def cell(job):
    fam, k, G, q = job
    T = k // 32
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, 16 * q, 8 * BLOCKS, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, q, "rowseed-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, q, "rowseed-B"))
    b0 = b[:8]
    cands = [[a[r * q + c:r * q + c + 1] for c in range(q)] for r in range(16)]
    word_sets = [len(atoms(pair_units(cands[0][c], b0[:1], G))) for c in range(min(q, 2))]
    # row 0: the candidate with the largest joint set over its 8 words
    best = max(((len(atoms(u)), c, u) for c in range(q) for u in [pair_units(*pair(cands[0][c], b0), G)]), key=lambda x: (x[0], -x[1]))
    S, chosen, trace = best[2], [cands[0][best[1]]], [best[0]]
    for r in range(1, 16):
        if not S:
            chosen.append(cands[r][0])
            trace.append(0)
            continue
        opts = [(len(atoms(kept)), c, kept) for c in range(q) for kept in [pack(*pair(cands[r][c], b0), G, S)]]
        n, c, kept = max(opts, key=lambda x: (x[0], -x[1]))
        chosen.append(cands[r][c])
        S = kept
        trace.append(n)
    A16 = np.concatenate(chosen, 0)
    Af, Bf = pair(A16, b0)
    S = atoms(pack(Af, Bf, G, S))                               # replay S on the whole fragment
    flags = C.debit_pure(Af, Bf) if G == 0 else C.debit(Af, Bf, G)[0]
    credit_word = k + (FADD * (k / 128 - 1) if G else 0) + 32 * k / 8192 + 4 * 32 + 64 * k / 8192
    debit_of_credit = float(flags.mean()) * 32 * T / credit_word
    cap = 1 / 1000 if G == 0 else 1 / 400
    undebited = sum(int((~flags[:, t]).sum()) for t in S) / (128 * T)
    transfer = []
    for blk in range(1, BLOCKS):
        kept = atoms(pack(*pair(A16, b[8 * blk:8 * blk + 8]), G, [(t,) for t in S])) if S else []
        transfer.append(len(kept))
    return {"family": fam, "k": k, "layout": "pure" if G == 0 else f"G{G}", "q": q,
            "in_domain": bool(np.all(fa) and np.all(la) and np.all(fb) and np.all(lb)),
            "single_word_sets": word_sets, "row0_set": trace[0], "trace": trace, "fragment_set_atoms": len(S), "fragment_set_share": len(S) / T,
            "fragment_undebited_share": undebited, "fragment_debit_of_credit": debit_of_credit, "cap": cap,
            "passes_cap": bool(debit_of_credit <= cap), "transfer_atoms_other_blocks": transfer}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--qs", default="1,16")
    ap.add_argument("--families", default="aligned-spikes-r56,aligned-spikes-r64,aligned-spikes-pm1-r64,gaussian")
    ap.add_argument("--layouts", default="4,0")
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    jobs = [(f, args.k, int(G), int(q)) for f in args.families.split(",") for G in args.layouts.split(",")
            for q in args.qs.split(",")]
    with Pool(min(args.procs, len(jobs))) as pool:
        for r in pool.imap_unordered(cell, jobs):
            print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main()
