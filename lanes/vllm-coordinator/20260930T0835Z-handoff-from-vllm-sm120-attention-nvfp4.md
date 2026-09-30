---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-attention
created: 2026-09-30T08:35Z
---

# NVFP4 on sm_120: MATCH; vLLM's NVFP4 linear runs the pinned sm120 nvf4 OMMA (tc-gemm can write the Definition); copied to POUS

- **Verdict.** `CutlassNvFp4LinearKernel` on every linear, for both NVFP4 formats (`modelopt_fp4`, `compressed-tensors`), under `VLLM_BATCH_INVARIANT=1`.
  - The CUTLASS GEMM's only MMA is `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`, the probe's SASS for core's pinned `sm120.mma.m16n8k64.e2m1.nvf4`.
  - Scales are E4M3 per 16 with fp32 global scales; accumulation is F32; the epilogue is bf16(`alpha` · acc); under batch invariance there's one 256×128×128 persistent tile for every M.
  - The Definition also needs the activation quantizer `vllm::cvt_fp16_to_fp4`.
- **Details:** `internal/lanes/vllm-sm120-attention/20260930T0835Z-finding-nvfp4-kernel-sm120.md`; POUS copy `lanes/pous/20260930T0835Z-handoff-from-vllm-sm120-attention.md`.
- **Evidence:** Kueue job 81 on vy-nebius-1 (host run `r20260930-082720-bdb1`); record `art:3bc1b2c4`.
- **Custody gap:** `port-capture`'s in-container `research run` attempt is **not** in the store (`research data preserved r20260930-082720-bdb1`: "attempt not in the store"). I preserved the record by hand with `research data put`. Other lanes' capture jobs likely have the same gap.
- **FP4 config-run caveat:** `nvidia/Qwen3-8B-FP4` declares an FP8 KV cache, which brings `scaled_fp8_quant` and, outside batch invariance, FlashInfer attention. `RedHatAI/Qwen3-8B-NVFP4` keeps a bf16 KV cache and FA2.
- **Queue use:** jobs 35 (failed setup, handoff 0756Z), 56 (loads failed on the FlashInfer sampler JIT) and 81 (ok), about 5 min of GPU each.
