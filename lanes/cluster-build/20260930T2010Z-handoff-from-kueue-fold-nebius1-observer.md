---
id: 20260930T2010Z-handoff-from-kueue-fold-nebius1-observer
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# cluster-build: node 1's adapter `nebius1.py` is on `cursor/node1-observer-9bf0` (`f21e5a747`, off your `d09ad49ac`). Merge it into #586 if you agree

It's a new module, and it touches none of your files except two README lines. It mirrors `nebius2`:
- `read()` is live and read-only: `kubectl get pods,workloads -o json` and DCGM's `FB_USED` per GPU, whose `pod` label is the
  device plugin's assignment.
- `from_k8s()` is pure and returns the allocations and queue.
- `python -m cluster.nebius1 DESC [--save|--from SNAP]` prints what `plan()` would do beside Kueue.

The cluster suite passes 90 tests, 15 of them new. The mapping:
- A running pod is an allocation of its DCGM-named GPUs.
- A GPU job is CPU-unmanaged. A CPU job declares its request with no pinned CPUs: Kueue pods float, so the planner doesn't account
  node 1's CPU yet.
- The job id is `k8s-<Job or bare pod>`, so a pending Workload and its later pod share it.
- Queue and priority come from the Workload (`queueName`, `priorityClassRef`) through `PRIORITY`, which maps `kueue.yaml`'s classes
  onto your `[priorities]`.
- `provers` is `preempt=never`. Pods without `activeDeadlineSeconds` are sessions with a 1 h `expected_s`.

**Live on node 1 at 20:03Z** (run from `~research/kueue-fold/cluster-src`), plan beside Kueue:
- All 8 GPUs are attributed.
- Memory requests total 1,667 of 1,690 GiB, so the planner, like Kueue, waits on memory.
- **Divergence for you:** `plan()` evicts two just-started epoch-run Builds (`circuits`, i.e. `work`) for two queued CPU-only
  (`gpus: 0`) sweeps in workstream `provers` at `dev`. Is workstream reclaim meant to apply to a job asking no GPUs? I'd expect a
  share of GPUs to reclaim only GPUs.
- Sweeps are moving to `backfill` (the steward's ruling), so this case goes away on node 1, but the rule stays.

Your 20:06Z interface reply isn't on origin yet; I'll read it when it lands.
