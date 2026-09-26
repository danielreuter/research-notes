---
lane: bench-spine
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T07:52Z
---

# Request: an NVFP4 input set for the two 5090 Flock cells (Fp4 / ShaFp4), so they don't run on backend-generated inputs

Overnight goal 5 asks for the two NVFP4 cells (flock-pure-block v2 layouts Fp4 and ShaFp4, sm120 `mma … e2m1` with ue4m3
block scales, K = 1536, 24 units of 64 codes + 4 scales per operand row). The store has no NVFP4 input set, and I'm told not
to generate my own. Could you register one?
- **Shape:** each VU is one x row and one W row of K = 1536 E2M1 codes (4-bit), with 96 scale bytes each, at block size 16.
  Output y is the FP32 accumulator word after 24 chained `tc_dot` steps (`verity.ml.tc`: the NVFP4 sm120 model that
  `ligero.fp4.chain` uses).
- **Ports I can read:** anything the manifest declares.
  - Preferred: `x.u8` / `w.u8`, holding 768 code bytes then 96 scale bytes per row. That is the `rowleaf.nvfp4_row_bytes`
    layout, 864 bytes, which the Fp4 / ShaFp4 row leaves hash.
  - Also fine: separate code and scale ports, plus `y.u32`.
- **Size:** 16,384 VUs covers the cells. The CN2 limits are Fp4 ≤ 32,768 VUs per proof and ShaFp4 ≤ 16,384, and on the 5090
  ShaFp4 binds at m33 (4,096 per proof).
- **Please send** the art id(s) to lanes/flock-backend. I'll extend `write_set` to your port layout and run the cells the
  moment an RTX 5090 pair is in stock.
