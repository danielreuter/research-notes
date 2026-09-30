---
id: 20260930T1915Z-handoff-from-infra-one-pool-fold-kueue
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Steward, Kueue owner and dispatcher: Daniel wants one pool and one central scheduler, so node 1's Kueue is folded in; a new lane, kueue-fold, leads it with you

Daniel's rulings of 19:12Z are in `note:20260930T1915Z-rulings-from-daniel-one-pool`.
- Both nodes are one pool, and borrowing goes both ways for GPUs and CPUs.
- There is one central queue and scheduler. Node 1's Kueue doesn't stay a separate scheduler.
- Access stays the simplest thing that works: the existing research key for agents, plus one `vy-cluster` key pair between the
  nodes.
- The node-2 cutover is approved.

**Who does what:**
- **kueue-fold** (a new infra lane): writes and runs the fold plan. It builds node 1's executor under the central scheduler,
  folds the dispatcher's intake into the central queue, and installs `vy-cluster` on both nodes.
- **Steward and Kueue owner:** please answer its asks in `lanes/kueue-fold/` quickly. It needs three things from you:
  - what must not break: the vLLM Build/Commit chaining, the check slots on CPUs 8–95, the quiet hour 12:30–13:30Z, Grafana and
    the alert sink;
  - the fastest safe path, for example turning Kueue into a runtime that admits whatever the scheduler sends, with no quota logic;
  - whether `kueue.yaml`'s priorities or the research coordinator's order is policy.
- **Dispatcher:** start now on the interim path. Queue PoUW's untimed overflow (work that neither ranks nor times sm_120) on
  node 1's `backfill`, and make backfill actually borrow idle GPUs. Node 1 at about 2% GPU busy is the largest waste in the
  pool, and the target is ≥95% busy with ≥90% of it useful.

**Earlier asks:**
- The alert-sink retarget to `lanes/infra/` still stands; verity-root agrees, so one change.
- The phase-1b shadow question is superseded: shadow runs are approved.
