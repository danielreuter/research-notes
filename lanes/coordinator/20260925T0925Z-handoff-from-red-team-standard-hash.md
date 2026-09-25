---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:25Z
---

# red-team SH: sp1-committed relation-committed/v1 R3 fix b54e42ed: FAIL (open) on the `--instances` path; an SP1 committed cell counts only with `instance_roots: true` on every rep

This is a code review; nothing was run e2e. Details and the fix are in
`lanes/sp1-committed/20260925T0925Z-handoff-from-red-team-standard-hash.md`.

- The `--batch` path is correct: `committed-verify` re-commits the rows from the batch and compares the roots, and
  `vector_run` requires `instance_roots is True`.
- Without `--batch`, `committed-verify` emits `"ok": true, "instance_roots": null`.
- `vector_run --instances` (the bf16-ampere frozen set) never passes `--batch` and skips the prover-chosen-roots negative.

So on that path prover-chosen roots (art:b11bc6ee) are still accepted. **A Table 2 SP1 committed cell built from an
`--instances` run is pulled** until its reps show `instance_roots: true`, or a non-producer root recomputation matches.
Cells from `--batch` runs with `instance_roots: true` stand; the guest and tree-check PASS is unchanged.
