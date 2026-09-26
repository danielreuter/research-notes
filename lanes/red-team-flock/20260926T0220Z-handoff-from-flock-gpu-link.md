---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:18Z
---

# For review: Chunk(16), bf16-ampere at K = 8192 on the captured #101 set

- **What's new:** 16 chunks per VU (counters up to 15, 15 committed cross-chunk accumulators), with the Y region at chunk 15.
  The code is the same as my 01:59Z note.
- **Evidence:** run r20260926-020230-8db3, art:71e39af5. CPU and GPU selftests pass on the A100 at 8 and 64 VUs. The
  captured y words match the model chain for all 1,920 VUs.
