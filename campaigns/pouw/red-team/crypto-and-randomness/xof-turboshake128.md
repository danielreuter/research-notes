---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `xof/turboshake128`: A

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** TurboSHAKE128 (Keccak-p[1600, 12], rate 168 bytes) under a domain byte, as an XOF for Pearl-C's message and leaf digests.

- TurboSHAKE is the Keccak team's 12-round sponge, the same permutation as KangarooTwelve, specified with its security claim of 128 bits.
- Public cryptanalysis of Keccak reaches about half the 12 rounds: practical collisions to 5–6 rounds, preimages fewer.
- It is not yet a `verity.claims` instance (the table's code follow-up).

**Rating.** **A.** A studied permutation at a 2× round margin over the best attacks; the XOF claim is the design's.
