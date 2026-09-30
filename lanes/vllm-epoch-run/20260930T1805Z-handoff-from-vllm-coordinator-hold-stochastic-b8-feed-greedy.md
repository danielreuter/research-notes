---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator · created: 2026-09-30T18:05Z · root's call

- **Keep the 130 stochastic deployments held.** Don't run them for the record; they rerun after vllm-staging-bug's fix, which is now the top vLLM priority. They're not labelled until then. Don't label them `fail` from the pattern.
- **Keep node 1 fed:**
  - greedy deployments at every batch and context;
  - stochastic deployments at B1 only where they're known to pass (not SmolLM2-135M Gumbel);
  - the re-runs already on your list: Qwen3-30B-A3B for its Attempt, Gemma-2 once #581 is on a pre-merge branch, the 4k context after build-optimization's fix.
  - The GEMM lane runs the 7 FP8 deployments.
- **Send vllm-staging-bug the run ids and commit logs** of the 5 failing and 1 passing B8 stochastic runs, as a `-handoff-` in `lanes/vllm-staging-bug/`.
