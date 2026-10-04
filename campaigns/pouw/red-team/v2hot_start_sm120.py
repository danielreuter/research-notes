"""`tt-out/pearl-c-sm120-unpromoted-hot` (v2-hot): does a salted start H_i, sized from salt-free statistics, close v2's chain
start on rows built to mis-size it?

§14's rule sizes |H_i| from the row's ρ (every 8th position) and the job's largest column RMS, to sit near the chain's
accumulator at atom t₀. ρ doesn't see 7 of every 8 positions, and liveness counts only entries ≥ 8ρ, so an in-domain row can
put its other positions at up to ~7.9ρ: the real accumulator is then several times the rule's. Measured on the bit-exact sm_120
unpromoted chain (the census's `step`), per word: exact on every step of atoms [0, w) for w = 4, 8, 14, on
  - gaussian rows (the census family), plain start (+0) and hot start;
  - `off-sample-heavy` rows (every-8th positions N(0,1), the rest ±U(4, 6.5)·ρ, inside liveness's 8ρ), plain and hot;
  - `early-light` rows (the first t₀ atoms at 1/64 of the rest, so the rule's H is far too big), plain and hot;
  - and, for comparison, the plain chain's mid-chain windows [t₀, t₀ + w), where the region lemma already holds.
H_i: sign and a 23-bit mantissa from a per-row RNG (standing in for the E_A sub-domain), exponent from the rule
  |H_i| ≈ sqrt(32·t₀) · (ρ_A α_A) · max_j(RMS_B,j α_B) · c,  t₀ = 16,
with c the ratio of the census rows' real accumulator at atom t₀ to that product (calibrated on gaussian rows, so the rule is
right for them by construction). Words per cell: 64 A rows × 64 B rows. k = 8,192 for the statistics; the chain runs 16 atoms.
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
T0, WS = 16, (4, 8, 14)


def rows(kind, n, k, rng):
    if kind == "gaussian":
        return rng.standard_normal((n, k))
    if kind == "early-light":                         # the first T0 atoms at 1/64 of the rest: the rule's H is far too big
        x = rng.standard_normal((n, k))
        x[:, :32 * T0] /= 64.0
        x[:, :32 * T0:8] = rng.standard_normal((n, 4 * T0)) / 64.0
        return x
    x = rng.uniform(4.0, 6.5, (n, k)) * rng.choice((-1.0, 1.0), (n, k))    # off-sample-heavy, inside liveness's 8ρ
    x[:, ::8] = rng.standard_normal((n, k // 8))
    return x


def stats(X):
    s = np.abs(X).max(1)
    rho = np.sqrt((X[:, ::8] ** 2).mean(1))
    alpha = C.Q_MAX / (s + 4 * rho)
    return rho, alpha


def run_chain(A, B, H, atoms, start=0):
    """Words w = 64 i + j; per word whether every step of atoms [start, start + w) is exact, for each w in WS; |acc| at t₀."""
    P = A.shape[0]
    X = H.astype(np.float64).copy()
    exact_all = np.ones(P, bool)
    out = {}
    for t in range(atoms):
        X, ex = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
        if t >= start:
            exact_all &= ex
            if t + 1 - start in WS:
                out[t + 1 - start] = float(exact_all.mean())
        if t + 1 == T0:
            out["acc_t0"] = float(np.median(np.abs(X)))
    return out


def cell(kind, k, rng, FcA, FcB, calib):
    XA, XB = rows(kind, 64, k, rng), rows("gaussian", 64, k, rng) if kind == "gaussian" else rows(kind, 64, k, rng)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, "v2hot", kind, "A"))
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, "v2hot", kind, "B"))
    rhoA, alA = stats(XA)
    rhoB, alB = stats(XB)
    colrms = float((rhoB * alB).max())
    A, B = np.repeat(a[0], 64, 0), np.tile(b[0], (64, 1))
    zero = np.zeros(A.shape[0])
    base = np.sqrt(32 * T0) * np.repeat(rhoA * alA, 64) * colrms
    if calib is None:
        plain = run_chain(A, B, zero, T0)
        calib = plain["acc_t0"] / float(np.median(base))
    mant = 1 + rng.random(A.shape[0])
    sign = rng.choice((-1.0, 1.0), A.shape[0])
    e = np.round(np.log2(base * calib))
    H = (sign * mant * 2.0 ** e).astype(np.float32).astype(np.float64)
    res = {"family": kind, "in_domain": bool(a[3] and a[4] and b[3] and b[4]), "calib_c": calib,
           "plain": run_chain(A, B, zero, T0), "hot": run_chain(A, B, H, T0),
           "plain_mid": run_chain(A, B, zero, T0 + max(WS), start=T0),
           "H_median": float(np.median(np.abs(H)))}
    return res, calib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--reps", type=int, default=4)
    args = ap.parse_args()
    FcA, FcB = C.s5_lines(args.k, 1, 16.0)
    rng = np.random.default_rng(20260930)
    calib = None
    for rep in range(args.reps):
        for kind in ("gaussian", "off-sample-heavy", "early-light"):
            res, c = cell(kind, args.k, rng, FcA, FcB, calib)
            if kind == "gaussian" and calib is None:
                calib = c
            res["rep"] = rep
            print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
