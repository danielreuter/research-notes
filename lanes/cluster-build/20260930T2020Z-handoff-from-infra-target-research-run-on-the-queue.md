---
id: 20260930T2020Z-handoff-from-infra-target-research-run-on-the-queue
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build and kueue-fold: the target is every lane submitting through `research run` onto the one queue across both nodes, as fast as possible

Daniel, 20:17Z: every lane's research jobs go through `research run` on the one queue across both nodes, and run optimally there.
The criteria for "settled" are in `lanes/infra/20260930T1845Z-report-infra.md`, § "Priority 1 settled".

**What that means for the build:**
- **`research run` is the only submit interface.** Give it a queue target, e.g. `research run --queue ...` or `--on cluster`, that
  hands the job to the central queue. The queue places it on either node, starts it, custodies its outputs, and records it in the
  ledger. Keep `--on <node>` as a placement constraint, not as a way around the queue.
- **Order of work:**
  1. node 2's agent live;
  2. the `research run` → queue path for batch jobs on node 2;
  3. node 1's executor (kueue-fold);
  4. session leases for interactive work.
- **Milestone to report to infra:** the queue accepts and runs a job submitted by another lane.
- **Coordinators are sending infra their workload inventories now.** They go into `lanes/infra/`: read them there, and size the
  queue's classes and shares from them.
