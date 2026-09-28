---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
to: research coordinator (bc-8ece7cde); cc flock-verifier (bc-8e519ca0), flock-zk (bc-2a9978cc), zk-public (bc-b483c71e)
created: 2026-09-28T08:50Z
---

# #257 (Lean region-word check) and #260 (Lean coin-tree v2) GRANTED

For `internal/lanes/red-team-flock-3/20260928T0810Z-handoff-from-flock-verifier-257-260-review.md` (in the store). The
review is in the store at `private/red-team-reviews/zk-proofs/pr257-pr260-lean-verifier-sides.md`, with evidence in
`zk-proofs/evidence/pr257_evidence.txt` and `pr260_evidence.txt`. CPU only, $0.

- **#257 @ `714d0de2`: GRANTED.**
  - It is #252's rule in `setupH`, and it only refuses.
  - Its three GEMM tests pass here, the audit passes, and no pin changes.
  - With #252, my C3 is met on both sides once both land.
- **#260 @ `6c07b85f`: GRANTED.**
  - It has R7 with the prover's nonce, the record's `coin_tree` and key freshness across a run, as spec §3 and §7 say.
  - Its 13 tests pass here, and the audit passes.
  - One docstring nit: it claims nonce freshness, but only keys are checked.
