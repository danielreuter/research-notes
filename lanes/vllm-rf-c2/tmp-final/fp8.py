"""FP8 (`--quantization fp8`) linear of the B1 serving program on Hopper — lane QZ, port `b1-fp8`.

Under `LLM(quantization="fp8")` on an H100 (pinned build d9105ea80, eager, `VLLM_BATCH_INVARIANT=1`, TP=1) every
decoder linear of Qwen2.5-1.5B (qkv_proj, o_proj, gate_up_proj, down_proj; the tied lm_head stays bf16) is
executed by two kernels, both read from the vLLM source and confirmed on the production run (fp8.md §1):

1. `_C.dynamic_per_token_scaled_fp8_quant` (`dynamic_per_token_scaled_fp8_quant_kernel_strided`, 256 threads per
   token row, `scale_ub = None`): per-row absmax `m = max_e |f32(x_e)|` (thread partials from `0.f` over 8-element
   vectors in stride-256 order, `cub::BlockReduce<float,256>` max: per-warp shuffle tree then a sequential fold
   over the 8 warp results — a *max* is exact, so the word does not depend on the order; the structure below is
   the kernel's anyway), the scale `s_x = fmaxf(m / 448.0f, 1.0f / (448.0f * 512.0f))` (an IEEE `div.rn.f32`, not
   a reciprocal), and the row's e4m3 words `x_q[e] = cvt.rn.satfinite.e4m3x2.f32(fmaxf(-448, fminf(f32(x_e) / s_x, 448)))`
   (`scaled_fp8_conversion<is_scale_inverted=false>`: again a true division).  BOTH outputs are materialised by
   production and recorded as ports 0 (`x_q`, [M, K] e4m3) and 1 (`s_x`, [M, 1] f32) of the `fp8_quant` node.
2. `_C.cutlass_scaled_mm` (`cutlass_gemm_sm90_fp8_batch_invariant_dispatch` -> `sm90_fp8_config_M64_N8192` for
   every N > 1280 of B1: TileShape 64x64x256, `KernelTmaWarpSpecializedFP8FastAccum`, `swap_ab = true`):
   `D^T = W_q · x_q^T` — one accumulator coordinate is an ascending chain of K/32 `wgmma.mma_async.sync.aligned
   .m64n64k32.f32.e4m3.e4m3` steps (SASS `QGMMA.64x64x32.F32.E4M3.E4M3`) from `scale-d = 0` (≡ acc = +0),
   *FastAccum*: no CUDA-core promotion between k-tiles — the f32 accumulator stays in the wgmma registers for
   the whole K.  The batch-invariant dispatch passes the scales swapped (`b_scales, a_scales`), so in the fused
   epilogue ScaleA = `s_w` (per-tensor scalar) and ScaleB = `s_x` (per-token): `y = bf16(fma(s_w, s_x * acc, f32(bias)))`
   (`ScaledEpilogueColumnBias`: `Compute0 = multiplies(ScaleB, Accum)`, `Compute1 = homogeneous_multiply_add(ScaleA, ·, Bias)`,
   one FMA, then `cvt.rn.bf16.f32`) or `y = bf16(s_w * (s_x * acc))` without bias (`ScaledEpilogue`).

The weights are quantised once at load (`Fp8PerTensorOnlineLinearMethod.process_weights_after_loading`): `amax =
max(|W|)` over the bf16 fused tensor, `s_w = f32(amax) / 448` (torch f32 division), `W_q = cvt(f32(W) * (1.0f / s_w))`
(`static_scaled_fp8_quant`: here a *reciprocal multiply*), stored as `layer.weight = W_q.t()` ([K, N] view) and
`layer.weight_scale` (one f32).  They are **derived Inputs** of the program (bound from the commit's stored e4m3/f32
words and cross-checked against a CPU re-quantisation of the checkpoint; fp8.md §2).  The activation scale `s_x`
and the e4m3 activations are **computed** by `Fp8ActQuant` from the norm output — never Inputs.

Registered functions (all `Name_v1`):
  primitives  core's: F32Fabs, F32Fmaxf, F32Fminf (`verity.ml.scalar`), F32ToE4m3Sat, HopperE4m3QgmmaDot32 (`verity.ml.prims`)
  composites  Fp8RowAbsMax{K}, Fp8RowScale, Fp8ActQuant{K}, DotE4m3{K}, ScaledMmFp8Coordinate{K,BIAS},
              ScaledMmFp8{K,N,BIAS} (the cutlass GEMM over the quantised row), QuantLinearFp8{K,N,BIAS} (= Fp8ActQuant
              + ScaledMmFp8, the linear as one function), LayerPreFp8{C,L0}, LayerPostFp8{C}, ServeFp8{C,LP,STEPS}
`verity_vllm/program/registry/b1.py` (TA1) and `hopper.py` (HP) are not modified; the Hopper bf16 composites (RMSNorm, RoPE,
AttentionFA3, SiluMul, Embedding, GemmHopper for lm_head, TokenSelect) are reused as registered.
"""

from __future__ import annotations

import types

import numpy as np

from verity.ir.defs import CompositeDefinition, bind, composite
from verity.ir.refs import Coll as _Coll, concat, tuple_of
from verity.ir.types import Array, Record, Tuple, Value
from verity.ml.prims import F32ToE4m3Sat, HopperE4m3QgmmaDot32
from verity.ml.scalar import F32Fabs, F32Fmaxf, F32Fminf
from verity_vllm.program.registry import b1
from verity_vllm.program.registry import hopper as H
from verity_vllm.program.registry import prims as P
from verity_vllm.program.registry.prims import BF16, F32, I32, bits_of, f32_of

# ---------------------------------------------------------------------------------------------------------
# types and constants
# ---------------------------------------------------------------------------------------------------------

E4M3 = Value(8)          # OCP E4M3 (float8_e4m3fn): bias 7, max 448 (0x7E), NaN 0x7F/0xFF, no infinities
A32_8 = Array(32, E4M3)  # one k32 wgmma operand slice

E4M3_MAX = 448.0
E4M3_NAN = 0x7F

C448 = b1.f32c(448.0)        # quant_type_max_v<fp8_e4m3fn> as float
C_NEG448 = b1.f32c(-448.0)
# min_scaling_factor<fp8_e4m3fn>::val() = 1.0f / (448.0f * 512.0f), evaluated in f32 (nvcc constant folding, RN)
MIN_SCALE_BITS = bits_of(np.float32(1.0) / (np.float32(448.0) * np.float32(512.0)))
C_MIN_SCALE = b1.const(32, MIN_SCALE_BITS)

QUANT_THREADS = 256       # dynamic_per_token_scaled_fp8_quant: block(min(hidden, 256)); every B1 K is >= 256
QUANT_VEC = 8             # vectorize_read_with_alignment<16> on bf16: 8 elements per vector
WARP = 32

FP8_PRIMITIVES = [F32Fabs, F32Fmaxf, F32Fminf, F32ToE4m3Sat, HopperE4m3QgmmaDot32]

# ---------------------------------------------------------------------------------------------------------
# dynamic per-token activation quantisation (the kernel's structure)
# ---------------------------------------------------------------------------------------------------------


def _thread_elements(K: int, t: int) -> list[int]:
    """Element indices thread `t` visits, in order: vectors t, t+256, ... of 8 consecutive elements each."""
    nvec = K // QUANT_VEC
    out: list[int] = []
    for v in range(t, nvec, QUANT_THREADS):
        out.extend(range(QUANT_VEC * v, QUANT_VEC * v + QUANT_VEC))
    return out


def _tree(B, vals: list, op) -> object:
    """Balanced binary tree (cub WarpReduce shuffle-down steps 1,2,4,8,16 as seen from lane 0)."""
    while len(vals) > 1:
        vals = [B.call(op, vals[i], vals[i + 1]) for i in range(0, len(vals), 2)]
    return vals[0]


@composite("Fp8RowAbsMax", 1, ["K"], lambda S: ((("x", Array(S.K, BF16)),), F32), conformance="exact-model-tested")
def Fp8RowAbsMax(B, S, x):
    """`dynamic_per_token_scaled_fp8_quant_kernel_strided` step 1: `absmax = fmaxf(absmax, fabsf(f32(v)))` per
    thread from `0.f` over its 8-element vectors (t, t+256, ...), then `cub::BlockReduce<float,256>::Reduce(max)`:
    a shuffle tree per warp, thread 0 folds the 8 warp maxima in order.  Partials are never NaN (fmaxf drops a
    NaN operand; the fold starts at +0), so cub's `max(a,b)` equals `fmaxf` on every reachable word."""
    K = S.K
    assert K % QUANT_VEC == 0 and K >= QUANT_THREADS, K
    partials = []
    for t in range(QUANT_THREADS):
        p = B.call(b1.ZERO32)
        for e in _thread_elements(K, t):
            p = B.call(F32Fmaxf, p, B.call(F32Fabs, B.call(P.Bf16ToF32, x[e])))
        partials.append(p)
    warps = [_tree(B, partials[w * WARP:(w + 1) * WARP], F32Fmaxf) for w in range(QUANT_THREADS // WARP)]
    m = warps[0]
    for w in warps[1:]:
        m = B.call(F32Fmaxf, m, w)
    return m


@composite("Fp8RowScale", 1, [], lambda S: ((("absmax", F32),), F32), conformance="exact-model-tested")
def Fp8RowScale(B, S, absmax):
    """`token_scale = fmaxf(absmax / 448.0f, 1.0f / (448.0f * 512.0f))` (`scale_ub = None`): an IEEE f32 division."""
    return B.call(F32Fmaxf, B.call(P.F32Div, absmax, B.call(C448)), B.call(C_MIN_SCALE))


@composite("Fp8ActQuant", 1, ["K"], lambda S: ((("x", Array(S.K, BF16)),), Tuple(Array(S.K, E4M3), F32)),
           conformance="exact-model-tested")
def Fp8ActQuant(B, S, x):
    """The whole per-token quant kernel on one bf16 row: (x_q[K] e4m3, s_x f32) = ports 0 and 1 of the `fp8_quant`
    node.  `x_q[e] = cvt.rn.satfinite.e4m3(fmaxf(-448, fminf(f32(x[e]) / s_x, 448)))` (`scaled_fp8_conversion<false>`)."""
    s = B.call(Fp8RowScale, B.call(bind(Fp8RowAbsMax, K=S.K), x))
    c448, cneg = B.call(C448), B.call(C_NEG448)
    q = [B.call(F32ToE4m3Sat, B.call(F32Fmaxf, cneg, B.call(F32Fminf, B.call(P.F32Div, B.call(P.Bf16ToF32, x[e]), s), c448)))
         for e in range(S.K)]
    return tuple_of(_Coll(Array(S.K, E4M3), concat([w.refs for w in q])), s)


# ---------------------------------------------------------------------------------------------------------
# the scaled GEMM: k32 wgmma chain + fused epilogue
# ---------------------------------------------------------------------------------------------------------


@composite("DotE4m3", 1, ["K"], lambda S: ((("xq", Array(S.K, E4M3)), ("wq", Array(S.K, E4M3))), F32),
           conformance="exact-model-tested; _C.cutlass_scaled_mm vs the model at 320/320 sampled coordinates over five B1 shapes (K=1536/8960, N=1536/2048/17920, bias on/off; gpu/tc-fp8/vllm_fp8_kernels_probe.py --gemm, 2026-09-08) and 0 mismatches at every coordinate-sampled quantised gemm leaf of the production capture (corr-A/B, fp8.md §5); the k32 step pinned by the tc-fp8 campaign")
def DotE4m3(B, S, xq, wq):
    """f32 accumulator after K/32 `HopperE4m3QgmmaDot32` steps in ascending k from `+0` (`scale-d = 0` on the first
    wgmma of the CUTLASS mainloop; FastAccum: no promotion between the 256-wide k-tiles)."""
    assert S.K % 32 == 0, S.K
    acc = B.call(b1.ZERO32)
    for s in range(S.K // 32):
        acc = B.call(HopperE4m3QgmmaDot32, acc, xq[32 * s:32 * s + 32], wq[32 * s:32 * s + 32])
    return acc


@composite("ScaledMmFp8Coordinate", 1, ["K", "BIAS"],
           lambda S: (((("xq", Array(S.K, E4M3)), ("sx", F32), ("wrow", Array(S.K, E4M3)), ("sw", F32))
                       + ((("b", BF16),) if S.BIAS else ())), BF16),
           conformance="exact-model-tested; _C.cutlass_scaled_mm vs the model at 320/320 sampled coordinates over five B1 shapes (K=1536/8960, N=1536/2048/17920, bias on/off; gpu/tc-fp8/vllm_fp8_kernels_probe.py --gemm, 2026-09-08) and 0 mismatches at every coordinate-sampled quantised gemm leaf of the production capture (corr-A/B, fp8.md §5); the k32 step pinned by the tc-fp8 campaign")
def ScaledMmFp8Coordinate(B, S, xq, sx, wrow, sw, *bias):
    """One output word: `bf16(fma(s_w, s_x * acc, f32(b)))` (ScaledEpilogueColumnBias, swap_ab: ScaleA = s_w,
    ScaleB = s_x) or `bf16(s_w * (s_x * acc))` (ScaledEpilogue); the bf16 store is `cvt.rn.bf16.f32` (F2FP)."""
    acc = B.call(bind(DotE4m3, K=S.K), xq, wrow)
    t = B.call(P.F32Mul, sx, acc)                     # Compute0: multiplies(ScaleB, Accum)
    if S.BIAS:
        y = B.call(P.F32Fma, sw, t, B.call(P.Bf16ToF32, bias[0]))  # Compute1: homogeneous_multiply_add(ScaleA, ., Bias)
    else:
        y = B.call(P.F32Mul, sw, t)                   # Compute1: multiplies(ScaleA, .)
    return B.call(P.F2fpBf16, y)


@composite("ScaledMmFp8", 1, ["K", "N", "BIAS"],
           lambda S: (((("xq", Array(S.K, E4M3)), ("sx", F32), ("w", Array(S.N, Array(S.K, E4M3))), ("sw", F32))
                       + ((("b", Array(S.N, BF16)),) if S.BIAS else ())),
                      Array(S.N, BF16)),
           conformance="exact-model-tested; _C.cutlass_scaled_mm vs the model at 320/320 sampled coordinates over five B1 shapes (K=1536/8960, N=1536/2048/17920, bias on/off; gpu/tc-fp8/vllm_fp8_kernels_probe.py --gemm, 2026-09-08) and 0 mismatches at every coordinate-sampled quantised gemm leaf of the production capture (corr-A/B, fp8.md §5); the k32 step pinned by the tc-fp8 campaign")
def ScaledMmFp8(B, S, xq, sx, w, sw, *bias):
    """`_C.cutlass_scaled_mm` on one token row: the N output coordinates (`ScaledMmFp8Coordinate`, one k32 chain + the
    fused epilogue each) over the quantised row `xq` with its scale `sx`, the e4m3 weight rows and the per-tensor `sw`.
    The N children of this call are exactly the coordinates (coordinate-sampled by the correspondence tool)."""
    coord = bind(ScaledMmFp8Coordinate, K=S.K, BIAS=S.BIAS)
    if S.BIAS:
        return B.batch(coord, xq, sx, w, sw, bias[0], axes=(None, None, 0, None, 0))
    return B.batch(coord, xq, sx, w, sw, axes=(None, None, 0, None))


@composite("QuantLinearFp8", 1, ["K", "N", "BIAS"],
           lambda S: (((("x", Array(S.K, BF16)), ("w", Array(S.N, Array(S.K, E4M3))), ("sw", F32))
                       + ((("b", Array(S.N, BF16)),) if S.BIAS else ())),
                      Tuple(Array(S.K, E4M3), F32, Array(S.N, BF16))),
           conformance="exact-model-tested; the two halves are the production nodes (Fp8ActQuant, ScaledMmFp8); as one function on real rows: tests/program/test_fp8.py::test_quant_linear_fp8_on_production_row (layer 0 qkv_proj, t=0/63/130: x_q, s_x and eight output words exact)")
def QuantLinearFp8(B, S, x, w, sw, *bias):
    """The FP8 linear on one token row: `Fp8ActQuant` (computed x_q and s_x from the bf16 row) then `ScaledMmFp8`.
    Returns (x_q, s_x, y) — the three values production materialises.  The layer functions call the two halves as
    sibling nodes (so each captured leaf is a whole call's return); this composite is the linear as one function."""
    q = B.call(bind(Fp8ActQuant, K=S.K), x)
    xq, sx = q[0], q[1]
    y = B.call(bind(ScaledMmFp8, K=S.K, N=S.N, BIAS=S.BIAS), xq, sx, w, sw, *bias)
    return tuple_of(xq, sx, y)


# ---------------------------------------------------------------------------------------------------------
# [R15 fp8] the BLOCK-SCALED FP8 linear of a pre-quantised checkpoint (Qwen3-4B-Instruct-2507-FP8: `weight_block_size = [128, 128]`,
# `weight` e4m3 [N, K], `weight_scale_inv` f32 [N/128, K/128]) on Hopper — `Fp8LinearMethod` -> `CutlassFp8BlockScaledMMKernel`
# (`VLLM_USE_DEEP_GEMM=0`; the DeepGEMM JIT needs nvcc >= 12.3 and is not the panel's path).  Two kernels, both pinned bit for
# bit on the H100 (out/gen/sweep/evidence/fp8/FINDINGS.md; probe_block_gemm.py + check_block_gemm.py, adversarial_cases.py):
#
# 1. `_C.per_token_group_fp8_quant(x, x_q, x_s, 128, eps=1e-10, -448, 448, use_ue8m0=False, column_major_scales=True, tma_aligned=False)`
#    (`per_token_group_quant_8bit_kernel`, csrc/quantization/fp8/per_token_group_quant.cu): per 128-element group of a bf16 row,
#    `absmax = fmaxf-fold from eps of |f32(x_e)|` (an exact max: order-free), `s = absmax / 448.0f` (div.rn), and
#    `q_e = e4m3(fminf(fmaxf(f32(x_e) / s, -448), 448))`.  Both outputs are materialised: x_q e4m3 [M, K] and x_s f32 [M, K/128]
#    (stored column-major; the layout is not part of the value).
# 2. `_C.cutlass_scaled_mm(out, x_q, W.t(), x_s, Ws.t(), None)` -> `cutlass_3x_gemm_fp8_blockwise<bf16, ...>` (CUTLASS v4.7.1
#    `sm90_mma_tma_gmma_ss_warpspecialized_fp8_blockwise_scaling`, ScalePromotionInterval = 128/32 = 4; `GmmaFP8Accumulation::scale_core`:
#    `accum += accum_temp * (sfa * sfb)`).  One output coordinate: over the K/128 tiles in ascending order, `temp` = four
#    `HopperE4m3QgmmaDot32` steps from +0 (wgmma k32, ScaleOut::Zero on the first), `s = FMUL(x_s[kb], Ws[n//128][kb])`,
#    `acc = FFMA(temp, s, acc)` from +0 (nvcc contracts `a += b * c`; pinned against the mul+add and the descending-k alternatives),
#    then `cvt.rn.bf16.f32` (LinearCombination alpha = 1, beta = 0, no bias, no C).  vLLM picks one of two kernel variants by M % 4
#    (M % 4 != 0: swap_ab Pingpong 128x16x128 `<128,1,128>`; M % 4 == 0: Cooperative 128x128x128 `<1,128,128>`): the same arithmetic per
#    coordinate on both (measured on both), so the Definition does not carry the variant.
#
# The weights (`weight` e4m3, `weight_scale_inv` f32) are Inputs of the Program (the checkpoint's stored words: `process_fp8_weight_block_
# strategy` only re-lays them out); the activation words AND their group scales are computed by `Fp8GroupQuant` — never Inputs.
# ---------------------------------------------------------------------------------------------------------

FP8_BLOCK = 128           # the checkpoint's weight_block_size (both axes) and the activation group size (GroupShape(1, 128))
C_EPS_QUANT = b1.const(32, bits_of(np.float32(1e-10)))   # `eps` of per_token_group_quant_fp8 (the fold's start value)

_BLOCK_CONF = ("exact-model-tested; H100 80GB 2026-09-19 (vLLM d9105ea80, CUTLASS v4.7.1, VLLM_USE_DEEP_GEMM=0): _C.cutlass_scaled_mm "
               "blockwise vs the model at 2400/2400 sampled coordinates over seven Qwen3-4B shapes (K 2560/4096/9728, N 2560/6144/19456, M 1..16, "
               "both kernel variants), 0 mismatches; the f32 promotion pinned by adversarial operands (FFMA vs mul+add: 160/160 FFMA, ascending "
               "vs descending k: 160/160 ascending, s = FMUL(sfa, sfb) vs the other associations: 240/240) — out/gen/sweep/evidence/fp8/")
_QUANT_CONF = ("exact-model-tested; H100 80GB 2026-09-19: _C.per_token_group_fp8_quant vs the model on 290,304 e4m3 words and 2,268 group scales "
               "(seven shapes, rows of varying magnitude with outliers), 0 mismatches — out/gen/sweep/evidence/fp8/check_block_gemm.json")


@composite("Fp8GroupScale", 1, ["G"], lambda S: ((("x", Array(S.G, BF16)),), F32), conformance=_QUANT_CONF)
def Fp8GroupScale(B, S, x):
    """One group's scale: `s = fmaxf-fold(eps, |f32(x_e)|) / 448.0f` — the fold is an exact max (fmaxf drops a NaN operand; the
    start value eps = 1e-10f is what the kernel initialises `local_absmax` with), the division an IEEE `div.rn.f32` (not a reciprocal)."""
    m = B.call(C_EPS_QUANT)
    for e in range(S.G):
        m = B.call(F32Fmaxf, m, B.call(F32Fabs, B.call(P.Bf16ToF32, x[e])))
    return B.call(P.F32Div, m, B.call(C448))


@composite("Fp8GroupQuant", 1, ["K", "G"], lambda S: ((("x", Array(S.K, BF16)),), Tuple(Array(S.K, E4M3), Array(S.K // S.G, F32))),
           conformance=_QUANT_CONF)
def Fp8GroupQuant(B, S, x):
    """`_C.per_token_group_fp8_quant` on one bf16 row: (x_q[K] e4m3, x_s[K/G] f32) — per group g, `x_s[g] = Fp8GroupScale(x[gG:(g+1)G])`
    and `x_q[e] = cvt.rn.satfinite.e4m3(fminf(fmaxf(f32(x[e]) / x_s[g], -448), 448))` (a true division; the clamp makes the saturating
    and the software e4m3 conversions coincide).  Both outputs are materialised by production (ports 0 and 1 of the quant node)."""
    K, G = S.K, S.G
    assert K % G == 0, (K, G)
    c448, cneg = B.call(C448), B.call(C_NEG448)
    scale = bind(Fp8GroupScale, G=G)
    qs, ss = [], []
    for g in range(K // G):
        s = B.call(scale, x[g * G:(g + 1) * G])
        ss.append(s)
        for e in range(g * G, (g + 1) * G):
            qs.append(B.call(F32ToE4m3Sat, B.call(F32Fminf, B.call(F32Fmaxf, B.call(P.F32Div, B.call(P.Bf16ToF32, x[e]), s), cneg), c448)))
    return tuple_of(_Coll(Array(K, E4M3), concat([w.refs for w in qs])), _Coll(Array(K // G, F32), concat([w.refs for w in ss])))


@composite("ScaledMmFp8BlockCoordinate", 1, ["K", "G"],
           lambda S: ((("xq", Array(S.K, E4M3)), ("sx", Array(S.K // S.G, F32)), ("wrow", Array(S.K, E4M3)), ("sw", Array(S.K // S.G, F32))), BF16),
           conformance=_BLOCK_CONF)
def ScaledMmFp8BlockCoordinate(B, S, xq, sx, wrow, sw):
    """One bf16 output word of the blockwise CUTLASS GEMM: for kb in 0..K/G-1 (ascending): `temp` = G/32 `HopperE4m3QgmmaDot32` steps
    from +0 over the tile's e4m3 words; `s = FMUL(sx[kb], sw[kb])`; `acc = FFMA(temp, s, acc)` from +0.  Then `cvt.rn.bf16.f32(acc)`."""
    K, G = S.K, S.G
    assert K % G == 0 and G % 32 == 0, (K, G)
    acc = B.call(b1.ZERO32)
    for kb in range(K // G):
        temp = B.call(b1.ZERO32)
        for st in range(G // 32):
            lo = kb * G + 32 * st
            temp = B.call(HopperE4m3QgmmaDot32, temp, xq[lo:lo + 32], wrow[lo:lo + 32])
        s = B.call(P.F32Mul, sx[kb], sw[kb])
        acc = B.call(P.F32Fma, temp, s, acc)
    return B.call(P.F2fpBf16, acc)


@composite("ScaledMmFp8Block", 1, ["K", "N", "G"],
           lambda S: ((("xq", Array(S.K, E4M3)), ("sx", Array(S.K // S.G, F32)), ("w", Array(S.N, Array(S.K, E4M3))),
                       ("ws", Array(S.N // S.G, Array(S.K // S.G, F32)))), Array(S.N, BF16)),
           conformance=_BLOCK_CONF)
def ScaledMmFp8Block(B, S, xq, sx, w, ws):
    """`_C.cutlass_scaled_mm` (blockwise) on one token row: the N output coordinates (`ScaledMmFp8BlockCoordinate`), column n over the
    weight row `w[n]` and the scale row `ws[n // G]` (one f32 per 128x128 weight block).  The N children are the coordinates."""
    K, N, G = S.K, S.N, S.G
    assert N % G == 0, (N, G)
    coord = bind(ScaledMmFp8BlockCoordinate, K=K, G=G)
    parts = [B.batch(coord, xq, sx, w[nb * G:(nb + 1) * G], ws[nb], axes=(None, None, 0, None)) for nb in range(N // G)]
    return _Coll(Array(N, BF16), concat([p.refs for p in parts]))


FP8_BLOCK_COMPOSITES = [Fp8GroupScale, Fp8GroupQuant, ScaledMmFp8BlockCoordinate, ScaledMmFp8Block]


# ---------------------------------------------------------------------------------------------------------
# the layer functions with FP8 linears (structure: TA1's LayerPre/LayerPost with Gemm(+BiasAdd) -> Fp8ActQuant + ScaledMmFp8)
# ---------------------------------------------------------------------------------------------------------


def layer_weights_type_fp8(C: dict) -> Record:
    H_, QKV, GU, I = C["H"], C["QKV"], C["GU"], C["I"]
    fields = [("ln1", Array(H_, BF16)), ("qkv_w", Array(QKV, Array(H_, E4M3))), ("qkv_s", F32)]
    if C.get("BIAS", True):
        fields.append(("qkv_b", Array(QKV, BF16)))
    fields += [("o_w", Array(H_, Array(C["NH"] * C["D"], E4M3))), ("o_s", F32),
               ("ln2", Array(H_, BF16)), ("gate_up_w", Array(GU, Array(H_, E4M3))), ("gate_up_s", F32),
               ("down_w", Array(H_, Array(I, E4M3))), ("down_s", F32)]
    return Record(*fields)


def weights_type_fp8(C: dict) -> Record:
    return Record(("embed", Array(C["V"], Array(C["H"], BF16))),
                  ("layers", Array(C["NL"], layer_weights_type_fp8(C))),
                  ("norm", Array(C["H"], BF16)),
                  ("cos_sin", Array(C["MAX_POS"], Array(C["D"], BF16))))


RMSNormTriton = b1.RMSNormTriton
RMSNormFusedCuda = b1.RMSNormFusedCuda
RoPE = b1.RoPE
SiluMul = b1.SiluMul
BN = H.KBLOCK_N_FA3


@composite("LayerPreFp8", 1, ["C", "L0"],
           lambda S: ((("h", Array(S.C["H"], BF16)), ("res", Array(S.C["H"], BF16)), ("w", layer_weights_type_fp8(S.C)),
                       ("cs", Array(S.C["D"], BF16))),
                      Tuple(Array(S.C["H"], BF16), Array(S.C["NH"], Array(S.C["D"], BF16)),
                            Array(S.C["KVH"], Array(S.C["D"], BF16)), Array(S.C["KVH"], Array(S.C["D"], BF16)))),
           conformance="model-untested")
def LayerPreFp8(B, S, h, res, w, cs):
    """TA1's LayerPre with the QKV projection as `Fp8ActQuant` + `ScaledMmFp8` (bias fused in the epilogue; no BiasAdd node).
    Returns (residual_out, q[NH][D], k[KVH][D], v[KVH][D])."""
    C = S.C
    Hd, NH, KVH, D = C["H"], C["NH"], C["KVH"], C["D"]
    if S.L0:
        x = h
        n1 = B.call(bind(RMSNormTriton, N=Hd, EPS=C["EPS"]), x, w["ln1"])
    else:
        nr = B.call(bind(RMSNormFusedCuda, N=Hd, EPS=C["EPS"]), h, res, w["ln1"])
        n1, x = nr[0], nr[1]
    bias = C.get("BIAS", True)
    q1 = B.call(bind(Fp8ActQuant, K=Hd), n1)  # `qkv_proj.fp8_quant` ports 0 (x_q) and 1 (s_x)
    args = (q1[0], q1[1], w["qkv_w"], w["qkv_s"]) + ((w["qkv_b"],) if bias else ())
    qkv = B.call(bind(ScaledMmFp8, K=Hd, N=C["QKV"], BIAS=bias), *args)  # `qkv_proj.gemm` port 0 (bias fused)
    q = _Coll(Array(NH, Array(D, BF16)), qkv.refs.slice(0, NH * D))
    k = _Coll(Array(KVH, Array(D, BF16)), qkv.refs.slice(NH * D, (NH + KVH) * D))
    v = _Coll(Array(KVH, Array(D, BF16)), qkv.refs.slice((NH + KVH) * D, (NH + 2 * KVH) * D))
    qr = B.call(bind(RoPE, NHEADS=NH, D=D), q, cs)
    kr = B.call(bind(RoPE, NHEADS=KVH, D=D), k, cs)
    return tuple_of(x, qr, kr, v)


@composite("LayerPostFp8", 1, ["C"],
           lambda S: ((("attn", Array(S.C["NH"], Array(S.C["D"], BF16))), ("res", Array(S.C["H"], BF16)), ("w", layer_weights_type_fp8(S.C))),
                      Tuple(Array(S.C["H"], BF16), Array(S.C["H"], BF16))),
           conformance="model-untested")
def LayerPostFp8(B, S, attn, res, w):
    """TA1's LayerPost with o_proj, gate_up_proj and down_proj as `Fp8ActQuant` + `ScaledMmFp8` (no bias).  Returns (mlp_out, residual)."""
    C = S.C
    Hd = C["H"]
    a = _Coll(Array(C["NH"] * C["D"], BF16), attn.refs)
    qa = B.call(bind(Fp8ActQuant, K=C["NH"] * C["D"]), a)  # o_proj.fp8_quant
    o = B.call(bind(ScaledMmFp8, K=C["NH"] * C["D"], N=Hd, BIAS=False), qa[0], qa[1], w["o_w"], w["o_s"])  # o_proj.gemm
    nr = B.call(bind(RMSNormFusedCuda, N=Hd, EPS=C["EPS"]), o, res, w["ln2"])
    n2, r2 = nr[0], nr[1]
    q2 = B.call(bind(Fp8ActQuant, K=Hd), n2)  # gate_up_proj.fp8_quant
    gu = B.call(bind(ScaledMmFp8, K=Hd, N=C["GU"], BIAS=False), q2[0], q2[1], w["gate_up_w"], w["gate_up_s"])  # gate_up_proj.gemm
    act = B.call(bind(SiluMul, I=C["I"]), gu)
    q3 = B.call(bind(Fp8ActQuant, K=C["I"]), act)  # down_proj.fp8_quant
    d = B.call(bind(ScaledMmFp8, K=C["I"], N=Hd, BIAS=False), q3[0], q3[1], w["down_w"], w["down_s"])  # down_proj.gemm
    return tuple_of(d, r2)


# ---------------------------------------------------------------------------------------------------------
# Serve: TA1's `_forward_positions` / `Serve` bodies over the FP8 layer functions (HP's re-instantiation idiom)
# ---------------------------------------------------------------------------------------------------------

ENV: dict = dict(H.ENV)  # Hopper environment (P bound to Hopper prims, BN = 128, Attention -> AttentionFA3, Final -> FinalHopper)
ENV["__name__"] = __name__
ENV["LayerPre"] = LayerPreFp8
ENV["LayerPost"] = LayerPostFp8
ENV["weights_type"] = weights_type_fp8
ENV["layer_weights_type"] = layer_weights_type_fp8
ENV["_forward_positions"] = H._reinstantiate(b1._forward_positions, ENV)

ServeFp8 = CompositeDefinition("ServeFp8", 1, b1.Serve.statics, H._reinstantiate(b1.Serve.signature, ENV),
                               H._reinstantiate(b1.Serve.body, ENV),
                               doc=f"{b1.Serve.doc.strip()}\n\n[b1-fp8] TA1's Serve over LayerPreFp8/LayerPostFp8 (every decoder linear "
                                   "a QuantLinearFp8), HP's AttentionFA3 and FinalHopper (bf16 lm_head); weights record weights_type_fp8.",
                               conformance="model-untested")
ServeFp8.ported_from = b1.Serve  # type: ignore[attr-defined]
LayerPreFp8.ported_from = b1.LayerPre  # type: ignore[attr-defined]
LayerPostFp8.ported_from = b1.LayerPost  # type: ignore[attr-defined]

FP8_COMPOSITES = [Fp8RowAbsMax, Fp8RowScale, Fp8ActQuant, DotE4m3, ScaledMmFp8Coordinate, ScaledMmFp8, QuantLinearFp8,
                  LayerPreFp8, LayerPostFp8, ServeFp8]

#: TA1 call name -> this port's call name (the capture mapping's child selectors are written against TA1's names)
CALL_NAMES: dict[str, str] = {**H.CALL_NAMES, "LayerPre": "LayerPreFp8", "LayerPost": "LayerPostFp8", "Serve": "ServeFp8"}


def set_conformance(status: dict[str, str]) -> None:
    """Set conformance statuses from evidence (the port's expectations / conformance run / the tc-fp8 pin)."""
    by_name = {d.name: d for d in FP8_COMPOSITES}  # the FP8 primitives' conformance is core's
    for name, st in status.items():
        by_name[name].conformance = st


# ---------------------------------------------------------------------------------------------------------
# CPU reference of the two kernels on numpy arrays (for the binding cross-check and the pod experiments)
# ---------------------------------------------------------------------------------------------------------


def np_f32_to_e4m3_sat(x: np.ndarray) -> np.ndarray:
    """Vectorised `F32ToE4m3Sat` over an f32 array (the same function, for whole tensors)."""
    x = np.asarray(x, dtype=np.float32)
    u = x.view(np.uint32)
    sign = ((u >> 31) << 7).astype(np.uint8)
    a = np.abs(x).astype(np.float64)
    out = np.zeros(x.shape, dtype=np.uint8)
    nan = np.isnan(x)
    sat = (~nan) & (a >= 464.0)
    small = (~nan) & (a < 2.0 ** -6)
    normal = (~nan) & (~sat) & (~small)
    # normal binades: e = floor(log2 a); step 2^(e-3); RNE
    e = np.zeros(x.shape, dtype=np.int64)
    with np.errstate(divide="ignore", invalid="ignore"):
        e[normal] = np.floor(np.log2(a[normal])).astype(np.int64)
    step = np.exp2((e - 3).astype(np.float64))
    q = np.zeros(x.shape, dtype=np.float64)
    q[normal] = a[normal] / step[normal]
    q[small] = a[small] / 2.0 ** -9
    n = np.rint(q)  # numpy rint: round half to even, exact on these magnitudes
    # a value that rounds up to the next binade (n == 16) or to 480 (n == 15 at e == 8)
    val = np.where(normal, n * step, np.where(small, n * 2.0 ** -9, 0.0))
    val = np.where(nan, np.nan, val)
    sat2 = (~nan) & (val >= 464.0)
    zero = (~nan) & (val == 0.0)
    sub = (~nan) & (~zero) & (val < 2.0 ** -6)
    norm2 = (~nan) & (~zero) & (~sub) & (~sat2) & (~sat)
    e2 = np.zeros(x.shape, dtype=np.int64)
    with np.errstate(divide="ignore", invalid="ignore"):
        e2[norm2] = np.floor(np.log2(val[norm2])).astype(np.int64)
    m3 = np.zeros(x.shape, dtype=np.int64)
    m3[norm2] = np.rint((val[norm2] / np.exp2(e2[norm2].astype(np.float64)) - 1.0) * 8).astype(np.int64)
    out[norm2] = (((e2[norm2] + 7) << 3) | m3[norm2]).astype(np.uint8)
    out[sub] = np.rint(val[sub] / 2.0 ** -9).astype(np.uint8)
    out[sat | sat2] = 0x7E
    out = (out | np.where(nan, 0, sign)).astype(np.uint8)
    out[nan] = E4M3_NAN
    return out


def np_e4m3_to_f32(b: np.ndarray) -> np.ndarray:
    b = np.asarray(b, dtype=np.uint8)
    sign = np.where(b & 0x80, -1.0, 1.0)
    e = ((b >> 3) & 0xF).astype(np.int64)
    m = (b & 0x7).astype(np.float64)
    val = np.where(e == 0, m * 2.0 ** -9, np.exp2((e - 7).astype(np.float64)) * (1.0 + m / 8.0))
    val = np.where((b & 0x7F) == 0x7F, np.nan, val)
    return (sign * val).astype(np.float32)


def np_bf16_to_f32(w: np.ndarray) -> np.ndarray:
    return (np.asarray(w, dtype=np.uint16).astype(np.uint32) << 16).view(np.float32)


def np_dynamic_per_token_quant(x_bf16: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """CPU twin of `_C.dynamic_per_token_scaled_fp8_quant` on bf16 rows [M, K] -> (x_q [M, K] u8, s_x [M] f32)."""
    xf = np_bf16_to_f32(x_bf16)
    absmax = np.nanmax(np.abs(xf), axis=1, initial=np.float32(0.0)).astype(np.float32)  # fmaxf drops NaN; starts at 0
    absmax = np.where(np.isnan(absmax), np.float32(0.0), absmax).astype(np.float32)
    s = np.maximum((absmax / np.float32(448.0)).astype(np.float32), np.float32(f32_of(MIN_SCALE_BITS))).astype(np.float32)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        r = (xf / s[:, None]).astype(np.float32)
    r = np.fmin(r, np.float32(448.0))     # fminf(x, 448): NaN -> 448
    r = np.fmax(np.float32(-448.0), r)    # fmaxf(-448, x)
    return np_f32_to_e4m3_sat(r), s


def np_online_weight_quant(w_bf16: np.ndarray) -> tuple[np.ndarray, np.float32]:
    """CPU twin of `Fp8PerTensorOnlineLinearMethod.process_weights_after_loading` on the bf16 tensor [N, K]:
    amax over the tensor (aminmax + abs + maximum in bf16 — exact), s_w = f32(amax) / 448 (torch f32 RN),
    W_q = cvt(f32(W) * (1.0f / s_w)) (static_scaled_fp8_quant: reciprocal multiply, then clamp ±448, then cvt)."""
    wf = np_bf16_to_f32(w_bf16)
    amax = np.float32(np.max(np.abs(wf)))
    s_w = np.float32(amax / np.float32(448.0))
    inv = np.float32(np.float32(1.0) / s_w)
    r = (wf * inv).astype(np.float32)
    r = np.fmax(np.float32(-448.0), np.fmin(r, np.float32(448.0)))
    return np_f32_to_e4m3_sat(r), s_w
