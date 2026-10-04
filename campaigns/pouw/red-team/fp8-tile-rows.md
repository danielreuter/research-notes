---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# The FP8-tile rows: `fp8-tile-only/sm120`, `fp8-limb-rate/sm120`, `fp8-merge-rate/sm120`, `no-exact-rewrite-wide/fp8`, `a2/fp8-tile`

30 Sep 2026, 09:20Z. Independent assessor (bc-d7d4b0d1). These are bc-b58c6093's rows under which v1 (rev1)'s tie-or-worse routes become a theorem on the 98.5% of promotion groups that are exact. The ratings are **B, B, B, B, C**.

## `fp8-limb-rate/sm120` and `fp8-merge-rate/sm120`: B (CPU, bit-exact forming, targeted at the domain's edge)

**Why the census's 0% is structural.** Pearl-C sets each row's noise from its RMS, not its spread (σ = ρ, δ = 1): every element carries noise of about ρ·α, and the domain requires ρ·α ≥ 1. A code is therefore deterministic only at |αx| well above ρα: about 24ρα, for the noise to sit under half an ulp at 1σ. The question is whether an in-domain row can put deterministic codes on whole blocks.

- **Every 16-block holds two of ρ's every-8th sample positions.** A deterministic block at code v therefore puts two samples of size v into ρ, and with n_b such blocks per row, ρα ≥ 4v·√(n_b / k).
- **Exactness needs ρα ≲ v/24,** so n_b ≤ k/9,216. That is zero blocks per row at k ≤ 8,192 and at most 7 of 4,096 at k = 65,536, each block then exact only at 1σ per element.
- **Chance doesn't help.** A block of noise-randomized codes is one NVFP4 block with probability below (1/4)^16.
- **Merges are worse.** A 16 × 32 merge fragment holds 64 sample-position elements.
- **MXF4** (E8M0 scales, 32-blocks) is a subset of NVFP4-exactness, so it is covered.

**The attack** (`limb_merge_attack_sm120.py`, `r20260930-090724-c3f0`, about 3 CPU-hours):
- 240 configurations of the best family I could build, formed exactly by `pearl_c.form_v1` on the sm_120 device:
  - one row-max entry of size L sets α;
  - n_b aligned blocks of 16, 32 or 64 entries, the same columns in every row, include their sample positions and sit at a value tuned so that α·V lands on an NVFP4 code (256 or 128);
  - the sweep covers L ∈ {60, 120, 240, 440}, n_b ∈ {1 … 16}, and k = 4,096 and 8,192 with T = 32.
- **Every configuration was in the domain,** and every one found 0:
  - 0 NVFP4-exact 16-blocks of 2,949,120;
  - 0 NVFP4 A-fragments (16 × k64) of 46,080;
  - 0 exact 16 × 32 merge fragments of 23,040.
- **The mechanism is the bound's.** The spikes raise the noise floor to ρ·α ≥ 8.05 in every configuration, and the "deterministic" spike codes spread over several ulps (88–128 for a target of 128).

**Int8 limbs** (the row's ≤ 0.29% on 32-slices) don't move the price: int8 runs at E4M3's rate on sm_120 (1,016 MACs/SM/clk), so an int8 limb is a tie.

- **Falsifier (↓):** an in-domain family whose deterministic codes avoid the sample positions yet fill whole k64 fragments on both operands. The sample-position argument says there is none.

## `fp8-tile-only/sm120`: B (GPU, every `mma.sync` kind timed)

The measured table is complete: every kind ptxas accepts for sm_120a is timed against E4M3 m16n8k32.

| Kind | MACs/SM/clk | Against E4M3 | Run |
|---|---|---|---|
| E4M3, E5M2, E3M2, E2M3 (`kind::f8f6f4`); E4M3 with E8M0 scales (`kind::mxf8f6f4`) | 1,011–1,013 | 1.00 | `r20260930-091638-9747` |
| E4M3 with FP16 accumulate, int8 | 1,016 | 1.00 | `r20260930-060338-26b9` |
| NVFP4 (`mxf4nvf4`, UE4M3) and MXF4 (UE8M0) | 2,027–2,033 | 0.50 | both runs |
| 2:4-sparse E4M3 (`mma.sp` m16n8k64) | 1,018 useful | 1.00 | `r20260930-071827-bcfb` |
| BF16, FP16 (FP32 accumulate) | 507 | 2.0 | `r20260930-060338-26b9` |
| TF32 | about 254 | 4.0 | `r20260930-060338-26b9` |
| int4 (s4) | 100 (ptxas emulates it on int8) | 10.2 | `r20260930-060338-26b9` |
| b1 AND-popc m16n8k256 | 630 one-bit MACs (no native BMMA; ptxas lowers it to `IMMA.16832.U8`) | about 103 per 8-bit product by bit planes | `r20260930-091638-9747` |

- **The table's closures:**
  - NVFP4 and MXF4 are the only kinds cheaper per product, and both are closed through the operands by `fp8-limb-rate/sm120` (above);
  - every FP6 and FP8 variant ties;
  - scaled FP8 ties;
  - 2:4 sparsity breaks even.
- **Fragment pricing** (each instruction priced by its whole fragment) is what `fragment-joint-skips.md` measured on passing units.
- **Not timed:** FP64 DMMA, a slow path on this part. wgmma and tcgen05 don't exist on sm_120.

## `no-exact-rewrite-wide/fp8` (v1, G = 4): B (GPU)

The row claims that BF16 or FP16 pre-adds of 3 or more entries, TF32 of 5 or more and FFMA of 9 or more don't pay.

- **Why they can't:** sub-products in BF16 or FP16 cost 2.0 per product, TF32 4.0 and FFMA 8.46 (measured above). A recursive bilinear scheme saves at most (7/8)^L, and at most 3 levels fit the group's depth cap.
- **What was measured:**
  - the break-even bound with the post-adds is 1.80× (`strassen_preadd_sm120.py`, `no-exact-rewrite-sm120-e4m3.md`);
  - a whole timed one-level Strassen of E4M3 on FP16 cuBLASLt sub-products runs 2.2–2.8× slower than cuBLASLt E4M3 at 8,192³ and 16,384³ (`r20260930-085618-5cfa`; code by bc-c7421547, reviewed and adopted).
- **Rating:** the row asserts less than `no-exact-rewrite-tc/sm120-e4m3`, so B.

## `a2/fp8-tile` (γ₂): C (idealized model)

Like `a2/sm120` (C, 08:55Z), this row is a modelling choice: nonlinear forming (limb splits under data-dependent scales, tables, bit tricks) is matched by the linear class within γ₂.

- **What the measurements show:** every nonlinear route measured on the card costs more than the product it replaces:
  - ≥ 3.1 per MAC for NVFP4 limbs, whose rate is 0 anyway (above);
  - ≥ 4.9 for int8 limbs;
  - ≥ 16.2 per lookup;
  - about 103 for b1 bit planes.
- **What they can't show:** no search can cover the class.
- **Falsifier (↓):** a data-dependent-scale limb route that pays on an in-domain fragment.
