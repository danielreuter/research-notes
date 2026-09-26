---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:13Z
---

# Chunk(4) with the bf16-hopper-wgmma netlist (12c3c8d3) on the H100, captured K = 2048 set

- **Code:** the same as my 01:59Z / 02:05Z notes. The netlist rows are bf16-hopper's; only the relation name in its header
  differs.
- **Evidence:** run r20260926-030801-4edb, art:8b8f7378. CPU and GPU selftests pass at 8 and 64 VUs.
