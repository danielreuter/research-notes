---
id: 20260930T1915Z-handoff-from-infra-cutover-approved-one-central-scheduler
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: the cutover is approved now; the goal is one central scheduler across both nodes; run the shadow as soon as it's built

Daniel's rulings: `note:20260930T1915Z-rulings-from-daniel-one-pool`. What changes for you:

- **Start the shadow run yourself on node 2** as soon as steps 2a–2c pass their gates. You no longer wait for me. The shadow's
  read-only conditions still hold.
- **You own the switch.** Make it when the evidence is good enough; the 3 h / 6-window bar is a guide, not a gate. Two things must
  hold before you switch:
  - every observed window would have got its GPUs within 5 s;
  - there has been no safety divergence.

  Tell the RTX PRO coordinator and node2-ops 15 minutes ahead (`lanes/pous/`, `lanes/node2-ops/`). Report to `lanes/infra/`
  after.
- **The target is ONE central queue and scheduler for both nodes,** with one ledger. It isn't a planner per node plus a router.
  Each node runs a thin executor that starts and stops the jobs it is granted.
  - Hard constraint: node 2's timed windows get their GPUs within 5 s even while the link between the nodes is down. `gpu-lease`
    and a local executor fall back to local grants.
  - Put the brain where that constraint is easiest to meet, and say where in your report.
- **The node-1 side** (a Kueue/SkyPilot executor, the dispatcher's intake, the `vy-cluster` key between the nodes) goes to a new
  lane, `kueue-fold`. Agree the job and executor interface with it in `tools/cluster`, and keep the model in your hands.
- **Borrowing covers CPUs too:** the description has one pool. Owners go first on their own nodes, and guests are preemptible
  and never run in node 2's windows.
