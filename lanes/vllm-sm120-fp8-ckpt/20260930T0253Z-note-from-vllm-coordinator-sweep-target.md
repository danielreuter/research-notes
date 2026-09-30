---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-fp8-ckpt · kind: note (target change) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T02:53Z

# Your target is now the one-night config sweep

**The plan:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/vllm-config-sweep-plan.md`. Daniel's new direction: the cluster's first night runs as many vLLM configs as possible as stripped-down **config runs** (Build, one instrumented Commit, random replay of proof units), **replacing the BF16 re-baseline epoch.**
- **Your scope is unchanged.** The port's BF16 steps (the target and GEMM, FA2, the kernels at 188 SMs) are the sweep's prerequisites. The FP8 work (5a/5b and the checkpoints) feeds a later FP8 night.
- **Drop:** anything aimed only at the old epoch's full row (the pairs, the control arm, manifest-verify).
- **Prioritise:** whatever makes a config run correct and fast on sm_120.
- **"Row" is now "config run"** in new code and notes.
