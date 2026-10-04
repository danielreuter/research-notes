---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out-u/*` (TT_OUT over U alone): B for the two FP8 rows; the FP4 row unrated

30 Sep 2026, 08:15Z. Independent assessor (bc-d7d4b0d1). The row is bc-b58c6093's restatement (`internal/pouw/ttout-restatements.md` §3). It is stronger than the (C̃, U) rows: it also carries skip sets that move C̃ only inside the bits U ignores.

**The attack.** `fragment_u_only_sm120.py` (`r20260930-075649-ff36`) reruns [the fragment test](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/fragment-joint-skips.md) with U-only acceptance: a skip counts if every checked U word is unchanged, whatever happens to C̃. Setup:
- the scheme's own replay: `form_v1`, `peel_factors_*` and `pearl_c.peel` on the sm_120 records at `af274df9`;
- chain replays on the census's vectorized atom, checked against `pearl_c.chain` word for word;
- the v1 (G = 4) and v2 (no promotion) records, 8 families including aligned spikes at the v2 cap (R = 48 and 56) and R = 444, at k = 1,024 and 8,192;
- one 16 × 8 fragment per cell, plus a per-word U-greedy on all 128 of its words.

**Results** (30 of the 32 cells pass their cap; the R = 444 family is rejected at k = 8,192 on both records):
- **Fragment-wide:** 0 atoms skippable under U-only acceptance in every cell, and 0 patchable (U unchanged on ≥ 123 of 128 words).
- **Per word:** the U-greedy's sets are at most 0.39% of atoms, and none of the accepted atoms moves C̃ (0.00 per word on average). They are lone skips the debit already removes. No atom is found whose skip changes C̃ but not U, which matches bc-b58c6093's lone-skip result at larger scale.

**Why larger sets can't do better fragment-wide.** U ignores a +1-ulp move of C̃ on only 8–32% of words (bc-b58c6093's measurement). A skip set that is U-invisible on all 128 words of a fragment therefore leaves C̃ exactly unchanged on the other 68–92%. That is the (C̃, U) fragment question, whose answer is 0 on every unit inside the cap. U's slack buys at most the patchable margin, and that is also 0.

**Rating.**
- **B** (CPU bit-exact on the scheme's replay, 0.03 GPU-h of prices): `tt-out-u/pearl-c-sm120-rev1` and `tt-out-u/pearl-c-sm120-unpromoted-cap1000`, with their tile twins.
- **Not rated:** `tt-out-u/fp4-sm120`. There is no Pearl-C4 replay in code; the FP4 chain being exact on its domain doesn't settle U's slack.
- **↓:** the per-word U-greedy is single-atom, so near-cancelling pairs inside U's slack are bounded by the argument above, not measured.
