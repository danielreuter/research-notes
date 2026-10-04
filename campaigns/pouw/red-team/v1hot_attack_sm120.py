"""Trying to break v1-hot (bc-b58c6093, `ttout-restatements.md` §9): v1's 4-atom groups, each started from a salted H_{i,g}
sized by `publicConst 64` (e_i = ⌊log₂(√512 · 64 · α_i·ρ_i)⌋, the same exponent for every group of the row).

Two gaps in §9's CPU run, which tested whole-group windows from H on three families:
  (1) **suffix windows inside a group**: atoms [4g + s, 4g + 4) for s = 1, 2, 3. The prefix is computed honestly, and
      nothing straddles a promotion. §9 folded starts 1 and 2 into "straddling" and didn't test them. A straddling window
      decomposes into a suffix of group g plus a prefix of group g + 1, so these two cases cover it;
  (2) **mis-sized H**: the families that push the real accumulator off the rule's H, as in my 12:55Z/13:08Z v2-hot
      checks. heavy × heavy undersizes H, and an absorbed H makes a group's later steps behave like v1's +0 start.
Measured on the bit-exact sm_120 E4M3 chain (the census's `step`): per word, the share with every step of a window exact,
for v1 (+0) and v1-hot (H), per group g and suffix start s. The +0 chain offers every free 4-atom shape (§9), so a hot
window at or above its +0 counterpart is the warning sign; far below it is the pass.
"""
import argparse, importlib.util, json, math, os, sys
from pathlib import Path
import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec); sys.modules["pearlc_census"] = C; _spec.loader.exec_module(C)
C.set_atom(os.environ.get("CENSUS_ATOM", "sm120-e4m3-k32"))
GROUPS = (0, 1, 2, 4)

def rows(kind, n, k, rng):
    x = rng.standard_normal((n, k))
    if kind == "early-light":
        x[:, :32 * 16] /= 64.0
    elif kind == "heavy":
        x = rng.uniform(4.0, 6.5, (n, k)) * rng.choice((-1.0, 1.0), (n, k))
        x[:, ::8] = rng.standard_normal((n, k // 8))
    elif kind == "spiky":
        for r in range(n):
            x[r, rng.choice(np.arange(1, k, 8), 8, replace=False)] = 7.9 * rng.choice((-1.0, 1.0), 8)
            x[r, int(rng.integers(1, k // 8)) * 8 - 3] = 64.0
    return x

def stats(X):
    s = np.abs(X).max(1); rho = np.sqrt((X[:, ::8] ** 2).mean(1))
    return rho, C.Q_MAX / (s + 4 * rho)

def group_exact(A, B, start, g):
    """Per word, whether each of the 4 steps of group g is exact, starting the group's word at `start`."""
    X = start.astype(np.float64).copy(); flags = []
    for t in range(4 * g, 4 * g + 4):
        X, ex = C.step(X, A[:, 32 * t:32 * t + 32], B[:, 32 * t:32 * t + 32])
        flags.append(ex)
    return np.stack(flags, 1)                                  # (P, 4)

def cell(kA, kB, k, rng, FcA, FcB):
    XA, XB = rows(kA, 64, k, rng), rows(kB, 64, k, rng)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, "v1hot", kA, kB, "A"))
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, "v1hot", kA, kB, "B"))
    rhoA, alA = stats(XA)
    A, B = np.repeat(a[0], 64, 0), np.tile(b[0], (64, 1)); P = A.shape[0]
    t = np.repeat((rhoA * alA).astype(np.float32), 64).astype(np.float64)
    e = np.floor(np.log2(np.sqrt(512.0) * 64.0 * t))
    out = {"A": kA, "B": kB, "in_domain": bool(a[3] and a[4] and b[3] and b[4]), "groups": {}}
    for g in GROUPS:
        H = (rng.choice((-1.0, 1.0), P) * (1 + rng.random(P)) * 2.0 ** e).astype(np.float32).astype(np.float64)
        fz = group_exact(A, B, np.zeros(P), g)
        fh = group_exact(A, B, H, g)
        # the group's word after 4 steps from +0: the scale H is sized against
        X = np.zeros(P)
        for tt in range(4 * g, 4 * g + 4):
            X, _ = C.step(X, A[:, 32 * tt:32 * tt + 32], B[:, 32 * tt:32 * tt + 32])
        row = {"H_over_groupword": float(np.median(np.abs(H)) / max(np.median(np.abs(X)), 1e-30))}
        for s in (0, 1, 2, 3):
            row[f"v1_[{s},4)"] = float(fz[:, s:].all(1).mean())
            row[f"hot_[{s},4)"] = float(fh[:, s:].all(1).mean())
        out["groups"][g] = row
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=1024); ap.add_argument("--reps", type=int, default=2)
    a = ap.parse_args()
    FcA, FcB = C.s5_lines(a.k, 1, 16.0)
    rng = np.random.default_rng(20260930)
    for rep in range(a.reps):
        for kA, kB in (("gaussian", "gaussian"), ("heavy", "heavy"), ("gaussian", "heavy"), ("gaussian", "spiky"), ("early-light", "early-light")):
            r = cell(kA, kB, a.k, rng, FcA, FcB); r["rep"] = rep
            print(json.dumps(r), flush=True)
