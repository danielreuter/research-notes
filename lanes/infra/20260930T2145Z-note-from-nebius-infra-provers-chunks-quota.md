---
id: 20260930T2145Z-note-from-nebius-infra-provers-chunks-quota
campaign: one-pool
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for node1-fill and kueue-fold
---

# @node1-fill @kueue-fold: `provers` chunks 5,000 and 7,500 wait on quota, not on a stale reservation (2:45 PM PDT)

This adds to `note:20260930T2140Z-handoff-from-infra-why-gpus-247-idle`, which covers who holds the reserved but idle GPUs.
- **Cause: `provers`' 3 GPUs (borrowingLimit 0, Daniel's ruling) were all held by `backend-sweep-2`'s own jobs.**
  - Whole-row chunks 0 and 2,500 have held two of them since 2:06 PM PDT, at 6–13% GPU utilization over the last 20 minutes.
  - `pc262` held the third (GPU 7, in its host phase) from 2:26 to 2:41 PM PDT.
  - Nothing is wrong in Kueue itself: the node selector (`verity.dev/server=vy-nebius-1`), the flavor `vy-nebius-1` and every
    reservation match the live pods.
- **Chunk 5,000 was admitted at 2:41:36 PM PDT, and its pod starts at 2:46:36 PM PDT.**
  - When `pc262` ended, `deployments-gpu` borrowed the freed GPU for Commit `da1e0354a7`. It may borrow up to 2 GPUs.
  - One second later, `provers` reclaimed the GPU (`InCohortReclamation`).
  - The evicted Commit then held the GPU for its full 300 s termination grace, because its PID 1 doesn't exit on SIGTERM.
- **Chunk 7,500 waits for chunk 0, 2,500 or 5,000 to finish.** The feeder writes nothing while it has a pending job, so the
  sampled-unit proves wait too.
- **Options.** These are policy calls, not mine to make. I apply quota changes in minutes on your word.
  1. Move a GPU from `deployments-gpu`'s 5 to `provers` (making it 4 and 4), or let `provers` borrow. Either costs the Commit queue,
     which has 29 jobs waiting.
  2. Set `deployments-gpu`'s GPU `borrowingLimit` to 0. A freed `provers` GPU then goes straight to `provers`' pending job, without
     the borrow, reclaim and 5-minute grace. The cost is that Commits can't use `provers`' GPUs while `provers` is idle.
  3. For the research coordinator: have the feeder gate on its own pending chunks, not on any pending job in `provers`, so the
     sampled-unit proves keep flowing.
