---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T1630Z-handoff-from-backend-sweep-libdevice-nan-probe
campaign: backend-sweep
lane: flock-ir-lowering
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f), via the coordinator
---

# The GPU's NaN is always `0x7FFFFFFF`: libdevice `logf` / `log1pf`, and FP32 add, sub, mul, div and fma

For [#300](https://github.com/danielreuter/verity/pull/300), which pins `sampling.LOG_INVALID_NAN = 0xFFC00000`. It's also for core's evaluators, which return the x86 host's `0xFFC00000` for add/sub/mul/div and `0x7FC00000` for fma.

**Answer: every NaN result is `0x7FFFFFFF`, on both GPUs, both toolkits, with the default flags and with the sampler's FTZ.** That holds for invalid operations and for NaN inputs. No input NaN's payload or sign survives, whether the input is quiet or signalling.

So:
- #300's constant and C-Flock's `nv_logf` piece (`tail_pieces`) should move to `0x7FFFFFFF`;
- core's add/sub/mul/div (now `0xFFC00000`) and fma (now `0x7FC00000`) should return `0x7FFFFFFF` for every NaN result, NaN inputs included.

**Evidence:** `art:e5dd6ce9fa74e7ca4538b848943d8bb555f2adac528277848395dbf4cdff66a5` (preserved), kind `libdevice-probe/v1`. It supersedes the logf-only `art:317bc0ae583507c058f3fdd7a8c51174bec2912e47ca447eafb3ddc2941a002f` (`refs.previous`). It holds:
- every input and output word;
- the probe source, `probe.cu` and `run.sh`;
- each build's PTX, SASS, nvcc version and libdevice hash;
- `summary.json` (logf / log1pf) and `summary-ops.json` (arithmetic).

It's labelled `answer=0x7FFFFFFF` and `for_pr=300`.

## What ran

- **The GPUs and toolkits:**

  | GPU | SM | Driver | nvcc |
  |---|---|---|---|
  | NVIDIA L40S (`ok1sb4wgkxvhne`) | 8.9 | 570.124.06 (CUDA 12.8; the 13.3 runtime through its compat library) | 12.4 V12.4.131 and 13.3 V13.3.73 |
  | NVIDIA H100 NVL (`jlduzt4m4hw41m`) | 9.0 | 580.159.04 (CUDA 13.0) | 12.4 V12.4.131 and 13.3 V13.3.73 |

- **The builds:** `nvcc -O3 -arch=sm_XX` with `-ftz=true` (the sampler's FTZ, Triton's `nvvm-reflect-ftz=1`) and with `-ftz=false` (the default): 4 builds per GPU. The PTX confirms the FTZ build compiles the C++ operators to `add.ftz`, `mul.ftz`, `div.rn.ftz` and `fma.rn.ftz`, and the default build to the plain forms.
- **libdevice:** the two toolkits' `libdevice.10.bc` differ (sha256 `8c593e48…` for 12.4, `d9ac7884…` for 13.3). I didn't build through Triton 3.7.1's own copy.
- **No constant folding:** every input word is read from device memory, and each op is an `asm volatile` PTX instruction.

## libdevice `__nv_logf` / `__nv_log1pf` (the same in all 16 builds unless noted)

| Input | `logf` | `log1pf` |
|---|---|---|
| −1.0f / −2.0f | `logf(−1)` = `7FFFFFFF` | `log1pf(−2)` = `7FFFFFFF` |
| −0.0f / −1.0f | `logf(−0)` = `FF800000` (−inf) | `log1pf(−1)` = `FF800000` (−inf) |
| just below −1 (`BF800001`) | | `7FFFFFFF` |
| −FLT_MAX | `7FFFFFFF` | `7FFFFFFF` |
| −inf | `7FFFFFFF` | `7FFFFFFF` |
| negative subnormal (`80400000`, `80000001`, `807FFFFF`) | **FTZ: `FF800000`**; default: `7FFFFFFF` | |
| 20,000 random words | 19,856 negative normals: `7FFFFFFF`; 72 subnormals: FTZ `FF800000`, default `7FFFFFFF`; **72 negative NaN inputs: `7FFFFFFF`** | 20,000 below −1: `7FFFFFFF` |

In the PTX, libdevice's special case is `fma.rn.ftz.f32 r, x, inf, inf`. It has no NaN constant, so the result is the FMA's own NaN, shown below.

## FP32 arithmetic on invalid operands and NaN inputs

- **The operands:** 15 specials: ±0, ±1, ±inf; quiet NaNs `7FC00000`, `FFC00000`, `7FC12345`, `FFC54321`; signalling NaNs `7F800001`, `FF800001`, `7FA00000`, `FFB00000`; and `7FFFFFFF`.
- **The cases:** every pair for the binary ops (225 per build) and every triple for fma (3,375 per build), with 8 builds per op (4 per GPU).

| Op (explicit PTX, and the C++ operator as the flags compile it) | Invalid cases (no NaN input) per build | NaN results over 8 builds | Output word |
|---|---:|---:|---|
| `add.rn.f32`, `add.rn.ftz.f32`, `sub.rn.f32`, `sub.rn.ftz.f32`, `a+b`, `a-b` (inf − inf) | 2 | 1,528 each | `7FFFFFFF` only |
| `mul.rn.f32`, `mul.rn.ftz.f32`, `a*b` (0 × inf, either order and sign) | 8 | 1,576 each | `7FFFFFFF` only |
| `div.rn.f32`, `div.rn.ftz.f32`, `div.full.f32`, `div.full.ftz.f32` (Triton's `/`), `div.approx.f32`, `div.approx.ftz.f32`, `a/b` (0/0, inf/inf) | 8 | 1,576 each | `7FFFFFFF` only |
| `fma.rn.f32`, `fma.rn.ftz.f32`, `fmaf(a,b,c)` (0 × inf + c, and ±inf ∓ inf in the add) | 60 | 25,752 each | `7FFFFFFF` only |

**No NaN input is ever propagated:** not its payload, its sign, or its signalling bit. A NaN in either operand, or any fma position, gives `7FFFFFFF`, and so does a NaN–NaN pair.

## Two details to check in #300

1. **A NaN input** to `logf` returns `7FFFFFFF`, not the input's payload. If the scalar lane or the rows twin propagates the input NaN, they differ there too. The same goes for core's arithmetic.
2. **With FTZ**, a negative subnormal goes to −0 and `logf` returns −inf, which matches #300's transcription fix.
