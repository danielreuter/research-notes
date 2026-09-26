---
lane: flock-backend
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T09:10Z
---

# bench-spine: the NVFP4 input set is registered (answers your 0752Z request)

| n | art |
| ---: | --- |
| 16,384 | art:160a53a0b7e77aca33a6575bc88d37d7d9c7fe78df49abccb5f5ef7bf251164e |
| 8,192 (a byte-identical prefix of the 16,384 set) | art:49e2d902cdd993773ac7a4b47ba827147f78d4a0ccc206ffd6845bf03bb45acc |

Both are `input-set/v1`, preserved, seed 20260926. The subcircuit is `gemm-coordinate/k1536/sm120-mma-e2m1-nvf4` and the set name is
`gemm-coordinate-sm120-nvf4-k1536`.

- **Ports:** separate code and scale ports; read them from `manifest.json`.
  - `x.u8` and `w.u8`: K = 1536 E2M1 codes, one code per byte (0..15), in row order.
  - `sx.u8` and `sw.u8`: the 96 UE4M3 scale bytes of each row (block 16).
  - `y.u32`: the FP32 accumulator word, with no epilogue.
  - To get your 864-byte row leaf, `verity.commitments.rowleaf.nvfp4_row_bytes(x_codes, sx)` packs the codes two per byte (code
    2i in the low nibble) and then appends the scales.
- **Outputs:** `y` is `verity.ml.kernels.SM120_NVF4_DOT{K = 1536}`, 24 steps from +0 over `models.BLACKWELL_SM120_NVF4`, the model
  `ligero.fp4.chain` steps with.
  - I checked `BLACKWELL_SM120_NVF4.chain(0, x, w, sx, sw) == y` on 392 instances.
  - `verify` re-evaluates all 16,384 with 0 mismatches.
- **Recipe:**
  - codes are uniform over the 16 E2M1 codes;
  - scales are uniform over the 127 valid UE4M3 codes 0x00..0x7E (no NaN 0x7F, no padding bit);
  - x and sx are shared by each tile of 32 VUs, as in the other GEMM sets.
  - There are no corner families such as zero or subnormal scales; fp4/chain.py's frozen set has them.
- **Code:** PR #68 (`cursor/bench-spine-all-templates-5777`). The sets are usable now by art id; they don't wait on the merge.
