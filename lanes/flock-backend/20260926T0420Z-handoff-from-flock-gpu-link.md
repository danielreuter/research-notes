---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T04:19Z
---

# NV5 is up: cursor/flock-gpu-link-797a @ e84e3fe2, a fast-forward on your 20082dcb. Merge it for the one merge request

- **What changed:** admission now pins the y leaf per relation (`pure_block::y_leaf`).
  - Epilogue (BF16) relations: `u16` over 2 bytes, with every y < 2^16.
  - fp8 and fp4: `u32` over 4 bytes.
  - It checks after NV2 / NV3 and before NV1. A mismatch exits 2 with `REFUSED NV5`.
- **Your writers:** they already emit exactly these leaves (`word_schema(y_bits)`, and write_fp4's u32), so no honest
  file changes, and every statement digest is unchanged.
- **Selftest output:** every run now prints `y_leaf_other_width` (NV5), and BF16 runs also print
  `y_word_exceeds_u16_leaf`. That makes one or two more NEG lines than at 45fdab2d.
- **Checked:** CPU selftests pass on Fp4, ShaFp4, Chunk(3) (bf16-hopper and bf16-ampere), Fp8, ShaFp8, ShaBf16, Chunk(8)
  and Chunk(4) wgmma. The GPU build compiles.
