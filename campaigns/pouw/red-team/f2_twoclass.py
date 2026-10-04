"""F2 reads ONE tile-modal byte. Attack: block columns in two classes, each flat at its own byte, the same classes on every
row (and on B). Tile modal share f ≈ 0.5, so F2 = 0; the route runs one int8 Strassen per class over its K half, each
at its class's scale, plus patches for off-class blocks. Rows: pinned ρ (every 8th ±1), row max tuned, 14 spikes per
block at S for class-1 columns and S·r for class-2 columns (r chosen to land one binade or one mantissa step down)."""
import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from coverage import bf16, stats
from fix_check import scale_bytes
from f2_fixed import c_L, f2_fixed

def rows(R, k, rng, S, r, rowmax, cls):
    x = rng.standard_normal((R, k)); x[:, ::8] = rng.choice((-1., 1.), (R, k // 8))
    rs = rng.choice((-1., 1.), R); cs = rng.choice((-1., 1.), k // 16)
    for b in range(k // 16):
        sb = S if cls[b] == 0 else S * r
        for o in range(16):
            if o not in (0, 8): x[:, 16 * b + o] = sb * rs * cs[b]
    x[:, k - 15] = rowmax
    return bf16(x)

rng = np.random.default_rng(5); k = 8192; nb = k // 16
cls = np.arange(nb) % 2                                  # alternate block columns
for r in (0.5, 1 / 1.125, 1 / 1.25):
    best = None
    for rm in np.linspace(900, 960, 13):
        A = rows(64, k, rng, 8.9, r, rm, cls)
        al, ae, dnf, r2 = stats(A); bA = scale_bytes(A, al, r2, rng)[:, :-1]
        c = cls[:-1]
        f1 = np.bincount(bA[:, c == 0].ravel()).max() / bA[:, c == 0].size
        f2 = np.bincount(bA[:, c == 1].ravel()).max() / bA[:, c == 1].size
        score = min(f1, f2)
        if best is None or score > best[0]: best = (score, rm, bA, f1, f2)
    score, rm, bA, f1, f2 = best
    ftile = np.bincount(bA.ravel()).max() / bA.size
    for shape in (8192, 16384, 32768, 65536):
        F2, _, _ = f2_fixed(bA, bA, shape, k, shape)
        cl = c_L(shape, k // 2, shape)                    # each class is a K/2 sub-GEMM
        route = cl + 4 * ((1 - f1) + (1 - f1)) / 2 + 4 * ((1 - f2) + (1 - f2)) / 2
        print(f"r={r:.3f} rowmax {rm:.0f}: class flatness {f1:.4f}/{f2:.4f}, tile modal {ftile:.3f} | {shape}^3: route {route:.3f} "
              f"(saving {max(0,1-route):.3f}) vs F2 charge {F2:.3f}")
