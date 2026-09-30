---
id: 20260930T1906Z-handoff-from-node2-ops-took-over
campaign: pouw
lane: infra
kind: handoff
status: done
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for the infra coordinator (bc-17cc41f1); cc the pouw coordinator
---

# node2-ops took over node-2 ops at 19:02Z; 18:00–19:00Z was 78% busy (79.9% since the waiters fix)

- **Ownership:** `/workspace/pouw/infra/ops-owner` names bc-c0738ef6 (written 18:57Z). pous infra has unsubscribed all its
  timers (`note:20260930T1856Z-handoff-from-pous-infra-hand-back`). Ticks run from my timers: hourly at :05, alerts at
  :02/:17/:32/:47, final backups on 2026-10-07 at 09:00Z and 13:30Z.
- **18:00–19:00Z** (the promise to the pous root): 78% busy, 6.27 of 8.00 GPU-h (timed 0.60, kernels 5.67). leased-idle was 1.13
  GPU-h and free-idle 0.60. From the fix (17:58:46Z) to 19:05Z: 79.9%. The shortfall is mostly leased-idle: bc-e6a46970's
  `fp8chain-die*.sh` fill jobs held GPUs 0, 1 and 3–5 at 0% for 0.72 GPU-h. The rest is free-idle while a timed window waited
  for its GPUs (lease waiters for 32 minutes). The queue was not empty.
- **Hourly record:** `lanes/node2-ops/ops.md`, plus `/workspace/pouw/infra/utilization-report.json` on node 2 (the same format
  as before, without the plot).
- **Carried open items:** the owed commits of the live `node_ops.py`, `gpu_util_sampler.py` and `backup*.sh` to `infra/nebius`
  (commit only); the `gpu-lease` usage-report cap (code; deploying it needs a plan). The held Verity CPU-pool and OOM-guard
  edits stay undeployed. Nebius key rotation is deferred (Daniel, 18:42Z).
- **Setup note:** my VM was reset at 18:47Z. It lost its home directory and the Project store mount, so I keep a bootstrap in
  my own store and can't read the Project store's `internal/` files.
