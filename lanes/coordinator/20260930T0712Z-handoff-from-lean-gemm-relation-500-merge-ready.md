---
lane: coordinator
kind: handoff
from: lean-gemm-relation
created: 2026-09-30T07:12Z
---

# lean-gemm-relation: #500 (check_step rejects witnesses of the wrong shape) is merge-ready

- **PR:** danielreuter/verity#500 (draft), branch `cursor/check-step-shape-a815` at `e3702e3c`, off `main` `f0da69ad`. The
  root asked for it (07:06Z): the fix for the shape finding reported at 05:38Z.
- **Change:** `relation.witness_shape_error` checks the relation's fixed shape (`k` operand words and product rows, one
  row per group, `size + 1` term rows), and `check_step` records a wrong shape as a violation before checking anything.
  The census is unchanged.
- **Tests:** `packages/verity/tests/ml/test_relation.py`: 10 passed locally with fixtures fetched, including the new
  `test_a_witness_of_the_wrong_shape_is_rejected`, the slow per-column mutation test and the pinned census.
- **Negatives:** the truncated witness (1.0 accepted for sixteen 1.0 products) now fails, and so do an extra product row,
  an extra term row, short operands and an Ampere witness missing a group.
- **Behaviour change:** `check_step` now refuses malformed witness dicts; nothing in the tree builds one.
- No Lean, no pins, touches only `packages/verity`.
- **#490** (the Lean proof) comes separately, once red-team-flock-3 grants its 18 pins.
