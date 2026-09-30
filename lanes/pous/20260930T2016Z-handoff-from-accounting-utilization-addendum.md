---
id: 20260930T2016Z-handoff-from-accounting-utilization-addendum
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# @old-accounting: add two utilization sections to the 21:00Z handoff (Daniel's 20:13Z priority 1)

This is an addendum to `note:20260930T2000Z-handoff-from-accounting-state-for-successor`, for your handoff worker bc-5ce2ff3f.
Daniel's first priority is using both servers optimally, on @infra's one pool and one central queue. The old agents know what
failed, so please add two sections to the same reply in `lanes/accounting/`. They can be a table each.

1. **Utilization failures in the last 48 hours**, on node 2, node 1 or pods. For each, give:
   - what happened and when;
   - the cause: a queue running dry, leased-idle, a timed window's wait, a failed job, a node fault, an agent stall, and so on;
   - the GPU-hours lost, roughly;
   - whether it's fixed, and by what (a commit, a rule, a runner change);
   - what would have prevented it.

   Include the ones node2-ops already logged: the `fp8chain-die*` jobs holding leases idle, and the rc-4 failures on GPU 5.
2. **The PoUW workloads that run on the nodes.** For each, give:
   - what it is: the timed window, kernel fill, capture, attacker, census, verify, MVP serving, evals, and so on;
   - the node and GPU class, and how many GPUs or CPUs;
   - how long one run takes and how often it runs;
   - whether it's timed (needs the node quiet) or preemptible;
   - how it's launched today: `gpu-lease`, the fill queue, `research run` or ssh;
   - the owner agent.

   @infra takes this inventory from me to move PoUW onto its central queue.
