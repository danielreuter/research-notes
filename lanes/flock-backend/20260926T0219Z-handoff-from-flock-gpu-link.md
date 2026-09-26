---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:18Z
---

# gemm_coordinate K = 8192 on the A100 (bf16-ampere), captured #101 set: layout Chunk(16). Selftests pass; all 1,920 VUs in 2.50–2.74 s

- **Layout:** `Chunk(16)`. A 16-bit K = 8192 row is 16 chunks and 512 units. Binary @ 758a8edf, SM = 80. Netlist e97ecb9e.
- **Inputs:** the captured set `gemm-coordinate-ampere-bf16-k8192`, art:927a4c3a. All 1,920 recorded y words equal the
  model chain's.
- **Evidence:** A100-SXM4-80GB, loopback verifier, run r20260926-020230-8db3, art:71e39af5 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m27) and 64 VUs (m30).
  - 512 VUs (m33): 0.80–0.91 s.
  - 1,024 VUs (m34): 1.45–1.50 s.
  - **All 1,920 VUs in one proof (m35): 2.50–2.74 s**, about 750 VU/s, or 12 k chunk-blocks/s.
  - That is the same cost per chunk as K = 2048: both sets are about 25–31 k blocks at m35.
- **Pod:** the A100 is terminated.
