# NVFP4 on sm_120: MATCH — vLLM's NVFP4 linear runs core's pinned block-scaled FP4 step

**Verdict: match.** On an RTX PRO 6000 Blackwell Server Edition (cc 12.0, 188 SMs, driver 580.17, SM clock locked at 2,092 MHz), vLLM `d9105ea80` runs both NVFP4 checkpoint formats on the same kernels:
- **Checkpoints:** `nvidia/Qwen3-8B-FP4` @ `ccd10a89` (quant method `modelopt_fp4`) and `RedHatAI/Qwen3-8B-NVFP4` @ `e391349c` (`compressed-tensors`, `CompressedTensorsW4A4Fp4`).
- **Linear kernel:** with `VLLM_BATCH_INVARIANT=1`, all 144 linears use `CutlassNvFp4LinearKernel`. vLLM's default (not batch-invariant) selection logs the same kernel. `lm_head` and the embeddings stay unquantized.
- **Per forward, each linear launches:**
  1. `vllm::cvt_fp16_to_fp4<bf16>`: dynamic activation quantization to e2m1, with per-16 UE4M3 scales under an fp32 global scale;
  2. CUTLASS `GemmUniversal<… MainloopSm120TmaWarpSpecializedBlockScaled, KernelTmaWarpSpecializedCooperativeBlockScaledSm120, float_e2m1_t / float_ue4m3_t …>`.
- **The instruction:** that GEMM's only MMA in SASS is `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`. It's the opcode that core's pinned `sm120.mma.m16n8k64.e2m1.nvf4` (`kind::mxf4nvf4.block_scale.scale_vec::4X … ue4m3`) compiles to on sm_120a: the repo's single-instruction probe `tools/tc_probe_fp4/mma_fp4.cu` gives exactly that for `nvfp4`, and `OMMA.SF.16864.F32.E2M1.E2M1.E8` for the ue8m0 MXFP4 variant.
- **Scales:** NVFP4 E4M3 per 16. For example qkv_proj has weight `uint8 [6144, 2048]` and `weight_scale float8_e4m3fn [6144, 256]` for K = 4096, plus fp32 `input_global_scale` and `alpha`.
- **Accumulate and epilogue** (the pinned source, `csrc/libtorch_stable/quantization/fp4/nvfp4_scaled_mm_sm120_kernels.cu`): F32 accumulate, with epilogue D = bf16(`alpha` · acc), `alpha` an fp32 pointer.
- **Tile:** under batch invariance, one tile for every M, 256×128×128 with a persistent scheduler. Without it, M ≤ 256 uses 128×128×128.

**What tc-gemm's Definition needs.**
1. The K-tile order: two k64 `OMMA`s per 128-K tile, chained in F32.
2. The `alpha` epilogue.
3. The activation quantizer `cvt_fp16_to_fp4`, a separate kernel with its own numerics.

**Caveat for FP4 config runs:** `nvidia/Qwen3-8B-FP4` also declares an FP8 KV cache (`kv_cache_quant_algo: FP8`). vLLM then launches `scaled_fp8_quant` for K/V and, outside batch invariance, selects FlashInfer attention, which failed to warm up in this venv. The RedHat checkpoint keeps a bf16 KV cache and FA2 attention.

**Evidence:** Kueue job 81 (`nvfp4-capture-attn-3`) on vy-nebius-1, host run `r20260930-082720-bdb1`. The record is `art:3bc1b2c4` (the job template's own attempt isn't published to the store). The script is `lanes/vllm-sm120-attention/tools/nvfp4_kernel_capture_gpu.py`.
