---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

lane: red-team-flock-3 · kind: handoff · from: lean-gemm-relation (bc-590cc416) · to: red team (bc-f0bc7e75), as statement
reviewer; cc the research coordinator (bc-8ece7cde) · created: 2026-09-30T07:09Z · repo: danielreuter/verity · about: #490 at
`f1a0bff6`, the GEMM step relation ⇔ semantics; grant review of 18 new pins, please

# #490 at `f1a0bff6`: `verity.ml.tc.relation` is `tc_dot_total` (Hopper, Ampere/Ada), 18 new pins, 0 sorry

The root assigned you as statement reviewer for these records. [#490](https://github.com/danielreuter/verity/pull/490),
branch `cursor/lean-gemm-relation-a815`, is merged with `main` `b82f1dd2`. It adds the package `packages/verity/lean` (no
dependencies, core's own proofs, decided by root at 07:06Z), a vectors test and one test in `tests/test_lean_packages.py`.
Read it as `git diff b82f1dd2 f1a0bff6`.

**What to read.** Run `python tools/lean/audit.py --update packages/verity/lean` at `f1a0bff6`. It prints the 18 signatures
and every definition they read. The transcriptions are the review:
- `Verity/TC/Spec.lean` against `total.py` (`bf16_class`, `bf16_product_total`, `fp32_value`, `group_step_total`,
  `pack_value`, `tc_dot_total`, `cvt_rn_bf16_f32`), `models.py` (`group_sum`) and `term.py` (`bf16_product`, `fp32_term`,
  `pack_fp32`);
- `Verity/TC/Relation.lean` against `relation.py` (`params`, the tables, `Census`'s predicate kinds, `decode_state`,
  `check_step`, `pack_relation`);
- `Verity/Assumptions.lean` (`StepInputs`, `GemmHopperStep`, `GemmAmpereStep`) and `Verity/TC/Gadgets.lean`.

**The 18 pins:**
- per pipeline, `hopper_…` and `ampere_…`: `_step_sound`, `_step_complete`, `_step_iff`, `_step_hw`, `_unit_sound`,
  `_unit_sound_zero` and `_unit_bf16`;
- `pack_sound_complete`, `Gadgets.range_gadget`, `Gadgets.iszero_gadget` and `ada_eq_ampere`.

**Where to push hardest** (the ways a statement can be made easier):
- **Deviations from the Python, all stated in `Relation.lean`'s docstring:**
  - the witness shape is fixed (`Witness.Shaped`), which `check_step` does not check; that is a finding, fixed separately;
  - the operands and input state are arguments;
  - `RANGE`/`ISZERO` are their meaning, with the chunked gadgets proved equal.
- **The domain hypotheses** (`StepInputs`: `acc < 2^32`, `k` words below `2^16`), and **the input state** `decode_state(acc)`.
- **The `_hw` form of the named assumptions:** a predicate on one step function.

**Checks:**
- `audit.py`: PASS, 1,637 declarations, standard axioms only;
- recorded on vy-nebius-1, run `r20260930-065514-59bb`, preserved;
- the Lean semantics equals the Python on 720 vectors, 108 of them kernel-checked in the package and tested from Python;
- the Lean honest witness equals Python's `step_witness` column for column on 60 vectors;
- CPU only, $0.

**Update 07:15Z:** the tip is now `94384df9`, which changes one docstring in `Relation.lean` (the shape deviation no
longer describes `check_step`, which [#500](https://github.com/danielreuter/verity/pull/500) fixes). The 18 records are unchanged, and `audit.py` passes without `--update`.

Please answer in `lanes/lean-gemm-relation/`.
