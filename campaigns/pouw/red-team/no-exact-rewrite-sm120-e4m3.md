---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `no-exact-rewrite/sm120-e4m3`: rated B (0.01 GPU-h on the RTX PRO 6000, about 0.2 CPU-h bit-exact)

30 Sep 2026, 06:30Z. Independent assessor (bc-d7d4b0d1), `red-team-pouw`, on [the rating scale](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/rating-scale.md).

**The question.** On sm_120, 98–99% of k32 steps are exact. Does that let a Strassen-style or exact-integer rewrite reproduce C̃'s words at sm_120 costs, and by how much would it lower the work?

**The answer: no rewrite of the MACs pays; the saving is zero.** Every exact route costs at least 1.25× the chain on the card's measured rates. The exactness does make one credited operation free, the first promotion add, but that isn't a rewrite of the MACs: it breaks the TT_OUT rows instead ([D note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/first-promotion-overcredit.md)).

## The card's prices (Measured, `r20260930-060338-26b9`)

GPU 6 (`GPU-2b59d5fe…`) of vy-nebius-2, locked-2100 (sampled 2,085–2,092 MHz). Register-only `mma.sync` and scalar throughput, with the SASS gated per kernel. Prices are relative to one FP8 E4M3 MAC with FP32 accumulate, which runs at 1,016 MACs/SM/clock, the full rate:

| Route's unit | Price | | Route's unit | Price |
|---|---|---|---|---|
| FP8 E4M3, FP16 accumulate | 1.00 | | TF32 | 4.00 |
| int8 → s32 | 1.00 | | int4 (ptxas emulates it on int8) | 10.2 |
| E2M1 via `f8f6f4` | 1.00 | | NVFP4 block-scaled | 0.50 |
| FP16 or BF16, FP32 accumulate | 2.00 | | FADD, FFMA | 8.46 |
| FP16, FP16 accumulate | 2.00 | | I2F | 32 |

This confirms `price-floor/sm120` clause (a) on this card. It also closes GPU 3's "FP8 at half rate" scenario, the only one in which a route saved anything (f16-accumulate FP8, 3.7%).

## The routes (bit-exact sm_120 atom, the scheme's s5 forming, 26 census families, k = 8,192 and 16,384, 64 × 64 tiles)

GPU 3's pricing tool, rerun independently (`r20260930-055203-10e8`, branch `cursor/pearl-c-sm120-attacks-cb92` at `d76342dd`), then re-priced at the measured rates:

| Route | Where it applies (in domain) | Cost per MAC |
|---|---|---|
| int8 limbs per (row, 32-slice) | everywhere; 1.94–2.14 limbs per operand | ≥ 4.9 (limbs² plus the rescale) |
| int8, one limb on both sides | ≤ 0.29% of slice pairs (the `constant` family) | 2.27 (I2F + FFMA rescale per 32 products) |
| FP8 with FP16 accumulate | 0.04–10% of atoms | 1.26 (the FP32 combine) |
| NVFP4 limbs per 16-block | everywhere; ≥ 2.49 limbs per operand; one-limb blocks 0% | ≥ 3.1 |
| 2:4-sparse FP8 | 0% of fragments; splitting a dense operand into two 2:4 halves costs 2 × 0.5 | ≥ 1.0 (break-even at best) |
| int4 | — | 10.2 |

**Strassen–Winograd within a promotion group** (G = 4, so the depth is 128):
- The pre-added operands leave E4M3. A pre-add is FP16-exact for 99.5% of elements and 84–100% of 32-slices, and BF16-exact for 96% of elements. So the sub-products run at 2.00.
- The FP16 atom is k16, so a 128-deep group allows at most 3 levels.
- The post-adds are per (word, group) and can't be amortized. With the best schedule (the single-target products accumulate in the tensor core), they cost 2((7/4)^L − 1) FADDs per group-word.

Even with ideal exact sub-products, per MAC against 1.00 for the chain:

| Levels | Sub-products | Post-adds | Total |
|---|---|---|---|
| 1 | 1.750 | 0.099 | 1.85 |
| 2 | 1.531 | 0.273 | **1.80** (the best) |
| 3 | 1.340 | 0.576 | 1.92 |

Only if FP16 ran at FP8's rate would one level approach 0.974, a 2.6% saving. The measurement rules that out.

**Unpromoted (v2).**
- There are no groups, and the whole chain is never an integer: 0% of words at k = 8,192 (`r20260930-053001-7934`, `-053120-6974`).
- A rewrite then needs runs of consecutive atoms that are exact across the whole tile. At the measured prices the break-even is about 3,900 deep (122 atoms, L ≈ 7).
- The sm_120 census finds at most 3 tile-exact atoms of 256 and no run at all (`r20260930-051554-b42a`).

**Generic cores** (Measured, `r20260930-062627-063a`, GPU 7):
- The fastest non-tensor-core MAC is `dp4a` at 4.05 per int8 MAC. That still needs about 2 limbs per operand.
- FFMA costs 8.46 and packed FP16/BF16 FMA 8.11.
- A lookup costs 16.2 with `PRMT` and ≥ 32 from shared memory (66 with random indices). A lookup-table route over the 256-code alphabet would need ≥ 32 MACs per lookup to break even.
- The low-rank noise's structure is Pearl's assumption (TT_OUT's part), not this row's.

## Rating: B (0.01 GPU-h on the RTX PRO 6000; about 0.2 CPU-h on the bit-exact atom)

The attack could have broken the row. Measured FP16 at FP8's rate, or FP8/FP32 at half rate, would each have given a route that pays; neither came out. The cheapest exact alternative costs 1.25× the chain, and Strassen costs 1.80×.

**↓ (what would lower it):**
- a faster exact unit found later, e.g. 2:4-sparse FP8 at more than 2× (not measured, public 2×);
- a second-promotion fusion that can be certified (TT_OUT's side).

**The statement needs two fixes:**
1. "(1 − γ_e)·32 per exact group-word" should read per exact atom-word, or (1 − γ_e)·(32·G + fadd) per group-word. A G = 4 group-word is 128 MACs.
2. For v2 (G = none) there are no promotion groups. Say "exact runs" instead.

The row's claim covers the MACs only. The promotion adds are TT_OUT's, and they are where the exactness bites (the D note).

## `no-exact-rewrite-tc/sm120-e4m3`: B (same evidence, 07:40Z)

This row is the same claim for fewer programs: bilinear rewrites at any level, int8/int4 limbs and 2:4 sparsity. So it is rated at least as high as the row above.
- **2:4 sparsity, measured:** the parent's one open ↓, 2:4-sparse FP8, is now closed. `mma.sp` m16n8k64 (`QMMA.SP.16864`) does 1,018 useful products per SM per clock, the same as dense (`r20260930-071827-bcfb`, GPU 6, locked-2100). Splitting a dense operand into two 2:4 halves exactly breaks even, and in-domain operands have no 2:4 fragments.
- **Strassen at any level:** at most 3 levels fit a 128-deep group. The best is 1.80× the chain at the measured FP16 price, and the post-adds grow faster than the sub-products shrink.
- **int4:** emulated, 10.2 units.
