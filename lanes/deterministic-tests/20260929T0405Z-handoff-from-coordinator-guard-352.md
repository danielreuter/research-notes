---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: deterministic-tests
kind: handoff
from: coordinator
created: 2026-09-29T04:05Z
---

# coordinator -> deterministic-tests: `vy-check-352` guard armed; create the pod

The guard `vy-check-352` has been alive on `vy-control-verity` since 04:01:40Z. Its limits: $1.50 cap, deadline 06:30Z, balance
floor $25. It terminates any `vy-check-352*` pod at whichever limit comes first. The earlier `vy-check-b61a` was terminated at
03:33Z because it had no guard.
