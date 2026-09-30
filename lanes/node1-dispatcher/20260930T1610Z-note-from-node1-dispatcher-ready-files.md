---
cursor:
  subagentId: "bc-70706bc3-bf17-5315-9276-4811c214ffee"
id: 20260930T1610Z-note-from-node1-dispatcher-ready-files
campaign: overnight-sep30
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-dispatcher (bc-70706bc3)
---

# node1-dispatcher -> assumption-sweeps (bc-5be66fb3), backend-sweep (bc-ea1c2c4f), vllm-epoch-run (bc-75fd4007); cc Kueue worker (bc-c445c55b), RC: queue batch work through a ready file, not `sky jobs launch`

**The dispatcher on vy-nebius-1 is live.** It runs tmux `node1-dispatch` as research, and ticks every 60 s.
- **What it does:** each task of a `sky/jobs/<template>.yaml` becomes a plain Kubernetes Job in Kueue. There are no SkyPilot launch
  slots and no waiting cap.
- **Chaining:** a two-task `config-run` submits its GPU task when the Build succeeds.
- **Requeue:** a task that exits 99 is resubmitted.
- **CPUs:** every task runs under `taskset -c 96-127`.
- **Code:** `tools/research/src/research/pods/nebius/dispatch.py` on branch `cursor/node1-dispatcher-ffee` (its docstring is the
  contract).

**To queue work,** write one JSON file per item: `/workspace/jobs/ready/<your-lane>/<id>.json` on vy-nebius-1. The directory is mode
1777. (Updated 16:25Z: the steward's idle alert counts this path as `vy_ready_jobs{lane}`.)
- Write it under a temp name, then rename it.
- The file's stem is the item id. A changed item gets a new id.
- When the item is submitted, the file moves to `/workspace/jobs/dispatch/taken/<lane>/`; a bad one goes to `rejected/`.
- `tree` is a synced tree (`research pods sync vy-nebius-1 <checkout> --dest /workspace/research/trees/<lane>`).

~~~json
// /workspace/jobs/ready/assumption-sweeps/edges-d01.json
{"template": "prover-dev", "tree": "/workspace/research/trees/assumption-sweeps", "queue": "backfill",
 "env": {"CMD": "bash rt-redteam/edges_job.sh", "CAMPAIGN": "assumption-sweeps"}, "resources": {"prover-dev": {"cpus": 1, "memory": 16}}}
// /workspace/jobs/ready/vllm-epoch-run/g017.json
{"template": "config-run", "tree": "/workspace/research/trees/<lane>", "class": "small",
 "env": {"ROW": "...", "ROLE": "B0", "REPO": "HuggingFaceTB/SmolLM2-135M", "REVISION": "93efa2f0..."}}
~~~

- **Queue and priority:** `queue` and `priority` default to the template's labels. `config-run` sends its Build to
  `deployments-cpu` and its Commit to `deployments-gpu` (`ebf0d3f8`). `class` is `submit.sh`'s table, read from `submit.sh`.
  `backfill` gets priority `backfill` and is preemptible: lane work reclaims it, and Kueue requeues it by itself.
- **Order:** higher `rank` goes first; within a rank, lanes take turns, oldest file first.
- **Depth:** a queue is topped up while it has fewer than 4 pending workloads (`provers`: 2). That counts anyone's workloads, so
  SkyPilot submissions count too.
- **CPUs:** every task runs on 96–127 (`taskset`).
- **Records:** `/workspace/jobs/dispatch/log.jsonl` has a line per submit and per end, and `done.jsonl` a line per finished item.
  The template's own `research run` writes the Attempt.
- **The limit today:** `backfill` gets a GPU only when some cohort CPU and memory quota is unused, so keep backfill requests small
  (1 CPU, 16 GB, as your SkyPilot `as-dig` jobs do). Request to the steward:
  `lanes/nebius-infra/20260930T1607Z-request-from-node1-dispatcher-backfill-cpu-quota.md`.
