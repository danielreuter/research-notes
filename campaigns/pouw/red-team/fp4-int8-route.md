---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# FP4's int8 route: the 1.34× floor doesn't hold with equal scales; NVFP4 is protected by scale non-flatness; the four wide-format rows

30 Sep 2026, 11:20Z. Independent assessor (bc-d7d4b0d1). The page is `docs/pouw/fp4-tile-model.md` §7 and §7.8 (bc-d9842080); the rows are in `internal/pouw/fp4-tile-model-rows.md`.

## 1. The finding: on shaped in-domain data the pre-add budget doesn't bind

**What the page takes as the floor.** §7.8 gives 1.34×: Strassen³, "with every scale equal", because the int8 pre-add budget (ℓ1 · 12 ≤ 127) stops Strassen at depth 3. That budget is a worst case, with every pre-added code at E2M1's largest (±6, 12 in half-units). A rewrite needs only its own data to fit, and the adversary chooses the data.

**The rows** (`fp4_int8_depth.py`, `r20260930-111221-4dcf`):
- **Content:** Gaussian background (RMS ρ, which is also the every-8th ρ), and one spike per 16-block at S·ρ with S = 6 or 9, below the dead screen at 10ρ.
- **Placement:** each spike at within-block offset 1, off the every-8th positions ρ samples.
- **Signs:** a recursive checkerboard that makes every Strassen pre-add's spike part 0 or ±12 at any depth. For A: s11 = s21 = +, s12 = s22 = −. For B: t11 = t21 = +, t12 = t22 = −, per level, multiplied over levels.

**Validated against the exact forming** (`pearl_c4.form`, `pearl_c4.row_passes`; tree `bfd950d8`, NVFP4, k = 1,024):
- admission: 4 of 4 rows pass at S = 6 and 3 of 4 at S = 9 (one row's ρ dipped below S/10);
- mean |code|: 2.24 exact against 2.27 in the vectorized forming;
- modal-scale share: 0.72 exact against 0.68 vectorized.

The vectorized forming is used for the large matrices.

**With scales equal (the floor's own assumption):** the largest pre-added |code| per Strassen depth, on A (4,096 × 8,192) and B (8,192 × 2,048). Depths 1–4 are enumerated in full; deeper ones use 3,000 sampled operands.

| Depth L | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| S = 9, A / B max | 12 / 12 | 16 / 16 | 23 / 21 | 31 / 31 | 41 / 45 | 60 / 55 | 76 / 76 | **96 / 104** |
| S = 6, A / B max | 18 / 16 | 24 / 24 | 34 / 34 | 55 / 45 | 66 / 68 | 89 / 85 | 108 / 115 | 142 / 142 (99.7–99.9% of operands fit s8) |

- **Every operand fits int8 (|v| ≤ 127) through depth 8 at S = 9,** and through depth 7 at S = 6.
- **The cost:** int8's measured price is 2 FP4 slots per MAC, so depth 8 costs 2·(7/8)⁸ = **0.69× of honest FP4**, plus one rescale per word (c = 1 on flat scales) and the merges. Priced like Strassen–Winograd's 2 merges per 4 blocks per level, the merges add about 0.02, so the total is about 0.71×.
- **So "floor 1.34× with every scale equal" is not a floor:** under that assumption the int8 route beats honest.

**What actually stops it is scale flatness.** Integer pre-adds need every combined block at one scale byte.

| Format | Modal-scale share per block, A / B | All blocks of a depth-L operand at one scale: L = 1, 2, 3, 4 |
|---|---|---|
| NVFP4, S = 6 | 0.682 / 0.682 | 0.46, 0.22, 0.047, **0.002** |
| NVFP4, S = 9 | 0.608 / 0.609 | 0.37, 0.14, 0.019, **0.0004** |
| MXFP4 (UE8M0, power-of-two scales) | **1.00 / 1.00** | 1, 1, 1, 1 |

- **NVFP4:**
  - **Why its scales can't be made flat:** the noise is σα with σ = ρ/4, about 4% of a spike's value at S = 6. A UE4M3 bucket is about ±4% wide, and staying under the dead screen (S ≤ 9.5) limits which bucket centers a spike can hit.
  - **The best case I could find:** four spikes per block, one per 4-group, would raise the modal share to about 0.85. Even then only 0.85³² ≈ 0.6% of depth-5 operands have all their blocks at one scale.
  - **So deep int8 Strassen isn't available on NVFP4,** and depth ≤ 3 costs ≥ 1.34×.
- **MXFP4** (`pearl-c-mxfp4-v0` in the same code): power-of-two scales stay flat on these rows. The int8 route at depth 8 is available at about 0.7×.
- **What this rests on:** the MXFP4 break is derived from measured components (admission, flatness, s8 fit, int8's price). I haven't run an end-to-end replay of the rewrite against the MXF4 chain. Products are integers at one exponent and totals stay under about 2²¹, so the chain words are exact and an exact rewrite matches them. The debits look small: no D-24 windows at a 37% zero share, and at most one spike per 4-group for the 2:4 term.

## 2. Ratings

- **The int8 floor as §7.8 states it** ("1.34× with every scale equal"): **D**. Under equal scales, shaped in-domain rows reach Strassen depth 8 within s8, at about 0.7×.
- **FP4's int8 closure by format:**
  - **MXFP4: D** (derived from measured components; the confirming run is an end-to-end rewrite replay).
  - **NVFP4: B** (CPU; the exact forming validates the vectorized flatness). It survives, but on scale non-flatness, which the page lists as "not needed". **What the table should add:** a row like `scale-flatness/nvfp4`, "in-domain NVFP4 blocks share one scale byte at most about 0.85 of the time under Pearl-C4's noise", as the load-bearing fact. The pre-add budget and bounded-support rank then stop mattering for NVFP4's int8 route.
- **`int8-preadd-budget/fp4`:**
  - **The arithmetic is right:** ℓ1 ≤ 127/12 = 10.58. One correction: at ℓ1 = 2 only the ×4 and ×5 merges fit (2 × 5 = 10); ×6 and ×7 need ℓ1 = 1.
  - **As a depth limit it is D:** "Strassen stops at depth 3" holds only for worst-case codes. Shaped data fits depth 8 (the table above).
- **`tile-index-sharing/sm120`: C ↑** (an unproved lemma; bc-d9842080 is proving it).
  - **Block-level Winograd doesn't escape it:** (U_a + V_b)(U_c + V_d) yields V_b·U_c, a Y × X block product, not the needed U_c·V_b, since matrices don't commute. So the quadratic trick must act on scalars inside a tile's k, where P is shared across the 8 columns and Q across the 16 rows. There the swapped part is useful on at most a matching.
  - **Cross-gate separation needs recomputation in every case I checked:** two useful partials in one gate output can be separated only by another gate output holding the same partials.
  - **What the proof must cover:** general linear forms with Strassen-like cancellation spread across gates.
  - **Falsifier:** an explicit mixed tile program, on a small tile, whose count beats bilinear by more than the matching fraction.
  - **For NVFP4 it is now secondary,** after scale non-flatness (§1): the Winograd–Strassen program needs integer pre-adds on equal-scale blocks too.
- **`int-scale-classes/fp4`, as a cost term: B.**
  - Its +0.05–0.07 is a lower bound: one FFMA rescale per (word, scale-product class), with I2F not charged. The counts (25–37 per word) are bc-f5bf55c8's measurement.
  - An adversary with flat scales has c = 1, so it adds nothing there. That is consistent with §1, where flatness, not c, is the lever.
- **`bounded-support-rank/fp4` (e = 0.30, s ≤ 32): C.**
  - **The catalogue** (`fmm-ranks.json`, 680 formats to 16) has no scheme below ρ = 0.5. The best is 0.5625 at ⟨16,16,16; 2,304⟩, and the largest exponent is α = 0.0752 (Smirnov ⟨3,3,6; 40⟩). So ρ < 1/2 takes a volume of about 10⁴.
  - **Within ℓ1 ≤ 10** the best is Strassen³, at 0.670.
  - **The conjecture is consistent with every known scheme,** and small-support schemes keep being found, so the attack surface is large.
  - **It is no longer load-bearing for FP4's int8 route:** on shaped data, supports to 2⁸ fit int8. There Strassen⁸, consistent with e = 0.30, already beats honest wherever scales are flat, so the closure rests on flatness, not on rank.

## Update 12:00Z: NVFP4 scales can be made flat, so NVFP4's int8 closure is also D

**The flattest rows** (`fp4_int8_depth.py` sweeps `r20260930-115010-05fc` and `r20260930-115117-80ad`; exact forming `flat_exact_big.py`, `r20260930-115314-251a`):
- ρ pinned: every-8th positions ±1 exactly, as bc-d9842080's construction has it;
- m spikes per 16-block at S = 8.9 (under the 9.5ρ screen) on offsets never ≡ 0 mod 8;
- one row-max entry in the row's last block (screened and debited), whose size sets α and so the UE4M3 bucket the block maximum lands in.

**Why more spikes are allowed:** bc-d9842080's "four spikes per block at most, since two salt-dead ±6 casts in a 4-group trigger the 2:4 debit" doesn't apply. Sub-screen spikes are salt-live under `salt_dead`'s worst-case support, so the debit is 0 with 14 per block (`fp4-base-split-break.md`, tile debit 0).

**On the exact forming** (`pearl_c4.form`, 16 rows, k = 8,192, 8,176 blocks; all 16 rows admitted):

| Spikes per block | Row max | Modal share | f⁵¹² (a 64³ tile's 512 blocks all at one byte) |
|---|---|---|---|
| 4 | 915 / 920 | 0.9938 / 0.9943 | 0.041 / 0.052 |
| **14** | **930 / 940** | **0.99927 / 0.99963** | **0.69 / 0.83** |

**What it breaks:**
- **`scale-flatness/nvfp4` (f\* ≈ 0.97): D.** The exact forming reaches 0.9996.
- **NVFP4's int8 closure: D** (was B at 11:20Z).
  - **Under bc-d9842080's own tile argument,** int8 Strassen runs on all-flat tiles only, and 69–83% of 64³ tiles are all-flat.
  - **The pre-adds fit:** the spikes' checkerboard signs keep every pre-added spike part at 0 or ±12, and the sample positions' codes sum as in §1's rows, within s8 through depth 8.
  - **The price:** depth ≥ 6 costs 2·(7/8)^L ≤ 0.90×, and 0.69× at depth 8, so the route costs about 0.17·1 + 0.83·0.69 ≈ **0.74× of honest**. The mixed-depth model gives about 0.72×.
- **Now both FP4 formats' int8 cells are open,** alongside the base-split break of `tt-out/fp4-sm120`, which is cheaper to exploit.
