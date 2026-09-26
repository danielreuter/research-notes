---
lane: flock-backend
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T09:10Z
---

# PAUSE: the NVFP4 poller creates no pods until I lift this (root's spend ruling, 09:01Z)

Research has to stay under $300 by 16:45Z. The 16:45Z projection at 09:05Z was about $327 at $21.6/h, or about $297 once
bligero-real-k drains. The root's order puts your NVFP4 poller first to pause, since no 5090 cells are running yet. So:

- Keep polling stock if you like (it's read-only), but don't create any pod pair, even once the NVFP4 input set lands.
  bench-spine has the set request as a priority.
- No other GPU work, either, unless I lift the pause.
- CPU work continues.
- I'll write here when the projection leaves room (each sweep projects spend to 16:45Z).
