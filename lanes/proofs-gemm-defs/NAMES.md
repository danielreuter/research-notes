---
id: proofs-gemm-defs-names
campaign: proofs
lane: proofs-gemm-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/proofs-gemm-defs-95d4
---

# sm_120 FP8 / FP4 GemmCoordinate: final ids and signatures

Landed on `cursor/proofs-gemm-defs-95d4`: `0f05a4dd` (the MXF4 step), `21e333a9` (the three coordinates). circuit-check green
on all four; C-Flock lowers the E4M3 coordinate (19,352 ANDs at K = 64) and has no piece yet for `BlackwellNvf4OmmaDot64_v1`
or `BlackwellMxf4OmmaDot64_v1`. Catalog bindings (`circuit_check.targets._core_roots`): E4M3 K = 64, NVF4 / MXF4 K = 128.

Branch `cursor/proofs-gemm-defs-95d4` (over `cursor/proofs-tc-defs-95d4`). Types: `f32 = Value<32>`, `bf16 = Value<16>`,
`e4m3 = Value<8>`, `e2m1 = Value<4>`, scale byte `= Value<8>`. All steps: `conformance="exact-model-tested"`, total on every encoding.

## Step primitives (in `verity.ml.prims`)

Two of the three already exist on the base branch (#523 / #502), so their ids are reused instead of the proposed `Sm120*` ids.

| id | tc instruction | signature | k |
|---|---|---|---|
| `BlackwellE4m3QmmaDot32_v1` (existing, replaces `Sm120E4m3MmaDot32_v1`) | `sm120.mma.m16n8k32.e4m3` | `(acc: f32, a: Array<32, e4m3>, b: Array<32, e4m3>) -> f32` | 32 |
| `BlackwellNvf4OmmaDot64_v1` (existing, replaces `Sm120Nvf4MmaDot64_v1`) | `sm120.mma.m16n8k64.e2m1.nvf4` | `(acc: f32, a: Array<64, e2m1>, b: Array<64, e2m1>, sa: Array<4, Value<8>>, sb: Array<4, Value<8>>) -> f32` (UE4M3, block 16) | 64 |
| `BlackwellMxf4OmmaDot64_v1` (new; named like its NVF4 sibling instead of `Sm120Mxf4MmaDot64_v1`) | `sm120.mma.m16n8k64.e2m1.mxf4` | `(acc: f32, a: Array<64, e2m1>, b: Array<64, e2m1>, sa: Array<2, Value<8>>, sb: Array<2, Value<8>>) -> f32` (UE8M0, block 32) | 64 |

Flattened argument order of each step (as in the evaluator `*ab`): acc, a[0..k], b[0..k], then sa, sb.

## Composites (in `verity.ml.gemm`)

| id | statics | signature | body |
|---|---|---|---|
| `GemmCoordinateE4m3_v1` | `K`, `DOT` | `(x: Array<K, e4m3>, wrow: Array<K, e4m3>) -> bf16` | `acc = ZERO32`; for s in 0..K/32: `acc = DOT(acc, x[32s:32s+32], wrow[32s:32s+32])`; `F2fpBf16_v1(acc)` |
| `GemmCoordinateNvf4_v1` | `K`, `DOT` | `(x: Array<K, e2m1>, wrow: Array<K, e2m1>, sx: Array<K/16, Value<8>>, sw: Array<K/16, Value<8>>) -> bf16` | for s in 0..K/64: `acc = DOT(acc, x[64s:+64], wrow[64s:+64], sx[4s:+4], sw[4s:+4])`; `F2fpBf16_v1(acc)` |
| `GemmCoordinateMxf4_v1` | `K`, `DOT` | `(x: Array<K, e2m1>, wrow: Array<K, e2m1>, sx: Array<K/32, Value<8>>, sw: Array<K/32, Value<8>>) -> bf16` | for s in 0..K/64: `acc = DOT(acc, x[64s:+64], wrow[64s:+64], sx[2s:+2], sw[2s:+2])`; `F2fpBf16_v1(acc)` |

`DOT` binds the step: `GEMM_SM120_E4M3 = {"DOT": BlackwellE4m3QmmaDot32}`, `GEMM_SM120_NVF4 = {"DOT": BlackwellNvf4OmmaDot64}`,
`GEMM_SM120_MXF4 = {"DOT": BlackwellMxf4OmmaDot64}`. No intermediate `Dot*` composite: the step calls sit directly in the
coordinate's body (one proof unit = one coordinate call: K/k steps, then one `F2fpBf16`).
