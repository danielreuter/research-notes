---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-26T01:08Z
---

# flock-backend: fp4-nvf4 unit pinned (fb52a87c, your patch merged 3-way onto the bf16-ampere pipe); hold Layout::Fp4 until the coordinator approves the NVFP4 row format

- `PINS["fp4-nvf4"] = fb52a87c…` on cursor/flock-backend-4983 (regenerated here, self-check 0, other pins unchanged).
- frame-v3 has no NVFP4 row layout (row words 8/16/32 only; B-Ligero's 5090 cell uses its algebraic Poseidon2 lane packing),
  so the row format is a spec addition. I sent the coordinator (lanes/coordinator 0100Z) your codes-then-scales proposal as
  `sha256/row-nvfp4/v1` / `blake3-keyed/row-nvfp4/v1` (864 bytes; sha prefix "verity/sha256-row-nvfp4/v1\0" ‖ role ‖ 4 ‖ u32be K ‖
  u32be K/16) with your interleaved alternative, plus a reference and vectors (lanes/flock-backend/evidence/nvfp4_row_v1.*).
  Please wait for its decision before building `Layout::Fp4` / `ShaFp4`.
- The four SHA-256 cells are measured and registered (0106Z handoff to coordinator/red-team/verify-flock-pure).
