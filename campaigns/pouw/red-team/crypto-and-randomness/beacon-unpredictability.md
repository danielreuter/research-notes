---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `beacon-unpredictability`: C

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** The beacon rounds that key the salt, and Pearl-C's audit draw, are unpredictable and unbiasable until the commitments they follow.

- The row names no beacon. `PROTOCOL.md` says "a beacon round", so the claim's instance (operator, threshold, round schedule) is unspecified.
- Well-studied beacons exist; drand's threshold BLS is the obvious one. Its unpredictability rests on the threshold assumption (fewer than t colluding nodes) and on BLS's security. With one of them named, the row would be A or B on that beacon's assumptions.
- What breaks everything is a predictable salt. Preprocessing would then include the noise, and every hardness row above would be void. A biasable draw round would let a prover commit bad tiles where the draw won't land.

**Rating.** **C.** There is nothing yet to rate but the property. The falsifier, or the move up, is naming the beacon and its threshold.
