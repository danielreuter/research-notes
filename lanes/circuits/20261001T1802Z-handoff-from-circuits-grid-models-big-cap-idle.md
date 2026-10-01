---
id: 20261001T1802Z-handoff-from-circuits-grid-models-big-cap-idle
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models (re note:20261001T1731Z-report-from-circuits-grid-models-counts-1030)
---

11:02 AM PDT: **gm-feed is sending nothing, and `big_cap` 8 is why.** All 177 eligible unsubmitted items are batch 8 or larger
(55 B8, 48 B16, 74 B32), and 11 batch-8+ items are already in Build or Commit. The CPU side has room: 5 Builds (472 GB) and 0
pending on `deployments-cpu`. Node 2 is running fill again.

**I recommend `big_cap` 14 now.** Builds hold no GPU, and release.py's MAX_BIG 4 still caps batch-8+ Commits on node 1. It
adds Builds that can end by 11:30 and keeps GPUs fed after it. The values from 10:02 (`builds_cap` 16, `build_mem_gb` 730)
stay as they are. I'll set it when you say yes. Otherwise the grid ends at about 230 by 11:30, and both together at about 425.

**Addendum (11:06 AM PDT):** `policy.json` changed at 10:25 AM PDT, and I only saw it now. Someone set `commit_cap` 4 and `big_cap`
4, so the throttle may be deliberate (goal 2?). If it was you, two things to know:
- `burst` (`["23:59", {"commit_cap": 14, …}]`) still applies all day and overrides `commit_cap` 4 with 14. Only `big_cap` 4 is
  in effect.
- Removing `burst` would put `commit_cap` 4, `per_tick` 6 and `cpu_pending_max` 4 in effect.

I've changed neither, and I'll do whichever you say.
