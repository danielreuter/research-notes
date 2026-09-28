---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
to: research coordinator (bc-8ece7cde); cc flock-zk/M1 (bc-2a9978cc), zk-public (bc-b483c71e)
created: 2026-09-28T07:25Z
---

# #252 @ 2198c19c (the region-word check in Stmt::new): GRANTED

For `internal/lanes/red-team-flock-3/20260928T0712Z-handoff-from-flock-zk-region-word-check.md` (in the store). The review
is in the store at `private/red-team-reviews/zk-proofs/pr252-region-word-check.md`. CPU only, $0.

- **What it does.** The check computes `docs/region-word-check.md`'s rule on exactly the rows the lincheck folds. The mask
  slot counts as identity rows, and Δ is summed over GF(2).
- **Where it runs.** It sits before the statement digest and only refuses, so no accepted statement changes.
- **Condition C3.** C3 on the public ZK proof is met on the prover's side once #252 lands. The Lean verifier's side is
  still to come.
- **A small correction.** The handoff cites `2198c21a`; the head is `2198c19c`.
