---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T14:28Z
---

# Urgent: #483/#501 model a path vLLM doesn't serve. Please pull them from the train; the fix is a new small PR on main

(This replaces a ~14:00Z handoff that a VM restart lost before it reached the store.)

**What vLLM runs on sm_120.** Under `VLLM_BATCH_INVARIANT=1`, `UnquantizedLinearMethod.apply` calls `linear_batch_invariant(x, W, b)`: the Triton `matmul_kernel_persistent`, then `output + bias` in bf16. That holds at every M. The GEMM correspondence (#483, #501) measured `F.linear`, i.e. cuBLASLt, which these layers don't use.
- **Job 197** (`r20260930-140739-7974`, Qwen2.5-0.5B qkv, K 896, N 1152, the sm_120 target's `HopperBF16WgmmaDot16` chain):

  | M | Triton + bf16 add, bias after rounding | `F.linear`, FP32 epilogue |
  |---|---|---|
  | 1 | 1152/1152 | 1152/1152 (cuBLAS gemv) |
  | 2, 7, 256 | all exact | all exact (CUTLASS wmma) |

  Each path is off in about 26% of words under the other path's bias form. The matmul chain itself is the same DOT on both paths.
- **Job 191** (`r20260930-133959-eed1`, #535's acceptance): identity coverage passes, 11,979 of 11,979. The replay fails 51 of 460, on `GemmBiasF32Epilogue_v1` (49, prefill) and `GemvBiasF32_v1` (2). The cause is #483's FP32 epilogue and #501's gemv.

**Main alone doesn't pass either** (CPU Build and manifest on main `8a4e1147`, `r20260930-141658-f051`, Qwen2.5-0.5B cc 12.0):
- qkv is `Gemm_v2{DOT}` followed by a separate `BiasAdd_v1`. That is numerically what vLLM runs, but it can't be committed:
  - the post-bias value is named `qkv_proj/bias`, while the collector binds `qkv_proj/0` (the original 10:27Z failure's first identity);
  - the pre-bias word `qkv_proj/triton_launch_N/out` is a required call-boundary identity (96 per 4-step Build), and serving has no source for it.
- cc 8.9 on the same run: `GemmBias_v1` is named `qkv_proj/out`, not `0`. That is the cc 8.x gap from my 12:31Z handoff, still on main.

**The fix, one small PR on main.** It needs none of #483/#501:
- `GemmBias_v2{K,N,DOT}`: `Gemm_v2`'s chain, then `BiasAdd_v1`'s add, per coordinate. This is `GemmBias_v1` with the target's DOT.
- `TritonGemmRule` binds it when the add is the launch's only reader, as it already does with `GemmBias_v1` on Ada. It does so only on `blackwell_consumer`.
  - Hopper keeps its split pair of record (the Qwen2.5 H100 row composes the interior `Gemm_v2`; `test_hopper_biased_linear_composes_the_interior_gemm_v2`).
  - So no cc 8.x or 9.0 Program digest moves.
- The residuals `GemmBias_v1`/`GemmBias_v2` `out` → `0` (from #535). This changes only manifest member names.
- A replay row, an evaluator, a circuit-check binding and tests.
- Acceptance: the CPU binding check, then the Qwen2.5-0.5B cc 12.0 B1 config run at `REPLAY_K=460` on main + this PR.

**Please decide:**
1. Pull #483 and #501 from the train.
2. #535 is superseded by the new PR.
3. Park #539: the Triton path has one chain at every M, so the per-step row count isn't needed for this family. #516 and #524 are stacked on #501, so they'd need restacking on main before they merge.

I'm starting the new PR now and will send its head with the CPU check.
