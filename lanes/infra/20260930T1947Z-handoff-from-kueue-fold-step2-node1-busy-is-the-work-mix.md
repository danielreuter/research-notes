---
id: 20260930T1947Z-handoff-from-kueue-fold-step2-node1-busy-is-the-work-mix
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# kueue-fold step 2: `pous-overflow` is live on `backfill`, but no quota change can lift node 1 above 1% GPU busy. Every GPU holder there is CPU-bound, and the lever is the work mix

- **Measured:** 1.0% over the last hour (DCGM).
- **Why quota doesn't help:** all 8 GPUs are reserved, and `backfill` already borrows whatever isn't. The holders are:
  - Commits running their CPU replay, at 0–5% each;
  - backend-sweep-2's `prover-bench` jobs in `provers`, at about 2%;
  - the circuits TP2 pod, at 10%.
- **Priority inversion:** 2 Commits (priority 600) wait behind those sweeps (priority 100), because nominal quota can't be reclaimed.
- **Co-location works** on node 1: a 0-GPU pod with `NVIDIA_VISIBLE_DEVICES=all` can target a GPU. I haven't built the daemon, because
  the pool has almost no GPU-heavy untimed work to put there.
- **What raises node 1's busy:**
  1. the deferred replay (PR A/B) plus more Commits, fed by Builds on node 2 (step 3, ready and waiting on node2-ops' pool deploy);
  2. sweeps that are GPU-bound, or sweeps moved to `backfill` at priority 10.

Details: `note:20260930T1935Z-report-kueue-fold`.
