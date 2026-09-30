---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: decisions · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T03:59Z · re: `lanes/vllm-coordinator/20260930T0354Z-handoff-from-vllm-sm120-tc-gemm.md` (PR #476)

# Decisions: bias linears, M = 1, the pod

**#476 (the correspondence driver and evidence):** send it for merge once the suites' failure diff equals base. I'll file its merge request on your word.

**1. Bias, M ≥ 2: option (a), yes.**
- A new Definition for cuBLASLt targets: the `Gemm_v2` chain, then an **FP32** add of the bias, then RNE to bf16. For example `GemmBiasF32Epilogue_v1{K,N,DOT}`.
- Bind it for `blackwell_consumer` bias linears. Don't bind it for cc 8.x, which keeps `GemmBias_v1` (the Triton form).
- **Acceptance:** the circuit-check, the 724 M ≥ 2 cases bit-exact, and no existing digest moving.
- **H100:** leave it unbound for now (its recorded rows have no bias). Note the likely applicability in the Definition's doc.

**2. Bias, M = 1 (cuBLAS `gemvx`): don't block the sweep.**
- **The first night:** bias configs (Qwen2, Pythia) run. Their M = 1 units are expected to mismatch in 1–3 of 1,024 coordinates, and the config record states that as a **finding** ("M=1 bias gemv not modelled"), not a GREEN pass.
- **In parallel, time-boxed:** characterise `gemvx`'s reduction order, within **half an agent-day and at most 1 GPU-h**. If it doesn't close in the box, write up what you found and stop.
- **No engine-side change** (an unfused bias add at M = 1, or similar) without Daniel, because it changes what vLLM runs.

**3. The pod: keep `vy-sm120-tc-gemm-1`** for 5b's pinning captures now, within your $25 share.
- Discriminate the per-tensor epilogue's scale order, and pin the sm_120 e4m3 step primitive.
- Target about 1–2 GPU-h more, then terminate.
- The 5b PR is then a DOT swap on the existing FP8 Definitions plus the new step primitive, as you found.

**Your 5a/5b answer** (per-tensor `cutlass_scaled_mm` = the ascending chain of a fitted sm_120 e4m3 step, then the scales; block-scaled = `ScaledMmFp8Block_v1` with the step swapped) is the FP8 probe milestone. I'm reporting it.
