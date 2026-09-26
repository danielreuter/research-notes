---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:19Z
---

# gemm_coordinate K = 8192 on the H100 (fp8-hopper): layout Chunk(8). Selftests pass; 1,920 VUs in 0.65 s

- **Layout:** `Chunk(8)`. Binary @ 758a8edf, SM = 90. Netlist 904ca664.
- **Inputs:** synthetic E4M3, 8,192 words per operand, drawn with `rng([seed, i])`. The batch is sized to the captured
  K = 8192 set (1,920 VUs).
- **Evidence:** H100 80GB HBM3, loopback verifier, run r20260926-021343-939d, art:29e1ccf1 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m26) and 64 VUs (m29).
  - 512 VUs (m32): 0.21 s.
  - 1,024 VUs (m33): 0.35 s.
  - **1,920 VUs in one proof (m34): 0.65 s**, about 2.96 k VU/s. The two reps prove in 0.40 s and 0.23 s.
