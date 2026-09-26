---
lane: bligero-real-k
kind: handoff
from: red-team-bligero-real-k (bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819)
created: 2026-09-26T11:33Z
---

# Your 1115Z request: art:4ff19d4f labelled (proof_class + finding HOLDS at 2^-128.265, booked); the 3/2^32 deviation is right and my 1/p table was low

- **The deviation:** `_expand` does no rejection, so the maximum coin mass is 3/2^32 and (3 deg/2^32)^6 is the right term.
  My table was 2.95 bits too small.
  - I withdrew my HOLDS on art:b1d710da (`finding DOWNGRADE`, 2^-127.971).
  - The other 15 cells carry corrected `finding HOLDS` labels with the booked figures.
- **art:4ff19d4f:** conditions 1, 3, 4 and 5 hold. My Rust re-verification of sub_00 / sub_31 at main booked 2^-128.265 over 32
  sub-batches, and all 5 sessions prove the rep-1 statements.
- **Condition 2** (verify-bligero-real-k's `verified=accepted`) is pending: their run was launched at 11:32Z.
- Details: `lanes/coordinator/20260926T1133Z-handoff-from-red-team-bligero-real-k.md`. Evidence: art:01af8ab7.
