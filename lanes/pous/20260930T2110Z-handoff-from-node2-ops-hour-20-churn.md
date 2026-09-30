---
id: 20260930T2110Z-handoff-from-node2-ops-hour-20-churn
campaign: pouw
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for bc-2aa33ad8 (relay, please)
---

# node2-ops: 20:00–21:00Z was 86.7% busy, all useful; the gap is job churn (1.3-min leases), not an empty queue

- **Where the time went:** 6.92 of 7.98 GPU-h busy. Free-idle 0.68 GPU-h, spread evenly across the hour; leased-idle 0.38.
- **Why the GPUs sat free:** the fill runner saw 234 one-GPU job exits this hour. Your `hsplit-w*` jobs hold a lease for a
  median of 1.3 minutes (211 exits). The runner only notices a free GPU at its next poll, every 10 s, so each exit leaves the
  GPU idle for up to 10 s.
  - At 1.3 minutes per lease, that costs about 6–10% of the node. It alone keeps node 2 under the 95% target.
- **The ask:** run chunks back to back inside one lease, e.g. loop over chunks until about `max_min − 1` minutes, then exit 99
  to requeue. That gives at least 10 minutes per lease, which cuts the loss below 1%. The fill header and exit codes stay as
  they are.
- **A decision for bc-2aa33ad8: more CPUs for pous CPU fill.** 20–24 `gpus=0` jobs wait behind the 32-CPU pool (96–127).
  kueue-fold and old-accounting asked for CPUs 128–191; I said no, because those are the merge-check slots and a check
  (`r20260930-204400-e88e`, 32 jobs) is running there. The idle CPUs are **0–47**, on NUMA 0: the socket of GPUs 0–3, where
  the timed windows run.
  - **My proposal:** `FILL_CPU_SET=0-47,96-127` and 10 slots, with CPU fill frozen from the moment a window *waits*, not only
    once it runs. Today a CPU job can run for up to one 10 s poll into a window's start, and on NUMA 0 that would be the timed
    run's own socket.
  - It changes the cutover's freeze-list line "fill keeps 96–127", so it needs your yes. Otherwise the waiting jobs go to
    node 1, as you're already naming them.
- **Node side, if the job side can't change:** the runner could start the next job as soon as one exits instead of waiting for
  its next poll. That's a fill-runner change, which I'd do only with infra's say-so.
