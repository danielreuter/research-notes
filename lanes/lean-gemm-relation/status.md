---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# lean-gemm-relation: status

**2026-09-30 06:32Z (23:32 PT): the proof closes. 0 sorry.** PR: [#490](https://github.com/danielreuter/verity/pull/490) (draft),
branch `cursor/lean-gemm-relation-a815` at `a0a1d503`.

- **Package:** `packages/verity/lean` (Lake package `verity`, no dependencies, builds in about 2 s).
- **Pinned theorems** (`lean-audit.json`), all proved with `propext`, `Classical.choice` and `Quot.sound` only:
  - `Verity.TC.hopper_step_sound`: every witness the relation accepts outputs `decode_state(tc_dot_total(acc, a, b))`;
  - `Verity.TC.hopper_step_complete`: the relation accepts a witness for every input;
  - `Verity.TC.hopper_step_iff`: the relation's possible outputs are exactly the semantics';
  - `Verity.TC.hopper_step_hw`: under `gemm-hopper-step`, the output is the decode of the device's word;
  - `Verity.TC.hopper_unit_sound`, `hopper_unit_sound_zero`: a verification unit's chained steps output the decode of
    `tc_dot_total` folded over the unit.
- **Sorry count:** 0. **Recorded audit:** run `r20260930-062851-727b` on vy-nebius-1, `audit.py --build`: PASS, 1,073
  declarations, 6 pins, kernel replay, 23 s build.
- **Assumptions used:** `Verity.Assumptions.GemmHopperStep` = `gemm-hopper-step(arch, bf16)`, only by `hopper_step_hw`. The
  equivalence itself is unconditional.
- **Scope:** the Hopper step (`HOPPER_BF16_WGMMA_K16`, same parameters as `HOPPER_BF16_M16N8K16`: H100 and sm_120), both
  alignment modes. Not yet: Ampere/Ada (two groups of eight, `W = 25`) and `pack_relation` (the BF16 output boundary).
- **Cross-checks:** the Lean semantics against the Python on 720 vectors (48 kernel-checked in the package and tested from
  Python); the Lean honest witness equals Python's `step_witness` column for column on 60 vectors.
- **Needs:** a named statement reviewer for the six pins before merge (all records are new).

**Finding (low):** `relation.check_step` does not check the witness's shape. A witness with truncated `prod`/`terms` lists is
accepted with a wrong output (1.0 where the semantics give 16.0). Details: `private/lean-gemm-relation/finding-check-step-shape.md`.
The Lean relation fixes the shape by type.

**Theorem table** (root's request): `internal/lanes/lean-gemm-relation/theorems.md`.
