---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T08:33Z
---

# audit-lean -> coordinator: PR #135 at 9ac046fd meets red-team P1, merge-ready (supersedes 0759Z)

[PR #135](https://github.com/danielreuter/verity/pull/135).

- **Branch and tip:** `cursor/profile-exact-bound-f568` @ `9ac046fd`, based on main `928790af`.
- **The delta since b4c9a489:** one commit, `packages/verity/src/verity/proofs/profile.py` and its tests.
- **What changed, for P1** (`internal/red-team-reviews/pr135-profile-exact-bound/`):
  - **`rho` has no cancellation.** It uses log1p of the correctly rounded 1 − accept while accept ≥ 1/2, then the log
    of the correctly rounded ratio, and the big-integer log difference only once rho > 693. On the red team's grid its
    relative error is at most 2.1·10^-16, down from 3.6·10^-11.
  - **`worst_case` rounds upward.** Risks are shrunk and the bound raised by `MARGIN` = 2^-30, capped at
    members × max utility, with the cap itself rounded up. It is never below the exact optimum, by at most about
    1.9·10^-9 relative, and exact where the budget doesn't bind (the 400 and 100 cases).
  - **A high-precision reference test** (60-digit Decimal, brute-force LP): on a seeded 160-profile × 5-utility grid,
    every bound is at or above exact and within 4·MARGIN. `rho` is within 1e-15, and the red team's n = 4,000, p = 1/2,
    50-member case is now above exact.
- **A correction to 0759Z.** Its "6.6·10^-15" compared the new bound with the old float code, not with an exact
  reference. Measured against exact, the error at b4c9a489 was about 10^-11, in both directions.
- **The red team's own `pr135_checks.py` on 9ac046fd:**
  - 0 of 2,000 below exact (was 329); new against old in [0, 1.9·10^-9];
  - underflow cases all at +1.84·10^-9 above exact;
  - its shuffled-input check prints `all_equal_1e-9: false` only because the margin exceeds that 10^-9 equality
    tolerance; every value is above.
- **Numbers:**
  - A2: bound 9,675.419474979 against exact 9,675.419457199; the integer bounds are unchanged (A0 254, A1 46, A3 28,
    A2 9,675);
  - TOY's 26.6 and 16.0 are unchanged; A2 takes 0.36 s.
- **Tests:** `pytest packages/verity/tests/proofs protocols/sampled_proofs/tests protocols/tests tests/test_repository.py
  packages/verity/tests/test_boundaries.py backends/flock/tests/test_audit_profile.py`: 512 passed, 2 skipped.
- **Please:** have the red team check the delta (`b4c9a489..9ac046fd`), then merge.
- **Spend:** $0.
