---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (CPU; gates #57) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T14:52Z

# #57's gate: host evaluation under 90 min per Commit. It hasn't passed; the measurement stands at about 16.4 h

**Needed:** a PR on main that brings #57's host evaluation under 90 min per Commit. Measure it on #57's stored B=8 Build (`art:f5671a8f`), on CPU.

**Candidates,** from your 11:20Z handoff:
- row kernels for the norm chain (`SquareF32`, `MeanTriton`, `AddScalarF32`, `RsqrtF32`, `ScaleRow*`, `MulVecF32`, `NarrowF32ToBf16`) and for `Bf16DivScalar` and `Bf16Tanh`;
- plus either a faster exact Gemm, or a `CLAIMS` tap of the pre-softcap `lm_head` output. The k16 chain alone is about 2.8 h.

**Acceptance:**
- per-Commit host time under 90 min, with the measurement in the PR;
- the host words are unchanged (bit-equal to `verity.evaluation.evaluate`);
- no digest moves.

Send me the head. #57's launch waits on it.
