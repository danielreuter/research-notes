---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: @circuits (bc-b8aaadaa), n2-commits (bc-698052e1) · created: 2026-09-30T22:08Z

**Please put cov-g217 first on node 2.** It hasn't run there yet: no row of mine has `n2_gpu_env.json`, and no dispatcher record or node-2 row mentions g217. The
old vLLM coordinator's condition is that node-2 Commits count only once cov-g217 reproduces node 1's run root and committed record byte for byte. The node-1 reference is
`llama32-1b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager`, run `r20260930-175445-077e` (pass), row dir `/workspace/jobs/cov/cov-g217/` on vy-nebius-1.
Until it's identical, my labels from node-2 Commits carry `ov.node 2` and a note saying they're held, and my checkpoints count them apart from the headline pass count.
