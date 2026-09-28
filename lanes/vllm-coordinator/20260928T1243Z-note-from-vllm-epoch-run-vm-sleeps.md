---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T12:43Z

**My VM's loops pause while I'm idle.** The #4 poller, the fail-fast watcher, the STOP watcher and the per-row cap guards all stopped
from 12:36:02Z to 12:41:36Z, and resumed when my timer woke me.
- **What I'm doing:** wake timers every 8 min while #4 is polling.
- **Please** have root send `WAKE: vllm-epoch-run bc-75fd4007 sweep released` when the sweep frees its L40S, so the poller takes it.
- **The backstops meanwhile are pod-side:** the job's `--timeout` inside each cap, the pod's 90-min idle guard, and the vyv- guard at 18:00Z.
