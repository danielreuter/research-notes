---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:18Z
---

# gemm_coordinate K = 8192 on the H100, BF16 wgmma, captured #101 set: layout Chunk(16). Selftests pass; all 1,920 VUs in 1.35–1.38 s

- **Layout and binary:** `Chunk(16)` with netlist 12c3c8d3. Binary @ 93773ddc, SM = 90.
- **Inputs:** the captured x / w of `gemm-coordinate-ampere-bf16-k8192` (art:927a4c3a), rechained under
  HOPPER_BF16_WGMMA_K16. **3 of 1,920** final words differ from the Ampere-recorded y.
- **Evidence:** H100 80GB HBM3, loopback verifier, run r20260926-031235-2e85, art:e52774ac (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m27) and 64 VUs (m30).
  - 512 VUs (m33): 0.43 s.
  - 1,024 VUs (m34): 0.75 s.
  - **1,920 VUs in one proof (m35): 1.35–1.38 s**.
- **Tonight's real-K set is complete** on H100 FP8, H100 BF16 wgmma, 4090 FP8 and A100 BF16, plus fp4-nvf4 (both leaf
  schemes) on the 5090. All pods are terminated.
