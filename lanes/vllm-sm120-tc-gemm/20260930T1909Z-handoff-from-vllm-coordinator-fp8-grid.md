---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: handoff · from: vllm-coordinator · created: 2026-09-30T19:09Z · Daniel 19:06Z: maximum coverage

**After the first 7 FP8 deployments** (my 17:22Z list), grow the FP8 block to the 7 families × batch 1/8/32 × context 256/32, 1k/128 × greedy, top-p: about 84.
- **Order:** breadth first, all B1 first.
- **#582's stack:** land it (#515 → #516 → #582, after #557) as fast as possible. Run the FP8 deployments from a pre-merge branch meanwhile, labelled as they finish.
