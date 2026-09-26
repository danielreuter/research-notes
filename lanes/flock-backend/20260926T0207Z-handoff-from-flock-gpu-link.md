---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:05Z
---

# gemm_coordinate K = 8192 on the 4090 (fp8-ada): layout Chunk(8). Selftests pass; 1,024 VUs in 0.42–0.43 s

- **Layout:** `Chunk(8)`. An 8-bit K = 8192 row is 8 chunks and 256 units. Binary @ 758a8edf, SM = 89. Netlist e66262a0.
- **Inputs:** synthetic E4M3, 8,192 words per operand, drawn with `rng([seed, i])` (`inst_k.py synth fp8-ada 8192`).
- **Evidence:** RTX 4090, loopback verifier, run r20260926-015829-b0eb, art:854209a6 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m26) and 64 VUs (m29).
  - 512 VUs (m32): 0.23–0.26 s.
  - **1,024 VUs (m33): 0.42–0.43 s**, about 2.4 k VU/s. This is the most that fits in 24 GB.
  - That is the same block count, and so the same prove time, as K = 2048 at 4,096 VUs. The cost is per chunk.
- **For the cell:** the captured K = 8192 batch is 1,920 VUs, so two sub-batches on the 4090.
- **Pod:** the 4090 is terminated.
