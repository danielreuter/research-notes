"""Candidate F2 break, tuned: two column-aligned classes, each with `tie` tied maxima per block, at S0 = 8.9ρ and
S1 = S0/1.125 (one UE4M3 mantissa step, the same binade), ρ pinned, and a screened row-max entry that sets α so both
classes' scales sit at representable UE4M3 values. F1' should be ~0 (few reliable codes per block); F2 reads one tile-modal
byte (~0.5) and gives 0; the masked int8 route runs one K/2 sub-GEMM per class."""
import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from coverage import bf16, stats
from fix_check import scale_bytes
from f2_fixed import c_L
from count_real import p_mode
from dnc import modal_and_realised
from dnc2 import debit as f1_debit

def build(R, k, rng, S0, S1, tie, rowmax):
    x = rng.standard_normal((R, k)); x[:, ::8] = rng.choice((-1., 1.), (R, k // 8))
    nb = k // 16; S = np.where(np.arange(nb) % 2 == 0, S0, S1)
    for i in range(tie):
        x[:, (1 + 2 * i)::16] = S * rng.choice((-1., 1.), (R, 1)) * rng.choice((-1., 1.), (1, nb))
    x[:, k - 15] = rowmax
    return bf16(x)

rng = np.random.default_rng(2); k = 8192
for tie in (1, 2, 3):
    best = None
    for rm in np.linspace(700, 1400, 71):
        A = build(64, k, rng, 8.9, 8.9 / 1.125, tie, rm)
        al, ae, dnf, r2 = stats(A); bA = scale_bytes(A, al, r2, rng)[:, :-1]
        c = (np.arange(k // 16) % 2)[:-1]
        f = [np.bincount(bA[:, c == j].ravel()).max() / bA[:, c == j].size for j in (0, 1)]
        if best is None or min(f) > best[0]: best = (min(f), rm, A, f, bA)
    _, rm, A, f, bA = best
    ftile = np.bincount(bA.ravel()).max() / bA.size
    al, ae, dnf, r2 = stats(A)
    p, s = p_mode(A); p = np.where(s, 0.0, p)
    mod, rea = modal_and_realised(A, al, r2, rng); off = (mod != rea).astype(int)
    f1 = f1_debit(p, off).mean()
    out = []
    for shape in (8192, 16384, 32768, 65536):
        route = c_L(shape, k // 2, shape) + 8 * np.mean([1 - x for x in f])
        F2 = max(0.0, 1 - c_L(shape, k, shape) - 4 * (2 - 2 * ftile))
        out.append(f"{shape//1024}k save {max(0,1-route):.3f}/F2 {F2:.3f}")
    print(f"tie={tie} rowmax {rm:.0f}: class flat {f[0]:.4f}/{f[1]:.4f}, tile modal {ftile:.3f}, F1' {100*f1:.2f}% | " + "; ".join(out), flush=True)
