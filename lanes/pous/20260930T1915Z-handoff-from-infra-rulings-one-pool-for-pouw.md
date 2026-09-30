---
id: 20260930T1915Z-handoff-from-infra-rulings-one-pool-for-pouw
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# pouw: Daniel approved the cutover and one pool; PoUW's untimed work may overflow to node 1 now, Verity guests arrive on node 2, and timed windows stay protected

For the pouw coordinator (bc-b729c175) and the RTX PRO coordinator (bc-2aa33ad8). Daniel's rulings are in
`note:20260930T1915Z-rulings-from-daniel-one-pool`.
- **The node-2 cutover is approved.** The `cluster-build` lane (bc-c2e4c12a) runs the shadow and makes the switch, telling you 15
  minutes ahead.
  - The freeze list stays untouched, and `gpu-lease` keeps its interface.
  - Please send the RTX PRO coordinator's freeze-list sign-off to `lanes/cluster-build/`. If it has an objection, it goes there
    too, before the switch.
- **One pool:** node 2's idle GPUs and CPUs take preemptible Verity guest jobs from now on (node2-ops deploys it). Guests are
  evicted or frozen for every timed window, and PoUW's own work always goes first.
- **Overflow:** PoUW work that neither ranks nor times sm_120 kernels (censuses, captures, CPU verifies, Lean) may go to node 1's
  idle GPUs through node1-dispatcher's backfill. Node 1 is about 2% busy.
- **Utilization target, confirmed:** ≥95% GPU busy with ≥90% of it useful. node2-ops keeps the standing backlog with bc-2aa33ad8.
