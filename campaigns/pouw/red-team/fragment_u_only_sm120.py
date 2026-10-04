"""Red-team for `tt-out-u/*` (TT_OUT over U alone, `internal/pouw/ttout-restatements.md` §3): skips that move C̃ only inside
the bits U ignores.

Under U-only binding a skip set is free whenever every checked U word is unchanged, even if C̃ moves. The (C̃, U) rows'
fragment test (`fragment-joint-skips.md`) is rerun with that weaker acceptance, on the scheme's own replay: `form_v1`,
`peel_factors_*` and `pearl_c.peel` at the device record, with the chain replays vectorized on `pearlc_census.step` (checked
against `pearl_c.chain` word for word). One 16 × 8 MMA fragment per cell:
  - fragment-wide sequential greedy: skip atom t (with the atoms already taken) iff all 128 U words are unchanged; how many
    of the taken atoms move C̃ (the hole U-only opens), their part beyond the (C̃-based) debit, and the patchable atoms
    (U unchanged on at least 123 of 128 words);
  - per word, the same greedy on one word (the census's search against U, singles), and how many words share an atom;
  - the fragment's debit share (lone skips for G = none, P1's one-group joint flags for G = 4) against the cap.
"""
import argparse, importlib.util, json, os, random, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TREE = Path(os.environ.get("SCHEME_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
sys.path[:0] = [str(TREE / "packages/verity/src"), str(TREE / "protocols/pouw"), str(HERE)]
_spec = importlib.util.spec_from_file_location("pearlc_census", Path(os.environ.get("CENSUS_FILE", HERE / "pearlc_census.py")))
CE = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = CE
_spec.loader.exec_module(CE)
CE.set_atom("sm120-e4m3-k32")
from verity_pouw.schemes import pearl_c as PC  # noqa: E402
from verity_pouw.schemes import pearl_c_device as D  # noqa: E402
from verity_pouw.schemes import pearl_kw as P  # noqa: E402
from pearlc_promotion_fusion import family as base_family, f32  # noqa: E402
import rt_result  # noqa: E402

PATCH_MAX = 5
ROWS, COLS = 16, 8


def family(name, k, rng, pos):
    if name.startswith("aligned-spikes-pm1-r") and name != "aligned-spikes-pm1-r444":
        R = float(name.removeprefix("aligned-spikes-pm1-r"))
        x = [rng.choice((-1.0, 1.0)) for _ in range(k)]
        for p in pos:
            x[p] = R * rng.choice((-1, 1))
        return x
    return base_family(name, k, rng, pos)


def build(dev, fam, k):
    rng = random.Random(f"{fam}/{k}/fragment")
    pos = sorted(rng.sample([l for l in range(k) if l % 8], k // 64))
    salt = f"{fam}/{k}/{dev.name}/fragment".encode()
    seed_b, seed_a = PC._labelled(salt + b"B", "seed-B"), PC._labelled(salt + b"A", "seed-A")
    rows_a = [[f32(v) for v in family(fam, k, rng, pos)] for _ in range(ROWS)]
    rows_b = [[f32(v) for v in family(fam, k, rng, pos)] for _ in range(COLS)]
    e_a = [P.sample_line(seed_a, 0, 0, i) for i in range(ROWS)]
    e_b = [P.sample_line(seed_b, 1, 0, i) for i in range(COLS)]
    a = PC.form_v1(rows_a, e_a, PC._basis(seed_b, 0, k, PC.LINE_NORM_V1), dev)
    b = PC.form_v1(rows_b, e_b, PC._basis(seed_b, 1, k, PC.LINE_NORM_V1), dev)
    pa = PC.peel_factors_a(a.codes, PC.scaled_noise(a, e_a), seed_b, k, PC.LINE_NORM_V1, dev)
    pb = PC.peel_factors_b(b.codes, PC.scaled_noise(b, e_b), seed_b, k, PC.LINE_NORM_V1, dev)
    ok = all(P.f32_of_bits(r) * P.f32_of_bits(al) >= P.SIGMA_MIN and PC.live_row(row)
             for side in (a, b) for r, al, row in zip(side.rho, side.alpha, side.x))
    return a, b, pa, pb, ok


def advance(A, B, t, X, tot, G, skip):
    T = A.shape[1] // 32
    if not skip:
        X, _ = CE.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
    if G and (t % G == G - 1 or t == T - 1):
        tot = (tot + X.astype(np.float32)).astype(np.float32)
        X = np.zeros_like(X)
    return X, tot


def run_from(A, B, t0, X, tot, G):
    for t in range(t0, A.shape[1] // 32):
        X, tot = advance(A, B, t, X, tot, G, False)
    return tot if G else X.astype(np.float32)


def bits(words):
    w = np.asarray(words, np.float32).view(np.uint32).astype(np.int64)
    return np.where(w == 0x80000000, 0, w)


def cell(job):
    devname, fam, k, per_word = job
    dev = D.DEVICES[devname]
    G = dev.g or 0
    a, b, pa, pb, in_domain = build(dev, fam, k)
    A = np.repeat(np.array(a.codes, np.uint8), COLS, 0)
    B = np.tile(np.array(b.codes, np.uint8), (ROWS, 1))
    ij = [(w // COLS, w % COLS) for w in range(ROWS * COLS)]
    start = (np.zeros(len(ij)), np.zeros(len(ij), np.float32) if G else None)
    c0 = bits(run_from(A, B, 0, *start, G))
    check = [PC.chain(a.codes[i], b.codes[j], dev) for i, j in ij[:4]]
    assert list(c0[:4]) == check, (list(c0[:4]), check)
    u0 = [PC.peel(int(c0[w]), pa[i], pb[j], dev) for w, (i, j) in enumerate(ij)]
    peel = lambda w, c: PC.peel(int(c), pa[ij[w][0]], pb[ij[w][1]], dev)  # noqa: E731
    T = k // 32
    flags = CE.debit_pure(A, B) if G == 0 else CE.debit(A, B, G)[0]
    X, tot = start
    S, moved, patch = [], 0, 0
    for t in range(T):
        Xs, ts = advance(A, B, t, X, tot, G, True)
        c = bits(run_from(A, B, t + 1, Xs, ts, G))
        fails = 0
        for w in np.flatnonzero(c != c0):
            if peel(w, c[w]) != u0[w]:
                fails += 1
                if fails > PATCH_MAX:
                    break
        if fails == 0:
            S.append(t)
            moved += bool((c != c0).any())
            X, tot = Xs, ts
        else:
            patch += fails <= PATCH_MAX
            X, tot = advance(A, B, t, X, tot, G, False)
    undebited = sum(int((~flags[:, t]).sum()) for t in S) / (len(ij) * T)
    pw_sets, pw_moved = [], []
    for w in range(min(per_word, len(ij))):
        Aw, Bw = A[w:w + 1], B[w:w + 1]
        st = (np.zeros(1), np.zeros(1, np.float32) if G else None)
        Xw, tw = st
        Sw, mv = [], 0
        for t in range(T):
            Xs, ts = advance(Aw, Bw, t, Xw, tw, G, True)
            c = bits(run_from(Aw, Bw, t + 1, Xs, ts, G))[0]
            if c == c0[w] or peel(w, c) == u0[w]:
                Sw.append(t)
                mv += c != c0[w]
                Xw, tw = Xs, ts
            else:
                Xw, tw = advance(Aw, Bw, t, Xw, tw, G, False)
        pw_sets.append(Sw)
        pw_moved.append(mv)
    share = Counter(t for s in pw_sets for t in s)
    fadd = 8.456
    credit_word = k + (fadd * (k / 128 - 1) if G else 0) + 32 * k / 8192 + 4 * 32 + 64 * k / 8192
    debit_of_credit = float(flags.mean()) * 32 * T / credit_word
    cap = 1 / 1000 if G == 0 else 1 / 400
    return {"device": devname, "family": fam, "k": k, "in_domain": bool(in_domain), "debit_of_credit": debit_of_credit,
            "cap": cap, "passes_cap": bool(debit_of_credit <= cap),
            "fragment_u_set_share": len(S) / T, "fragment_u_set_moving_c": moved, "fragment_u_undebited_share": undebited,
            "fragment_u_patchable_atoms": patch,
            "per_word_words": len(pw_sets),
            "per_word_u_set_share_mean": float(np.mean([len(s) / T for s in pw_sets])) if pw_sets else None,
            "per_word_u_set_share_max": float(max(len(s) / T for s in pw_sets)) if pw_sets else None,
            "per_word_u_moving_c_mean": float(np.mean(pw_moved)) if pw_moved else None,
            "max_words_sharing_an_atom": max(share.values(), default=0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--devices", default="sm120,sm120-unpromoted")
    ap.add_argument("--families", default="gaussian,constant,laplace,small-integers,zero-slices,aligned-spikes-pm1-r48,"
                                          "aligned-spikes-pm1-r56,aligned-spikes-pm1-r444")
    ap.add_argument("--ks", default="1024,8192")
    ap.add_argument("--per-word", type=int, default=128)
    ap.add_argument("--procs", type=int, default=32)
    args = ap.parse_args()
    jobs = [(d, f, int(k), args.per_word) for d in args.devices.split(",") for f in args.families.split(",")
            for k in args.ks.split(",")]
    cells = []
    with Pool(min(args.procs, len(jobs))) as pool:
        for r in pool.imap_unordered(cell, jobs):
            cells.append(r)
            print(json.dumps(r), flush=True)
    inside = [c for c in cells if c["in_domain"] and c["passes_cap"]]
    meas = [("cells", len(cells), "cells"), ("cells_inside_cap", len(inside), "cells"),
            ("fragment_u_undebited_max_inside_cap", max((c["fragment_u_undebited_share"] for c in inside), default=0.0),
             "fraction"),
            ("fragment_u_moving_atoms_max_inside_cap", max((c["fragment_u_set_moving_c"] for c in inside), default=0), "atoms"),
            ("fragment_u_patchable_max_inside_cap", max((c["fragment_u_patchable_atoms"] for c in inside), default=0), "atoms"),
            ("per_word_u_set_share_max_inside_cap", max((c["per_word_u_set_share_max"] or 0 for c in inside), default=0.0),
             "fraction")]
    rt_result.write("fragment-u-only-sm120", meas, {"cells": cells, "patch_max": PATCH_MAX},
                    detail="U-only acceptance: skips that move C~ only inside U's slack; scheme replay + census atom")


if __name__ == "__main__":
    main()
