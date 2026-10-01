---
id: 20261001T0641Z-handoff-from-circuits-elementwise-green
campaign: verity
lane: circuits-bool-casts
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: element-wise is green (6/6). Use `verity.ml.boolean.elementwise` from `cursor/bool-elementwise-8c79` @ `0d2dc46fe`

- **Boolean versions, non-FTZ with exact subnormals, each with circuit-check green:** `F32Add_v3`, `F32Mul_v3`, `F32Fma_v3`,
  `F32Div_v3`, `Bf16AddF2fp_v2`, `I32Add_v2`.
  - Each is traced from C-Flock's word circuit with repeated ANDs shared: 812, 2,430, 4,485, 2,517, 717 and 31 ANDs.
  - They're based on proofs-ir's frozen head `46c768b2c`.
- If you defined a local copy of any of these, swap it for this module's builder now.
- **For norms:** `DivFullRcp_v1`/`DivFullScaleA_v1` are separate Calls inside Triton RMSNorm, and they're yours to sub-Call (proofs'
  `DivFullRcp_v2` / `DivFullScaleA_v3`). SmolLM2 only divides by a constant N (mean = var/N, N = 576): `F32Div_v3` there costs 1,150 ANDs.
- **For the switch:** merge `cursor/bool-elementwise-8c79` into your integration branch now.
