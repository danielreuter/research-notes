---
id: 20260930T0813Z-handoff-from-red-team-vllm-semantics-fp8-scale-order
campaign: overnight-sep30
lane: red-team-vllm-semantics
kind: handoff
status: open
repo: danielreuter/verity
origin: red-team-vllm-semantics
cursor:
  subagentId: "bc-05c0bb3e-507d-57b1-ae79-cac14d00af0d"
---

# The sm_120 FP8 per-tensor linear must not reuse `ScaledMmFp8_v1`'s scale order

Rated `fp8-per-tensor-scale-order` as **conditions**, not broken, because nothing sm_120-FP8 is bound on main yet. It changes the plan in the 04:28Z tc-gemm handoff, which says "the per-tensor Definition is `ScaledMmFp8_v1`'s order with the sm_120 step".

- **What the hardware does.** vLLM's sm_120 CUTLASS FP8 dispatch (`scaled_mm_sm120_fp8_dispatch.cuh` at d9105ea80) has no swap_ab, so ScaleA is `a_scales` (the activation scale, s_x):
  - no bias: `bf16(s_x * (s_w * acc))`;
  - with bias: `bf16(fma(s_x, s_w * acc, b))` (`ScaledEpilogueBias`).
  - Run `r20260930-041842-76a2` measured "sa*(sb*acc)" with sa = `a_scales`, which is this order.
- **What the registered Definition does.** `ScaledMmFp8Coordinate_v1` computes `s_w * (s_x * acc)` and `fma(s_w, s_x*acc, b)`. That is the sm_90 batch-invariant dispatch, which always swaps (ScaleA = `b_scales`). In the 5b run, this order is "sb*(sa*acc)", which misses 89 of the 125 discriminating coordinates.
- **Reproducer** (CPU, recorded as `r20260930-081238-476e`): `python rt-redteam/fp8_order_repro.py`. On 5 of 5 discriminating operand sets, the Definition returns the swap_ab word. For example, `sx=3c3d982f sw=3c0d3421 acc=3d102000`: sm_120 gives `366b`, the Definition gives `366c`. The script lives in the lane store at `internal/lanes/red-team-vllm-semantics/scripts/`.
- **Fix:** give the sm_120 binding its own coordinate, `F32Mul(sw, acc)` then `F32Mul(sx, ·)` (with bias, `F32Fma(sx, ·, b)`). The DOT is the sm_120 e4m3 step.
