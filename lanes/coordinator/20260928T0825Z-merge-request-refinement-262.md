---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T08:25Z · repo: danielreuter/verity · about: [#262](https://github.com/danielreuter/verity/pull/262),
branch `cursor/refinement-basis-cddd` at `2899399d`

# Merge request: #262, refinement R6b (the batched basis)

- **Order:** after #259. The stack below it is #254, #237, #230, #222 and #209.
- **What:** the pinned `basis_eq` and `ligerito_accepts_opening`. From ring switching's output through Ligerito's
  verdict, the executable now refines the model up to the seams and the Merkle interpretation (R7, next).
- **Files:** `soundness/FlockSoundness/Refine/Basis.lean`, the aggregator, and `soundness/lean-audit.json` (2 new
  pins, none changed).
- **Audit:** PASS (5,496 declarations, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T0825Z-handoff-from-refinement-262-pin-review.md`.
