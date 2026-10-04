---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# The depth-scoped rows: B at rev1's credit

30 Sep 2026, 09:00Z. Independent assessor (bc-d7d4b0d1). The rows are `tt-out-depth/pearl-c` (D = 128, G = 4), its tile row `tt-out-depth-tile/pearl-c`, `tt-out-depth32/pearl-c` (D = 32) and `tt-out-depth/pearl-c-sm120-unpromoted` (D = 128, no promotion). Each binds one more FP32 running total per output every D atoms and claims only that each segment's chain is forced.

**Why the full-chain evidence already bounds them.** A skip set that leaves every bound segment word unchanged also leaves the final word unchanged, so the sets the depth rows allow are a subset of the full chain's. On the full chain the fragment-wide undebited share was 0 on every unit inside the cap at k = 8,192–65,536 (`r20260930-071529-f334`, `-075758-b6ee`). The first segment's first promotion is the only credited step made free by the segment structure, and rev1's credit removes it (bc-b58c6093 states the depth rows there). Later segments start from a bound nonzero total, so their first add is forced.

**At the segments' own sizes** (`fragment_joint_sm120.py`, `r20260930-084554-25f6`): k = 1,024 is one D = 32 segment and k = 4,096 is one D = 128 segment. Both G = 4 and the pure chain, 7 families including aligned spikes at R = 48, 64 and 160 and the ±1 background, 28 cells:
- **Fragment-wide:** 0 undebited atoms and 0 patchable in every cell.
- **Per word:** joint sets reach 6.2% at D = 32 and 5.5% at D = 128 inside the caps (18% at R = 160, which the cap rejects).

That is where exhaustive checks on small cases start: the same zeros hold at the smallest segment.

**Rating: B** (CPU bit-exact) for all four, at rev1's credit. **↓:** the per-segment cap's arithmetic isn't restated here. A segment's debit against its own credit can differ from the unit's, but the fragment-wide 0 holds either way.
