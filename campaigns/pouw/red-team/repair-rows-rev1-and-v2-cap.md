---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# The repair rows: rev1 (H100 and sm_120), v2 at the cap 1/1,000, and cross-group knowledge

30 Sep 2026, 07:40Z. Independent assessor (bc-d7d4b0d1), on [the rating scale](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/rating-scale.md). The shared evidence is in [fragment joint skips](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/fragment-joint-skips.md). The exact-rewrite row is in [its own note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/no-exact-rewrite-sm120-e4m3.md).

## `tt-out/pearl-c-sm120-rev1` and its tile row: B (CPU on the bit-exact atom, about 3 CPU-h on node 2; 0.03 GPU-h of prices)

**Is any other credited step skippable?** I went through `creditOf` (Lean `Game.creditOf`, `pearl_c.credit_of`) term by term:
- **Promotion adds after the first** (`rev1_promotions_sm120.py`, `r20260930-071537-652b`: 22 in-domain cells, 64 × 64 tiles, k = 8,192 and 16,384):
  - No promotion ever lands on a +0 total.
  - Fusing T_{g−1} into the group's first atom instead of adding it would be right for up to 92% of words on Gaussian-like inputs, but only with an oracle. Deciding which words are safe costs at least one instruction per word, more than the 8.46-unit add it saves.
  - The cheap per-tile certificate (a Cauchy–Schwarz bound against the products' lowest bit) certifies 0 of the 63–127 later groups.
  - Forced.
- **The chain's MACs:** rewrites don't pay (B, the exact-rewrite note). The joint sets inside the cap (R ≤ 48: 2.8–9.4% per word) are unrealizable fragment-wide: 0 atoms, 0 patchable.
- **The fused A′·F_B (1 per MAC):** its BF16-rounded words feed U, and there is no cheaper exact engine than the FP8 MMA it already uses.
- **The peel:** BF16 depth 64 into C̃'s word; U is checked, so it can't be skipped. Half of each peel operand is E4M3, but FP8 limbs only break even with the BF16 MMA at 2.00.
- **Forming** (the noise atom 32 plus the cast): elements whose code the noise can't change are P3's salt-dead debit. On the tensor core the atom is an m × k × 32 GEMM at 1 per MAC.
- **Already uncredited:** ρ (4, activations alone), the weight side, and hashing.

**Rating B, at the stated parameters.** Every attack I ran could have broken it and none did:
- the census (26 families, `r20260930-051554-b42a`);
- the credit audit and promotion fusion;
- fragment-wide joint skips on the families at the cap;
- exact rewrites at the measured prices.

**↓ (what isn't covered):**
- no algebraic attack on the quantized rank-32 noise itself (Pearl's assumption, the conjecture's core);
- the joint-skip result rests on `w1-complete/sm120` pricing `mma.sync` by shape.

**Wording:** "the first promotion" should read "every promotion into a +0 total". The effect is at most 4·10⁻⁶ of later promotions on the H100 atom and 0 on sm_120, so it changes no number.

## `tt-out/pearl-c-h100-rev1` and its tile row: B (CPU on the Hopper atom; the H100 prices of Rounds 7–11, not remeasured)

The same audit on `HOPPER_E4M3_K32` (`r20260930-072335-f9d9`):
- a promotion into +0 appears at ≤ 3.9·10⁻⁶ of later promotions;
- oracle fusion works for ≤ 27% of words, 0 fragment-wide, nothing certified.

On the H100 atom (`r20260930-072316-a4cf`):
- inside the cap, per-word joint sets are ≤ 3.9%, and 0 fragment-wide;
- the aligned-spike families' 33–71% per-word sets all sit in units the 1/400 cap rejects (debit 1.3–31%).

The device is withdrawn, so nothing here was run on an H100.

## `tt-out/pearl-c-sm120-unpromoted-cap1000`: B (CPU on the bit-exact atom; 0.03 GPU-h of prices)

**The cap works as claimed.** It rejects R = 64 at k = 8,192 (debit 0.120%) and R ≥ 40 at k = 16,384 (0.110%). That agrees with the Lean freezing census, which rates the family dangerous by its joint skips (≥ 14.7% per word).

**Just inside the cap the hole is real per word, but no prover can use it:**
- The families: R = 56 at k = 8,192 (debit 0.096%, per-word joint sets up to 10.2%) and ±1 R = 40 at k = 16,384 (0.098%, up to 16.0%). That is 40–64× γ₀, carried by the conjecture alone.
- Fragment-wide the undebited share is 0 in all 17 cells that pass the cap. No atom is even patchable.
- Across all 128 words of one R = 56 fragment, the most-shared atom is in 24 words' sets and the best pair leaves 3 words unchanged.
- The positive control finds 73–75% fragment-wide on the H100's frozen pure chains. So the zeros mean something.

**No other free credited step:** v2's credit has no promotion term, so the first-promotion hole doesn't exist there, and the rest of the audit above applies.

**↓ (what isn't covered):**
- ~~k from 32,768 to 2^16 wasn't sampled.~~ Sampled at 08:15Z (`r20260930-075758-b6ee`, 17 cells, one fragment each):
  - the cap falls between R = 24 (0.075%) and 28 (0.108%) at k = 32,768, and between R = 16 (0.043%) and 20 (0.119%) at k = 65,536, as the debit's k·R² scaling predicts;
  - 0 fragment-wide undebited atoms and 0 patchable in every cell, inside the cap and out.
- The rating depends on MMA pricing by shape, as for rev1.
- Pearl's noise core isn't attacked.

**Why it can hold at all:** v2 debits only lone skips, so everything rides on the joint part being unrealizable. That is a property of the tensor core's granularity plus per-row noise, not of the cap.

## `cross-group-knowledge/pearl-c`: B (CPU on the bit-exact atom, both atoms)

The claim is that no program saves more than γ_x = 1/800 of the credit through cross-group sets. With the products in hand (an oracle stronger than any program), the saving available on units that pass the cap is 0 fragment-wide, on the sm_120 atom at G = 4 (9 cells) and on the H100 atom (5 cells). An attacker would need to find sets that a greedy with the products can't find either.

**↓:** the sampled families are the census's; there is no adversarial search for fragment-aligned inputs beyond aligned spikes. The per-row noise at δ = 1 is what defeats alignment.
