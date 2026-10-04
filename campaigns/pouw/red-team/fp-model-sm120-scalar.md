---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `fp-model/sm120-scalar`: B, exhaustive on the cast

30 Sep 2026, 09:20Z. Independent assessor (bc-d7d4b0d1). The row covers the three scalar facts Pearl-C's noisy cast and noise-loss proof read on the RTX PRO 6000:
- `cvt.rn.satfinite.e4m3x2.f32` rounds once to nearest-even with saturation;
- the promotion FADD rounds to nearest without flushing;
- the MMA doesn't flush E4M3 subnormals.

The table listed no sm_120 evidence. This is an independent capture on GPU 6 (`r20260930-091638-9747`, about 0.02 GPU-hours, under a `gpu-lease --wait` lease; the first pass is `r20260930-091437-f48d`). Code: `scalar_model_sm120.cu`, `scalar_model_check.py`, `scalar_model_sm120.sh`.

| Fact | Check | Result |
|---|---|---|
| The cast | All 2³² FP32 bit patterns, both lanes of `e4m3x2` (SASS `F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C`), against an integer reference; the reference and the device against `pearl_kw.f32_to_fp8` on 1,544,077 sampled inputs (midpoints ± 1 ulp, the 448/464/480 edges, 82,143 subnormal results) | **0 mismatches** on every finite input; ±Inf → ±448. A NaN input gives 0x7F whatever its sign; the pinned cast rejects non-finite inputs, so that is outside the domain |
| The promotion FADD | `add.rn.f32` (SASS `FADD`, no `.FTZ`) on 2³² pairs weighted to subnormals, ties and near-cancellation, against the double sum rounded once, which is innocuous since 53 ≥ 2·24 + 2; plus 1,000,000 sampled pairs against `verity.ml.tc.fp32.add` | **0 mismatches** on 4,294,967,191 finite pairs (1.06 × 10⁹ touching subnormals) and on the 10⁶ pinned-model pairs (453,389 subnormal). The 105 non-finite pairs (93 NaN payload differences) are outside the domain |
| Positive control | The same test with `add.rn.ftz.f32` (SASS `FADD.FTZ`) | 488,294,393 mismatches, so the test detects flushing |
| MMA subnormals | `mma.sync` m16n8k32 E4M3 × E4M3 → FP32 (`QMMA.16832.F32.E4M3.E4M3`) with both operands broadcast: all 254 × 254 finite code pairs, D = 32·c·d exactly | **0 mismatches** of 64,516, 6,916 with a subnormal operand |

**Rating: B** (GPU, deployment card, exhaustive on the cast). A is reserved for public primitives with years of study.

**One exposure is in the build, not the hardware.** The positive control shows that a kernel compiled with `-ftz=true` or `--use_fast_math` emits `FADD.FTZ` and breaks the model on subnormal promotions. The kernel lane's SASS gate should reject `FADD.FTZ` in the chain's promotion, as the generic-GEMM gate rejects tensor ops.

## Update 10:00Z: the `.FTZ` allowlist for nvcc's correctly rounded div, rcp and sqrt

nvcc (CUDA 13.0, `cuda_13.0.r13.0/compiler.36424714_0`) lowers `div.rn.f32`, `rcp.rn.f32` and `sqrt.rn.f32` to sequences that contain `.FTZ` ops even without an FTZ flag. The harness's SASS gate allows exactly those sequences. I checked independently that they are exact on the card (`divsqrt_ftz_sm120.cu`, `divsqrt_ftz_check.py`, `r20260930-095650-85ec`, GPU 6).

| Operation | Checked against a once-rounded double reference (innocuous: 53 ≥ 2·24 + 2) | Subnormal cases | Mismatches |
|---|---|---|---|
| `sqrt.rn.f32` | all 2³² inputs | 16,777,214 | **0** |
| `rcp.rn.f32` | all 2³² inputs | 50,331,644 | **0** |
| `div.rn.f32` | 2³² pairs weighted to subnormal operands and results, short mantissas and the overflow edge | 1,150,047,535 | **0** |
| div and sqrt against `verity.ml.tc.fp32.div` and `fp32.sqrt` | 1,000,000 pairs (499,485 sqrt inputs) | 394,898 | **0** |

**What the SASS shows.** Each sequence has `FADD.FTZ`, `FMUL.FTZ` and `FSETP.*.FTZ` beside `MUFU.RCP` or `MUFU.RSQ`, and a range test that branches (`CALL.REL.NOINC`) to a slow-path subroutine for subnormal and edge operands. That branch is why the sequences are exact despite the flushing ops. (The `MUFU.*64H` ops in the kernels come from the double-precision reference, not from the f32 sequences.)

**The arithmetic is sound. A hole could only be in the matcher, which should:**
- pin each allowed sequence whole: its `.FTZ` ops, the range test and the slow-path call target. Allowing `.FTZ` ops by opcode or by proximity to a `MUFU` would admit a stray flushing add;
- reject `--use_fast_math`'s `div.full` and `sqrt.approx`, which have the same `MUFU` and `.FTZ` ops but no slow path and are not correctly rounded. The pinned test kernel should carry that build as a negative control;
- be keyed to the nvcc version, since the sequences change across compilers. A new nvcc means re-running the pinned test.

## Update 10:20Z: `__frsqrt_rn` (added to the allowlist for GPU 1's forming)

`frsqrt_sm120.cu` and `.sh`. The reference is exact, not a once-rounded double: y is correct iff the midpoints around it satisfy m−²x < 1 < m+²x, with m²x − 1 formed exactly by an FMA two-product.

| nvcc 13.0 build | `.FTZ` ops in the `__frsqrt_rn` sequence | Mismatches, all 2³² inputs | Run |
|---|---|---|---|
| default flags | **0** (FFMA, FMUL, `MUFU.RSQ`, a slow-path CALL) | **0** (8,388,607 positive subnormal inputs) | `r20260930-101332-226b` |
| `-ftz=true` | 27 (`FFMA.FTZ`, `FMUL.FTZ`, `FSETP.*.FTZ`) | 8,388,607, the count of one sign's subnormals. The first is a negative subnormal returning −∞ where NaN is correct | `r20260930-101522-345f` |

- **The premise doesn't reproduce with default flags.** On this toolkit (the node's `/usr/local/cuda`, 13.0), `__frsqrt_rn` emits `.FTZ` ops only under `-ftz=true`.
- **If GPU 1's build shows them, its build likely differs:** either an FTZ flag, which would also turn its plain float ops into `FADD.FTZ` and `FMUL.FTZ` for the gate to catch, or another nvcc.
- **The allowlist entry should be pinned to the sequence GPU 1 actually builds** (compiler version and flags), and its exactness test run on that build.
- **The difference under `-ftz=true` is outside the forming's domain.** Negative subnormal inputs can't reach a reciprocal square root of a sum of squares, but the test should say so rather than pass by omission.
