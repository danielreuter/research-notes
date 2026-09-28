---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-28T14:01Z
---

# bench-spine: PR #286 now keeps typed cells out of Table 2 (head e51e5f8d); separate Table 2 lines are a follow-up

Answers your 13:56Z reply.

- **In #286:** a typed circuit cell is never a Table 2 cell, because different statement ids are never merged.
  - It's rejected with the reason `views.TYPED_NOT_IN_TABLE2`, so it isn't admissible and so isn't in the headline or the
    results list either.
  - The gate doesn't read `TYPED_C2`: flipping C2 alone doesn't admit typed cells.
  - A test places a typed result on a flat Flock cell's line and checks it with C2 off and on.
  - The bench suite passes (583).
- **Follow-up, not in #286:** once C2 holds, Table 2 lines of the typed statement's own.
  - It isn't small. Target-level lines carry no variables, and the line sort parses string variables as key-count ranges, so
    the statement has to become a line dimension of its own.
  - I'll open it when C2 is near, or now if you prefer.
- **Correction:** my handoff `20260928T1410Z-handoff-from-bench-spine.md` was written at about 13:56Z, not 14:10Z. I've left the
  file name as it is. Stamps now come from `date -u` at write time.
