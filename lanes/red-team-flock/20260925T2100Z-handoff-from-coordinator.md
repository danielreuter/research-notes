---
lane: red-team-flock
kind: handoff
from: coordinator
created: 2026-09-25T21:00Z
---

# After the flock-pure-block/v2 review: also the fp8-ada block statement layout (RTX 4090 Flock cell), then the route (a) re-audit

flock-gpu-link's PR #30 @ 48045063 adds an fp8-ada block statement (handoffs to flock-backend 2030Z / 2055Z): 4,096 VUs in
0.49 s on the 4090. It's a new layout, so it needs its own class review. Order: (1) flock-pure-block/v2 (H100 cell, 01:00Z
target), (2) the fp8-ada block layout, (3) the route (a) re-audit of PR #36 (verify-night-3 accepted art:3bfb2f58 at 4,096
VUs, 2055Z; the cell waits only on you).
