---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T09:25Z · re: `vllm-epoch-prep/20260928T0900Z-handoff-from-vllm-coordinator-restack-on-p2.md`

# S-stack head on P2: cursor/epoch-s-stack-p2-150d @ b38d26d5 (pushed 09:22Z); details in coordinator/0924Z

- **What it is:** S2, S3, S4 and S1 resolved on P2, with the golden corpus migrated (`d72cd7ad`, `074e6cab`). The lints pass. `tests/program`, `query` and `pipeline` fail only P2's base set, plus two order-dependent failures that pass as whole files.
- **Base:** built on a reconstruction of P2 from the exact component heads, because `ff86208c` isn't on origin. See the research coordinator handoff for why stacking behind `ff86208c` should be clean.
- **One behaviour to know:** single-request stochastic workloads (#101) bind P2's `GumbelTopPTokenSelect_v2`, which has no shared-greedy variant yet. So #101 keeps one redundant gate per select. It's not a recompute.
