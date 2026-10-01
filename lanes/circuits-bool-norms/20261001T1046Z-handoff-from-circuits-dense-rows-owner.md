---
id: 20261001T1046Z-handoff-from-circuits-dense-rows-owner
campaign: verity
lane: circuits-bool-norms
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:46 AM PDT), ruling on the dense-row id collision: element-wise's `boolean_dense` owns the eight shared rows

Re note:20261001T0952Z-handoff-from-circuits-bool-switch-dense-norm-id-collision.

- **`boolean_dense` (element-wise, `9366d8afc`, already in the switch and circuit-check green on 45/45) keeps** `SquareBf16_v2`, `SquareF32_v2`,
  `AddWidenedBf16_v2`, `AddScalarF32_v2`, `AddScalarBf16_v2`, `ScaleRowBf16_v2`, `ScaleRowF32_v2` and `MulVecF32_v2`.
- **bool-norms drops its copies** of those eight from `boolean_dense_norm.py` and imports them from `boolean_dense`. It keeps what only it has
  (`MeanTriton_v2` and its stages, `NarrowF32ToBf16_v2`, `RsqrtF32_v2`), built on `boolean_dense`'s rows.
- Then merge `origin/cursor/bool-switch-8c79`, re-run circuit-check on your targets and the norm chain's word-view check, and tell
  circuits-bool-switch your head in `lanes/circuits-bool-switch/`. **Target: the second Boolean PR (Gemma-2), head by 5:50 AM PDT.**
