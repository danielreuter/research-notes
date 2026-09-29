---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T14:46Z · repo: danielreuter/verity · about: [#291](https://github.com/danielreuter/verity/pull/291),
branch `cursor/refinement-setup-cddd` at `363a4264`

# Merge request: #291, refinement R9c (both setups' statements are well formed)

- **Order:** after #278 (`20260928T1112Z-merge-request-refinement-278.md`) and #282 (the verifier lane's refusals). The
  branch contains both.
- **What:** the pinned `setup_wf`, `setupH_wf` and `stmtOf_linkLayout`. For the verifier's own statements, R9's layout and
  region facts are theorems, so `verify_refines_ofCircuit` has only `13 ≤ m` and the unsalted scheme left.
- **Files:**
  - `soundness/FlockSoundness/Refine/Setup.lean` and `Refine/Walk.lean`;
  - the aggregator;
  - `soundness/lean-audit.json`: 3 new pins, none changed, and the package's first `compile_time` entry, for `Walk`'s
    tactic.
- **Build and audit:** audit PASS (6,087 declarations in 110 modules, standard axioms, replay clean).
  - `Refine/Setup.lean` takes about 9 GB to build, one theorem at a time (`Elab.async false`), so the `check` machine needs
    that much memory.
  - The Lean-package, repository and audit-tool tests pass (35).
- **Statement reviewer:** red team, requested in `lanes/red-team-flock-3/20260928T1446Z-handoff-from-refinement-291-pin-review.md`.
- **`check`:** not recorded here. This VM has no evidence store, so please record one on `363a4264`.
