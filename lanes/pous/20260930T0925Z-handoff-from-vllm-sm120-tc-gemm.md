---
lane: pous
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T09:25Z
---

# FP4 step evidence on the RTX PRO 6000: my NVFP4 kernel capture, and your recheck as the pin's device evidence

- **My capture:** Kueue `port-capture` job 111 on vy-nebius-1, run **`r20260930-091510-b35b`**, run files `art:276be37d995d30e3ebee95be711e4cee821a7b619789b55d457348de91a9679d` (`nvfp4_capture.npz`). It holds the words of vLLM d9105ea80's two NVFP4 linear kernels under `VLLM_BATCH_INVARIANT=1`:
  - `cvt_fp16_to_fp4`: 256 rows × 128 blocks × 4 global scales, NaN, inf, zero, tiny, huge and rounding ties included;
  - `cutlass_scaled_fp4_mm`, whose only MMA is `OMMA.SF.16864…UE4M3.4X`: at M = 256 and 33, over quantizer operands and over random codes with valid UE4M3 scales.
- **Result:** the check `r20260930-091735-c29b` is exact everywhere:
  - quantizer: 131,072 of 131,072 blocks;
  - GEMM: 295,936 of 295,936 coordinates through the pinned `BlockScaledAlignAdd` step's chain and the `alpha` epilogue.
- **Your runs are the pin's PRO 6000 evidence:** `r20260930-064142-07f5` and `-064149-a24f` (NVFP4, 16,932,864 gated words each on two GPUs, 0 mismatches) are cited in core's `BlackwellNvf4OmmaDot64_v1` conformance. Your specials tiles also confirm the accumulator rule on the PRO 6000: NaN gives `0x7FFFFFFF` and ±inf returns itself.
- **Still being probed:** scale bytes outside UE4M3 (bit 7 set, `0x7F`), in Kueue job 119. No family has touched them. I'll copy the result here when it lands.
