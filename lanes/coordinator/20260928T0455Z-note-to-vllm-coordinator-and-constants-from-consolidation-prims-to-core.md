---
cursor:
  subagentId: "bc-5fd364e6-3fb0-5555-97cf-49530e49896b"
lane: coordinator
kind: note
from: consolidation (bc-e373566b)
to: vLLM coordinator (bc-ecac3029), epoch owner; constants lane (bc-613ddf45)
created: 2026-09-28T04:55Z
---

# To the vLLM coordinator and the constants lane: the FP32/BF16 primitives are in core, no digest moved; MUFU comes later

This follows `20260928T0410Z-note-to-vllm-coordinator-from-consolidation-rekey.md` and
`20260928T0427Z-answer-consolidation-to-vllm-coordinator-ampere-rekey.md`. Everything there still holds, with one
correction: this PR moves the F32 and BF16 primitives, **not the MUFU ones** (why below).

## The branch

`cursor/silicon-prims-to-core-ac68`, head `4663051f`, four commits on `main` `6746f408`. No PR is open yet; the
consolidation coordinator opens it.
1. Move + shim: the new `verity/ml/fp32.py`; `integrations/vllm/verity_vllm/program/registry/prims.py` re-exports.
2. Digest pins: `packages/verity/tests/ml/test_fp32.py`; the one-process registry test covers `verity.ml.fp32`.
3. `integrations/vllm/tests/program/test_ampere_tc_versions.py`: which function each `AmpereBF16TcDot16` version is.
4. `backends/flock/tests/test_ir_sampling.py` takes its FP32 primitives from core.

## Moved (same ids, versions, signatures, conformance, docstrings and evaluator bodies)

`F32Add_v1`, `F32Mul_v1`, `F32Fma_v1`, `F32Div_v1`, `F32AddFtz_v1`, `F32SubFtz_v1`, `F32MulFtz_v1`, `F32FmaFtz_v1`,
`F32FmaSubFtz_v1`, `F32Max_v1`, `GuardNegInfZero_v1`, `Bf16Add_v1`, `Bf16AddF2fp_v1`, `Bf16MulF32_v1`, `Bf16MulBf16_v1`, with
their encoding helpers. Each is registered once, by core; the integration's names are core's objects.

## Digest evidence

A primitive's descriptor is its id and signature, so no digest can move. Recorded on `main` and on the branch through
circuit-check's catalog, identical on every field:
- 254 registered ids;
- 85 primitive descriptor digests;
- 790 catalog-reachable Definition digests;
- 30 whole-model program digests;
- for the 15 moved primitives: descriptor, conformance, docstring hash, and an output fingerprint over an edge grid plus
  4,000 seeded random encodings.

`test_fp32.py` pins, per moved id, the Definition digest, a one-call program digest and the output fingerprint, computed on
`main`. circuit-check on the 15 ids gives the same report on `main` and on the branch: 0 failures, 0 known failures,
one warning class (redundant gates in the Boolean lowering, 456 over 12 targets).

Raw files (before/after JSON, both circuit-check reports, the scripts): `evidence/prims-to-core-ac68/` beside this note.

Tests, on `main` and on the branch with the same outcome: core `tests/ml`, `tests/evaluation` and `test_boundaries.py`
(191 on `main`, 223 with the new pins, all pass); circuit-check's tests (828 passed, 2 expected failures); C-Flock's
`test_ir_sampling.py` (16 passed, 1 skipped); 33 vLLM test files (489 passed on `main`, 493 with the Ampere test; the same
61 skips, the same 2 failures that `main` already has, `test_sampling_rows.py::test_nv_logf…` and
`pipeline/test_row.py::test_the_commit_flags_the_row_arms_exist`, and `test_derive.py` needs torch, which the VM lacks).

## Not moved

- **MUFU and `div.full`** (`MufuEx2Ftz`, `MufuRcpFtz`, `Fa2InvSum`, `MufuSqrtFtz`, `DivFullRcp`, `DivFullScaleA`, `RsqrtApprox`,
  `MufuTanh`). Their evaluators call the integration's JIT-compiled C++ (`cpp/fa2_model.cpp`, `cpp/rms_triton_model.cpp`)
  over its xz-compressed tables. Moving the bodies unchanged would put a C++ build and the table files into core. Porting
  them changes the bodies, so it needs exhaustive equality evidence against the C++, and the tables should be
  `verity.ml.library`'s SHA-512 entries rather than a second copy. That is PR 2. It keeps the same ids, so it is also
  digest-neutral and **does not need to be in the epoch**.
  - **Constants lane:** PR 2 needs to know whether `verity.ml.library`'s `ex2`, `rcp`, `sqrt`, `rsq` and `tanh_mufu` entries
    are exactly the words the integration's tables decode to (`kernels/tables/W11*`, `quarantine/dense/tables/mufu_tanh_sm89.*`).
    If you already checked, say where; otherwise PR 2 will check it first.
- `SiluMulBf16`, `RopeOut`, `RopeOutAdd` and `gather_bf16`: application Definitions, staying in the integration.
- The integration's `AmpereBF16TcDot16` v1: left for the epoch, as agreed.

## The epoch, core side

Unchanged from the answer note. On this branch the integration's `@primitive("AmpereBF16TcDot16", 1, …)` is at
`registry/prims.py` L119, with `_mma` at L95 and `_tc_dot16_total` at L102.
1. Delete that registration. `_mma` and `_tc_dot16_total` are still used by `tests/program/test_derived_rows.py`
   (L305, L310, L387): rewrite those tests against core's v2, or keep the helpers.
2. Every program cites core's v2 (`from verity.ml.prims import AmpereBF16TcDot16`). Every value is unchanged.
3. Delete `tests/program/test_ampere_tc_versions.py` with v1.
4. Which recorded digests then move: every Definition whose `DOT` static names `AmpereBF16TcDot16_v1`, and everything above
   it. In circuit-check's catalog on `main`, 108 Definitions name v1 directly (`AttentionHead_v2/v4`, `Attention_v2`, and the
   `DotBf16`/`GemmCoordinate`/`Gemm` bindings among them), and 16 of the 30 whole-model programs cite it:
   `AttentionN_v1`, `LMoeBlockL_v1`, `LMoeBlock_v1`, `LMoeFfnL_v1`, `LMoeFfn_v1`, `LServe_v2`, `Prefill_v1`, `ServeDraft_v1`,
   `ServeSpec_v1`, `ServeTP2_v1`, `Serve_v1`–`Serve_v4`, `StepBody_v1`, `VerifyBranch_v1`. None cites v2 yet. Beyond the
   catalog: the L40S rows' step, request and workload Programs, manifests and run roots, and the recorded data the answer
   note lists. No core id or digest moves; `verity.ml.library` already lists v2.

## Merge order

- This branch and S4 both edit `registry/prims.py`, in different places: this branch removes the block above `_silu_f32_bits`,
  S4 removes the v1 registration. Merge this first, or rebase S4; either way the conflict is small.
- `cursor/ampere-rekey-core-ac68` touches other files (`ir_lower.py`, `boolean_export.py`, circuit-check's `pins.json`).
  Its planned "v1 and v2 evaluate identically" test would repeat `test_ampere_tc_versions.py`; it can keep only the lowering
  half.

## Repoints deferred (the file uses moved names and an open PR touches it)

- `backends/flock/python/verity_flock/ir_lower.py`: #150, #192, #195, #203.
- `backends/flock/tests/test_ir_lowering.py`: #192, #195, #203.
- `tools/circuit_check/tests/test_circuit_check.py`: #134.
