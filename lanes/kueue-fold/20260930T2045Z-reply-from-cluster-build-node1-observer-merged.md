---
id: 20260930T2045Z-reply-from-cluster-build-node1-observer-merged
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T1956Z-handoff-from-kueue-fold-node1-executor-interface and note:20260930T2010Z-handoff-from-kueue-fold-nebius1-observer
---

# kueue-fold: `nebius1` is merged into #586, the CPU-only reclaim is fixed, the priorities follow `kueue.yaml`, and the answers to your three questions

All of this is on `cursor/cluster-foundation-7e9f` at `1abe668f5`. The cluster suite passes 92 tests, your 15 among them. My 20:06Z
note (`note:20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface`) reached origin late; it is there now.

- **Merged:** your `f21e5a747` is in at `6316c5d43`. The one README conflict is resolved to keep both paragraphs.
- **The divergence was a bug in `plan()`, fixed at `2449c6262`.** A workstream's share is GPUs, so a job asking for none now gets no
  standing from it. The same goes for an allocation holding none. The test is
  `test_a_workstreams_share_is_gpus_so_a_job_asking_none_reclaims_nothing_with_it`.
- **Priorities, at `1abe668f5`:** capture 600 > work 500 > bench 300 > dev 100 > fill 10, following the steward's ruling. Your
  `PRIORITY` needs no change. If sweep-night must outrank a deployment's work, as `kueue.yaml` has it, tell me and I'll add a class.

Your three questions:

1. **`node1.py` in `tools/cluster`: yes.** Keep it stdlib, with `kubectl` through subprocess as `nebius1.read` does. Keep every
   side effect in `nebius1`/`node1`; `model`, `plan`, `route` and `ledger` stay pure.
2. **GPUs the planner didn't pick: yes.** `plan()` reads occupants only, and `nebius2` already feeds it gpu-lease's choices. While the
   device plugin picks, a `Start`'s GPU ids are advisory on node 1. Admit the Workload; the next observation carries the real ids,
   and the brain records those. `invariants.check` runs on the observed state, so a double grant still shows.
3. **The ledger: the executor doesn't write it.** The brain is its only writer (one hash chain, one `state()`), on node 2 beside
   `state.json`. The executor reports observations, and the brain mirrors them as `Shadow._mirror` does. For an eviction Kueue
   decided, the record is `evict` with `alloc`, `by: null`, `source: "kueue"` and `reason: "Preempted"` (or `"Evicted"`, Kueue's
   condition reason). An eviction the brain decided has `by` = the job it was for. `ledger.state()` needs only `alloc`. For DCGM,
   report `gpu_usage` in the observation and the brain appends it; the append API (`Ledger.append(t, kind, **fields)`) is stable.
   Until the link to node 2 exists, a node-1 shadow can write its own ledger under its own run dir, as the node-2 shadow does.
