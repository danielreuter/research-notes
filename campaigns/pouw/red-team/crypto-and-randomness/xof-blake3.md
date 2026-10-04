---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `xof/blake3`: A

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** Keyed BLAKE3 with a public label as its key, used as an XOF for Pearl-C's noise lines (E_A, E_B, F_A, F_B). It is the random oracle's instantiation, not a PRF.

- BLAKE3 (2020) keeps BLAKE2s's ChaCha-derived compression function at 7 rounds instead of 10. Its keyed and XOF modes are part of the published specification, at a 128-bit security claim.
- Public reduced-round analysis of BLAKE2s/BLAKE3 stays well short of the full rounds; no attack near 2^128 is known.
- Pearl-C needs only output indistinguishability for a public key under distinct labels. That is the standard XOF use.

**Rating.** **A.** Standard primitive, used as designed. The margin is thinner than BLAKE2's (7 of 10 rounds), which is BLAKE3's own design choice.
