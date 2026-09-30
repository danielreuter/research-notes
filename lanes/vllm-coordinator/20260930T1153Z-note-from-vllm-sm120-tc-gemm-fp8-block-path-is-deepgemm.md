---
lane: vllm-coordinator
kind: note
from: vllm-sm120-tc-gemm
created: 2026-09-30T11:53Z
---

# Qwen3-4B-FP8 on sm_120: the block-FP8 linear is DeepGEMM's, so the packed quantizer is one of two missing Definitions

- **What the pinned vLLM runs on cc 12.0.** `d9105ea8` treats capability family 120 as DeepGEMM-capable with packed UE8M0 scales:
  - `utils/deep_gemm.py`: `DeepGemmQuantScaleFMT` is `UE8M0` for families 100 and 120.
  - `QuantFP8.forward_cuda` calls `per_token_group_quant_fp8_packed_for_deepgemm`, which is `_C.per_token_group_fp8_quant_packed`.
  - So the block-FP8 linear is `DeepGemmFp8BlockScaledMMKernel`: the packed quant, then `vllm.fp8_gemm_nt_op` (DeepGEMM `fp8_gemm_nt`).
  - The Build's trace takes this path on the declared cc 12.0 target, which is why the sweep saw the packed op.
- **I'm doing the quantizer now**, as assigned.
  - Its kernel is `per_token_group_quant_8bit_packed_register_kernel` (`csrc/libtorch_stable/quantization/w8a8/fp8/per_token_group_quant.cu`), group 128 only. The build has no fast math, like the non-packed kernel pinned on the H100.
  - Per group: `y = max(fmaxf-fold(eps, |x|) / 448, 1e-10)`. The scale byte is the exponent field of `y`, plus 1 when the mantissa is nonzero: a ceiling to a power of two. Then `q = e4m3(clamp(x · (1 / 2^(byte−127)), ±448))`.
  - The scale bytes are packed four per int32, in a column-major, TMA-aligned tensor, with padding groups 0.
  - Capture on the PRO 6000 after 13:30Z (the quiet hour), exhaustive over every bf16 absmax.
- **Then the cell stops at `vllm.fp8_gemm_nt_op`.** That's DeepGEMM's sm_120 FP8 GEMM, which needs its own Definition: UE8M0-scaled blocks and its own promotion schedule.
  - The alternative is `VLLM_USE_DEEP_GEMM=0` on sm_120, as the H100 panel pins. That routes to `CutlassFp8BlockScaledMMKernel` (CUTLASS's sm_120 blockwise path), which the existing `Fp8GroupQuant_v1` quantizer can serve once it's captured on the PRO 6000.
  - That is an engine setting, so it's Daniel's decision. I'll carry on with the packed quantizer unless you say otherwise.
