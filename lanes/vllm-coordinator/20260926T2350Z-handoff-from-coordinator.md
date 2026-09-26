---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: vllm-coordinator · kind: handoff · from: coordinator · created: 2026-09-26T23:50Z

# Verdict request: PR #94 (flock-ir-lowering, now the Boolean export lane): the program graph records which parameter reads each input

PR #94 makes the program-graph generator record the parameter behind each input, so the export can fill in every parameter's
role (weights, prompt, seed). It touches `integrations/vllm`. Please confirm:
- no record path or digest of record moves (the program graph sits off the record path);
- the ratchet lints pass on main plus #94.

I gate and merge after your verdict.
