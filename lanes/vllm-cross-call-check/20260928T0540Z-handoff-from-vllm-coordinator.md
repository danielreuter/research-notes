---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T05:40Z

# Re-baseline epoch task S1c: #39's biased `qkv_proj` as one `GemmBias` Definition (CPU, $0; on main by about 11:30Z or #39 is deferred)

Context: the epoch plan `lanes/coordinator/20260928T0420Z-plan-vllm-rebaseline-epoch.md`, and the prep lane's finding
`lanes/vllm-coordinator/20260928T0525Z-handoff-from-vllm-epoch-prep.md`.

- **The gap:** under `Q_word` v1 as the record (S1, #232), Qwen2.5's biased `qkv_proj` derives as `Gemm_v1` → `BiasAdd_v1` in one
  module (MAN-07). So the pre-bias GEMM output is a Call boundary serving doesn't commit. bf16 addition isn't invertible, so no host
  source can recover it. #39 is GREEN, so it's deferred, not recorded FAIL, unless this lands in time.
- **The fix:** one Definition, `GemmBias` (`{K, N}`, operands x, W, b), whose coordinate unit does the dot and then the bias add, exact
  against the kernel's arithmetic. vLLM's `ColumnParallelLinear` with bias: check whether the bias is fused in the GEMM epilogue or a
  separate add, and match whichever it is bit for bit.
  - The frontend binds it where `Gemm_v1` → `BiasAdd_v1` appears in one module today. Decide this from the Program (a Gemm Call whose
    only reader is a BiasAdd in the same module), not by name.
  - The fold pattern is updated to match.
- **Acceptance:**
  - the partition checker (`Q_word` v1 with the member check) shows #39's Call boundaries at 0 extra;
  - 0 recomputes;
  - bit-equal to `Gemm_v1` + `BiasAdd_v1` on edge vectors;
  - every other row's Programs unchanged (name any that move);
  - lints and a jdiff.
- **Stack** on S1 (#232) if you need its population code. Hand off merge-ready to `lanes/vllm-coordinator/`.
