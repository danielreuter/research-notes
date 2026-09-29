---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T05:26Z · repo: danielreuter/verity · about: [#237](https://github.com/danielreuter/verity/pull/237),
branch `cursor/refinement-opening-cddd` at `236160ed`

# Merge request: #237, refinement R4 (ring switching and batching)

- **Order:** after #209, #222 and #230. All three are in this branch.
- **What:** the pinned `opening_refines`, which completes the three phases before Ligerito.
- **Files:** `soundness/FlockSoundness/Refine/Opening.lean`, `Refine/Tapes.lean` (`opMsgs`, `OpenRel`), the aggregator,
  and `soundness/lean-audit.json` (1 new pin, none changed).
- **Audit:** PASS (4,982 declarations, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T0526Z-handoff-from-refinement-237-pin-review.md`.
