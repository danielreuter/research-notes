"""F2 with bc-d9842080's two edits (patch 4 FP4 slots/side = 8·(1−f) symmetric; depth cap L ≤ log2(k/16); c_L the
per-shape formula = my 13:14 add model). Honest tiles (f≈0.14) must charge 0; the flat attack family must be caught."""
import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from coverage import bf16, stats
from fix_check import scale_bytes, spike_rows

def c_L(m, k, n):
    S = lambda L: ((7 / 4) ** L - 1) / 0.75
    Lmax = int(np.log2(k / 16))
    return min(2 * (7 / 8) ** L + 4.25 * (1 / m + 1 / n) * S(L) for L in range(1, Lmax + 1))

def f2_fixed(bA, bB, m, k, n):
    fA = np.bincount(bA.ravel()).max() / bA.size
    fB = np.bincount(bB.ravel()).max() / bB.size
    return max(0.0, 1 - c_L(m, k, n) - 4.0 * ((1 - fA) + (1 - fB))), fA, fB

print("c_L by shape:", {s: round(c_L(s, s, s), 3) for s in (8192, 16384, 32768, 65536)})
print("break-even f* (1-(1-cL)/8):", {s: round(1 - (1 - c_L(s, s, s)) / 8, 4) for s in (8192, 16384, 32768, 65536)})
rng = np.random.default_rng(20260930)
k = 8192
# flat attack rows: pinned rho, tuned row max (one max per block region), both sides such rows
best = None
for rm in np.linspace(900, 960, 13):
    A = spike_rows(64, k, 8.9, rng, rowmax=rm, pin=True)
    al, ae, dnf, r2 = stats(A); bA = scale_bytes(A, al, r2, rng)[:, :-1]
    f = np.bincount(bA.ravel()).max() / bA.size
    if best is None or f > best[0]: best = (f, rm, bA)
f, rm, bA = best
for shape in (8192, 16384, 32768, 65536):
    s, fA, fB = f2_fixed(bA, bA, shape, k, shape)
    print(f"flat family f={f:.5f} at {shape}^3: F2_fixed = {100*s:.1f}% of chain")
# one-max-per-block family (f ~ 0.965): the case the note says only wins at >=32768
A1 = spike_rows(64, k, 8.9, rng, rowmax=None, pin=True)   # 14 spikes; try a single-max variant
def one_max(R, k, rng, S=8.9):
    x = rng.standard_normal((R, k)); x[:, ::8] = rng.choice((-1., 1.), (R, k // 8))
    x[:, 7::16] = S * rng.choice((-1., 1.), (R, 1)) * rng.choice((-1., 1.), (1, k // 16))
    return bf16(x)
Ao = one_max(64, k, rng); al, ae, dnf, r2 = stats(Ao); bo = scale_bytes(Ao, al, r2, rng)
fo = np.bincount(bo.ravel()).max() / bo.size
for shape in (8192, 16384, 32768, 65536):
    s, _, _ = f2_fixed(bo, bo, shape, k, shape)
    print(f"one-max family f={fo:.4f} at {shape}^3: F2_fixed = {100*s:.1f}%")
