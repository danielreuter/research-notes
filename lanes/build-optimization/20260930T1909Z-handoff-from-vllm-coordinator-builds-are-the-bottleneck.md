---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: build-optimization (bc-47d0a3ed) · kind: handoff (PRIORITY) · from: vllm-coordinator · created: 2026-09-30T19:09Z · Daniel 19:06Z

**CPU Builds are now the bottleneck for vLLM coverage.** Commits starve waiting for them, and the grid is growing to about 740 deployments (16 models × batch 1–64 × 3 contexts × 3 samplers, plus TP2 and FP8).

**The ask, in order of payoff:**
1. **Reuse across a model's deployments.** Deployments of one model differ in batch, context and sampler. Cache and reuse everything that doesn't depend on those: the per-layer Definitions, the derived step's module bodies, the unit-rule cache (#482), and the Program cache (`--program-cache`) keyed as finely as the digest allows. A model's second deployment should cost a fraction of its first.
2. **The 4k-context request derive** (my 16:39Z handoff): 16+ deployments timed out at 7,200 s.
3. **Build RAM and cores per job:** tighten the plan so more Builds fit at once on node 1's CPU share. Node 2's spare CPU may come too, pending Daniel's yes.

**Constraint:** digests stay byte-identical for rows that build today. Prove it on one before and after.

Send PR heads as `-handoff-` files in `lanes/vllm-coordinator/`. I grant straight away.
