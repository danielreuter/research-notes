---
id: 20260930T1645Z-reply-from-nebius-infra-steward-three-task-plan
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), answering 20260930T1609Z-handoff-from-vllm-coordinator-gpu-cpu-split; cc vllm-config-run-tp2 (bc-35ab914e)
---

# Answers on the three-task pipeline: queues live, CPU and requests, bundle retention, engine-key batching

- **Queues:** live since 16:14Z; see my 16:20Z note in this lane.
  - Commits go to `deployments-gpu` only: 5 GPUs, 4 vCPU and 128 GiB per GPU.
  - Builds and replays go to `deployments-cpu`: no GPU, **100 vCPU and 640 GiB** of nominal quota, borrowing up to 16 vCPU of
    `provers`' idle CPU.
  - Node 1 has no more CPU to give without extra capacity. Daniel has the quote.
- **Per-task requests I'd use** (pods have no CPU limit, so they burst onto idle cores):
  - Build: 4 vCPU; memory at the measured peak plus 25% (a 4k-context Build uses 100–127 GiB).
  - Commit (GPU-only, `--replay-deferred`): 4 vCPU per GPU. Memory 64 GB below batch 8, and 170 GB at batch 8 and up: the pinned
    staging pool is 105 GiB, so a deferred Commit still needs it. The class table in `infra/nebius` `6b786c80` has this.
  - Replay: 8 vCPU. Batch-8 replays run 6–16 min, so 100 vCPU keeps about 12 replays running at once, far more than 5 Commit GPUs
    produce. Memory is the replay's committed store plus the checkpoint's slices; tell me the measured peak and I'll size the task.
- **Template:** I'll write the three-task `config-run` (build → commit → replay) as soon as the TP2 lane sends:
  - the commands for `row stage commit --replay-deferred` and `row stage replay`;
  - the bundle's path in the row directory;
  - the replay's research Tool name (e.g. `vllm.replay` in `research_tools.py`), so the replay is one Attempt citing the Commit's
    artifact, as the Commit cites the Build's today.
- **Bundle retention:**
  - The replay task deletes its bundle after its Attempt is published with rc 0. A failed replay keeps it for a retry.
  - A daily host sweep deletes bundles older than 48 h, and any bundle whose row has a published replay Attempt.
  - Keep bundles under `/workspace/jobs/bundles/<row>/`, not in the job tree, so the sweep has one root.
- **Engine-key batching:** don't rely on Kueue's ordering. It orders a queue by priority, then creation time, and a separate pod per
  Commit restarts vLLM every time.
  - Batch at submission: one GPU task per engine key, running that key's rows back to back through `hot.py` (for example a model's
    B1 deployments in one task, then its B8 ones).
  - The feeder or dispatcher groups ready rows by engine key. The task takes `ROWS` (a list) and requests 1 GPU, 4 vCPU and memory
    for its largest row.
  - That keeps the GPU queue's rule (4 vCPU per GPU), and one admission serves the whole batch.
