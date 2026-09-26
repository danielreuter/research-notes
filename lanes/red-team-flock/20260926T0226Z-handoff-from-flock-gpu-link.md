---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:24Z
---

# For review: Chunk(2), fp8-hopper at K = 2048

- **Code:** the same as my 01:59Z note, with netlist 904ca664.
- **Evidence:** run r20260926-021842-f98b, art:511a98d2. CPU and GPU selftests pass on the H100 at 8 and 64 VUs.
- **Status:** this completes the six Chunk(n) layouts, all at @ 758a8edf. The runs are listed in my flock-backend notes
  from 01:58Z to 02:25Z.
