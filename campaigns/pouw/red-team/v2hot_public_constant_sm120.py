"""`tt-out/pearl-c-sm120-unpromoted-hot` (v2-hot) under the public-constant H_i rule, the rule the panel publishes.

The public-constant rule replaces §14's column factor max_j(RMS_B,j·α_B) with a public constant c₀; the row factor ρ_A·α_A
is forming's own:  |H_i| ≈ sqrt(32·t₀) · (ρ_A α_A) · c₀ · c,  t₀ = 16. So B̃'s own shape now mis-sizes H_i too, which the
11:45Z run (`v2hot_start_sm120.py`, the design's column-RMS rule) never exercised. c₀ is set so the two rules agree on the
census's gaussian job (the job the rule is tuned for); c is that run's calibration.
Measured on the bit-exact sm_120 unpromoted chain (the census's `step`), per word, exact on every step of atoms
[s, s + w) for w = 4, 8, 14 and start s = 0, 1, 2, 4 (a mis-sized H absorbed in the first atoms would leave a plain-like
start at s ≥ 1), on A × B family pairs chosen to push the real accumulator off c₀ in both directions:
  gaussian × gaussian            the rule is right (calibration)
  gaussian × heavy               B's off-sample positions at ±U(4, 6.5)ρ: the real accumulator above c₀'s, H too small
  heavy × heavy                  both sides: H too small by the product of both factors, the extreme in-domain case
  gaussian × spiky               8 entries per B row at 7.9ρ and one row max at 64ρ: α_B about 8× small, H too big
  early-light × early-light      the first t₀ atoms at 1/64 on both sides: H far too big
with the plain chain's own start [s, s + w) and mid-chain windows [t₀, t₀ + w) beside each. Words per cell: 64 × 64.
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
T0, WS, STARTS = 16, (4, 8, 14), (0, 1, 2, 4)


def rows(kind, n, k, rng):
    x = rng.standard_normal((n, k))
    if kind == "early-light":
        x[:, :32 * T0] /= 64.0
    elif kind == "heavy":
        x = rng.uniform(4.0, 6.5, (n, k)) * rng.choice((-1.0, 1.0), (n, k))
        x[:, ::8] = rng.standard_normal((n, k // 8))
    elif kind == "spiky":
        for r in range(n):
            pos = rng.choice(np.arange(1, k, 8), 8, replace=False)
            x[r, pos] = 7.9 * rng.choice((-1.0, 1.0), 8)
            x[r, int(rng.integers(1, k // 8)) * 8 - 3] = 64.0
    return x


def stats(X):
    s = np.abs(X).max(1)
    rho = np.sqrt((X[:, ::8] ** 2).mean(1))
    return rho, C.Q_MAX / (s + 4 * rho)


def chain_flags(A, B, H, atoms):
    X = H.astype(np.float64).copy()
    ex = np.zeros((A.shape[0], atoms), bool)
    acc_t0 = None
    for t in range(atoms):
        X, ex[:, t] = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
        if t + 1 == T0:
            acc_t0 = float(np.median(np.abs(X)))
    return ex, acc_t0


def windows(ex, starts):
    return {f"[{s},{s + w})": float(ex[:, s:s + w].all(1).mean()) for s in starts for w in WS}


def cell(kA, kB, k, rng, FcA, FcB, cal):
    XA, XB = rows(kA, 64, k, rng), rows(kB, 64, k, rng)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, "v2hot-pub", kA, kB, "A"))
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, "v2hot-pub", kA, kB, "B"))
    rhoA, alA = stats(XA)
    rhoB, alB = stats(XB)
    A, B = np.repeat(a[0], 64, 0), np.tile(b[0], (64, 1))
    P = A.shape[0]
    atoms = T0 + max(WS)
    plain, acc_t0 = chain_flags(A, B, np.zeros(P), atoms)
    rowf = np.sqrt(32 * T0) * np.repeat(rhoA * alA, 64)
    colrms = float((rhoB * alB).max())
    if cal is None:
        cal = {"c": acc_t0 / float(np.median(rowf * colrms)), "c0": colrms}
    res = {"A": kA, "B": kB, "in_domain": bool(a[3] and a[4] and b[3] and b[4]), "c0": cal["c0"], "colrms": colrms,
           "acc_t0": acc_t0, "plain_start": windows(plain, STARTS), "plain_mid": windows(plain, (T0,))}
    mant, sign = 1 + rng.random(P), rng.choice((-1.0, 1.0), P)
    t = np.repeat((rhoA * alA).astype(np.float32), 64).astype(np.float64)
    rules = (("public", np.round(np.log2(rowf * cal["c0"] * cal["c"]))),
             ("column-rms", np.round(np.log2(rowf * colrms * cal["c"]))),
             ("publicConst64", np.floor(np.log2(np.sqrt(512.0) * 64.0 * t))))   # bc-b58c6093's pinned rule, 13:05Z
    for rule, e in rules:
        H = (sign * mant * 2.0 ** e).astype(np.float32).astype(np.float64)
        hot, _ = chain_flags(A, B, H, atoms)
        res[rule] = {"H_over_acc_t0": float(np.median(np.abs(H))) / acc_t0, "hot": windows(hot, STARTS)}
    return res, cal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--reps", type=int, default=2)
    args = ap.parse_args()
    FcA, FcB = C.s5_lines(args.k, 1, 16.0)
    rng = np.random.default_rng(20260930)
    cal = None
    pairs = [("gaussian", "gaussian"), ("gaussian", "heavy"), ("heavy", "heavy"), ("gaussian", "spiky"),
             ("early-light", "early-light")]
    for rep in range(args.reps):
        for kA, kB in pairs:
            res, c = cell(kA, kB, args.k, rng, FcA, FcB, cal)
            if cal is None:
                cal = c
            res["rep"] = rep
            print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
