---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T06:26Z · supersedes the RunPod part of the 05:22Z GO

**HOLD every RunPod coverage cell (L40S, A100, H100), even if the guard shows `vyv-cov-`.** Root's overnight spend line is at $451.54 of $480, so the line has less than $30 of real headroom. Root has asked Daniel whether to raise it. Launch nothing on RunPod until I write "release" in this folder.

**Keep going:** the sm_120 cells as Kueue `config-run` jobs on vy-nebius-1 (note 06:17Z) cost nothing extra. Label them as they finish (note 06:10Z). The held RunPod cells aren't labelled yet; leave them unlabelled rather than `unsupported`.
