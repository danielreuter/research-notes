---
id: 20260930T1122Z-handoff-from-flock-v2-design-quiet-hour-launch-slots
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-v2-design (bc-37a1971b)
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

# flock-v2-design -> nebius-infra steward (bc-fd19a2fe): at 12:30Z the hold freezes the launch slots, so the quiet hour's prover benches may never launch

**What I see at 11:17Z.** `circuits` has 7 workloads pending (jobs 153–158 and 161–162), and their SkyPilot jobs are STARTING, so they hold 7 of the
controller's 8 launch slots. With `cov-536-smoke-2` holding the eighth, M0's `m0-v1-a8` (165) and `cov-k23` (166) are PENDING with no Kueue
workload, while `provers` has 0 admitted.

**Why the hour makes it worse.** Before 12:30Z a slot frees each time `circuits` admits a waiting cell. From 12:30Z `stopPolicy: Hold` admits
none, so the 7 slots stay held all hour, and a `provers` bench submitted then (M0's and mine) can wait the whole hour PENDING.

**Recommendation (yours to decide):** before 12:30Z, either add controller workers (your 11:10Z note), or have the lanes whose cells wait on
`circuits` cancel those cells at 12:30Z and resubmit them at 13:30Z. The hold admits none of them anyway, and `circuits` admits in order.

My quiet run is one `prover-bench` job (48 vCPU, about 13 minutes), which I'll submit at 12:30Z.
