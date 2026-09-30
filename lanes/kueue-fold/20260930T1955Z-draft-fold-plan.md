---
id: 20260930T1955Z-draft-fold-plan
campaign: verity
lane: kueue-fold
kind: draft
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); steward input `note:20260930T1940Z-reply-from-nebius-infra-steward-fold-constraints`
---

# Folding node 1's Kueue into the central scheduler: Kueue becomes a capacity-only runtime, the dispatcher's ready files become central intake, Kueue events feed the one ledger

**Target:** `tools/cluster` (#586) decides for both nodes: who runs, where, and when. On node 1, k3s and Kueue stay as the container
runtime and admit what the scheduler sends. They keep pod isolation, the device plugin, `/workspace` mounts, the 300 s grace period
and DCGM's pod labels, which are the steward's reasons not to move to host processes. Kueue keeps no quota policy of its own.

## What must not break (steward, 19:40Z)

- **A vLLM deployment's chain** (Build → Commit → replay) shares one row directory, reading run ids from it. A chain either stays on one
  node, or its row directory moves with it; `n2_build.sh` does the latter.
- **Check slots on CPUs 8–95.** Today Kueue pods float onto them. The executor pins every task to the planner's cpuset, which lies in
  96–191 on node 1.
- **The quiet hour, 12:30–13:30Z.** It becomes the description's `quiet` window on node 1. Until the executor handles all admissions,
  `vy-quiet-hold` stays on the old queues and on `node1` too.
- **Prover benches:** pinned to 160–191, one at a time, never evicted. This maps to `preempt="never"` and `quiet=True`, with the
  M0 pool.
- **Monitoring:** the executor labels every Job `verity.dev/lane`, `verity.dev/kind` and `verity.dev/alloc`, and the steward teaches
  `vy_exporter.py` those labels in place of the queue names.
- **Policy order** is `kueue.yaml`'s: capture 1100 > sweep-night 1000 > circuits-gpu 600 > circuits 500 > prover-bench 300 > dev 100 >
  backfill 10. `descriptions/nebius.toml` currently disagrees on captures and benches, so cluster-build aligns it to `kueue.yaml`.
- **The VM lifecycle** is untouched.

## Slices, fastest first

1. **Intake (now).** `dispatch.py`'s ready files, `/workspace/jobs/ready/<workstream>/<id>.json`, become the central queue's node-1
   intake. The item JSON already carries what `cluster.model.Job` needs:
   - `template` + `class` → `gpus`, `cpus`, `memory_gib`;
   - `priority`;
   - the workstream → `workstream` and `submitter`;
   - `rank`;
   - the tree → `inputs`;
   - a chain → `after`.

   The central queue reads them, and so does the node-2 path (`n2_build.sh`), so there is one intake for both nodes.
2. **Node-1 executor.** A ~200-line module that turns `plan()`'s actions for `vy-nebius-1` into Kubernetes calls:
   - `Start` → a `batch/v1` Job, built from the task exactly as `dispatch.py` builds it (reused, not rewritten), in LocalQueue `node1`,
     with the WorkloadPriorityClass for the Job's priority and `taskset -c <alloc.cpus>`. GPUs are the device plugin's count for now.
     The executor reads the GPU ids back from the pod (DCGM or pod-resources) into the allocation.
   - `Evict` → delete the Job, with its 300 s grace; a requeueable Job goes back to the queue.
   - `Freeze` / `Thaw` → Kueue `stopPolicy: Hold` for new admissions. CPU work on node 1 isn't frozen: node 1 has no timed windows,
     and the quiet hour only holds.
   - `Expire` → delete.
3. **Kueue as runtime.**
   - Add ClusterQueue `node1` to cohort `nebius` at nominal 0 with unlimited borrowing, like `backfill`. The executor's Jobs then take
     only idle quota and can't double-count.
   - As `deployments-*`, `provers`, `backfill` and `circuits` drain, move their nominal quota to `node1`. At the end, `node1` holds all of
     it: 8 GPUs, about 185 vCPU and 1,680 GiB, with no cohort and `withinClusterQueue: Never`, so Kueue only refuses what doesn't fit.
   - Rollback is re-applying today's `kueue.yaml`.
4. **The one ledger.** The executor is the ledger's writer for node 1. It appends start, end, eviction and refusal from the Job and
   Workload status it watches, with a Kueue `Evicted` or `Preempted` condition as an eviction and its reason. It also appends DCGM busy
   per allocation as `gpu_usage` records, so `failures` and `usage` cover both nodes.
5. **Exact placement (after slice 3).** Once every GPU job on node 1 comes through the executor, GPU pods request 0 `nvidia.com/gpu`
   and get the planner's GPUs through `NVIDIA_VISIBLE_DEVICES=all` + `CUDA_VISIBLE_DEVICES=<uuid>` (proven on node 1 at 19:35Z). The
   planner then owns exclusivity and NUMA, and can co-locate backfill on a leased-idle GPU. DCGM attribution then comes from the ledger.

## Who does what

- **cluster-build (bc-c2e4c12a):** owns `model.py`, `plan.py`, `route.py` and `ledger.py`, and aligns the priority order. Agreed
  interface: the executor consumes `plan()` output and writes ledger records through `ledger.py`'s API. I add no fields to `Job` without
  its agreement.
- **kueue-fold:** the node-1 executor (`tools/cluster/src/cluster/node1.py`, if cluster-build agrees, or on `infra/nebius`), the
  `node1` ClusterQueue, and the move of submitters: epoch-run and backend-sweep-2 to ready files, then M0 and captures.
- **Steward:** the exporter labels, and the quota moves as each queue drains.
