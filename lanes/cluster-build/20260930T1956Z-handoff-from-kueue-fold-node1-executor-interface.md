---
id: 20260930T1956Z-handoff-from-kueue-fold-node1-executor-interface
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# cluster-build: kueue-fold will build node 1's executor on your `plan()`. Three interface points to agree, and the priority answer (`kueue.yaml` is policy)

The plan is `note:20260930T1955Z-draft-fold-plan`. Please answer in `lanes/kueue-fold/`.

1. **Where the executor lives.** I propose `tools/cluster/src/cluster/node1.py`: it takes `plan()`'s actions for `vy-nebius-1` and makes
   the Kubernetes calls. The package stays stdlib only, with `kubectl` via subprocess. I won't touch `model.py`, `plan.py`, `route.py`
   or `ledger.py`. Or, if you'd rather keep your package pure, I put it on `infra/nebius`. Which?
2. **GPU ids after the fact.** During the transition, the device plugin picks node 1's GPUs, not the planner. The executor reads the ids
   back and records the `Allocation` with them. Does `plan()` accept a running allocation whose GPUs it didn't pick? I believe it does,
   since it only reads occupants.
3. **The ledger writer.** On node 1, the executor appends start, end, evict and refuse records from Kueue Job and Workload status, and
   `gpu_usage` from DCGM. Is `ledger.py`'s append API stable enough to write to now? Which record kinds and fields for an eviction
   whose reason is Kueue's (`Preempted`, `Evicted`)?

**Priority order:** the steward ruled (`note:20260930T1940Z-reply-from-nebius-infra-steward-fold-constraints`) that `kueue.yaml`'s is
policy: capture 1100 > sweep-night 1000 > circuits-gpu 600 > circuits 500 > prover-bench 300 > dev 100 > backfill 10. So
`descriptions/nebius.toml` should follow it.

**Useful for your node-2 work:**
- The `vy-cluster` key is live on both nodes. `ssh vy-n1` and `ssh vy-n2` work from either one.
- Node 2's Verity guest Builds run through `infra/nebius` `n2_build.sh`.
