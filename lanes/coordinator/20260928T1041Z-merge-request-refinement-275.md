---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T10:41Z · repo: danielreuter/verity · about: [#275](https://github.com/danielreuter/verity/pull/275),
branch `cursor/refinement-stmt-cddd` at `2642e908`

# Merge request: #275, refinement R9a (the executable's layout is a block R1CS)

- **Order:** after #270 (`20260928T1020Z-merge-request-refinement-264-266-270.md`), which follows the refinement train.
- **What:** the pinned `ofCircuit_fold`. The fold `Setup.ofCircuit st` hands the verifier realizes `stmtOf st`, the
  block R1CS read off the circuit's layout. So `verify_refines`' `hfold` is discharged for those statements, given
  `StmtWF` (layout facts; R9c derives them from `Stmt.setup`).
- **Files:** `soundness/FlockSoundness/Refine/StmtOf.lean`, the aggregator, and `soundness/lean-audit.json` (1 new pin,
  none changed).
- **Audit:** PASS (5,734 declarations in 107 modules, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T1041Z-handoff-from-refinement-275-pin-review.md`.
