"""P2's named falsifier family (`tt-out/pearl-c-sm120-rowseed`): rows chosen after seeing earlier rows' realized codes.

With per-row seeds the prover sees A′ of rows < j before it fixes x_j. The sign-off expects row j's fresh, full-strength noise
to leave its codes dense whatever x_j is. Families (each row j built from base row i, and base row l, after their forming):
  - duplicate      x_j = x_i (the same row at another position: independent noise)
  - adaptive-copy  x_j = dec(A′_i) with one off-sample entry set so that α_j = 1 exactly-ish: α_j·x_j = A′_i's values
  - shared-prefix  x_j = x_i on [0, k/2), fresh on [k/2, k)
  - low-rank       x_j = x_i + x_l, measured against dec(A′_i) + dec(A′_l)
Reported per family: the share of equal codes, of equal k32 atom slices (all 32 codes, the unit a partial product could be
reused at), of equal FP32 words of C̃ over 8 B rows (v1 rev1's G = 4 chain), and (low-rank) of elements where the codes add.
"""
import argparse
import importlib.util
import json
import os
import sys
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
    v[0x7F] = v[0xFF] = np.nan
    return v


DEC = dec_table()


def chain_words(A, B, G=4):
    T = A.shape[1] // 32
    X, tot = np.zeros(A.shape[0]), np.zeros(A.shape[0], np.float32)
    for t in range(T):
        X, _ = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
        if t % G == G - 1 or t == T - 1:
            tot = (tot + X.astype(np.float32)).astype(np.float32)
            X = np.zeros_like(X)
    return tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=64)
    args = ap.parse_args()
    k, R = args.k, args.rows
    rng = np.random.default_rng(20260930)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    Xi = rng.standard_normal((R, k))
    Xl = rng.standard_normal((R, k))
    XB = rng.standard_t(4, (8, k))
    Ai = C.form_s5(Xi, FcA, 1.0, 16.0, C._rng(1, "adaptive", k, "i"))[0]
    Al = C.form_s5(Xl, FcA, 1.0, 16.0, C._rng(1, "adaptive", k, "l"))[0]
    Bc = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, "adaptive", k, "B"))[0]
    vi, vl = DEC[Ai], DEC[Al]
    fams = {}
    fams["duplicate"] = Xi.copy()
    xa = vi.copy()
    p = 1                                                # off the every-8th sample positions
    for _ in range(3):                                   # the row max M with M + 4ρ = 448, so α_j = 1
        rho = np.sqrt((xa[:, ::8] ** 2).mean(1))
        xa[:, p] = 448.0 - 4 * rho
    fams["adaptive-copy"] = xa
    sp = Xi.copy()
    sp[:, k // 2:] = rng.standard_normal((R, k - k // 2))
    fams["shared-prefix"] = sp
    fams["low-rank"] = Xi + Xl
    out = []
    Wi = chain_words(np.repeat(Ai, 8, 0), np.tile(Bc, (R, 1)))
    for name, Xj in fams.items():
        Aj, _, _, fok, lok = C.form_s5(Xj, FcA, 1.0, 16.0, C._rng(1, "adaptive", k, name))
        eq = Aj == Ai
        mask = np.ones(k, bool)
        if name == "adaptive-copy":
            mask[p] = False
        if name == "shared-prefix":
            mask[k // 2:] = False
        code_eq = float(eq[:, mask].mean())
        atom_eq = float(eq.reshape(R, k // 32, 32).all(2).mean())
        Wj = chain_words(np.repeat(Aj, 8, 0), np.tile(Bc, (R, 1)))
        r = {"family": name, "k": k, "rows": R, "in_domain": bool(fok and lok), "code_equal": code_eq,
             "atom_slice_equal": atom_eq, "word_equal": float((Wj == Wi).mean())}
        if name == "low-rank":
            r["codes_add"] = float((DEC[Aj] == vi + vl).mean())
        if name == "adaptive-copy":
            r["codes_within_one_step"] = float((np.abs(np.searchsorted(np.sort(np.unique(DEC[np.isfinite(DEC)])), DEC[Aj]) -
                                                     np.searchsorted(np.sort(np.unique(DEC[np.isfinite(DEC)])), vi)) <= 1)[:, mask].mean())
        print(json.dumps(r), flush=True)
        out.append(r)


if __name__ == "__main__":
    main()
