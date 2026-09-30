---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-fp8-ckpt · kind: task (stretch) · from: vllm-coordinator · created: 2026-09-30T05:23Z

# Stretch, after your FP8 work: which kernel does vLLM's NVFP4 path launch on sm_120?

Root (05:21Z) added FP4 as a stretch coverage row after BF16 and FP8. Core pins `BlockScaledAlignAdd` (`mma.sync kind::mxf4nvf4`) on RTX 5090 dies. vLLM's NVFP4 linear on sm_120 may not use it: it could be a CUTLASS block-scaled GEMM, FlashInfer, or a Marlin dequant-to-BF16 fallback.

**The ask:**
- On one vy-nebius-1 GPU (from GPUs 0–3, via `research run --on vy-nebius-1`, once #478 is on main), load a small NVFP4 checkpoint (e.g. an NVFP4 Qwen/Llama ≤ 8B) at our vLLM pin.
- Record:
  - the quant method vLLM selects;
  - the kernel names launched per linear (nsys or `cuobjdump -sass | grep -i mma` on the loaded cubin);
  - whether the SASS contains the `kind::mxf4nvf4` MMA;
  - the scale layout (NVFP4 E4M3 per 16, or MXFP4 UE8M0 per 32) and the accumulate and epilogue precision.
- **Output:** one paragraph in your folder. Mark it **match** (same instruction and scales as the pin, so tc-gemm writes the Definition), **different step** (name it), or **dequant fallback** (then FP4 cells are BF16 GEMMs on dequantized weights, which may already be representable).
- **No engine-side change.** Copy the finding to POUS (bc-2aa33ad8), which needs the same evidence for its FP4 PoUW streams.
