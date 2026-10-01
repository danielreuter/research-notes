---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T17:40Z

**Gemma-2-2B step 3 replay: still compiling at 10:40 AM PDT, so the 11:20 result may be late.** `boolean-replay`
`r20261001-163611-11a7` opened the keep, checked the partition of record and opened 316/316 weights by 9:37. Since then it has
been in `prewarm`, compiling the Boolean version of each of the 460 picks' 36 specializations serially before it forks its 30
workers. Those include 16 `AttentionSoftcap_v3` specializations at different T (D=256) and `Gemm_v3{K=2304,N=256000}`.
SmolLM2's prewarm took 31 minutes; this one is at 64 minutes and 46 GB, still growing. After the fork, the Boolean and word
replays follow. I'll report 460/460 or the mismatches when it ends. Steps 1, 2 and the Build are done (earlier checkpoints),
and the PR body is in the store at `internal/circuits/bool-gemma2-pure-pr-body.md`. Its result lines are pending.
