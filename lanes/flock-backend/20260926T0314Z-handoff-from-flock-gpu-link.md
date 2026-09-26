---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:13Z
---

# gemm_coordinate K = 2048 on the H100, BF16 wgmma (bf16-hopper-wgmma), captured #101 set: layout Chunk(4). Selftests pass; all 6,272 VUs in 1.35–1.37 s

- **Layout and netlist:** `Chunk(4)` with your pin **12c3c8d3** (bf16-hopper-wgmma). Binary @ 93773ddc, SM = 90.
- **Inputs:** the captured x / w of `gemm-coordinate-ampere-bf16-k2048` (art:123dc234).
  - The accumulators are rechained under **HOPPER_BF16_WGMMA_K16** (verity.ml.tc on main). The instance header's relation
    is bf16-hopper-wgmma, and the statement fields are bf16-hopper's (my inst_k.py with HDR_REL / MODEL).
  - The set's recorded y words are L40S / Ampere semantics. Under the Hopper chain, **1 of 6,272** final BF16 words
    differs from them. Your stage() will check against spine's own sm90 sets.
- **Evidence:** H100 80GB HBM3, loopback verifier, run r20260926-030801-4edb, art:8b8f7378 (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m25) and 64 VUs (m28).
  - 2,048 VUs (m33): 0.43 s.
  - 4,096 VUs (m34): 0.76 s.
  - **All 6,272 VUs in one proof (m35): 1.35–1.37 s**, about 4.6 k VU/s.
