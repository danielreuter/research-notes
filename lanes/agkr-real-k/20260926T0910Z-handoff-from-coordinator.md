---
lane: agkr-real-k
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T09:10Z
---

# PAUSE: GPU cell runs stop now; code work continues on CPU (root's spend ruling, 09:01Z)

Research has to stay under $300 by 16:45Z. The 16:45Z projection at 09:05Z was about $297 even after bligero-real-k drains,
so the root's order pauses your cell runs next. Your two pods, `vy-agkr-real-k-a100` and `vy-agkr-real-k-ver`, cost $3.18/h,
and pausing them brings the projection to about $272.

- Let any run already in flight finish and reach custody. Then drain and terminate both pods
  (`research pods drain` / `terminate --require-preserved`), and checkpoint which runs completed.
- Don't create new GPU pods until I lift this.
- CPU work continues: code, tests, local checks.
- I'll write here when the projection leaves room (each sweep projects spend to 16:45Z).
