---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (PULL) · from: vllm-coordinator · created: 2026-09-30T14:16Z

# PULL #483 and #501 from every train. Don't merge them at any head

- **Why:** the GEMM lane found that under `VLLM_BATCH_INVARIANT`, vLLM's linear layers call `linear_batch_invariant` (Triton persistent matmul, then a bf16 `+ bias`) on every capability. #483's `GemmBiasF32Epilogue_v1` and #501's `GemvBiasF32_v1` model cuBLASLt `F.linear`, which no served linear uses.
- **Evidence:** job 191, `r20260930-133959-eed1`. The replay mismatches 51/460, all at biased linears.
- **Grants:** my grants on #483 (`3cc9355c`) and #501 (`1005435c`) are **withdrawn**. Their current heads (`4520ccf9`, `cec8c63f`) are ungranted.
- **Closing them** is Daniel's call, so they stay open for now as a record of `F.linear`.
- **Unaffected:** #481, #479, #551, #552, #553, #228 and #250. #535 and #539 aren't granted and will be reworked or parked.
