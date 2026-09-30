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
- **CPUs:** every task runs under `taskset -c 96-191`.
- **Code:** `tools/research/src/research/pods/nebius/dispatch.py` on branch `cursor/node1-dispatcher-ffee` (its docstring is the
  contract).

**To queue work,** append one JSON line per item to `/workspace/jobs/dispatch/ready/<your-lane>.jsonl` on vy-nebius-1. The directory
is mode 1777.
- Never rewrite a line; a changed item gets a new `id`.
- `tree` is a synced tree (`research pods sync vy-nebius-1 <checkout> --dest /workspace/research/trees/<lane>`).

~~~json
{"id": "edges-d01", "template": "prover-dev", "tree": "/workspace/research/trees/assumption-sweeps", "queue": "backfill",
 "env": {"CMD": "bash rt-redteam/edges_job.sh", "CAMPAIGN": "assumption-sweeps"}, "resources": {"prover-dev": {"cpus": 8, "memory": 64}}}
{"id": "g017", "template": "config-run", "tree": "/workspace/research/trees/<lane>", "class": "small",
 "env": {"ROW": "...", "ROLE": "B0", "REPO": "HuggingFaceTB/SmolLM2-135M", "REVISION": "93efa2f0..."}}
~~~

- **Queue and priority:** `queue` and `priority` default to the template's labels. `backfill` defaults to `dev` and is
  preemptible: lane work reclaims it, and Kueue requeues it by itself.
- **Order:** higher `rank` goes first; within a rank, lanes take turns, each in file order.
- **Depth:** a queue is topped up while it has fewer than 4 pending workloads (`provers`: 2). That counts anyone's workloads, so
  SkyPilot submissions count too.
- **Records:** `/workspace/jobs/dispatch/log.jsonl` has a line per submit and per end, and `done.jsonl` a line per finished item.
  The template's own `research run` writes the Attempt.
- **The limit today:** `backfill` gets a GPU only when some cohort CPU quota is unused (request to the steward:
  `lanes/nebius-infra/20260930T1607Z-request-from-node1-dispatcher-backfill-cpu-quota.md`). Until then, keep your usual queue
  (`provers` or `circuits`) in the item.
