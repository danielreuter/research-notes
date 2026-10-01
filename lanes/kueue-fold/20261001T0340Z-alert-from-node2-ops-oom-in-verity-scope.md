---
id: 20261001T0340Z-alert-from-node2-ops-oom-in-verity-scope
campaign: verity
lane: kueue-fold
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# kueue-fold: three cgroup OOM kills inside `fill-verity-*` scopes on node 2 (7:18, 7:59 and 8:29 PM PDT), most likely `verity-build-cov-g080-r1`

- **The scopes:** `fill-verity-1790818768317`, `-1790821132606` and `-1790823571175`. The last ended `Failed with result 'oom-kill'`.
  None of the fill jobs failed.
- **The suspect:** `verity-build-cov-g080-r1` (Qwen3-30B-A3B) has run since 3:21 PM PDT, more than 5 hours, against the pool's
  256 GiB per-job `MemoryMax`.
- **Please check:** whether its Build retries a step that gets OOM-killed. If it needs more than 256 GiB, say so: the pool's total is
  1,024 GiB, and its job cap is a fill_runner setting.
- 9:00 PM PDT: a fourth OOM kill in a `fill-verity-*` scope (`vmstat oom_kill` 5 to 6). Same pattern.
