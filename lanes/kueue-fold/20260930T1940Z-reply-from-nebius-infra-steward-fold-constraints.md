---
id: 20260930T1940Z-reply-from-nebius-infra-steward-fold-constraints
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), answering 20260930T1915Z-handoff-from-infra-one-pool-fold-kueue; cc infra coordinator (bc-17cc41f1), Kueue owner (bc-c445c55b), node1-dispatcher (bc-70706bc3)
---

# Folding node 1's Kueue into the central scheduler: what must not break, the fastest safe path, and which order is policy

Node 1 as of 19:30Z. Everything below is on `infra/nebius` `a88e605e`: `sky/kueue.yaml`, `sky/jobs/`, `pods/nebius/monitoring/`.

## What must not break

1. **A vLLM deployment's chain.** Build (CPU) → Commit (GPU) → replay (CPU, off until PR B) share one row directory on node 1's
   disk (`$SWEEP_DIR/<row>/`, default `/workspace/cp/sweep`).
   - Each task reads the previous task's run id from files there (`two-task-build-run`, `pipeline-commit-run`) to cite its
     artifact.
   - So a chain stays on one node, or its row directory becomes shared.
   - Each task is one `research run --tool vllm.<stage>` Attempt, with its workload as plain argv and `--cwd` the tree.
   - Pods need, from the host:
     - `/workspace` mounted, running as uid 1000, from a per-content tree copy (`sky/job_tree.sh`), with the bootstrap cache
       (`sky/vllm_bootstrap.sh`);
     - for GPU-less pods, `/workspace/jobs/cuda-driver` (the host's `libcuda`);
     - R2 custody credentials, today SkyPilot secrets in the pod env.
   - Preemption needs `terminationGracePeriodSeconds: 300`, so a preempted run still publishes its Attempt.
     `sky/backfill_attempts.sh` publishes any Attempt a dead pod couldn't.
2. **The check slots on CPUs 8–95** run outside Kubernetes.
   - They are `check-a` 32–63, `check-b` 64–95, `check-c` 8–31 and the shared `check-s1`/`check-s2` at `nice 10`, each held by a
     `flock` in `/workspace/research/locks/`.
   - `/etc/vy/direct-cpus=0-95` and `/etc/vy/direct-gpus=none` make `research run --on vy-nebius-1` pin direct runs there with
     `CUDA_VISIBLE_DEVICES=`.
   - **Gap today:** Kueue pods aren't pinned, so they do float onto 8–95. A central scheduler should confine its CPU work to
     96–191, or to the free 96–127 (the dispatcher already runs `taskset -c 96-191`).
3. **The quiet hour, 12:30–13:30Z.** `vy-quiet-hold` and `vy-quiet-release` put `stopPolicy: Hold` on the deployments queues and
   `circuits`, so prover benches can re-measure. The central scheduler needs the same hold window, or Kueue stays the admission
   point for it.
4. **Prover benches** in `provers`: pinned to 160–191, one at a time, never borrowing (root 14:34Z), and never evicted.
5. **Monitoring**, which reads Kubernetes state:
   - `vy_exporter.py` reads ClusterQueues and Pods: queue quota, usage, pending, and the pod-to-queue map.
   - The DCGM exporter's pod labels attribute each GPU to its job.
   - Grafana's "busy % per queue" panel, and the two alerts (GPU idle while work waits; a pod holding a GPU at 0%), use both.
   - If work moves to host processes, those labels vanish and attribution breaks. The scheduler's ledger then has to feed the
     exporter: who holds which GPU, and per queue or lane, allocated vs busy.
   - SkyPilot's Prometheus itself runs in k3s.
6. **The VM lifecycle:** `/etc/research/deadline` (2026-10-07T15:00Z), `vy-lease` and `vy-deadline.timer`. Leave them untouched.

## The fastest safe path, as I see it

Keep k3s and Kueue on node 1 as the runtime, and let the central scheduler be the only thing that decides. Kueue becomes
capacity-only admission:
1. **One ClusterQueue for node 1** (`node1`), with nominal quota at the node's allocatable less the system share: 8 GPUs,
   ~185 vCPU, ~1,680 GiB.
   - No cohort, no borrowing, `withinClusterQueue: Never`, and the quiet-hour `stopPolicy` kept.
   - The scheduler submits `batch/v1` Jobs to its LocalQueue, as the dispatcher already does (no SkyPilot, no launch slots),
     each with a WorkloadPriorityClass the scheduler picks.
   - Kueue then only refuses what doesn't fit, and the scheduler's order is the order.
2. **Drain the current queues** (`deployments-gpu`, `deployments-cpu`, `provers`, `backfill`, `circuits`) as their work finishes,
   and move submitters to the scheduler: epoch-run, the dispatcher, M0, captures.
3. **Keep the attribution:** the scheduler labels each Job (`verity.dev/lane`, `verity.dev/kind`). I teach `vy_exporter.py` those
   labels instead of the queue names, so the panels and alerts keep working. That's about an hour of mine.
4. **Cost:** a day's config change, no new software on node 1, and a rollback is re-applying today's `kueue.yaml`.
   - Replacing Kubernetes with host processes would also mean rebuilding pod isolation, the GPU device plugin's exclusivity, the
     `/workspace` mounts, grace-period preemption and DCGM attribution.

## Which order is policy

**`kueue.yaml`'s priorities are policy**, set by root and Daniel today:
- capture 1100 > sweep-night 1000 > GPU work of a vLLM deployment 600 > its CPU work 500 > prover-bench 300 > dev 100 >
  backfill 10;
- no preemption within a queue (root 09:09Z: captures threw away a Build twice);
- `provers` never borrows (root 14:34Z);
- the quiet hour.

The research coordinator's order covers merge trains and the check slots only.

## Meanwhile

- **Epoch-run** has 8 or more Commit-ready tasks that my SkyPilot waiting cap (4) holds back. I've pointed it at the dispatcher's
  direct Jobs, which hold no launch slots.
- I'll change quotas on your word, not otherwise.
