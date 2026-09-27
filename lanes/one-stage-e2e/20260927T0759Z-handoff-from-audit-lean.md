---
lane: one-stage-e2e
kind: handoff
from: audit-lean
created: 2026-09-27T07:59Z
---

# audit-lean -> one-stage-e2e: core's IntegrityProfile now serves A2; you can drop the 6ccb9b7b workaround

[PR #135](https://github.com/danielreuter/verity/pull/135) (`cursor/profile-exact-bound-f568` @ `322ab36f`, against main)
fixes core's `verity.proofs.profile`. The coordinator has the merge-ready handoff.

- **`rho`** is exact in log space from integer binomials. It never underflows: `rho(n − k)` is 1935.5 at A2's size.
- **`worst_case`** is linear, read off the upper concave envelope, using monotonicity of C(n − m, k)/C(n, k). A2 runs in
  0.23 s.
- **Your numbers are pinned, and they match your direct bisection to the last digit.** A0 254.226… (254), A1 46.924…
  (46), A3 28.256… (28), A2 9675.419457199421 (9,675).
- **What to change on #116.** `verity_one_stage.audit.wrong_units_bound` can go back to
  `p.worst_case(lambda m: float(m))` once #135 merges. Keep your A2 test as a regression, or drop it: core pins the same
  numbers now.
- **One reading note.** The integer bound, floor of the value, is the largest K with C(n − K, k)/C(n, k) ≥ δ. So "at most
  46 wrong" for A1, not 47. That is the count the Lean `audit_count` curve doesn't exclude at δ.
