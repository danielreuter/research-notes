---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:19Z
---

# For review: Chunk(8), fp8-hopper at K = 8192

- **Code:** the same as my 01:59Z note, with the fp8-hopper netlist 904ca664 (granted).
- **Evidence:** run r20260926-021343-939d, art:29e1ccf1. CPU and GPU selftests pass on the H100 at 8 and 64 VUs.
