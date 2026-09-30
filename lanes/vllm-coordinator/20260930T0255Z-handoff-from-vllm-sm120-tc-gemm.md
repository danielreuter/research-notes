---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T02:55Z
---

# sm_120 bf16 linears are cuBLASLt, not the Triton GEMM, at the pinned vLLM: step 2 becomes a cuBLASLt correspondence (affects lane C)

- **Finding.** In pinned vLLM `d9105ea80` `batch_invariant.py::enable_batch_invariant_mode`, the Triton `matmul_kernel_persistent` overrides are installed only when `is_device_capability_family(80)` (major 8). On cc 12.0, as on 9.0 and 10.0, the bf16 linear stays on **cuBLASLt with split-K disabled** (`CUBLAS_WORKSPACE_CONFIG=:16:8`, `CUBLASLT_WORKSPACE_SIZE=1`, reduced-precision reduction off, `preferred_blas_library=cublaslt`). The integration already says this for cc 9.0 (`check/replay/driver.py::ENGINE_FACTS_RULE`, `derived_rows.py` near line 466).
- **Consequence for step 2.** The brief's "Triton GEMM, default tiling, M tails" doesn't apply to linears on sm_120. The question is whether cuBLASLt on sm_120 under VLLM_BATCH_INVARIANT=1 computes `Gemm_v2{K,N,DOT=HopperBF16WgmmaDot16_v1}` (ascending k16 chain from zero, then RNE to bf16) on the 13 configs' linear shapes for every M. That is the analogue of the H100 R17 dense probe (`gemm_v2-hopper-pin`). The risk is real: cuBLASLt heuristics may pick sliced-K kernels (intra-CTA K split, which the workspace setting doesn't disable) for some M, and those would break the single chain. I'm writing the driver now (`verity_vllm/program/kernels/gemm_target_correspondence.py`, restored from the one deleted in 528f9d21): capture through `init_batch_invariance()` + `F.linear`, the cuBLASLt kernel name per case, many M values; check with `cpu_model.gemm_model` under the registered step, cross-checked against `derived_rows.tc_dot16_hopper`.
- **Consequence for lane C.** The plan's "batch-invariant GEMM's NUM_SMS specialisation changes at 188 SMs" doesn't apply to the linears on sm_120 (no persistent-matmul launch). vLLM's other BI Triton kernels (mean.dim, softmax, log_softmax, bmm) still run there.
- **PR #465 updated** (`cursor/vllm-sm120-target-422d` @ `f740c1d5`): only comments, evidence and instruction text changed, to say that cc 12.0's linear is cuBLASLt and that the correspondence still to run is of that path. The code and the byte-identity of cc 8.x/9.0 are unchanged.
- **Open question for you or the RC.** How do H100 rows resolve their cuBLASLt linears in Match/fold (the GEMM fold pattern resolves only Triton launches)? sm_120 rows will need the same path. I assume lane C or the run lane handles it once the correspondence holds.
- **Pods.** I saw your budget-line note. First pod next: `vy-sm120-tc-gemm-1`, 1x RTX PRO 6000 secure on-demand, about 3.5 GPU-h (~$7). It will run the bootstrap checks, the vLLM suite for #465, the 5a FP8 probe and the step 2 capture.
