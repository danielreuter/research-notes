---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T08:42Z · repo: danielreuter/verity · about: [#266](https://github.com/danielreuter/verity/pull/266),
branch `cursor/refinement-paths-cddd` at `5f5b296a`

# Merge request: #266, refinement R7 (Merkle paths, SHA-512)

- **Order:** after #264. The stack below it is #262, #259, #254, #237, #230, #222 and #209.
- **What:** the pinned `merkleCheck_verifies` and `opensOK_of`. A passed SHA-512 Merkle check is the model's
  `Merkle.Verifies`, and a rep's passed checks are the model's `OpensOK` at the proof's openings.
- **Files:** `soundness/FlockSoundness/Refine/Paths.lean`, the aggregator, and `soundness/lean-audit.json` (2 new
  pins, none changed).
- **Audit:** PASS (5,583 declarations, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T0842Z-handoff-from-refinement-266-pin-review.md`.
