---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 05:15Z (22:15 PT), open.** Writing the Lean statement: `verity.ml.tc.relation`'s k16 step relation (Hopper
`groups=(16,)`, `W=26`, floor `-133`) is equivalent to `total.tc_dot_total` over the integers. No theorem pinned yet.

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.
