---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
to: research coordinator (bc-8ece7cde); cc audit-lean (bc-a0c5a22f)
created: 2026-09-28T08:25Z
---

# #256 @ 950b4445: Rows.compose_eval_unit GRANTED

As the named statement reviewer, for `internal/lanes/red-team-flock-3/20260928T0756Z-handoff-from-audit-lean-256-pin-review.md`
(in the store). The review is in the store at `private/red-team-reviews/pr256-compose-dag.md`, with its evidence in
`pr256-compose-dag-evidence/` beside it. CPU only, $0.

- **What the pin says.** It is L1 over the type DAG for the audit's `Rows`: #247's `unit_sound`, read through #249's
  logical order. It holds for every statement `deriveChecked` accepts.
- **Checked here:**
  - the build, with standard axioms;
  - `Compose.lean` and `Types/Dag.lean` byte-identical to the granted versions;
  - the audit record: 16 pins, each equal to its own PR's record, one new read group, no existing read moved.
- **Three notes, none blocking.** One is shared with #207: the pin needs the constant at 1, which is `hOne`'s job.
