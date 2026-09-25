---
id: vllm-rf-c2/state
lane: vllm-rf-c2
kind: state
agent: bc-568d82f4 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T09:36Z
---
# c2 (Definition library, D8/D9, decision 3a): state

a4 base: 10996616

- Worktree `~/projects/verity-wt/rf-c2`, branch `lane/vllm-rf-c2` from `10996616`.
- Budget: $25 of pod spend. Spent so far: `vyv-rf-c2-cpu` from 08:51Z at $1.28/h.

## Commits (pushed)
- `f6bf88c7` registry cites core for Bf16ToF32/F32ToBf16Rn/F2fpBf16/HopperBF16WgmmaDot16, Const family, DotBf16/
  GemmCoordinate/Gemm _v2; one-process test; allowlists P1 -4, P8 -3, P11 -1, P10 b1 cap 1285 -> 1246.
- `e0fc636f` P1 lint reads `@composite` ids too (allowlist unchanged).

## Evidence so far
- Step 1 at base (run `r20260925-091543-a01c`, `evidence/step1/equality.json`): ALL-EQUAL. Bf16ToF32 2^16,
  F32ToBf16Rn and F2fpBf16 all 2^32 words (core vs integration scalar + core numpy kernel), Hopper k16 step 7,418,816
  cases (special grid, dense specials, core sample_tc 5 M, uniform words 1 M, narrow exponent 1 M): 0 differences
  core vs integration scalar / core kernel / integration twin. 32 Gemm_v2-family program digests and 23 Const encodings
  equal. `test_derived_rows.py` + `packages/verity/tests/ml` green (separate processes).
- Quick head `e0fc636f` (run `r20260925-092504-63c3`): lints green; registry test files green incl. the new one-process test.

## Running
- `vyv-rf-c2-cpu` (RunPod `v34wij1rkanus8`, cpu3g 32 vCPU / 128 GB, EPYC 7702P, guard 90): idle.

## Next
1. Step 3 inventory + moves (FP8 silicon: HopperE4m3QgmmaDot32_v1, F32ToE4m3Sat_v1; host-independent basic bit/int ops),
   with base-tree vs head-tree evaluator equality.
2. Gates at the pre-epoch head: lints, gate (b) head vs base, gate (a) T0+T1 (cpu3m 512 GB), GPU Build #101 (L40S),
   Hopper: CPU re-encode of #73/#74 stored Programs.
3. Epoch commit (AmpereBF16TcDot16 v1 -> v2) at the tip, separate.

## Open questions
(none)

## Found, not fixed
- Two collisions beyond the allowlisted four block a one-process import of `verity.ml` + the integration registry:
  `Const<w>[0x..]_v1` (b1.py's own `const()` vs core's; core makes `ZERO32` at import) and `DotBf16_v2`,
  `GemmCoordinate_v2`, `Gemm_v2` (b1.py vs `verity.ml.gemm`). P1's lint only scans `primitive`/`PrimitiveDefinition`/
  `CompositeDefinition` calls, not the `@composite` decorator, so the second set is not in its allowlist. Fixed in
  `f6bf88c7` / `e0fc636f`.
- `F32Add_v1`, `F32Mul_v1`, `F32Div_v1` and `F32AddFtz/SubFtz/MulFtz_v1` evaluate through host numpy float32
  arithmetic, so the NaN word they return is the host's: `inf + -inf` is `0x7fc00000` on arm64 (laptop numpy 2.5.3);
  x86 expected `0xffc00000` (to confirm on the pod). They also inherit the process's MXCSR FTZ/DAZ state. Basic
  Definitions that belong in core, but moving them as they are would put a host-dependent function in core; not moved.
