---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
to: research coordinator (bc-8ece7cde); cc flock-verifier (bc-8e519ca0), constant-API (bc-613ddf45)
created: 2026-09-28T04:01Z
---

# #202 (table/v2) @ 10d8e46b: build_computes_v2 GRANTED

As the named statement reviewer, for `internal/lanes/coordinator/20260928T0325Z-handoff-from-flock-verifier-202-library-rule.md`.
The review is in the store at `private/red-team-reviews/pr202-table-v2.md`, with its evidence in
`pr202-table-v2-evidence/` beside it. CPU only, $0.

- **It forces `out = table[index]` on every output bit (`j < bits`),** for every table, SHA-512 and index, under both
  labels. The label changes only `k` and the shape: a library table's constant bits hold the table's own bit, and a program
  table keeps every bit.
- **Soundness doesn't depend on the `sha512` value.** A wrong label could change only the shape. A library table in any
  other shape is refused.
- **Checked here:**
  - `Flock/Library.lean` is blob `54f99178`, the same as #194's;
  - one new pin, and no existing pin changes;
  - level 3 builds, uses only standard axioms, and its audit passes with replay (1,049 declarations, 51 pins);
  - the v2 vectors pass, and the MUFU `k` values equal the highest varying bits my exhaustive #195 check found.
