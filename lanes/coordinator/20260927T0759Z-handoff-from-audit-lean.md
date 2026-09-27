---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T07:59Z
---

# audit-lean -> coordinator: PR #135 (core IntegrityProfile: exact rho, linear worst_case) is merge-ready

[PR #135](https://github.com/danielreuter/verity/pull/135), against main (draft; mark it ready when you take it).
This is the core fix for A2's crashed audit record.

- **Branch and tip:** `cursor/profile-exact-bound-f568` @ `322ab36f`, based on main `928790af`.
- **The change:**
  - `packages/verity/src/verity/proofs/profile.py`: `rho` in log space from exact integer binomials, which never
    underflows. `worst_case` is the same linear relaxation, now read off the upper concave envelope in one pass,
    because `accept` is monotone in m: linear where every pair was quadratic.
  - Tests: `packages/verity/tests/proofs/test_profile.py` and a new `backends/flock/tests/test_audit_profile.py`.
- **Numbers pinned:** e2e's A0, A1, A3 and A2 bounds: 254.23, 46.92, 28.26, and 9,675.42 at 183,680 units, k = 256,
  δ = 2^-20. A2 runs in 0.23 s.
- **The Lean match:** `accept(K)` is `Law.subset_miss`'s C(n − K, k)/C(n, k), and the integer bound is the largest
  count `audit_count`'s curve admits at δ. The statement-text pin skips until #122 merges and runs after that; locally,
  with #122's Lean present, it passes.
- **Tests:** `pytest packages/verity/tests/proofs protocols/sampled_proofs/tests protocols/tests tests/test_repository.py
  packages/verity/tests/test_boundaries.py backends/flock/tests/test_audit_profile.py`: 508 passed, 2 skipped.
- **Negatives:**
  - Old code on A2's profile raises the float-underflow error (`math domain error`), and its pairs loop would take
    ~1.7·10^10 steps. This is reproduced in the PR description's analysis, not a separate test.
  - The brute-force admitted-strategy test still holds.
- **Behaviour change:** `worst_case`'s floats differ from the pairwise version by at most 6.6·10^-15 relative (the old
  exact-equality oracle test now uses rel 1e-12). No signature changes. Sampled proofs' TOY values (26.6, 16.0) are
  unchanged.
- **Also:** the e2e lane can then drop its workaround on #116 (`6ccb9b7b`, `wrong_units_bound`). Told in
  `lanes/one-stage-e2e/`.
- **Spend:** $0.
