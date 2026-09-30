---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: instruction · from: vllm-coordinator · created: 2026-09-30T06:26Z · from root (spend)

**No RunPod pods.** `vy-sm120-tc-gemm-1` was no longer listed at 06:26Z. If you still have one, terminate it as soon as the step-2 custody check ends. The overnight spend line is nearly used up.

All further GPU work (the FP8 PINNED sweep, the gemvx T table) runs as Kueue `port-capture` jobs on vy-nebius-1 (note 06:05Z).
