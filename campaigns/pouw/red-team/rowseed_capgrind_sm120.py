"""P2 (`tt-out/pearl-c-sm120-rowseed`): can per-row grinding steer a tile's replayed debit under the cap?

With per-row seeds a prover can draw q variants of each of a tile's 64 rows and keep the one with the smallest flagged share,
where unit seeds give one draw for the whole tile. For a family the cap rejects (aligned spikes at R = 56 or 64), this forms
N candidate rows against one 64-row block of B (a 64 x 64 tile's columns), computes each row's replayed debit (v2's lone
flags for the pure chain, rev1's one-group joint flags for G = 4) as a share of rev1's credit, and reports the tile's debit
when each of its 64 rows is the best of q disjoint candidates, for q = 1, 2, 4 (N = 256), against the cap.
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


def job(args):
    fam, k, G, n, lo, hi = args
    T = k // 32
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, n, 64, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, n, "capgrind-A"))[0]
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, n, "capgrind-B"))[0]
    credit_word = k + (FADD * (k / 128 - 1) if G else 0) + 32 * k / 8192 + 4 * 32 + 64 * k / 8192
    out = []
    for r in range(lo, hi):
        A, B = np.repeat(a[r:r + 1], 64, 0), b
        flags = C.debit_pure(A, B) if G == 0 else C.debit(A, B, G)[0]
        out.append(float(flags.mean()) * 32 * T / credit_word)
    return fam, G, lo, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--families", default="aligned-spikes-r64,aligned-spikes-r56")
    ap.add_argument("--layouts", default="0,4")
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    step = 8
    jobs = [(f, args.k, int(G), args.n, lo, lo + step) for f in args.families.split(",") for G in args.layouts.split(",")
            for lo in range(0, args.n, step)]
    rows = {}
    with Pool(args.procs) as pool:
        for fam, G, lo, out in pool.imap_unordered(job, jobs):
            rows.setdefault((fam, G), {})[lo] = out
    for (fam, G), parts in sorted(rows.items()):
        d = np.array([x for lo in sorted(parts) for x in parts[lo]])
        cap = 1 / 1000 if G == 0 else 1 / 400
        tiles = {}
        for q in (1, 2, 4):
            if 64 * q <= len(d):
                tiles[q] = float(d[:64 * q].reshape(64, q).min(1).mean())
        print(json.dumps({"family": fam, "k": args.k, "layout": "pure" if G == 0 else f"G{G}", "rows": len(d), "cap": cap,
                          "row_debit_mean": float(d.mean()), "row_debit_sd": float(d.std()), "row_debit_min": float(d.min()),
                          "tile_debit_best_of_q": tiles,
                          "tile_passes_best_of_q": {q: v <= cap for q, v in tiles.items()}}), flush=True)


if __name__ == "__main__":
    main()
