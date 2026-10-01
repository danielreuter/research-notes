---
id: 20261001T0952Z-handoff-from-circuits-bool-switch-dense-norm-id-collision-circuits-bool-norms
campaign: verity
lane: circuits-bool-norms
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---
# @circuits, @circuits-bool-norms, @circuits-bool-elementwise: two lanes wrote Gemma-2's norm rows on bits under the same ids

2:52 AM PDT. `cursor/bool-norms-8c79` @ `8e0e73ba7` (`c120cf0f6`, `boolean_dense_norm.py`) and the elementwise lane's
`boolean_dense.py` (`a38c5b2ee`, already on `cursor/bool-switch-8c79`) both register **`SquareBf16_v2`, `SquareF32_v2`,
`AddWidenedBf16_v2`, `AddScalarF32_v2`, `AddScalarBf16_v2`, `ScaleRowBf16_v2`, `ScaleRowF32_v2`, `MulVecF32_v2`** as different
Definitions. The registry raises on a second Definition per id, so the two can't be imported together.

- I **did not merge** bool-norms' 3 new commits; they stay on their branch. The integration branch keeps `boolean_dense`'s
  (elementwise's) versions. Neither is on the target row (SmolLM2-135M, purity 0 without them).
- Ask (circuits decides): one owner per family. Suggestion: bool-norms keeps what only it has (`MeanTriton_v2` and its stages,
  `NarrowF32ToBf16_v2`, `RsqrtF32_v2`) and builds on `boolean_dense`'s rows instead of redefining them (or the reverse, with
  `boolean_dense` dropping its copies). The other lane then merges `cursor/bool-switch-8c79`. Whichever lands first, I merge it.
