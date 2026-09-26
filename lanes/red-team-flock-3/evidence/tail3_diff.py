#!/usr/bin/env python3
"""red-team-flock-3: the Rust tail interpreter's attention primitives (`ir_tail::apply` through the `rtf3-tail` harness) against the
IR primitives (verity_vllm.program.registry.prims / verity.ml.prims `.evaluate`), bit for bit.

  A. unary (MufuEx2Ftz, Fa2InvSum, GuardNegInfZero, F2fpBf16): EXHAUSTIVE over all 2^32 f32 words, against the IR vectorised on
     the IR's own models (fa2_model.mufu_ex2 / mufu_rcp are the C++ functions the scalar prims call on one-element arrays); the
     vectorised forms are first checked against the scalar prims on every special word and 2^17 random words.
  B. binary / ternary (F32AddFtz, F32SubFtz, F32MulFtz, F32FmaFtz, F32FmaSubFtz, F32Max): N random special-heavy vectors each
     (subnormal operands and results, NaN payloads with both operands NaN, exact cancellation, overflow, the ftz thresholds),
     plus every pair (every triple for the fmas) of an edge-word set.

  tail3_diff.py RTF3_TAIL_BIN TABLES_DIR N [A|B|AB] [chunks]
"""
import itertools
import random
import subprocess
import sys
import time

import numpy as np

B, TD, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
PARTS = sys.argv[4] if len(sys.argv) > 4 else "AB"
CHUNKS = int(sys.argv[5]) if len(sys.argv) > 5 else 256
rng = random.Random(20260926 + 3)

from verity_vllm.program.kernels import fa2_model, fa2_relation  # noqa: E402
from verity_vllm.program.registry import prims as P  # noqa: E402

FT = fa2_relation.tables()


def isnan(x):
    return ((x & 0x7F800000) == 0x7F800000) & ((x & 0x7FFFFF) != 0)


def v_ex2(x):
    return fa2_model.mufu_ex2(x.view(np.float32), FT).view(np.uint32)


def v_invsum(x):
    r = fa2_model.mufu_rcp(x.view(np.float32), FT).view(np.uint32)
    return np.where(((x & 0x7FFFFFFF) == 0) | isnan(x), np.uint32(0x3F800000), r).astype(np.uint32)


def v_guard(x):
    return np.where(x == np.uint32(0xFF800000), np.uint32(0), x).astype(np.uint32)


def v_f2fp(x):
    y = x.astype(np.uint64)
    r = ((y + 0x7FFF + ((y >> 16) & 1)) >> 16) & 0xFFFF
    return np.where(isnan(x), np.uint64(0x7FFF), r).astype(np.uint32)


UNARY = {"ex2": (v_ex2, P.MufuEx2Ftz), "invsum": (v_invsum, P.Fa2InvSum), "guard": (v_guard, P.GuardNegInfZero), "f2fp": (v_f2fp, P.F2fpBf16)}
BINARY = {"addf": (P.F32AddFtz, 2), "subf": (P.F32SubFtz, 2), "mulf": (P.F32MulFtz, 2), "max": (P.F32Max, 2),
          "fmaf": (P.F32FmaFtz, 3), "fmasubf": (P.F32FmaSubFtz, 3)}


def edge_words():
    w = set()
    for s in (0, 0x80000000):
        for e in (0, 1, 2, 126, 127, 128, 150, 151, 252, 253, 254, 255):
            for m in (0, 1, 2, 0x3FFFFF, 0x400000, 0x400001, 0x7FFFFE, 0x7FFFFF):
                w.add(s | (e << 23) | m)
    return sorted(w)


def part_a():
    print("A: vectorised IR vs scalar IR prims", flush=True)
    ew = np.array(edge_words() + [rng.getrandbits(32) for _ in range(1 << 17)], dtype=np.uint32)
    for name, (vf, p) in UNARY.items():
        got = vf(ew)
        want = np.array([p.evaluate(int(x)) & 0xFFFFFFFF for x in ew], dtype=np.uint32)
        print(f"  {name:7s} vectorised-vs-scalar on {len(ew)} words: {int((got != want).sum())} differences", flush=True)
        assert (got == want).all(), name
    print(f"A: exhaustive over {CHUNKS} x 2^24 words", flush=True)
    for name, (vf, _) in UNARY.items():
        t0 = time.time()
        pr = subprocess.Popen([B, TD, "exhaustive", name, "0", str(CHUNKS)], stdout=subprocess.PIPE, bufsize=1 << 26)
        bad, first = 0, []
        for c in range(CHUNKS):
            buf = pr.stdout.read(4 << 24)
            got = np.frombuffer(buf, dtype="<u4")
            x = (np.arange(1 << 24, dtype=np.uint64) + (c << 24)).astype(np.uint32)
            want = vf(x)
            d = np.nonzero(got != want)[0]
            bad += len(d)
            for i in d[:max(0, 4 - len(first))]:
                first.append((f"{int(x[i]):08x}", f"ir {int(want[i]):08x}", f"rust {int(got[i]):08x}"))
        pr.wait()
        print(f"  {name:7s} {CHUNKS << 24:11d} words {bad:9d} mismatches ({time.time() - t0:.0f} s)", first, flush=True)


def word(fam):
    s = rng.getrandbits(1) << 31
    m = rng.getrandbits(23)
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 1 << 23)
    if fam == "inf":
        return s | 0x7F800000
    if fam == "qnan":
        return s | 0x7FC00000 | rng.getrandbits(22)
    if fam == "snan":
        return s | 0x7F800000 | rng.randrange(1, 1 << 22)
    if fam == "big":
        return s | (rng.randrange(0xFB, 0xFF) << 23) | m
    if fam == "tiny":
        return s | (rng.randrange(1, 4) << 23) | m
    if fam == "mid":
        return s | (rng.randrange(100, 155) << 23) | m
    return s | (rng.randrange(1, 0xFF) << 23) | m


FAMS = ["norm", "norm", "mid", "mid", "zero", "sub", "inf", "qnan", "snan", "big", "tiny"]


def part_b():
    cs = []
    for name, (p, ar) in BINARY.items():
        for _ in range(N):
            a = [word(rng.choice(FAMS)) for _ in range(ar)]
            k = rng.randrange(8)
            if k == 0:                       # exact cancellation / near-cancellation
                if name in ("addf",):
                    a[1] = a[0] ^ 0x80000000
                elif name == "subf":
                    a[1] = a[0] ^ rng.choice([0, 1])
                elif ar == 3:
                    a[2] = P.F32Mul.evaluate(a[0], a[1]) ^ (0 if name == "fmasubf" else 0x80000000)
            elif k == 1:                     # both (first two) operands NaN: the payload choice
                a[0], a[1] = word("qnan"), word(rng.choice(["qnan", "snan"]))
            elif k == 2 and ar == 3:         # NaN addend with finite product / inf * 0
                a[2] = word("qnan")
                if rng.random() < 0.5:
                    a[0], a[1] = word("inf"), word("zero")
            elif k == 3:                     # results near the subnormal / ftz boundary
                a[0] = (rng.getrandbits(1) << 31) | (rng.randrange(60, 70) << 23) | rng.getrandbits(23)
                a[1] = (rng.getrandbits(1) << 31) | (rng.randrange(60, 70) << 23) | rng.getrandbits(23)
                if ar == 3:
                    a[2] = word(rng.choice(["sub", "tiny", "zero"]))
            cs.append((name, tuple(a)))
    ew = edge_words()
    small = ew[::5]
    for name, (p, ar) in BINARY.items():
        for a in (itertools.product(ew, repeat=2) if ar == 2 else itertools.product(small, repeat=3)):
            cs.append((name, a))
    t0 = time.time()
    want = [BINARY[n][0].evaluate(*a) & 0xFFFFFFFF for n, a in cs]
    t1 = time.time()
    inp = "\n".join(n + " " + " ".join(f"{x:08x}" for x in a) for n, a in cs) + "\n"
    got = subprocess.run([B, TD, "lines"], input=inp, capture_output=True, text=True, check=True).stdout.split()
    t2 = time.time()
    assert len(got) == len(cs)
    per, first = {}, {}
    for (n, a), w, g in zip(cs, want, got):
        c, bad = per.get(n, (0, 0))
        g = int(g, 16)
        per[n] = (c + 1, bad + (g != w))
        if g != w and len(first.setdefault(n, [])) < 4:
            first[n].append(([f"{x:08x}" for x in a], f"ir {w:08x}", f"rust {g:08x}"))
    print(f"B: {len(cs)} cases (IR {t1 - t0:.0f} s, Rust {t2 - t1:.0f} s); edge set {len(ew)} words (fma triples over {len(small)})")
    for n, (c, bad) in per.items():
        print(f"  {n:8s} {c:9d} cases {bad:6d} mismatches", first.get(n, ""), flush=True)


if "A" in PARTS:
    part_a()
if "B" in PARTS:
    part_b()
