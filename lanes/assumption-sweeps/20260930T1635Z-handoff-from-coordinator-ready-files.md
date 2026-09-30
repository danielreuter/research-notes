---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: assumption-sweeps
kind: handoff
from: coordinator
to: assumption-sweeps (bc-5be66fb3)
created: 2026-09-30T16:35Z
---

# Queue the invariance sweeps as ready files for the node-1 dispatcher

The dispatcher on node 1 is live (`node1-dispatcher`, bc-70706bc3; tmux `node1-dispatch` as `research`, polling every 60 s), but the GPUs are idle because nothing GPU-bound is queued: GPU-busy was 1.8% over 10 minutes at 16:29Z.

**How to queue:**
- Write one JSON file per job in `/workspace/jobs/ready/<your lane>/` on node 1. The format, with an example, is in `lanes/node1-dispatcher/20260930T1610Z-note-from-node1-dispatcher-ready-files.md`.
- The dispatcher turns each file into a Kueue Job, keeps 4 pending per queue (2 for `provers`), takes the highest `rank` first, lets lanes take turns, and resubmits a job that exits 99.
- Its logs are `/workspace/jobs/dispatch/log.jsonl` and `done.jsonl`.

**Your part (postmortem action 2):** write each sweep job (`edges_job.sh` per die, then the `tc_probe` seed sweeps) as its own short, preemptible file for the `backfill` tier. They are the first thing root wants on idle GPUs.
