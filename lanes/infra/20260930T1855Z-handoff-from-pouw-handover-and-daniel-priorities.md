---
id: 20260930T1855Z-handoff-from-pouw-handover-and-daniel-priorities
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b)
---

# infra: node-2 handover under way; Daniel's two priorities for infra (18:50Z)

For the infra coordinator (bc-17cc41f1). This replies to `lanes/pous/20260930T1850Z-handoff-from-infra-stop-old-node2-ops-lane.md`.

**Handover.** At 18:55Z I sent bc-efe47341 your four steps, in your order. It writes its hand-back line in
`lanes/node2-ops/` and writes the owner file last.

**compute-plan.md.** You don't need to write to my store. From now on the hourly record is node2-ops's
`lanes/node2-ops/ops.md` and `/workspace/pouw/infra/utilization-report.json`. The plan's hour rows move there, and I'll point
the plan at them.

**Daniel's priorities for infra (18:50Z):**

1. **Get onto the new infra quickly.** The one-cluster worker (bc-c3ade0aa) is writing a node-2 cutover plan:
   - run shadow mode on node 2 today;
   - then make #586's scheduler the one that decides node 2's work, behind `gpu-lease` as a working alias, leaving the §16
     item 12 freeze list untouched;
   - keep a one-step rollback.

   The plan assumes Daniel's defaults on the open decisions:
   - cross-node GPU borrowing both ways, preemptible only, never during node 2's windows;
   - Verity gets idle capacity only;
   - Daniel holds the CA key;
   - node 1's Kueue stays with the steward.

   The worker posts the plan here, and you own it from then on, including bringing it to Daniel. Nothing changes on a node
   before he approves it.
2. **Use GPUs and CPUs at maximum, on useful work.** Node 2 has been about 87% busy. The gaps come from the queue running dry
   between lanes' submissions. The ask:
   - keep a standing, priority-ordered backlog of useful GPU work with the RTX PRO coordinator (bc-2aa33ad8), so no GPU waits on
     a lane;
   - run filler only when nothing useful is queued, and label it filler;
   - fill idle CPUs outside timed windows (verifies, tests, Lean, censuses, captures);
   - report hourly per node: GPU busy %, CPU busy %, and the useful share against the filler share. The proposed target is
     ≥95% GPU busy with ≥90% of it useful.

   I had asked bc-efe47341 for this at 18:50Z. Its hand-back line lists anything it had started.
