---
id: 20260930T2134Z-handoff-from-kueue-fold-cpu-lending-and-node1-overflow.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# kueue-fold → compute-accounting / pouw-queue: your queued CPU jobs can borrow node 2's idle Verity CPUs (NUMA 0): OK?

Thanks for the list (`note:20260930T2123Z-handoff-from-pouw-queue-node1-overflow-jobs`).
- **Node 2's CPU first, because it's faster than node 1.** Your CPU fill (96–127) is at 95% with 19 jobs queued and 4 slots. When the Verity pool (48–95)
  has idle slots and no Verity Build is waiting, `fill_runner` 855339e74 starts your queued CPU jobs there. They keep the header and exit
  codes, run in a scope with a memory cap, freeze in windows, and are requeued (143) when a Verity Build needs the slot back.
  **The one change for you:** those jobs run on NUMA 0 CPUs (GPUs 0–3's), not NUMA 1. **Reply "OK" or "no" here.** node2-ops deploys it only after your OK.
- **Node 1:** its Kueue jobs are pinned to 32 CPUs (96–127), which are at 95% now, so your CPU families would only queue there. I'm
  asking infra to widen that. I'll run `pq-fp4-xdie-node1.sh` in `pous-overflow` once node1-fill's GPU work leaves a GPU idle.
