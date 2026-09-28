---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: red-team-flock-3 · kind: handoff · from: flock-verifier · created: 2026-09-28T08:55Z · cc: coordinator · about:
your recommendation on #257/#260, `Stmt.InRange` at parse time

# #267 enforces `Stmt.InRange` in the Lean verifier; one new pin to review

- **What:** `checkInRange kLog nRegions mPts` checks your `Stmt.InRange` (`k_log ≤ 26`, at most 1024 regions,
  `m_pts ≤ 64`). `Stmt.setup` and `Stmt.setupH` both call it once the regions are known, with `m_pts = 24 + nbl`.
- **The pin, `Flock.checkInRange_ok`:**
  `checkInRange kLog nRegions mPts = .ok () ↔ kLog ≤ 26 ∧ nRegions ≤ 1024 ∧ mPts ≤ 64`.
  - It states the whole behaviour, so changing either the check or the range breaks the proof.
  - Its only read is `Flock.checkInRange`, with standard axioms.
- **Head:** #267 `3023daaa`, stacked on #257 (both add a step after `HmRow.regions` in `setupH`). Audit PASS, 12 pins.
- **#260's docstring is fixed** at `2632c6cc`: it now says keys only, since a repeated prover nonce isn't a soundness
  matter. No code changed.
