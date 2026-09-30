---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20260930T1523Z: Daniel yes (15:22Z): sm_120 FP8 with VLLM_USE_DEEP_GEMM=0 (CUTLASS block-scaled). GO to tc-gemm: scoped pin on blackwell_consumer (recorded), PRO 6000 capture of CutlassFp8BlockScaledMMKernel + non-packed per_token_group_quant, Definition/binding PRs, then the 7 FP8 cells on node 1 (postmortem ws2 row). #546 + DeepGEMM Definition parked. Epoch-run told to leave FP8 cells to tc-gemm.
