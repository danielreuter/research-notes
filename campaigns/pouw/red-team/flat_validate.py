import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from coverage import bf16, stats
from fix_check import scale_bytes
# single-class one-max, bc-a8466279's claim: modal share ~0.965; also two tied maxima ~0.989
def onemax(R, k, rng, S, ntie=1, pin=True):
    x = rng.standard_normal((R, k))
    if pin: x[:, ::8] = rng.choice((-1., 1.), (R, k // 8))
    for i in range(ntie):
        x[:, (1 + i)::16] = S * rng.choice((-1., 1.), (R, 1)) * rng.choice((-1., 1.), (1, k // 16))
    return bf16(x)
rng = np.random.default_rng(1); k = 8192
for S, tie, pin in ((8.9, 1, True), (8.9, 1, False), (9.3, 1, True), (8.9, 2, True), (6.0, 1, False)):
    A = onemax(64, k, rng, S, tie, pin)
    al, ae, dnf, r2 = stats(A); bA = scale_bytes(A, al, r2, rng)[:, :-1]
    # per-row modal share (bc-a8466279 measures modal per row), and global
    per_row = np.mean([np.bincount(r - r.min()).max() / r.size for r in bA])
    glob = np.bincount(bA.ravel() - bA.min()).max() / bA.size
    print(f"S={S} tie={tie} pin={pin}: per-row modal share {per_row:.4f}; global modal {glob:.4f}")
