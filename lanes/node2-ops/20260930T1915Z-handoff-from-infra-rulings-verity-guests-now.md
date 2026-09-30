---
id: 20260930T1915Z-handoff-from-infra-rulings-verity-guests-now
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: Daniel approved the one pool, so deploy the held Verity guest path now and agree the cutover with cluster-build

Daniel's rulings are in `note:20260930T1915Z-rulings-from-daniel-one-pool`. For you:

1. **Deploy the held Verity-pool changes now.** These are the interim guest path from
   `note:20260930T1629Z-reply-from-pous-infra-to-nebius-infra-steward-spare-cpu`: `fill_runner` plus `node_ops` from
   `/workspace/pouw/infra/lane/`. Before you deploy:
   - **Take GPUs too:** borrowing now covers them, so extend the pool from CPUs only to preemptible GPU fill as well, with the
     owner first and guests evicted in windows. Follow the pattern pous infra wrote.
   - **Commit first, then deploy:** put the code on `infra/nebius` before it goes live, using `restart_fill_after_window.sh`,
     outside a window.

   The pool is live when a Verity job submitted as `project=verity` runs, and is frozen or evicted in a window. Say so in
   `lanes/infra/` and `lanes/nebius-infra/` so Verity lanes can use it.
2. **Deploy the usage-report cap.** You committed it and held it back as a node change; it no longer needs to wait.
3. **The cutover is approved.** The `cluster-build` lane (bc-c2e4c12a) runs the shadow and makes the switch. Answer its asks
   quickly, and agree the switch time with it.
4. **Keep going on everything else:** Daniel's priority 2 (`note:20260930T1905Z-handoff-from-infra-daniel-priority-2-utilization`),
   with the target confirmed at ≥95% GPU busy, ≥90% of it useful. Your lane's notes can be read without asking.

Report results, not steps.
