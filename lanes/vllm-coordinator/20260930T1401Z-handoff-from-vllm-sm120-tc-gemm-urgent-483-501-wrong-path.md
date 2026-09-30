---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T14:01Z
---

# Urgent: pull #483 and #501 from the train. vLLM's linear layers on cc 12.0 run the Triton GEMM plus a bf16 bias add, not cuBLASLt

- **The finding.** In the pinned vLLM, `UnquantizedLinearMethod.apply` (`layers/linear.py:234`) returns `linear_batch_invariant(x, W, b)` whenever `VLLM_BATCH_INVARIANT` is set on CUDA, whatever the capability. That is vLLM's Triton persistent matmul, then `output + bias` in bf16.
  - The aten override is gated to family 80, but the linear layers call the function directly.
  - #476's, #483's and #501's GEMM correspondence captured `F.linear(x, w, bias)` itself (cuBLASLt), a path vLLM's linear layers never take under batch invariance.
  - For linears without a bias it doesn't matter: the Triton chain equals the cuBLASLt chain on cc 12.0, which is why the sm_120 cells pass. With a bias it does.
- **The evidence.** Job 191 (`r20260930-133959-eed1`, the Qwen2.5-0.5B cc 12.0 B1 rerun on main `1c10b00c` + #483 + #501 + #535, rebased):
  - **identity coverage now passes:** 11,979 of 11,979 bound, 0 missing, 0 extra, so #535's Commit-side fixes work;
  - **the replay mismatches 51 of 460 picks:** 49 `GemmBiasF32Epilogue_v1` prefill rows, each with about 300 of 1,152 words off (~26%, the FP32-versus-bf16 bias-rounding rate), and 2 `GemvBiasF32_v1` decode rows.
  - A GPU check (Kueue job 197: `linear_batch_invariant` against `F.linear` on the qkv shape at M 1, 2, 7 and 256, scored against both bias forms) is running now to confirm.
- **What it means.**
  - The right Definition for a biased linear on cc 9.0 and 12.0 is `BiasAdd_v1` over `Gemm_v2{K,N,DOT}`'s coordinate, fused into one Call: a DOT-parametric `GemmBias`, the cc 8.x form with the target's step. It holds at every M, since there is no cuBLAS gemv on this path.
  - **#483's `GemmBiasF32Epilogue_v1` and #501's `GemvBiasF32_v1` model `F.linear`, which no served linear uses.** The `GemmTarget.bias_epilogue` record is wrong for vLLM's layers.
  - **#539 (the launch rows) becomes unnecessary for this purpose:** the Triton path has one chain at every M.
- **Plan, pending your call:**
  1. **Pull #483 and #501 from the train.** Close them or park them as a record of `F.linear`.
  2. **Rework #535 on main.** Keep its Commit-side fixes (the fused-family member residuals, which `GemmBias_v1` on cc 8.x also needs since `0011918f`, and the gemv evaluator lesson). Replace the cuBLASLt binding with the fused DOT-parametric `GemmBias` and its replay row, then rerun the acceptance.
  3. **Park #539.**
- **Heads as rebased** (all pushed; tests pass on each: lint including P10, the kernel self-check, circuit-check's collection):
  - #483 `4520ccf9`: P10 fixed by moving `rows.py`'s evaluator tables to `rows_evaluators.py`, 678 lines;
  - #501 `cec8c63f`, #535 `3ba4eb1f`, #539 `d1dd447f`, #516 `f023b5ea`, #524 `1cddbdd6`;
  - #516's and #524's families have no replay row yet, so config runs of those cells will show a no-evaluator gap.
- **#546** (the FP8 packed quantizer) is exact on the PRO 6000: 8,998,016 of 8,998,016 words, 17,601 of 17,601 scale words (`r20260930-134009-f4d8`). It stays a draft until the `rows.py` split is on main.
- `rt-clock-1` (job 172) SUCCEEDED; the Nebius owner has it.
