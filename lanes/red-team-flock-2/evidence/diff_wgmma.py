#!/usr/bin/env python3
"""red-team-flock-2: bf16-hopper-wgmma (netlist 12c3c8d3, rows = bf16-hopper's da1bbe2c) against its declared semantics.

The netlist computes HOPPER_BF16_M16N8K16 (GroupSum 16 : 26 : -133), then f32_to_bf16. The relation declares
tc_dot_total(HOPPER_BF16_WGMMA_K16) and F2fpBf16. This compares the two on finite units (random plus edge families) and
the two epilogues on finite words (F2fpBf16 is prims.F2fpBf16's body, cast.f32_to_bf16_hw_word).  Usage: diff_wgmma.py N [seed]
"""
import random, sys

from verity.ml.tc.cast import f32_to_bf16_hw_word as F2fpBf16, f32_to_bf16_word
from verity.ml.tc.models import HOPPER_BF16_M16N8K16 as GS
from verity.ml.tc.total import HOPPER_BF16_WGMMA_K16 as WG, tc_dot_total


def finite_bf16(rng, fam):
    s = rng.getrandbits(1) << 15
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 0x80)
    if fam == "big":
        return s | (rng.randrange(0xF0, 0xFF) << 7) | rng.getrandbits(7)
    if fam == "tiny":
        return s | (rng.randrange(1, 0x10) << 7) | rng.getrandbits(7)
    return s | (rng.randrange(1, 0xFF) << 7) | rng.getrandbits(7)


def finite_f32(rng, fam):
    s = rng.getrandbits(1) << 31
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 1 << 23)
    if fam == "big":
        return s | (rng.randrange(0xF0, 0xFF) << 23) | rng.getrandbits(23)
    if fam == "tiny":
        return s | (rng.randrange(1, 0x20) << 23) | rng.getrandbits(23)
    if fam == "tie":
        return s | (rng.randrange(1, 0xFF) << 23) | (rng.getrandbits(7) << 16) | 0x8000
    return s | (rng.randrange(1, 0xFF) << 23) | rng.getrandbits(23)


def main():
    n = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 20260926)
    fams = ["rand", "rand", "zero", "sub", "big", "tiny"]
    units = mism = nonfinite = 0
    for i in range(n):
        fa, fc = rng.choice(fams), rng.choice(fams + ["tie"])
        a = [finite_bf16(rng, rng.choice([fa, "rand"])) for _ in range(16)]
        b = [finite_bf16(rng, rng.choice([fa, "rand"])) for _ in range(16)]
        if i % 7 == 0:                       # exact cancellation: b_k = -b_j for a_k = a_j
            for k in range(8):
                a[8 + k], b[8 + k] = a[k], b[k] ^ 0x8000
        c = finite_f32(rng, fc)
        w = tc_dot_total(WG, c, a, b)
        if (w >> 23) & 0xFF == 0xFF:
            nonfinite += 1
            continue
        g = GS.step(c, a, b)
        units += 1
        if g != w or f32_to_bf16_word(g) != F2fpBf16(w):
            mism += 1
            if mism <= 5:
                print("MISMATCH", hex(c), [hex(x) for x in a], [hex(x) for x in b], hex(g), hex(w))
    words = mw = 0
    for i in range(n * 4):
        u = finite_f32(rng, rng.choice(fams + ["tie", "tie"]))
        words += 1
        mw += f32_to_bf16_word(u) != F2fpBf16(u)
    print(f"diff_wgmma: {units} finite units, {mism} mismatches ({nonfinite} non-finite results skipped); "
          f"{words} finite f32 words, {mw} epilogue mismatches")


if __name__ == "__main__":
    main()
