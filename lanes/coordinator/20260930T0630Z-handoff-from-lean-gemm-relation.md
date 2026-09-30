---
lane: coordinator
kind: handoff
from: lean-gemm-relation
created: 2026-09-30T06:30Z
---

# lean-gemm-relation: the GEMM step relation proof closes (Hopper, 0 sorry), PR #490, needs a statement reviewer

- **Proved in Lean, 0 sorry, standard axioms only:** `verity.ml.tc.relation`'s k16 step relation is exactly
  `total.tc_dot_total` for the Hopper pipeline (H100 and sm_120), over the integers, both alignment modes:
  `Verity.TC.hopper_step_sound`, `_complete`, `_iff`, plus `hopper_unit_sound` (a verification unit's chained steps).
  Under the named assumption `gemm-hopper-step`, `hopper_step_hw` makes it the device's word.
- **Recorded:** `audit.py --build` on vy-nebius-1, run `r20260930-062851-727b`: PASS, 1,073 declarations, 6 pins.
- **PR:** danielreuter/verity#490 (draft), branch `cursor/lean-gemm-relation-a815` at `a0a1d503`. New package
  `packages/verity/lean` (no dependencies); the placement is flagged in the PR.
- **Before merge:** a named statement reviewer for the six new pins (Spec.lean against total.py/models.py/term.py,
  Relation.lean against relation.py).
- **Not yet:** Ampere/Ada (two groups of eight) and the BF16 output boundary (`pack_relation`). I start Ampere/Ada next.
- Status and the theorem table: the Project store's `internal/lanes/lean-gemm-relation/status.md` and `theorems.md`.
