---
id: 20260930T2205Z-handoff-from-resource-steward
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: resource-steward (bc-b154b9ef-b9e0-560b-857b-56c2d5530ead), worker of the infra coordinator (bc-17cc41f1)
---

# resource-steward takes over node 1's disk reporting and owns disk, cache and RAM decisions on both nodes

Daniel ruled at 2:52 PM PDT that one agent keeps disk, RAM and other resources on both GPU nodes from being overwhelmed. The
policy is `note:20260930T2205Z-report-resource-steward` (`lanes/resource-steward/`).

What changes for the nebius-infra steward:
- **Node 1's disk reporting folds into the resource steward.** Its probe (`infra/nebius` `233f451f2`,
  `~/resource-steward/bin/resource_probe.py` on node 1) runs every 20 minutes. Its watermarks are: `/workspace` alert 80% and
  hold 85%; root free under 60 GB alert and under 45 GB no new checks; inodes 80%; RAM available under 10%; replay RAM to come
  over half of available RAM.
- If you see disk, RAM or inode pressure, please write an `*alert*` note to `lanes/resource-steward/`, and route the Grafana
  resource alerts there too if you can. The steward is woken by those notes.
- At node 1's `/workspace` 85%, the steward will ask kueue-fold, you and @circuits to hold new Builds and Commits.
- The check-cache move (`r20260930-213917-d6b3`, `~/.cache/verity-check` to `/workspace`) is still running. The steward
  leaves `lean-deps` and `circuit-check` to it, and only clears orphaned `lean-audit-scratch-*` (no open files, untouched for
  2 h). There is none at 2:55 PM PDT.
- Baseline at 2:55 PM PDT: node 1's `/workspace` is at 71% (1.58 TB free); `/workspace/jobs` has grown to 517 GB (from 398 GB
  at 2:27 PM PDT). Root has 155 GB free, RAM 73% available.
