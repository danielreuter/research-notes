---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:58Z
---

# fp4-nvf4 on the 5090, keyed-BLAKE3 rows (blake3-keyed/row-nvfp4/v1): layout Fp4. CPU and GPU selftests pass; 8,192 VUs in 0.30–0.32 s

- **Layout:** `Fp4`, block = VU, `k_log` 20.
  - Each role is ONE keyed-BLAKE3 chunk of 14 compressions: 13 full blocks, then a 32-byte final block with CHUNK_END |
    ROOT flags and message words 8–15 zero. Key, counter, block_len and flags are per-slot constants.
  - The root outputs are the row digests: verifier-known regions, with no chaining-value publics.
  - 24 units. Netlist fb52a87c.
- **Binary:** `cursor/flock-gpu-link-797a` @ 0bb25e8a, SM = 120. It fixes the device path for layouts without
  chaining-value publics; 7b3ba797's GPU run crashed there.
- **Inputs:** B-Ligero's synthetic NVFP4 set, as in my 02:54Z note, with blake3-keyed/row-nvfp4/v1 leaves.
- **Evidence:** RTX 5090 32 GB, loopback verifier, run r20260926-025307-9297, art:f1ee8a75 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m23) and 64 VUs (m26).
  - 2,048 VUs (m31): 0.12–0.13 s.
  - 4,096 VUs (m32): 0.18 s.
  - **8,192 VUs (m33): 0.30–0.32 s**, about 27 k VU/s.
- **Superseded run:** r20260926-024322-fab8 (7b3ba797) segfaulted in the GPU cases and is not evidence. Its CPU selftests
  passed.
- **Pod:** the 5090 is terminated. No flock-gpu-link pods are up.
