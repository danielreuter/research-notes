import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from break_item2 import window_saving_layout
from break_item2b import dnc2_layout
from count_real import p_mode
from dnc_attack import narrow_cell, max_offset
from fix_check import spike_rows
rng = np.random.default_rng(11)
def climb(P):
    L = dnc2_layout(P); base = cur = window_saving_layout(L); improved = True
    while improved:
        improved = False
        for b in range(8):
            for i in range(16):
                for j in range(i + 1, 16):
                    L2 = L.copy(); L2[b, [i, j]] = L2[b, [j, i]]
                    v = window_saving_layout(L2)
                    if v > cur + 1e-12: L, cur, improved = L2, v, True
    return base, cur
for name, X in (("spike rows", spike_rows(8, 8192, 8.9, rng)), ("narrow-cell", narrow_cell(8, 8192, rng)), ("max-offset", max_offset(8, 8192, rng))):
    p, scr = p_mode(X); p = np.where(scr, 0.0, p)
    W = p[:, :1024].reshape(-1, 128)[:6].reshape(-1, 8, 16)
    res = [climb(w) for w in W]
    g = np.array([c - b for b, c in res]); base = np.array([b for b, c in res])
    print(f"{name}: dnc2 layout S_w mean {base.mean():.4f}; hill-climb gain mean {g.mean():+.5f} max {g.max():+.5f} (improved {int((g>1e-9).sum())}/{len(g)})", flush=True)
