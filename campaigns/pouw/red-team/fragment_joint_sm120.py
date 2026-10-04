"""Red-team: which joint skips can a tensor-core prover actually take, on units that pass the verifier's cap?

The census's joint sets are per word. A prover saves W1 only by not issuing an `mma.sync m16n8k32`: one k32 slice for 16
rows of A and 8 rows of B, 128 words at once, priced by its full shape. Re-doing one word's atom on generic cores to patch
around it costs about 700 units (32 exact products and the 26-bit truncating sum at the measured prices of 4-16 units per
op) against 4,096 for the whole MMA, so a (fragment, atom) is worth skipping only if at most about 5 of its 128 words need
it. This script measures, on census-formed operands (s5 forming, the bit-exact sm_120 atom), per cell:
  - the replayed debit share on a 64 × 16 block (lone skips for the pure chain, v2; P1's one-group joint flags for G = 4,
    v1), and whether the block passes the cap ρ (1/1,000 for v2, 1/400 for v1);
  - per-word greedy joint sets on a few words (the hole the unpromoted TT_OUT carries, as the census counts it);
  - on two 16 × 8 fragments: the fragment-wide greedy joint set S (atoms whose skip, with S, leaves all 128 words
    unchanged), its undebited part, and the atoms skippable for at least 123 of 128 words (patchable).
"""
import argparse, importlib.util, json, os, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
ATOM = os.environ.get("CENSUS_ATOM", "sm120-e4m3-k32")     # hopper-e4m3-k32 for the H100 rows
FADD = float(os.environ.get("FADD_UNITS", "8.456"))         # the H100 statement's 32; sm_120 measured 8.456
C.set_atom(ATOM)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

PATCH_MAX = 5


def advance(A, B, t, X, tot, G, skip):
    """One atom of the chain (skipped or not), then the promotion if t ends a group; the pure chain (G = 0) has no total."""
    T = A.shape[1] // 32
    if not skip:
        X, _ = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
    if G and (t % G == G - 1 or t == T - 1):
        tot = (tot + X.astype(np.float32)).astype(np.float32)
        X = np.zeros_like(X)
    return X, tot


def run_from(A, B, t0, X, tot, G, skip=frozenset()):
    """Replay atoms t0 .. T-1 from state (X, tot). Returns the words: the promoted total, or the pure chain's value."""
    for t in range(t0, A.shape[1] // 32):
        X, tot = advance(A, B, t, X, tot, G, t in skip)
    return tot if G else X


def frag_greedy(A, B, G):
    """Fragment-wide sequential greedy: skip atom t (with the atoms already skipped) iff every word's output is unchanged.
    Also counts atoms whose skip leaves at least 128 - PATCH_MAX words unchanged (patchable) though not all."""
    P, k = A.shape
    T = k // 32
    start = (np.zeros(P), np.zeros(P, np.float32) if G else None)
    final = run_from(A, B, 0, *start, G)
    X, tot = start
    S, patch = [], 0
    for t in range(T):
        Xs, ts = advance(A, B, t, X, tot, G, True)
        same = int((run_from(A, B, t + 1, Xs, ts, G) == final).sum())
        if same == P:
            S.append(t)
            X, tot = Xs, ts
        else:
            patch += same >= P - PATCH_MAX
            X, tot = advance(A, B, t, X, tot, G, False)
    assert (run_from(A, B, 0, *start, G, frozenset(S)) == final).all()
    return S, patch


FRAG_ONLY = os.environ.get("FRAG_ONLY") == "1"     # large k: the debit and the greedy on one 16 x 8 fragment only


def cell(job):
    fam, k, G, words = job
    ra, cb = (16, 8) if FRAG_ONLY else (64, 16)
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, ra, cb, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-B"))
    A, B = np.repeat(a, cb, 0), np.tile(b, (ra, 1))                 # w = cb i + j
    T = k // 32
    flags = C.debit_pure(A, B) if G == 0 else C.debit(A, B, G)[0]
    credit_word = k + (FADD * (k / 128 - 1) if G else 0) + 32 * k / 8192 + 4 * 32 + 64 * k / 8192   # rev1's credit
    debit_share = float(flags.mean())
    debit_of_credit = debit_share * 32 * T / credit_word
    cap = 1 / 1000 if G == 0 else 1 / 400
    rng = np.random.default_rng(7)
    pw = []
    for w in rng.choice(A.shape[0], words, replace=False):
        s = C.greedy_pure(A[w:w + 1], B[w:w + 1]) if G == 0 else C.greedy_set(A[w:w + 1], B[w:w + 1], G)
        pw.append(len(s) / T)
    frags = []
    for f0 in ((0,) if FRAG_ONLY else (0, 1)):                   # fragments: A rows 16 f0 .. +16, B rows 0 .. 8
        idx = np.array([cb * i + j for i in range(16 * f0, 16 * f0 + 16) for j in range(8)])
        S, patch = frag_greedy(A[idx], B[idx], G)
        undebited = sum(int((~flags[idx, t]).sum()) for t in S) / (128 * T)
        frags.append({"set_share": len(S) / T, "undebited_share": undebited, "patchable_atoms": patch})
    return {"family": fam, "k": k, "atom": ATOM, "layout": "pure" if G == 0 else f"G{G}", "in_domain": bool(fa and la and fb and lb),
            "debit_share": debit_share, "debit_of_credit": debit_of_credit, "cap": cap,
            "passes_cap": bool(debit_of_credit <= cap), "per_word_joint_share_mean": float(np.mean(pw)) if pw else None,
            "per_word_joint_share_max": float(np.max(pw)) if pw else None, "fragments": frags,
            "fragment_undebited_max": max(f["undebited_share"] for f in frags),
            "fragment_patchable_max": max(f["patchable_atoms"] for f in frags)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default="")
    ap.add_argument("--words", type=int, default=4)
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    jobs = []
    for spec in args.jobs.split(";"):
        fam, k, G = spec.split(",")
        jobs.append((fam, int(k), int(G), args.words))
    with Pool(min(args.procs, len(jobs))) as pool:
        cells = []
        for r in pool.imap_unordered(cell, jobs):
            cells.append(r)
            print(json.dumps(r), flush=True)
    inside = [c for c in cells if c["in_domain"] and c["passes_cap"]]
    meas = [("cells", len(cells), "cells"), ("cells_inside_cap", len(inside), "cells"),
            ("fragment_undebited_max_inside_cap", max((c["fragment_undebited_max"] for c in inside), default=0.0), "fraction"),
            ("fragment_patchable_max_inside_cap", max((c["fragment_patchable_max"] for c in inside), default=0), "atoms"),
            ("per_word_joint_max_inside_cap", max((c["per_word_joint_share_max"] or 0 for c in inside), default=0.0),
             "fraction")]
    rt_result.write("fragment-joint-sm120", meas, {"cells": cells, "patch_max": PATCH_MAX},
                    detail="bit-exact sm_120 atom, s5 forming; per-word vs fragment-wide joint skips on units that pass the cap")


if __name__ == "__main__":
    main()
