---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator · created: 2026-09-30T18:56Z

**The staging bug is fixed: [#594](https://github.com/danielreuter/verity/pull/594)** (`cursor/warmup-seeded-plans-c646` @ `6a7ff652`, granted, next train).
- **Cause:** the warm-up dropped each request's `seed`, so the learned plans lacked the seed tail (8 B per request; 64 B at B8) that seeded steps stage. Where a plan ended on a 256 B chunk boundary, the step failed closed.

**Do now:**
1. **Cherry-pick `6a7ff652`** (or merge the branch) into your run branch.
2. **Acceptance first:** re-run **two of the failing stochastic B8 deployments from two different models** (not SmolLM2-135M). If both pass 460/460, release the 130 held deployments in breadth-first order.
   - If either still fails with the same message, stop, keep them held, and send me the runs; that would be a second cause.
3. **Already-passing stochastic deployments don't need re-running.** The fix doesn't change their committed bytes (SmolLM2-360M's root is identical).
4. `ov.note` prefix gains `#594`.

The staging lane found your workload files untracked on the run branch, and that the word check needs the Gumbel gate-limit variables. Make sure both are in the tree you submit from.
