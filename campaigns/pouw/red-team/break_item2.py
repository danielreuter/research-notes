"""Open item 2: is sorted-neighbour pairing the cheater's best within-block layout (the one that MAXIMISES the split's
saving, i.e. MINIMISES the excess beyond 2:4)? If some permutation of a block's 16 codes gives a larger window saving
than dnc2's sorted layout, F1' undercharges. Search random permutations and a greedy 'spread reliable across pairs'
alternative against the sorted layout, on random and adversarial p-vectors."""
import sys; sys.path.insert(0, "/tmp/f1p")
import itertools, numpy as np
C = 16.92 / 128; XM = 4
COMBOS = list(itertools.product(range(3), repeat=4))
EXC = []
for js in COMBOS:
    dev = sorted(j for j in js if j > 0)
    EXC.append(min(sum(dev[:len(dev) - 2]) if len(dev) > 2 else 0, XM))
VX = np.array([max(0.0, 0.5 - C * x) for x in range(XM + 1)])

def conv_trunc(a, b, m=XM):
    out = np.zeros(m + 1)
    for i in range(m + 1):
        for j in range(m + 1 - i):
            out[i + j] += a[i] * b[j]
    out[m] += a.sum() * b.sum() - out.sum()
    return out

def block_excess_layout(p16):
    """excess distribution of one block laid out as chunk0=pairs(0,1)(2,3)(4,5)(6,7), chunk1=(8,9)...(14,15)."""
    pr = p16.reshape(8, 2)
    pj = np.stack([(1 - pr[:, 0]) * (1 - pr[:, 1]), pr[:, 0] * (1 - pr[:, 1]) + (1 - pr[:, 0]) * pr[:, 1], pr[:, 0] * pr[:, 1]], -1)
    d = None
    for ch in (pj[0:4], pj[4:8]):
        dd = np.zeros(XM + 1)
        for js, x in zip(COMBOS, EXC):
            dd[x] += ch[0, js[0]] * ch[1, js[1]] * ch[2, js[2]] * ch[3, js[3]]
        d = dd if d is None else conv_trunc(d, dd)
    return d

def sorted_layout(p16):
    return np.sort(p16)

def block_saving(p16):  # excess-route saving of one block (2:4 part only), for layout comparison
    return None

def window_saving_layout(P):  # P: (8,16) per-block p, given a per-block layout already applied
    d = block_excess_layout(P[0])
    for b in range(1, 8): d = conv_trunc(d, block_excess_layout(P[b]))
    s = (d * VX).sum()
    p = P.reshape(128)
    for h in (slice(0, 64), slice(64, 128)):
        dd = np.zeros(XM + 1); dd[0] = 1
        for t in range(64):
            q = p[h][t]; nd = dd * (1 - q); nd[1:] += dd[:-1] * q; nd[XM] += dd[XM] * q; dd = nd
        s += (dd * VX).sum()
    return s

rng = np.random.default_rng(3)
worst_gain = 0.0
for trial in range(400):
    kind = trial % 4
    if kind == 0: P = rng.random((8, 16)) * 0.5
    elif kind == 1: P = np.where(rng.random((8, 16)) < 0.2, rng.random((8, 16)) * 0.5, rng.random((8, 16)) * 0.02)
    elif kind == 2: P = rng.choice([0.001, 0.13, 0.45], (8, 16), p=[0.5, 0.4, 0.1])   # narrow-cell-like
    else: P = np.tile(rng.random(16) * 0.4, (8, 1))
    Ps = np.sort(P, axis=1)
    s_sorted = window_saving_layout(Ps)
    best = s_sorted
    for _ in range(300):
        Pr = np.stack([rng.permutation(row) for row in P])
        best = max(best, window_saving_layout(Pr))
    # 'spread' layout: interleave reliable and unreliable so each pair has one of each
    Psp = np.stack([r[np.argsort(np.argsort(r) % 8 * 2 + np.argsort(r) // 8)] for r in P])
    best = max(best, window_saving_layout(Psp))
    worst_gain = max(worst_gain, best - s_sorted)
    if best - s_sorted > 1e-9 and trial < 40:
        print(f"trial {trial} kind {kind}: sorted {s_sorted:.4f} best-found {best:.4f} gain {best-s_sorted:+.4f}")
print(f"max saving a non-sorted layout beats sorted by, over 400 windows x 300 perms: {worst_gain:+.6f}")
