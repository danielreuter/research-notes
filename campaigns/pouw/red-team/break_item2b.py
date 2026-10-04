import sys; sys.path.insert(0, "/tmp/f1p")
import numpy as np
from break_item2 import window_saving_layout
from dnc2 import window_saving as dnc2_window_saving
ALT = np.array([0, 1, 4, 5, 8, 9, 12, 13, 2, 3, 6, 7, 10, 11, 14, 15])     # dnc2: sorted pairs 0,2,4,6 -> chunk 0
def dnc2_layout(P): return np.stack([np.sort(r)[ALT] for r in P])
rng = np.random.default_rng(3)
# 1) my window saving at dnc2's layout must equal dnc2's own window_saving
P = rng.random((8, 16)) * 0.4
print("cross-check (mine at dnc2 layout, dnc2):", round(window_saving_layout(dnc2_layout(P)), 6), round(float(dnc2_window_saving(P.reshape(1, 128))[0]), 6))
gains = []
for trial in range(300):
    kind = trial % 4
    if kind == 0: P = rng.random((8, 16)) * 0.5
    elif kind == 1: P = np.where(rng.random((8, 16)) < 0.2, rng.random((8, 16)) * 0.5, rng.random((8, 16)) * 0.02)
    elif kind == 2: P = rng.choice([0.001, 0.13, 0.45], (8, 16), p=[0.5, 0.4, 0.1])
    else: P = np.tile(rng.random(16) * 0.4, (8, 1))
    s_d = window_saving_layout(dnc2_layout(P))
    best = s_d; arg = None
    cand = [np.stack([np.sort(r) for r in P])]                       # concentrate: 4 most reliable pairs in chunk 0
    for _ in range(300): cand.append(np.stack([rng.permutation(r) for r in P]))
    for L in cand:
        v = window_saving_layout(L)
        if v > best: best, arg = v, L
    gains.append((best - s_d, kind, s_d, best))
g = np.array([x[0] for x in gains])
print(f"layouts beating dnc2's sorted-alternating layout: {int((g > 1e-9).sum())} of {len(g)}; max gain {g.max():+.4f}; mean gain {g.mean():+.4f}")
for kind in range(4):
    gk = [x for x in gains if x[1] == kind]
    top = max(gk, key=lambda x: x[0])
    print(f"  kind {kind}: max gain {top[0]:+.4f} (dnc2 {top[2]:.4f} -> best {top[3]:.4f}); beaten in {sum(x[0] > 1e-9 for x in gk)} of {len(gk)}")
