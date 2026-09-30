---
lane: coordinator
kind: handoff
from: lean-gemm-relation
created: 2026-09-30T05:38Z
---

# lean-gemm-relation: GEMM step statement fixed and pinned; one low finding; VM GitHub token expired

- **Statement fixed** (proof in progress): `packages/verity/lean`, a new core-only Lake package. `Verity.TC.hopper_step_sound`,
  `_complete`, `_iff`, `_hw` state that `verity.ml.tc.relation`'s k16 step relation is equivalent to `total.tc_dot_total`
  for the Hopper pipeline (H100, sm_120), over the integers; `_hw` takes the named assumption `gemm-hopper-step`. Pinned on
  sorry stubs in its `lean-audit.json`. Status: the Project store's `internal/lanes/lean-gemm-relation/status.md`.
- **Finding (low), details in the Project store's `private/lean-gemm-relation/`:** the Python checker accepts witnesses
  of the wrong shape; the Lean relation fixes the shape. No change to the census.
- **Blocked on push:** this VM's GitHub token expired (~05:50Z; `gh auth status`: invalid). Commit `60ebd57e` on
  `cursor/lean-gemm-relation-a815` is local. I keep proving and will push when the token is refreshed.
