---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T03:54Z
---

# Step 2 done: sm_120 plain linears are exact Gemm_v2 (Hopper step); bias linears need an FP32-epilogue Definition, and M=1 bias hits a cuBLAS gemv that isn't the chain (decision needed)

- **PR #476** (`cursor/vllm-sm120-gemm-corr-422d` @ `9755dc08`, stacked on #465): the `verity-vllm gemm-correspondence capture|check` driver, restored from 528f9d21 and target-agnostic, plus the correspondence evidence on the `blackwell_consumer` record. Lint scans are clean; CPU tests are in `tests/program/test_gemm_target_correspondence.py`.
- **Run `r20260930-031354-3b6d`** (RTX PRO 6000, VLLM_BATCH_INVARIANT=1, i.e. cuBLASLt with split-K disabled): all 14 bf16 HF configs at TP1 and TP2, M from 1 to 8192 (31 values), four stress families, 4,794 cases, about 30 cuBLASLt kernels (CUTLASS s16816 and wmma s161616, chosen by M).
  - **Plain linears:** every case bit-exact against `Gemm_v2{K,N,DOT=HopperBF16WgmmaDot16_v1}` (181M coordinates), with the step cross-checked against the registered primitive and every GPU rerun bit-identical. **The BF16 GEMM target holds for every linear without a bias.**
  - **Bias linears, M >= 2:** exact with the bias added **in FP32 before the rounding** (the cuBLASLt epilogue), 724 cases. `GemmBias_v1` (bf16 add after the rounding, the Triton form of cc 8.x) is wrong on this target: it misses about 25% of coordinates.
  - **Bias linears, M = 1:** cuBLAS runs a non-tensor-core `gemvx` kernel; 20 of 24 cases are off in 1 to 3 of 1,024 coordinates.
- **Who is affected:** configs with biased linears, i.e. the Qwen2 family (Qwen2.5-0.5B/1.5B/7B qkv) and Pythia (every linear). M = 1 happens at every decode step with one active request (every B=1 decode, and the tail of every batch). The same logic very likely applies to H100 (cc 9.0 also uses cuBLASLt), but its recorded rows have no biases.
- **Decision needed (options):**
  - (a) A new bias Definition for cuBLASLt targets (`Gemm_v2` chain, then an FP32 add of the bias, then RNE), which closes M >= 2. It's a small IR change with circuit-check; I can do it.
  - (b) For M = 1, either characterise cuBLAS `gemvx`'s reduction order (a research task: closed-source kernel, uncertain) or keep bias configs out of the first night.
  - (c) An engine-side choice such as an unfused bias add at M = 1. That changes what vLLM runs, so it's your call.
- **5b first look** (run `r20260930-035259-0b54`, Qwen3-4B's four linear shapes x M {1,7,16,129,1024}):
  - vLLM's CUTLASS sm_120 FP8 `cutlass_scaled_mm` (per-tensor, `enable_sm120_family` GemmUniversal) is exactly an ascending chain of the fitted sm_120 e4m3 step, then the scales: 16,896/16,896 coordinates.
  - The block-scaled `cutlass_3x_gemm_fp8_blockwise` is exactly `ScaledMmFp8Block_v1`'s structure (a fresh 4-step chain per 128-wide k-block, then `FFMA(temp, sa*sb, acc)`) with only the step swapped: 16,896/16,896. The unfused alternative misses 2.
  - So 5b is a DOT swap on the existing FP8 Definitions plus the new step primitive, not new structure. The scale order of the per-tensor epilogue isn't discriminated yet.
- **vLLM suite** on #476's tree and on origin/main, same pod: both are stuck on the slow `test_tp_moe_members` MoE manifest test. I'll send the failure diff when they finish.
- **Pod** `vy-sm120-tc-gemm-1`: up since 03:07Z, about $2 spent. Terminating after the suites, unless you want 5b's pinning captures on it now.
