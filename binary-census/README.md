---
cursor:
  subagentId: "bc-5e26cfdd-9228-573c-9503-eb06c6be897c"
---

# Binary-field census scripts (evidence for docs/binary-backend-census.md and docs/flock-link-protocol.md)

CPU-only, Python 3.12, no dependencies beyond the repo's stdlib-only `verity.ml.tc` (imported read-only from `/workspace/packages/verity/src`). Nothing here touches the repo.

| file | what it does |
| --- | --- |
| `gf2.py` | GF(2) R1CS builder in Flock's model: wires are XOR forms over committed bits, every non-trivial AND is one committed bit (row); live-cone counting; bit-sliced evaluation; adders, carry-save trees, multipliers, barrel shifters, leading-zero count |
| `unit.py` | the exact circuit of one tensor-core transition unit (`GroupSum.step`) for BF16 and E4M3 pipelines, plus the `f32_to_bf16` epilogue |
| `test_unit.py` | random + cancellation cases against `pipeline.step`, non-finite negatives, counts; `python3 test_unit.py ampere_bf16 hopper_bf16 ada_e4m3 hopper_e4m3` |
| `test_more.py` | targeted families (realistic, exact cancellation, subnormal results, floor region, near overflow, big accumulator, zeros), the 24 captured K=1536 VUs chained through 96 steps, and the frozen `vu-k1536-neg` set |
| `pad_rank.py` | simulated redraw rates of the link's zero-knowledge pad over GF(2^128) (GHASH polynomial) |

Results at the time of writing (Fri Sep 25, 2026):

| pipeline | ANDs per unit | committed bits (inputs + ANDs + 32 output copies) | tests |
| --- | --- | --- | --- |
| Ampere BF16 (FIRST) | 7,100 | 7,676 | 3,000 random (1,210 saturating) + 3,500 targeted: 0 mismatches; 24 real VUs x 96 steps: 0 mismatches, all 24 hardware words reproduced; negatives 64/64 and frozen set 8/8 reject, 44/44 correct word |
| Hopper BF16 | 6,718 | 7,294 | 3,000 random + 3,500 targeted: 0 mismatches; negatives 64/64 |
| Ada FP8 E4M3 | 6,744 | 7,320 | 3,000 random: 0 mismatches; negatives 64/64 |
| Hopper FP8 E4M3 | 6,374 | 6,950 | 3,000 random: 0 mismatches; negatives 64/64 |
| epilogue (RNE f32 to bf16) | 31 | 79 | exercised by the real-VU chain test |

`pad_rank.py 200`: redraws per 200 draws: one point with 128 / 256 / 512 pad bits: 143 / 0 / 0; two points with 256 pad bits: 151; two points with 512 pad bits (one 2^9 sub-cube, or two 2^8 sub-cubes): 0 and 0.
