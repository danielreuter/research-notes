---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-staging-bug (bc-6a0184ce) · kind: handoff (scope widened) · from: vllm-coordinator · created: 2026-09-30T17:49Z

**The SmolLM2-135M 256-byte staging mismatch isn't Gumbel-only.**
- **g230** (SmolLM2-135M, **top-p 0.95, batch 8**) hits the same +256 B mismatch, on the **prefill** step.
- Top-p still passes at **batch 1**.
- **20 deployments are now held on it** (up from 10).
- The dated update is in the epoch lane's finding: `lanes/vllm-coordinator/20260930T1703Z-finding-from-vllm-epoch-run-smollm135-gumbel-staging.md`.

**What that changes:**
- The trigger isn't the Gumbel sampler itself. It looks like a SmolLM2-135M-specific size (hidden 576, 9 heads, 3 KV heads) meeting a layout or padding quantum.
  - At B1 it shows only when the Gumbel/top-p=1 path adds one more buffer.
  - At B8 top-p it shows already at prefill.
- **Things to check:**
  - buffers whose byte size is a multiple of 576, or of 9 × 64, times ntok or nreq, and are rounded to 256 somewhere in the plan but not in the staged step (or the reverse);
  - whether the warm-up's plan is learned at a different (ntok, nreq) than the committed prefill uses at B8.
- **Proving set** for your fix: SmolLM2-135M Gumbel B1, SmolLM2-135M top-p B8 (g230), and one passing neighbour, all with identical roots where they passed before.

Report to me with a `-handoff-` in `lanes/vllm-coordinator/`.
