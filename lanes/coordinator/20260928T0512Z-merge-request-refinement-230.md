---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T05:12Z · repo: danielreuter/verity · about: [#230](https://github.com/danielreuter/verity/pull/230),
branch `cursor/refinement-lincheck-cddd` at `acf6534c`

# Merge request: #230, refinement R3 (the lincheck)

- **Order:** after #209 and #222. Both are in this branch.
- **What:** `FoldRealizes`, and the pinned `lincheck_refines`.
- **Files:** `soundness/FlockSoundness/Refine/{Realizes,Lincheck}.lean`, `Refine/Tapes.lean` (`lcMsgs`, `ClaimRel`), the
  aggregator, and `soundness/lean-audit.json` (1 new pin, none changed).
- **Audit:** PASS (4,923 declarations, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T0512Z-handoff-from-refinement-230-pin-review.md`.
