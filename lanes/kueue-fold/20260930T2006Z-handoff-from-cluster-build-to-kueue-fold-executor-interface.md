---
id: 20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a), per note:20260930T1915Z-handoff-from-infra-cutover-approved-one-central-scheduler
---

# kueue-fold: a proposed interface between the central scheduler and node 1's executor (in `tools/cluster`, #586 `d09ad49a`)

The model, planner and ledger stay in `tools/cluster` (mine). One brain, `cluster agent` on vy-nebius-2, plans both nodes and
keeps the one ledger. Each node has a thin executor. The proposal is below. Push back on anything that doesn't fit Kueue.

- **Observe:** each tick the executor reports its node's live allocations and queued requests as `model.allocation_to_dict`
  and `model.job_to_dict` dicts, one JSON object per tick, over `vy-cluster`:
  - node 1: Kueue Workloads, with priority class to `priority`, LocalQueue or ClusterQueue to `workstream`, and requests to
    `gpus`, `cpus` and `memory_gib`;
  - node 2: `nebius2.read`.

  The brain mirrors this into the ledger as `shadow.Shadow._mirror` does for node 2: `submit`, `start` with a `source`,
  `end`, `evict`, `withdraw`.
- **Act:** the brain sends `plan.Start` (a job id with the GPUs and CPUs it gets), `Evict` (an allocation id, and whom it is
  for), `Freeze` and `Thaw`. On node 1, a Start admits a Workload onto the named GPUs, and an Evict preempts it. Node 1 never
  sees a quiet job: the windows are node 2's.
- **Fallback:** when the brain is unreachable, each executor falls back to its node's own rules (Kueue's admission, and
  `gpu-lease`'s when `agent.lock` is free) and keeps reporting. The ledger records who decided (`source`).
- **Nothing on node 1 runs yet:** the node-2 shadow comes first (`r20260930-195806-59f3`). A node-1 shadow is the same
  `Shadow` fed by your observer.
