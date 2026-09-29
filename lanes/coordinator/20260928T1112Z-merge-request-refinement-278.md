---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T11:12Z · repo: danielreuter/verity · about: [#278](https://github.com/danielreuter/verity/pull/278),
branch `cursor/refinement-regions-cddd` at `c5a1180a`

# Merge request: #278, refinement R9b (the region claims; verify refines for `Setup.ofCircuit`)

- **Order:** after #275 (`20260928T1041Z-merge-request-refinement-275.md`).
- **What:**
  - the pinned `ofCircuit_extra`: the statement's region claims are the model's `extraClaims`;
  - the pinned `verify_refines_ofCircuit`: `verify_refines` for `Setup.ofCircuit st`, with `hfold` and `hext` both
    discharged. Its hypotheses left are layout and region facts (`StmtWF`, `RegionsWF`; R9c) and the unsalted scheme
    (R10).
- **Files:** `soundness/FlockSoundness/Refine/Regions.lean`, the aggregator, and `soundness/lean-audit.json` (2 new pins,
  none changed).
- **Audit:** PASS (5,866 declarations in 108 modules, standard axioms, replay clean).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T1112Z-handoff-from-refinement-278-pin-review.md`.
- **One open item for flock-verifier, possibly:** the regions' free bits are assumed distinct, and `mkRegion` doesn't
  check it. R9c tries to prove it from the layout first; if that fails, the fix is a one-line check in `mkRegion`.
