---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out-aw/*` (TT_OUT for the approved-weights fork): B for the two FP8 rows; NVFP4 not rated

30 Sep 2026, 08:50Z. Independent assessor (bc-d7d4b0d1). The rows state TT_OUT for Pearl-C with the weights bound to a registered checkpoint. The deployed codes are the keyed rotation of a committed master, and the noise is on the activations only: B̃ = B, U = C̃ − β·E_A·(B·F_A)ᵀ (peel depth r), with no A′·F_B columns.

**What they rest on, and each component's rating:**
- the chain-forcing part as in the (C̃, U) rows: `tt-out/pearl-c-sm120-rev1` B, v2 at cap 1/1,000 B, `cross-group-knowledge` B, `no-exact-rewrite` B;
- the fork's two new components: `known-weights/sm120-e4m3` B and `structure-free/rot-e4m3` B ([note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/known-weights-and-structure-free.md));
- the rotation's key (`beacon-unpredictability`, C until a beacon is named). It is taken as uniform here, as TT_OUT takes the salt.

**What changes with the fork, checked:**
- **The credit.** The fork drops the A′·F_B term and halves the peel's depth. G = 4 still has promotions, so **the fork must be stated at rev1's credit** (k/(32G) − 1 promotions per word). Otherwise it inherits the first-promotion D. The row cites rev1's `Costs`; the table should say so explicitly. No other credited step is free, by the same term-by-term audit as rev1 ([rev1 note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/repair-rows-rev1-and-v2-cap.md)).
- **Joint skips with noise-free weights.** Per-word joint sets still depend on each activation row's own noise, so they stay word-specific. The lane's census on transformed Qwen2.5-7B weights finds 0.0% skippable (0.2% from planted duplicates, uncredited by the rule; `r20260930-073807-c5c8`). A fragment-wide set can be no larger, and the (C̃, U) rows' fragment test found 0 on every unit inside the cap.
- **The v2 cap.** After the rotation the weights have no spikes (max/RMS ≤ about 6). The R = 64 aligned-spike family needs spikes on both operands, so it can't form, and 1/400 may suffice, as the lane notes. Nothing here depends on it.

**Ratings:**
- **B** (CPU bit-exact, at rev1's credit): `tt-out-aw/pearl-c-sm120` and `tt-out-aw/pearl-c-sm120-unpromoted`, with their tile twins.
- **Not rated:** `tt-out-aw/pearl-c-nvfp4-sm120` and its tile twin. They wait on the Pearl-C4 replay and on NVFP4's `known-weights` and `structure-free` rows (C).
- **↓:** the census on transformed weights at GPU scale (the lane's fill candidate), and more keys.
