"""Bit-equality of ScaledMmFp8BlockSharedScale_v1 and ScaledMmFp8Block_v1 under the reference evaluator on edge vectors."""
import random
import time
from collections import Counter

from verity.evaluation import evaluate
from verity.ir.defs import bind
from verity_vllm.program.registry import fp8

E4M3_FINITE = [0x00, 0x80, 0x01, 0x81, 0x07, 0x87, 0x08, 0x88, 0x38, 0xB8, 0x7E, 0xFE, 0x77, 0xF7]
E4M3_NAN = [0x7F, 0xFF]
F32_FINITE = [0x00000000, 0x80000000, 0x00000001, 0x80000001, 0x007FFFFF, 0x807FFFFF, 0x00800000, 0x3F800000, 0xBF800000,
              0x7F7FFFFF, 0xFF7FFFFF, 0x3B124925, 0x1F800000, 0x5F800000, 0x0DA24260, 0x72000000, 0x00400000, 0x2B8CBCCC]
F32_SPECIAL = [0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000, 0x7F800001, 0x7FBFFFFF, 0xFFFFFFFF]
K, N, G = 256, 256, 128
old, new = bind(fp8.ScaledMmFp8Block, K=K, N=N, G=G), bind(fp8.ScaledMmFp8BlockSharedScale, K=K, N=N, G=G)
rng = random.Random(0xF8B10C)


def byte(p_edge, p_nan):
    r = rng.random()
    if r < p_nan:
        return rng.choice(E4M3_NAN)
    if r < p_nan + p_edge:
        return rng.choice(E4M3_FINITE)
    b = rng.getrandbits(8)
    return 0x38 if b & 0x7F == 0x7F else b


def scale(mode):
    if mode == "special":
        return rng.choice(F32_SPECIAL + F32_FINITE)
    if mode == "tiny":                                     # products underflow: subnormal or zero, the FMA then sees them
        return rng.choice([0x00000001, 0x007FFFFF, 0x00800000, 0x00400000, 0x1F800000, 0x0DA24260]) if rng.random() < 0.5 else \
            rng.randrange(1, 60) << 23 | rng.getrandbits(23)
    return rng.randrange(100, 127) << 23 | rng.getrandbits(23)   # 2^-27 .. 1: the checkpoint's and the quant's scales


def vec(k):
    mode = ("normal", "tiny", "special", "normal")[k % 4]
    p_edge, p_nan = (0.4, 0.0) if k % 8 != 7 else (0.2, 0.0005)
    xq = [byte(p_edge, p_nan) for _ in range(K)]
    w = [byte(p_edge, p_nan) for _ in range(N * K)]
    sx = [scale(mode) for _ in range(K // G)]
    ws = [scale(mode) for _ in range(N // G * (K // G))]
    return xq, sx, w, ws


def cls(b):
    e, m = (b >> 7) & 0xFF, b & 0x7F
    return "nan" if e == 0xFF and m else "inf" if e == 0xFF else "zero" if not (b & 0x7FFF) else "subnormal" if e == 0 else "normal"


t = time.time()
diff, seen = 0, Counter()
for k in range(96):
    a = vec(k)
    yo, yn = evaluate(old, *a), evaluate(new, *a)
    assert len(yo) == len(yn) == N
    diff += sum(p != q for p, q in zip(yo, yn))
    seen.update(cls(p) for p in yo)
print(f"96 vectors x {N} words: {diff} differ; output classes {dict(seen)}; {time.time() - t:.0f}s")
assert diff == 0
