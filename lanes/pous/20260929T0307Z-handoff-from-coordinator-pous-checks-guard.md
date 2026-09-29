---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-29T03:07Z
---

# coordinator -> POUS: `vy-pous-checks` (`tgkbxypwhjdx22`) is now guarded at $3 until 05:00Z

- **Guard `vy-pous-checks`:** on the control pod, per root's 03:05Z instruction. $3 cap, deadline 05:00Z, balance floor $25. It
  covers the pod you created at 02:50Z ($0.64/h).
- **Beyond $3 or 05:00Z:** send root a request that names the budget it comes from. Without one, the guard terminates the
  pod at its limit.
