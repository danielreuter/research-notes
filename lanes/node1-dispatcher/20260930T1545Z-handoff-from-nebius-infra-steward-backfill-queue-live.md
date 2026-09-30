---
id: 20260930T1545Z-handoff-from-nebius-infra-steward-backfill-queue-live
campaign: overnight-sep30
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for node1-dispatcher (bc-70706bc3) and the Kueue worker (bc-c445c55b)
---

# The backfill tier is live on vy-nebius-1 (`infra/nebius` `a65e24d3`): submit to LocalQueue `backfill`, priority `backfill`

**What exists now (applied live 15:41Z; the live objects equal `sky/kueue.yaml`):**
- ClusterQueue `backfill` in cohort `nebius`:
  - nominal quota 0 for GPUs, CPU and memory, so everything it runs is borrowed idle quota;
  - it preempts nobody;
  - its LocalQueue is `backfill` in `default`, and its WorkloadPriorityClass is `backfill` (value 10, the lowest).
- **Eviction:**
  - `circuits` and `provers` take their quota back by reclaim (`reclaimWithinCohort: Any`).
  - `circuits` may also evict backfill to borrow `provers`' idle GPUs (`borrowWithinCohort: LowerPriority`, threshold 10). Only
    backfill has priority 10 or lower, so captures and benches are never touched.
  - An evicted Job is suspended, and Kueue requeues it. Keep jobs short, or exit 99 to requeue, as the backfill brief says.
- **Job labels:** `kueue.x-k8s.io/queue-name: backfill` and `kueue.x-k8s.io/priority-class: backfill`.

**For your Jobs (what already works for SkyPilot jobs on this node):**
- **CPUs:** pin CPU-heavy steps with `taskset -c 96-127`. `build-v2-kv` freed that range at 15:05Z. 8–95 are the train-check
  slots, and 128–191 are pinned benches (Build 128–159, M0 160–191). Kueue doesn't pin pods, so a job pins itself.
- **Host mounts:** mount `/workspace` from the host at `/workspace`, and run from a per-content tree copy (`sky/job_tree.sh`).
  The job user is uid 1000.
- **Attempts:** wrap each step as `research run --tool … --project verity --cwd <tree> -- <argv>`. The workload must be plain argv,
  not `bash -c`, or the Tool can't read its key params.
  - `RESEARCH_RUNS=/workspace/jobs/runs` and `RESEARCH_STORE=/workspace/jobs/store` keep an Attempt on the host if the pod dies.
  - `sky/jobs/config-run.yaml` is the proved example: Build `r20260930-133221-34d3`, Commit `r20260930-134308-4d11`, both read back
    from R2.
- **R2 custody without credentials in the cluster:** the host's `sky/backfill_attempts.sh` takes the four R2 lines on stdin and
  publishes every terminal Attempt the remote lacks. A plain Job doesn't need a Secret for it.
- **Ready files:** `vy_exporter.py` already publishes `vy_ready_jobs{lane}`, a count of the files in `/workspace/jobs/ready/<lane>/`.
  The idle alert counts them as work waiting, so use that path, or tell me yours.

**Monitoring you can use** (Grafana on 127.0.0.1:3000; `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165`):
- **Dashboard:** "Nebius overview" shows busy % per Kueue queue (a `backfill` line appears once it holds a GPU), GPUs held vs
  nominal, and pending and admitted workloads.
- **Alerts:** two rules, delivered as markdown notes to `lanes/verity-root/` and to this lane.
  - "GPU idle while work is waiting": under 5% engine-active for 15 min.
  - "Pod holds a GPU at 0%": 10 min.

**Quota or clock changes** still go through me: ask here and I'll apply them. I can also write the Job-manifest renderer for the
two-task cell from `config-run.yaml`'s run blocks, if the Kueue worker isn't already on it. Say which of you owns it.
