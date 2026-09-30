---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 06:12Z (23:12 PT), open: soundness proved; completeness in progress.** PR: [#490](https://github.com/danielreuter/verity/pull/490) (draft).

- **Package:** `packages/verity/lean` (Lake package `verity`, no dependencies, builds in ~2 s), branch
  `cursor/lean-gemm-relation-a815`, commit `60ebd57e` (local: the VM's GitHub token expired at ~05:35Z, push pending).
- **Definitions:** `Verity.TC.Spec` transcribes `total.tc_dot_total` (checked against the Python on 720 vectors, 0
  mismatches); `Verity.TC.Relation` transcribes `relation.check_step`, independent of the semantics, with the witness
  shape fixed.
- **Pinned statements** (`lean-audit.json`, recorded on `sorry` stubs):
  - `Verity.TC.hopper_step_sound`: every accepted witness outputs `decode_state(tc_dot_total(acc, a, b))`;
  - `Verity.TC.hopper_step_complete`: the relation accepts a witness for every input;
  - `Verity.TC.hopper_step_iff`: the relation's possible outputs are exactly the semantics' (proved from the two);
  - `Verity.TC.hopper_step_hw`: under `gemm-hopper-step`, the output is the decode of the device's word.
- **Sorry count:** 1 (`hopper_step_complete`; `hopper_step_iff` uses it). `hopper_step_sound` and `hopper_step_hw` are proved with `propext`, `Classical.choice`, `Quot.sound` only.
- **Assumptions used:** `Verity.Assumptions.GemmHopperStep` = `gemm-hopper-step(arch, bf16)`, only by `hopper_step_hw`.
  The equivalence itself is unconditional.

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.

**Theorem table** (root's request): `internal/lanes/lean-gemm-relation/theorems.md`.
