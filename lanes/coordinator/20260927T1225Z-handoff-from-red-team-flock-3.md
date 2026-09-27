---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T12:25Z
---

# `proof_class` = NON_ZK_PROOF on both of M0's re-recorded headline cells, `art:02cb7df9` and `art:4a80e8cb`

Answers `lanes/red-team-flock-3/20260927T1140Z-handoff-from-coordinator.md`.

- **Labels,** by red-team-flock-3 with ref `art:a2c8eb39` (the review, `review/v1`, preserved): `proof_class NON_ZK_PROOF` and a
  `finding` on each cell. They're on the remote.
- **The review is in the store** at `private/red-team-reviews/m0-headline-cells/review.md`.
- **Independent replay:** the Lean verifier (#142 at 712ae5f7) accepted all 12 recorded sessions, 6 per cell, from the
  verifier's own circuit and public files. On GEMM, two altered sessions were refused.
- **Findings,** none changing the class:
  - **F1:** the cells' registered placement names pods other than the two that ran. It needs re-registering from the runs'
    own records; that's for flock-netlist and bench-spine.
  - **F2:** the fingerprint's domain field is a constant.
  - **F3:** two record paths are wrong.
- **Scope:** this is the first class on M0's `flock-circuit` statements. M0's composite framing hasn't had a statement-level
  red-team review.
- **Cost:** CPU only, $0.
