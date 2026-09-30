---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 06:42Z (23:42 PT): Hopper and Ampere/Ada both proved, 0 sorry.** PR: [#490](https://github.com/danielreuter/verity/pull/490)
(draft), branch `cursor/lean-gemm-relation-a815` at `5d8ef983` (merged with `main`, records in main's SHA-256 format).

- **Package:** `packages/verity/lean` (Lake package `verity`, no dependencies, builds in about 2 s).
- **Pinned theorems** (13, `lean-audit.json`), all proved with `propext`, `Classical.choice` and `Quot.sound` only:
  - Hopper (`HOPPER_BF16_WGMMA_K16` = `HOPPER_BF16_M16N8K16`; H100, sm_120): `Verity.TC.hopper_step_sound`, `_complete`,
    `_iff`, `_hw`, `hopper_unit_sound`, `hopper_unit_sound_zero`;
  - Ampere/Ada (`AMPERE_BF16_M16N8K16`; A100, RTX 4090): `Verity.TC.ampere_step_sound`, `_complete`, `_iff`, `_hw`,
    `ampere_unit_sound`, `ampere_unit_sound_zero`, and `ada_eq_ampere`.
  - `_sound`: every witness the relation accepts outputs `decode_state(tc_dot_total(acc, a, b))`; `_complete`: the relation
    accepts a witness for every input; `_iff`: exactly the semantics' output; `_unit_sound`: a unit's chained steps;
    `_hw`: the device's word, under the named assumption.
- **Sorry count:** 0. **Recorded audits:** `r20260930-062851-727b` (Hopper, 6 pins: PASS); `r20260930-064104-5cf0` (13 pins).
- **Assumptions used:** `gemm-hopper-step(arch, bf16)` (`Verity.Assumptions.GemmHopperStep`) by `hopper_step_hw` only;
  `gemm-ampere-step(arch, bf16)` (`GemmAmpereStep`) by `ampere_step_hw` only. The equivalences are unconditional.
- **Not yet:** `pack_relation` (the BF16 output boundary: FP32 word to `cvt.rn.bf16.f32`).
- **Cross-checks:** the Lean semantics against the Python on 720 vectors (80 kernel-checked in the package and tested from
  Python); the Lean honest witness equals Python's `step_witness` column for column on 60 vectors.
- **Needs:** a named statement reviewer for the 13 pins before merge (all records are new).

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.

**Theorem table** (root's request): `internal/lanes/lean-gemm-relation/theorems.md`.
