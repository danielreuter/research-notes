---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-l40s-101 · kind: handoff · from: coordinator · created: 2026-09-26T12:40Z

# Idle pods: the H100 pair costs $6.98/h

Since 12:15Z the steward has seen these pods idle (GPU 0%, no work process):
- vy-flock-l40s-101-h100 and -h100-ver: $3.49/h each;
- vy-flock-l40s-101b and -ver: $1.09/h each.

Terminate any pod that has no queued run. Spend is still under the cap, with a projection of about $274 by 16:45Z, but
these two H100s are the largest single burn right now.
