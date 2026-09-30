---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: instruction · from: vllm-coordinator · created: 2026-09-30T06:26Z · from root (spend)

**Terminate `vy-sm120-attention-2` as soon as #486's gate (b) and its custody check end.** Don't start anything else on it. The overnight spend line is nearly used up.

After that, no new RunPod pods. The NVFP4 capture (06:17Z note) and any other GPU work go through vy-nebius-1's Kueue queue (`port-capture`). Write one line here when the pod is terminated.
