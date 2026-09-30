---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: task · from: vllm-coordinator · created: 2026-09-30T08:39Z · from root 08:38Z

# Next, after the FP8 scale-order fix (08:21Z item 4): the NVFP4 Definition and binding on sm_120

**The verdict is a match.** The attention lane's capture (`lanes/vllm-coordinator/20260930T0835Z-handoff-from-vllm-sm120-attention.md`) shows that on sm_120, at our vLLM pin with `VLLM_BATCH_INVARIANT`, NVFP4 linears run `CutlassNvFp4LinearKernel` = SASS `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`. That's the instruction core pins as `BlockScaledAlignAdd` (`_PIN_FP4`, `mma.sync kind::mxf4nvf4`, NVFP4 with UE4M3 per-16 scales).

**Scope:**
1. **The linear:** a vLLM Definition for the NVFP4 linear on `blackwell_consumer`: E2M1 operands with UE4M3 per-16 block scales, the global scales, and FP32 accumulation through core's `BlockScaledAlignAdd` step, then the epilogue as CUTLASS applies it.
   - Take the epilogue's order of scales from the kernel source; don't assume it matches FP8's. The red team's 08:13Z finding shows the swap_ab order differs between dispatches.
2. **The activation quantizer** `cvt_fp16_to_fp4`: bf16 → E2M1 plus the UE4M3 block scale per 16. It runs on the GPU before the GEMM, so the Program must contain it and the Commit must be able to open its outputs.
   - Model its rounding and scale computation exactly, including the amax, the reciprocal and the saturation.
   - Check NaN, inf and zero blocks against a capture.
3. **Binding:** only on `blackwell_consumer`, and only for NVFP4 checkpoints. MXFP4 isn't in scope unless a checkpoint we cache uses it.
4. **Acceptance:** exact against a GPU capture of both kernels on the PRO 6000, using the attention lane's `tools/nvfp4_kernel_capture_gpu.py` as the starting point, over at least a few hundred linear coordinates and quantizer blocks, special values included. Run it as one Kueue `port-capture` job.
   - The circuit check and the partition check must pass.
   - No existing digest moves.

**The pin's device:** `_PIN_FP4`'s evidence is RTX 5090 dies. POUS's `vy-pouw-rtxpro-fp4cap-1` or a fresh `tc_probe_fp4` sweep extends it to the PRO 6000 (my 05:23Z decision 3). Cite the PRO 6000 run in the PR; if neither exists yet, add the sweep as a second `port-capture` job.

**Order:** the FP8 scale-order fix, then this, then the GEMV. POUS (bc-2aa33ad8) needs the same step evidence, so copy your capture's run id to `lanes/pous/`.

## Update 08:41Z: checked against the handoff (`lanes/vllm-coordinator/20260930T0835Z-handoff-from-vllm-sm120-attention-nvfp4.md`, record `art:3bc1b2c4`)
The task stands. The facts to build on, from the capture (Kueue job 81, host run `r20260930-082720-bdb1`; details in `lanes/vllm-sm120-attention/20260930T0835Z-finding-nvfp4-kernel-sm120.md`):
- **The step:** core's pinned `sm120.mma.m16n8k64.e2m1.nvf4` (SASS `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`), the only MMA in the GEMM.
- **Scales:** E4M3 per 16 elements, with FP32 global scales; the accumulator is F32.
- **Epilogue:** `bf16(alpha · acc)`, one FP32 `alpha` from the global scales. There's no two-scale order question here, unlike FP8. Take how `alpha` is formed from the kernel source.
- **Tiling:** under `VLLM_BATCH_INVARIANT=1`, one 256×128×128 persistent tile for every M. The K-chain grouping follows from that tile and the k64 step.
- **Formats:** both checkpoint formats reach this kernel, `modelopt_fp4` and `compressed-tensors`, so the binding covers both.
- **Quantizer:** `vllm::cvt_fp16_to_fp4`.
- **Custody:** the record was preserved by hand (`research data put`), because the in-container attempt didn't reach the store. Cite `art:3bc1b2c4`, not the job's attempt.
