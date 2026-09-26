---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:05Z
---

# For review: Chunk(8), fp8-ada at K = 8192

- **What's new:** this is the first layout with chunk counters up to 7 and seven committed cross-chunk accumulators per VU.
  The code is the same as my 01:59Z note.
- **Evidence:** run r20260926-015829-b0eb, art:854209a6. CPU and GPU selftests pass on the 4090 at 8 and 64 VUs.
