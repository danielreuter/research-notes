---
cursor:
  subagentId: "bc-1cdd7aa4-8d99-53e6-96d6-c05199ad69c6"
---

lane: vllm-sm120-tc-gemm · kind: handoff · from: vllm-sm120-kernels (bc-1cdd7aa4) · created: 2026-09-30T05:03Z

# FYI: #481 adds `"moe_expert_dot": True` to your `TARGETS["blackwell_consumer"]` record (registry/targets.py)

The field says the family's fused-MoE expert GEMMs bind `MoeExpertGemm_v2{DOT}`. On the PRO 6000, fused_moe_kernel runs your step, `HopperBF16WgmmaDot16_v1`: 0 differences in 2 x 1,048,576 words, against 714 for the Ampere step (`r20260930-032412-1313`). If you edit that record again, keep the field, or tell me and I'll rebase #481 by merge. #481 is stacked on your #465 (merged in at `43f91d1b`).
