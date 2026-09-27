---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T01:00Z

# An addition to the 00:20Z handoff: the guarded-max label too

PR #95 (the guarded-max tap, opt-in `GUARDED_MAX_TAP`) is approved and waiting to merge. In the same follow-up PR, set
`_STREAM["GuardNegInfZero_v1"]` / `committed_today` to "ROW word 3 (`GUARDED_MAX_TAP=1`)", or keep it as a new tap
whose `new_tap_in` names that flag, whichever matches how the table treats opt-in taps (norm scales, router softmax).
Say which in the handoff.

In the plan doc, the guarded-max column's note becomes "built (#95, opt-in)". Stack on #95 if it hasn't merged when you
open the PR.
