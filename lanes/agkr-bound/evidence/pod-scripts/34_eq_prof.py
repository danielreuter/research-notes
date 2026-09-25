"""agkr-bound: the eq table over GF(2^256) -- gpu/link.py's byte-table levels against nibble tables (64 x 16 x 32 B = 32 KB
per level, cache-resident) truncated to n_pos rows; equality on every row < n_pos.  python 34_eq_prof.py [REPS]"""
import sys
import time

import numpy as np
import torch
import triton
import triton.language as tl

sys.path.insert(0, ".")
from gpu import link as LK                     # noqa: E402

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
dev = torch.device("cuda")
N_POS, M = 201326592, 28
rng = np.random.default_rng(3)
r = [int.from_bytes(rng.bytes(32), "little") for _ in range(M)]


@triton.jit
def eq_level4(T, TW, TAB, h, lim, BLOCK: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < h
    l0 = tl.zeros([BLOCK], dtype=tl.int64)
    l1 = tl.zeros([BLOCK], dtype=tl.int64)
    l2 = tl.zeros([BLOCK], dtype=tl.int64)
    l3 = tl.zeros([BLOCK], dtype=tl.int64)
    for w in tl.static_range(8):
        x = tl.load(TW + i * 8 + w, mask=m, other=0)
        for nb in tl.static_range(8):
            q = TAB + ((w * 8 + nb) * 16 + ((x >> (4 * nb)) & 15).to(tl.int64)) * 4
            l0 ^= tl.load(q, mask=m, other=0)
            l1 ^= tl.load(q + 1, mask=m, other=0)
            l2 ^= tl.load(q + 2, mask=m, other=0)
            l3 ^= tl.load(q + 3, mask=m, other=0)
    mo = m & (i + h < lim)
    o = T + (i + h) * 4
    tl.store(o, l0, mask=mo)
    tl.store(o + 1, l1, mask=mo)
    tl.store(o + 2, l2, mask=mo)
    tl.store(o + 3, l3, mask=mo)
    o = T + i * 4
    tl.store(o, tl.load(o, mask=m, other=0) ^ l0, mask=m)
    tl.store(o + 1, tl.load(o + 1, mask=m, other=0) ^ l1, mask=m)
    tl.store(o + 2, tl.load(o + 2, mask=m, other=0) ^ l2, mask=m)
    tl.store(o + 3, tl.load(o + 3, mask=m, other=0) ^ l3, mask=m)


def tabs4(r):
    sel = ((np.arange(16)[:, None] >> np.arange(4)[None, :]) & 1).astype(bool)
    out = np.zeros((len(r), 64, 16, 4), dtype=np.int64)
    for j, v in enumerate(r):
        basis = np.zeros((256, 4), dtype=np.int64)
        for s in range(256):
            basis[s] = LK._split(v)
            v = ((v << 1) & LK.MASK) ^ (LK.RED if v >> 255 else 0)
        basis = basis.reshape(64, 4, 4)
        for c in range(4):
            out[j] ^= np.where(sel[None, :, c, None], basis[:, None, c, :], 0)
    return out


def eq4(r, n_pos):
    t0 = time.perf_counter()
    tabs = torch.from_numpy(tabs4(r)).to(dev)
    th = time.perf_counter() - t0
    T = torch.zeros((n_pos, 4), dtype=torch.int64, device=dev)
    T[0, 0] = 1
    tw = T.view(torch.int32)
    for j in range(len(r)):
        h = 1 << j
        eq_level4[(triton.cdiv(h, 512),)](T, tw, tabs[j], h, n_pos, BLOCK=512)
    return T, th


def timed(f):
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    x = f()
    torch.cuda.synchronize(dev)
    return x, time.perf_counter() - t0


for rep in range(REPS + 1):
    A, ta = timed(lambda: LK.eq_table(r, dev))
    (B, th), tb = timed(lambda: eq4(r, N_POS))
    if rep == 0:
        assert torch.equal(A[:N_POS], B), "nibble eq table differs"
        print("nibble table equals the byte table on every row < n_pos", flush=True)
    print(f"rep {rep - 1}: byte-table 2^28 {ta:.4f} s; nibble-table n_pos {tb:.4f} s (host tables {th:.4f})", flush=True)
    del A, B
