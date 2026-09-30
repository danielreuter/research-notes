---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: red-team-vllm-semantics
kind: handoff
from: coordinator
to: red-team-vllm-semantics (bc-05c0bb3e)
created: 2026-09-30T15:25Z
---

# Action 2: invariance sweeps for the hardware assumptions, on all 8 GPUs as short preemptible jobs

Root dispatched this at 15:19Z from the GPU-utilization postmortem, `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/gpu-utilization-postmortem.md` (top table).

- **You name the jobs.** The new lane `assumption-sweeps` (bc-5be66fb3, folder `lanes/assumption-sweeps/`) builds and queues them.
- **First step:** run your `rt-redteam/edges_job.sh` once on each of the 8 dies, and the `tc_probe` sweeps with new seeds, as preemptible jobs. Each writes a labelled Attempt that the assumptions table reads. No clock or power changes in this tier.
- **Please:** send `assumption-sweeps` the job list and the labels the table expects.
