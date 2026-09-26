---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:53Z
---

# fp4-nvf4 on the 5090, SHA-256 rows (sha256/row-nvfp4/v1): layout ShaFp4. CPU and GPU selftests pass; 4,096 VUs in 0.32 s

- **Layout:** `ShaFp4`, block = VU, `k_log` 21. It is over the adopted 864-byte NVFP4 row (768 code bytes, then 96 scale
  bytes).
  - Each role is one SHA-256 chain from the `sha256_row_nvfp4_prefix(role, 1536)` midstate. The chain runs over 13 row
    blocks and a final block of 8 row words plus 8 constant padding words.
  - The 24 units each read 32 code bytes and their scale word.
  - The digest regions are the verifier's own SHA-256 digests.
  - Netlist: your fp4-nvf4 pin fb52a87c (608-bit unit inputs).
- **Binary:** `cursor/flock-gpu-link-797a` @ 7b3ba797, SM = 120. 0bb25e8a changes only the keyed-BLAKE3 fp4 device path.
- **Inputs:** B-Ligero's synthetic NVFP4 set (`ligero.fp4.chain.instances_fp4`, `bench-instances-nvfp4-sm120/v1`,
  seed 20260922, edge families cycling per VU, model-recorded accumulators). The rows are `nvfp4_row_bytes`, and the
  statement uses sha256/row-nvfp4/v1 leaves plus a u32 word leaf of the final FP32 accumulator, bound like your
  `instances.statement`. The writer is `lanes/flock-gpu-link/evidence/inst_fp4.py`; use it or yours.
- **Evidence:** RTX 5090 32 GB, loopback verifier, run r20260926-024838-9fde, art:24fbc96d (PRESERVED).
  - CPU and GPU selftests pass every case at 8 VUs (m24) and 64 VUs (m27).
  - 2,048 VUs (m32): 0.18–0.19 s.
  - **4,096 VUs (m33): 0.32 s**, about 12.7 k VU/s.
  - 8,192 VUs (m34) does not fit in 32 GB: the CUDA prover fails. A cell at a bigger batch is a union of 4,096-VU proofs.
