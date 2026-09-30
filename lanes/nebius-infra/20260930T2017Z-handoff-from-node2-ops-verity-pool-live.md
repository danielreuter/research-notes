---
id: 20260930T2017Z-handoff-from-node2-ops-verity-pool-live
campaign: verity
lane: nebius-infra
kind: handoff
status: done
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for Verity lanes
---

# Node 2's Verity guest pool is live (20:08Z): `project=verity` fill jobs on CPUs 48–95, frozen in PoUW's timed windows

- **What you get:** 6 slots, at most 256 GiB per job and 1,024 GiB in total, `max_min` up to 360. Jobs start only while the disk
  is under 55% full and before 2026-10-07T12:00Z, and they're stopped at 13:00Z.
- **GPU guests (`gpus=1`):** they run only when no pous GPU job is ready. They're preempted first, and stopped in every window.
- **How to submit:** `note:20260930T2015Z-reply-from-node2-ops-verity-pool-live`.
- **Who to tell about problems:** node2-ops.
