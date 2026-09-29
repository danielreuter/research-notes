---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T09:32Z · repo: danielreuter/verity · about: [#270](https://github.com/danielreuter/verity/pull/270),
branch `cursor/refinement-table-cddd` at `4f7f822a`

# Merge request: #270, refinement R8b (the verifier refines the model's table)

- **Order:** after #266. Under it are #264 and the granted train #209–#262
  (`20260928T0914Z-merge-request-refinement-train-209-262.md`).
- **What:** the pinned `verify_refines` and `verify_tableAfter`. When `Flock.verify` accepts under unsalted SHA-512, on a
  statement that realizes the model's, both reps' compiled games accept on the proofs' messages and the record's coins,
  at the proofs' openings, against one cap. That is one accepting run of `tableAfter`.
- **Files:** `soundness/FlockSoundness/Refine/Table.lean`, the aggregator, and `soundness/lean-audit.json` (2 new pins,
  none changed).
- **Audit:** PASS (5,627 declarations in 106 modules, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T0932Z-handoff-from-refinement-270-pin-review.md`.
- **#264 and #266 have new heads**, `f34c5b6d` and `d3e503d0`: `main` merged in and re-recorded with its printer. Printing
  only, with every hash as reviewed. Their merge requests' heads are superseded by these.
