---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:24Z
---

# gemm_coordinate K = 2048 on the H100 (fp8-hopper): layout Chunk(2). Selftests pass; all 6,272 VUs in 0.64 s

- **Layout:** `Chunk(2)`. Binary @ 758a8edf, SM = 90. Netlist 904ca664.
- **Inputs:** synthetic E4M3, 2,048 words per operand, drawn with `rng([seed, i])`. The batch is sized to the captured
  K = 2048 set (6,272 VUs).
- **Evidence:** H100 80GB HBM3, loopback verifier, run r20260926-021842-f98b, art:511a98d2 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m24) and 64 VUs (m27).
  - 2,048 VUs (m32): 0.21 s.
  - 4,096 VUs (m33): 0.35–0.36 s (11.6 k VU/s).
  - **All 6,272 VUs in one proof (m34): 0.64 s**, about 9.75 k VU/s.
- **Superseded run:** r20260926-014840-95cf was launched before its netlist was in the inputs and never proved anything.
  I killed it and labelled it outcome=failed.
- **Summary of the six layouts landed tonight:** fp8-ada K = 2048 / 8192 (4090), bf16-ampere K = 2048 / 8192 (A100,
  captured), and fp8-hopper K = 8192 / 2048 (H100). All pods are terminated.
- **Next:** H100 BF16 wgmma, once wgmma-bf16's semantics land and you pin a lowering for them. It is `Chunk(4)` /
  `Chunk(16)` again, with the captured x / w and the accumulators recomputed under the wgmma model. NVFP4 waits on its
  frame-v3 row spec.
