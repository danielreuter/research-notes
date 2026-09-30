---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator · created: 2026-09-30T15:23Z

**Daniel approved `VLLM_USE_DEEP_GEMM=0` for sm_120 FP8** (CUTLASS block-scaled). The GEMM lane (bc-049fc756) captures that path, then runs the **7 FP8 cells** itself.
- Don't submit sm_120 FP8 cells; leave them to it.
- Send it your FP8 cell list (row slugs) as a `-handoff-` in `lanes/vllm-sm120-tc-gemm/`, if you have one.
