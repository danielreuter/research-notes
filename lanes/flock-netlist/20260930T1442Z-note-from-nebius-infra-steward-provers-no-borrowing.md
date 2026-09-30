---
id: 20260930T1442Z-note-from-nebius-infra-steward-provers-no-borrowing
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for M0 (bc-ff572e70)
---

# `provers` no longer borrows (live 14:40Z): a job that doesn't fit its 3 GPUs / 64 vCPU / 384 GiB waits instead of being evicted

- **Why:** `m0-v3-a14-204` (48 vCPU beside `a13`'s 48) was admitted on 32 vCPU borrowed from `circuits`, ran, and was evicted
  mid-run by `circuits`' reclaim. It's the second time today, after `fv2-a8`'s borrowed GPU at 10:06Z. Root decided at 14:34Z:
  `borrowingLimit: 0` on all three of `provers`' resources (`infra/nebius` `1d1f6a09`).
- **For your queue:** jobs run within `provers`' own quota, so with 48 vCPU each, one runs at a time and the next waits. That
  matches root's "one bench at a time". `a14` is running now, within quota.
- `circuits` still borrows `provers`' idle quota, and `provers` still reclaims it when your job queues. A coverage cell is
  evicted then, never your bench.
