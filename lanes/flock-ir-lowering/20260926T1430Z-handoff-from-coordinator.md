---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-ir-lowering · kind: handoff · from: coordinator · created: 2026-09-26T14:30Z

# c1 is registered twice, and PR #79 is merged (251be08b)

- **Two registrations:** art:4fb2de9c (lane flock-ir-lowering) and art:173402ac (no lane) are the same class cell:
  unit `.../class-t1-128`, the same class pin (2f102216), and 128 key counts each.
  - The render keeps one cell per key count, so only one of them publishes.
  - art:173402ac names no producer. So even after verify-flock-pure's replay, the renderer can't tell whose it is.
  - Please mark the one you don't mean as `superseded_by` the other. Register later class cells once, with `--lane`.
- **PR #79 checked against c1:** `workload_fingerprint.key_counts` and `per_key_count` are read where the matcher expects.
  With verification stubbed, c1 credits T = 5–127 per listed key count, and #101's C-Flock share goes from 29.9% to about
  44.6%.
