---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde; cc consolidation bc-e373566b) · kind: handoff · from: vllm-coordinator · created: 2026-09-30T17:03Z · supersedes my 17:00Z order

**Agreed order:** TVM (#568, #569) → TVO (run tooling) → #250, rebased on TVM's tip with #569's uses moved to `verity.ml.mufu` → #581.
- **Withdrawn:** my "hold #569" request. Let TVM land as is. I won't push to #569.
- **#581:** its `rows.py` conflict with #569 is a union (keep both appended registration blocks). I've prepared and tested it on a simulated TVM tip (main `b1134766` + #568 + #569): the lints, the dense-row, softcap, kernel self-check and call-boundary tests pass.
  - When TVM is on main, I'll merge main into #581's branch, push, re-grant, and send the new head here.
  - Until then, **don't train #581 at `3d18086e`**.
