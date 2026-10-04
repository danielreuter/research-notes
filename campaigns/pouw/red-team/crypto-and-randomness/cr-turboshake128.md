---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `cr/turboshake128`: A

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** No adversary below 2^128 work finds two inputs with equal 32-byte TurboSHAKE128 outputs (Pearl-C's message and leaf commitments).

- A 256-bit output gives a 2^128 generic collision bound, which equals the capacity bound (c = 256) of TurboSHAKE128.
- No collision attack comes near 12 rounds (see `xof/turboshake128`).

**Rating.** **A.** The claim equals the generic bound of the design.
