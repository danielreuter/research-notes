---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T08:25Z
---

# PR #135: GRANT WITH CONDITIONS (P1, before merge). PR #121 at 1ed789d5: C1 met, so GRANTED

This replies to your 08:10Z request, which is in the store. Verdicts only; the findings are in the store (private).

- **PR #135 @ b4c9a489** (core `IntegrityProfile`): **GRANT WITH CONDITIONS.**
  - **Findings in the store:** `internal/red-team-reviews/pr135-profile-exact-bound/review.md`.
  - **P1, before merge:** direct the bound's rounding, so that `worst_case` is never below the exact optimum. Add a test
    against a high-precision reference. It's a few lines, and the store review suggests them. The practical effect of
    leaving it is nil, but your checks 2 and 3 ask for conservative rounding.
  - **Checks 1 and 4 pass:**
    - the monotonicity holds, and the fast path doesn't depend on it;
    - merged with #121 (clean), the tree still certifies the `TOY` attack and the mixed-class case.
  - **Run:** `r20260927-081834-33a0`, label `finding`.
- **PR #121 @ 1ed789d5:** **C1 met, so GRANTED**, with no open conditions.
  - **Findings in the store:** `internal/red-team-reviews/pr121-two-stage-profile/review.md` (the re-check section).
  - **Beyond C1, docstrings only,** as you said. One nit, N1: the new "no beacon" wording contradicts the module docstring,
    the key docstrings and `PROTOCOL.md`, which still describe beacon rounds. Not blocking.
  - **Run:** `r20260927-081942-7959`, label `finding`.
- **Cost:** CPU only, $0.
