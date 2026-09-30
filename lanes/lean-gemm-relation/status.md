---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 06:57Z (23:57 PT): done for tonight's scope, 0 sorry.** PR: [#490](https://github.com/danielreuter/verity/pull/490)
(draft), branch `cursor/lean-gemm-relation-a815` at `461f7020` (merged with `main`; SHA-256 records).

- **Package:** `packages/verity/lean` (Lake package `verity`, no dependencies, builds in about 2 s).
- **Pinned theorems** (18, `lean-audit.json`), all proved with `propext`, `Classical.choice` and `Quot.sound` only:
  - Hopper (`HOPPER_BF16_WGMMA_K16` = `HOPPER_BF16_M16N8K16`; H100, sm_120): `Verity.TC.hopper_step_sound`, `_complete`,
    `_iff`, `_hw`, `hopper_unit_sound`, `hopper_unit_sound_zero`, `hopper_unit_bf16`;
  - Ampere/Ada (`AMPERE_BF16_M16N8K16`; A100, RTX 4090): `Verity.TC.ampere_step_sound`, `_complete`, `_iff`, `_hw`,
    `ampere_unit_sound`, `ampere_unit_sound_zero`, `ampere_unit_bf16`, and `ada_eq_ampere`;
  - the boundary and gadgets: `Verity.TC.pack_sound_complete`, `Verity.TC.Gadgets.range_gadget`, `iszero_gadget`.
  - `_sound`: every witness the relation accepts outputs `decode_state(tc_dot_total(acc, a, b))`; `_complete`: the relation
    accepts a witness for every input; `_iff`: exactly the semantics' output; `_unit_sound`: a unit's chained steps;
    `_unit_bf16`: a unit from `zero_state` commits `cvt_rn_bf16_f32` of the semantics' accumulator; `_hw`: the device's
    word, under the named assumption.
- **Sorry count:** 0. **Recorded audits** (vy-nebius-1, all PASS): `r20260930-062851-727b` (Hopper, 6 pins),
  `r20260930-064104-5cf0` (13 pins), `r20260930-065207-fd65` (16 pins), `r20260930-065514-59bb` (18 pins, final).
- **Assumptions used:** `gemm-hopper-step(arch, bf16)` (`Verity.Assumptions.GemmHopperStep`) by `hopper_step_hw` only;
  `gemm-ampere-step(arch, bf16)` (`GemmAmpereStep`) by `ampere_step_hw` only. Everything else is unconditional.
- **Cross-checks:** the Lean semantics against the Python on 720 vectors (108 kernel-checked in the package and tested from
  Python); the Lean honest witness equals Python's `step_witness` column for column on 60 vectors.
- **Needs:** a named statement reviewer for the 18 pins before merge (all records are new).

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.

**Theorem table** (root's request): `internal/lanes/lean-gemm-relation/theorems.md`.
