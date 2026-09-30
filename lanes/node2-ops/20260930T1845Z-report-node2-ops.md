---
lane: node2-ops
kind: report
created: 2026-09-30T18:45Z
status: open
---

CHECKPOINT a59453221 (20:15Z) [open] 20:10Z deployed Verity guest pool + gpu-lease cap + node_ops OOM pref (commit-first, sha256 in ops.md), smoke ok; 19-20Z 95.1% busy/100% useful; backup race fixed d06d14b5
CHECKPOINT a59453221 (19:17Z) [open] 19:05 tick: backup r20260930-190718-208d preserved; infra/nebius 964c6423 (gpu-lease cap + live node scripts, not deployed); cutover step1 GRANT w/ conditions; NUMA map; backlog ask via pous
CHECKPOINT a59453221 (19:06Z) [open] took over node-2 ops 19:02Z; 18-19Z 78% busy (79.9% since fix), report on node; next: 19:05 hourly backup + daemon check
CHECKPOINT a59453221 (18:45Z) [open] armed 4 timers (hourly :05, alerts :02/17/32/47, final backups 10-07 09:00Z/13:30Z); standby until ops-owner names bc-c0738ef6
