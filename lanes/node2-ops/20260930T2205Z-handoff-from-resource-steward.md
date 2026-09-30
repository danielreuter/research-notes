---
id: 20260930T2205Z-handoff-from-resource-steward
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: resource-steward (bc-b154b9ef-b9e0-560b-857b-56c2d5530ead), worker of the infra coordinator (bc-17cc41f1)
---

# resource-steward now owns disk, cache and RAM decisions on node 2; you keep the OOM guard and the job-start disk stop

Daniel ruled at 2:52 PM PDT that one agent keeps disk, RAM and other resources on both GPU nodes from being overwhelmed. The
policy is `note:20260930T2205Z-report-resource-steward` (`lanes/resource-steward/`).

What changes for node2-ops:
- **You keep enforcement:** the OOM guard in `node_ops.py`, the fill runner's 55% job-start stop, and `node_ops.py`'s 60% disk
  alert. The steward only verifies that they're working.
- **Disk and cleanup decisions come to the steward:** what to delete or move, cache trimming, and when to ask an owner. If
  you see disk, RAM or inode pressure, please write an `*alert*` note to `lanes/resource-steward/` (or have `alerts.jsonl`'s
  relay do it), in addition to anything you already send. The steward is woken by those notes, and by a 20-minute timer.
- The steward's probe (`infra/nebius` `233f451f2`, `~/resource-steward/bin/resource_probe.py` on node 2) is read-only. It never
  touches NVML, and it doesn't run while `fill/status.txt` says `timed True`.
- Job norms (idle-in-lease, unleased GPUs, the top-3 wasters) stay with you.

One item that needs you now. Node 2 has 13 finished runs older than 1 h without `.custody`, `.fetched` or `preserved.json`,
over the steward's threshold of 10:
- Your stalled backups: `r20260930-081105-b32f` (17 GB), `r20260930-091913-2c58` (17 GB) and `r20260930-102051-0e13` (3.9 GB),
  which the 60 MiB chunked backups superseded from 10:27Z.
- Ten small runs with no lane set (`true`, `sha256sum` and `bash`; 104 KB to 1.2 MB): `r20260930-143454-b1fe`, `-143525-16e4`,
  `-144424-18a4`, `-145634-28e5`, `-145903-8de6`, `-154844-9f93`, `-155050-ea92`, `-182541-cc16`, `-183127-1bb0` and
  `-185538-212f`.

Could you publish them, or say whose they are and whether they're superseded? The steward deletes nothing without custody,
and nothing in `research/runs` without its owner's yes.
