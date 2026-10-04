"""Red-team: can a Strassen/Winograd rewrite of an exact sm_120 promotion group keep its pre-additions exact?

Setting (from exact_chain_sm120.py, run r20260930-052358-a5f0): at k = 8,192 the whole chain is essentially never an
exact integer (0% Gaussian), but ~98.5% of G = 4 promotion groups (128 deep) are. So the only rewrite that can
reproduce the bound C-tilde word is a GROUP-level one: compute each 128-deep group sum exactly, then replay the
cheap FP32 promotion adds in the honest order.

A Strassen level over the (m, n) block structure forms pre-additions of two operands taken at the SAME k position
from two DIFFERENT rows (A11 + A22, ...), and two levels form sums of four. E4M3 + E4M3 leaves the E4M3 grid, so
the sub-products must run in a wider tensor-core format. This test is ATTACKER-FAVOURABLE: it assumes every
sub-product is computed exactly by an ideal wide accumulator, so Strassen reproduces the exact group sum iff every
pre-added operand is exactly representable in the sub-product's format. It measures that per-element rate p for
FP16 and BF16, and the implied rate that a whole pre-added block (all its elements) is exact.
"""
import argparse, math, random, struct, sys

import numpy as np

sys.path.insert(0, "/workspace/packages/verity/src")
sys.path.insert(0, "/home/ubuntu/redteam")
from exact_chain_sm120 import make_row  # the same Pearl-C-like forming (labelled stand-in)
import rt_result


def e4m3_to_float(word):
    s = -1.0 if word & 0x80 else 1.0
    exp = (word >> 3) & 0xF
    man = word & 0x7
    if exp == 0:
        return s * (man / 8.0) * 2.0 ** -6  # subnormal
    return s * (1.0 + man / 8.0) * 2.0 ** (exp - 7)


def exact_in_fp16(v):
    return float(np.float16(v)) == v and math.isfinite(float(np.float16(v)))


def to_bf16(v):
    b = struct.unpack("<I", struct.pack("<f", v))[0]
    lsb = (b >> 16) & 1
    b = (b + 0x7FFF + lsb) & 0xFFFF0000  # round to nearest even on the top 16 bits
    return struct.unpack("<f", struct.pack("<I", b))[0]


def exact_in_bf16(v):
    return to_bf16(v) == v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--rows", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--block", type=int, default=4096, help="elements in one pre-added Strassen block")
    args = ap.parse_args()

    out = {}
    meas = []
    for kind in ("gauss", "spike300", "narrowband"):
        rng = random.Random(args.seed)
        rows = [[e4m3_to_float(w) for w in make_row(kind, args.k, rng)] for _ in range(args.rows)]
        cells = {}
        for lvl, fan in (("L1_sum2", 2), ("L2_sum4", 4)):
            ok16 = okbf = tot = 0
            for _ in range(20000):
                l = rng.randrange(args.k)
                idx = rng.sample(range(args.rows), fan)
                v = sum(rows[i][l] for i in idx)  # exact in float64 for these magnitudes
                tot += 1
                ok16 += exact_in_fp16(v)
                okbf += exact_in_bf16(v)
            p16, pbf = ok16 / tot, okbf / tot
            # a whole pre-added block is exact only if all its elements are
            blk16 = math.exp(args.block * math.log(p16)) if p16 > 0 else 0.0
            blkbf = math.exp(args.block * math.log(pbf)) if pbf > 0 else 0.0
            cells[lvl] = {"p_fp16": p16, "p_bf16": pbf, "block_exact_fp16": blk16, "block_exact_bf16": blkbf}
            meas += [(f"{kind}.{lvl}.p_fp16", p16, "fraction"), (f"{kind}.{lvl}.p_bf16", pbf, "fraction")]
            print(f"{kind:10s} {lvl}: per-element exact  FP16 {p16:7.3%}  BF16 {pbf:7.3%}   "
                  f"| whole {args.block}-elt block exact  FP16 {blk16:.2e}  BF16 {blkbf:.2e}")
        out[kind] = cells
    rt_result.write("strassen-preadd-sm120", meas, {"params": vars(args), "results": out},
                    detail="attacker-favourable: ideal exact sub-products; Strassen exact iff all pre-adds exact")


if __name__ == "__main__":
    main()
