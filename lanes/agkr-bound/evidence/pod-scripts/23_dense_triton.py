"""agkr-bound: 21_dense_gpu.py's dense check with fused Triton kernels (one per eq doubling level; one for coefficients +
inner product), same random public-coin values and N; checks the result against the torch version.  cwd backends/gkr.
    python 23_dense_triton.py [N] [REPS]
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import triton
import triton.language as tl

P = 2**31 - 2**27 + 1
N = int(sys.argv[1]) if len(sys.argv) > 1 else 393216 * 512
REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
dev = torch.device("cuda")
M = math.ceil(math.log2(N))
MASK = (1 << 128) - 1
rng = np.random.default_rng(20260925)


def gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a = (a & MASK) ^ 0x87
    return r


def split(v: int):
    s = lambda x: x - (1 << 64) if x >> 63 else x
    return s(v & ((1 << 64) - 1)), s(v >> 64)


r = [int.from_bytes(rng.bytes(16), "little") for _ in range(M)]
tabs = np.zeros((M, 16, 256, 2), dtype=np.int64)
for j in range(M):
    for k in range(16):
        base = [gmul(1 << (8 * k + q), r[j]) for q in range(8)]
        for b in range(256):
            v = 0
            for q in range(8):
                if (b >> q) & 1:
                    v ^= base[q]
            tabs[j, k, b] = split(v)
tabs = torch.from_numpy(tabs).to(dev)
rho = rng.integers(0, P, size=(128, 6), dtype=np.int64)
U = np.zeros((16, 256, 6), dtype=np.int64)
for k in range(16):
    for b in range(256):
        U[k, b] = sum((rho[8 * k + s] for s in range(8) if (b >> s) & 1), np.zeros(6, dtype=np.int64)) % P
U = torch.from_numpy(U).to(dev)
U32 = U.to(torch.int32)
bits = torch.from_numpy(rng.integers(0, 2, size=N, dtype=np.int8)).to(dev)


@triton.jit
def eq_level(T, TB, TAB, h, BLOCK: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < h
    lo = tl.zeros([BLOCK], dtype=tl.int64)
    hi = tl.zeros([BLOCK], dtype=tl.int64)
    for k in tl.static_range(16):
        b = tl.load(TB + i * 16 + k, mask=m, other=0).to(tl.int64)
        lo ^= tl.load(TAB + (k * 256 + b) * 2, mask=m, other=0)
        hi ^= tl.load(TAB + (k * 256 + b) * 2 + 1, mask=m, other=0)
    tl.store(T + (i + h) * 2, lo, mask=m)
    tl.store(T + (i + h) * 2 + 1, hi, mask=m)
    tl.store(T + i * 2, tl.load(T + i * 2, mask=m, other=0) ^ lo, mask=m)
    tl.store(T + i * 2 + 1, tl.load(T + i * 2 + 1, mask=m, other=0) ^ hi, mask=m)


@triton.jit
def coef_ip(TB, U, BITS, ACC, n, p, BLOCK: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * BLOCK + tl.arange(0, BLOCK).to(tl.int64)
    m = i < n
    bit = tl.load(BITS + i, mask=m, other=0).to(tl.int64)
    c0 = tl.zeros([BLOCK], dtype=tl.int64)
    c1 = tl.zeros([BLOCK], dtype=tl.int64)
    c2 = tl.zeros([BLOCK], dtype=tl.int64)
    c3 = tl.zeros([BLOCK], dtype=tl.int64)
    c4 = tl.zeros([BLOCK], dtype=tl.int64)
    c5 = tl.zeros([BLOCK], dtype=tl.int64)
    for k in tl.static_range(16):
        q = U + (k * 256 + tl.load(TB + i * 16 + k, mask=m, other=0).to(tl.int64)) * 6
        c0 += tl.load(q, mask=m, other=0)
        c1 += tl.load(q + 1, mask=m, other=0)
        c2 += tl.load(q + 2, mask=m, other=0)
        c3 += tl.load(q + 3, mask=m, other=0)
        c4 += tl.load(q + 4, mask=m, other=0)
        c5 += tl.load(q + 5, mask=m, other=0)
    # c_e < 16 p < 2^35 and a block sums <= BLOCK of them: one reduction mod p per block, partials summed on the host
    o = ACC + tl.program_id(0).to(tl.int64) * 6
    tl.store(o + 0, tl.sum(c0 * bit, 0) % p)
    tl.store(o + 1, tl.sum(c1 * bit, 0) % p)
    tl.store(o + 2, tl.sum(c2 * bit, 0) % p)
    tl.store(o + 3, tl.sum(c3 * bit, 0) % p)
    tl.store(o + 4, tl.sum(c4 * bit, 0) % p)
    tl.store(o + 5, tl.sum(c5 * bit, 0) % p)


def run():
    t = torch.zeros((1 << M, 2), dtype=torch.int64, device=dev)
    t[0, 0] = 1
    tb = t.view(torch.uint8).view(1 << M, 16)
    BL = 1024
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    for j in range(M):
        h = 1 << j
        eq_level[(triton.cdiv(h, BL),)](t, tb, tabs[j], h, BLOCK=BL)
    torch.cuda.synchronize(dev)
    t1 = time.perf_counter()
    nb = triton.cdiv(N, BL)
    part = torch.empty((nb, 6), dtype=torch.int64, device=dev)
    coef_ip[(nb,)](tb, U32, bits, part, N, P, BLOCK=BL)
    acc = part.sum(0) % P
    torch.cuda.synchronize(dev)
    t2 = time.perf_counter()
    return t, acc, t1 - t0, t2 - t1


runs = []
for rep in range(REPS + 1):
    t, acc, te, tc = run()
    runs.append({"rep": rep - 1, "eq_s": te, "coef_ip_s": tc, "total_s": te + tc})
    print(json.dumps(runs[-1]), flush=True)
for i in (0, 1, N // 3, N - 1):
    want = 1
    for j in range(M):
        want = gmul(want, r[j] if (i >> j) & 1 else r[j] ^ 1)
    lo, hi = int(t[i, 0]) & ((1 << 64) - 1), int(t[i, 1]) & ((1 << 64) - 1)
    assert lo | (hi << 64) == want, f"eq({i}) mismatch"
tb = t[:N].contiguous().view(torch.uint8).view(N, 16).long()
ref = torch.zeros(6, dtype=torch.int64, device=dev)
for s in range(0, N, 1 << 22):
    c = U[0][tb[s:s + (1 << 22), 0]]
    for k in range(1, 16):
        c = c + U[k][tb[s:s + (1 << 22), k]]
    ref = (ref + ((c % P) * bits[s:s + (1 << 22), None].long()).sum(0)) % P
assert torch.equal(ref, acc), "coef/ip mismatch against torch"
print("eq spot checks and coef/ip cross-check OK", flush=True)
med = lambda xs: float(np.median(xs))
summary = {"N": N, "m": M, "eq_s": med([x["eq_s"] for x in runs[1:]]), "coef_ip_s": med([x["coef_ip_s"] for x in runs[1:]]),
           "total_s": med([x["total_s"] for x in runs[1:]])}
print("SUMMARY " + json.dumps(summary), flush=True)
Path("/workspace/agkr-bound/dense").mkdir(parents=True, exist_ok=True)
Path("/workspace/agkr-bound/dense/dense_triton.json").write_text(json.dumps({"runs": runs, "summary": summary}, indent=1))
