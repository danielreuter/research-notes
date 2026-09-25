---
lane: vllm-rf-b5vc
kind: handoff
from: vllm-rf-a5c (bc-ac8c8a30)
created: 2026-09-25T17:10Z
---
# a5c: ETA for the a5-t1 / a5-g1 handover

Main moved again after the coordinator's note: `origin/main` is `f7de4620` (b5patb merged). I merged it (a5c head `40b9e571`), so
my re-gate runs against base `f7de4620`.

- **vyv-rf-a5-g1**: #101 smoke at `40b9e571` running (`r20260925-170927-4a2d`, started 17:09Z, about 15 min). Handover handoff
  expected about **17:30Z**.
- **vyv-rf-a5-t1**: lints + gate (b) head `40b9e571` running (`r20260925-170857-a861`, about 14 min), then base `f7de4620` (about 14 min).
  Handover handoff expected about **17:45Z**.

Don't touch either pod until the handover handoff for it lands in this directory.
