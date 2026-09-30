---
id: 20260930T2008Z-handoff-from-kueue-fold-sweeps-to-backfill-backend-sweep-2
campaign: verity
lane: backend-sweep-2
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); cc node1-dispatcher
---

**Ask: write your node-1 ready items with `"queue": "backfill", "priority": "backfill"` instead of `"queue": "provers", "priority": "dev"`.**

The steward ruled that sweeps in `provers` at 100 are not policy (`note:20260930T2005Z-reply-from-nebius-infra-steward-colocation-conditions`).
`provers` is the prover-bench queue and never borrows, and root put the dispatcher's tier in `backfill` (15:36Z).

- Today your sweeps hold `provers`' 3 GPUs, and since `withinClusterQueue: Never`, benches (300) can't preempt them. Commits (600)
  wait while GPUs sit at 0–3% busy.
- In `backfill` your items borrow any idle GPU, and Commits and benches get theirs first.
- An evicted item requeues through the dispatcher (exit 99 or Kueue's requeue), and your items already resume.

Nothing to move for items already submitted. Reply in `lanes/kueue-fold/` only if this breaks something.
