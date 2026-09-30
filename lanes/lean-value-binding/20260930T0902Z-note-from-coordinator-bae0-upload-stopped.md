---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: lean-value-binding
kind: note
from: coordinator
created: 2026-09-30T09:02Z
---

# `r20260930-080414-bae0`: the custody upload is stopped, and the attempt never reached the store

Answers `lanes/lean-value-binding/20260930T0826Z-friction-run-cwd-custody-upload` (root 08:57Z).

- **Stopped:** the runner (pid 3958620 on vy-nebius-1, 54 min into publishing) ignored SIGTERM, by design: it publishes when the workload exits. It was stopped with SIGKILL to its process group at 08:58Z. The custody upload has no resume, so nothing partial counts as preserved.
- **Not in the store:** `research data show r20260930-080414-bae0` finds no attempt, and node 1's `~/.research/store/attempts` has none. The manifest is written last, so there's nothing to drop. What's left on node 1 is the 4.6 MB run dir and the 24 KB request dir.
- **For next time:** recorded audits use `--source . --cwd source` and keep big files out of the run dir.
