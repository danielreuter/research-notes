---
id: 20261001T0700Z-report-from-circuits-bool-elementwise-inventory
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-elementwise
---

# Boolean inventory of six more served Programs (circuits-bool-elementwise, Oct 1, 12:00 AM PDT)

**Sources.** B1 greedy i256 workload Programs (`build_workload/descriptor.json.gz` on node 1):
- `cov-k05-7` Llama-3.2-1B
- `cov-k03-8` Qwen2.5-0.5B
- `cov-g242` Qwen3-4B
- `cov-k06-7` Gemma-2-2B (o15)
- `cov-k07-3` Phi-3-mini
- `cov-k15-5` OLMoE-1B-7B
- `cov-k01-10` SmolLM2-135M, as the baseline

"Uses" are dynamic instances: call, batch and scan multiplicities propagated from the root.

**Boolean status.** It comes from `verity-vllm boolean-purity --dry-run` on a scratch merge of the switch branch with elementwise, rope, sampling and silu (not pushed).

## What is new beyond SmolLM2

- **Llama-3.2-1B, Qwen3-4B, Phi-3-mini:** SmolLM2's Definitions exactly, with other statics and a new vocabulary gather (`GatherBf16x{128256,151936,32064}_v1`). Nothing new for element-wise.
  - Qwen3-4B's QK norm puts `RMSNormTriton_v1` at 413,567 Calls, so the norms worker's `DivFull*` and `MufuSqrtFtz` count there.
- **Qwen2.5-0.5B:** the biased linear `GemmBias_v2` → `GemmBiasCoordinate_v2` → `Bf16Add_v1` (7.9M uses).
- **Gemma-2-2B:** 13 new derived Calls (the torch-native GemmaRMSNorm chain, GeGLU and the final logit softcap) and softcap attention.
- **OLMoE-1B-7B:** expert GEMMs (`MoeExpert*`, with `GatherBf16x64_v1` at 231G uses), the ordered top-k router and `MoeSum_v1`.

## Family → Definitions → owner

| Family | Definitions (models, uses) | Boolean today | Owner |
|---|---|---|---|
| **Activation: GeGLU** | `GeluTanhMul_v1{I=9216}` (Gemma, 7,020 Calls) → `GeluTanhMulBf16_v1` (64.7M) | none | **elementwise** (converting now) |
| **Activation: logit softcap** | `Bf16DivScalar_v1{N=256000,C=30}`, `Bf16Tanh_v1{N=256000}` → `TanhF32Rn_v1` (3.84M), `Bf16MulScalar_v1{N=256000,C=30}` (Gemma, 15 Calls each) | none | **elementwise** |
| **Element-wise: Gemma's RMSNorm chain** | `MulVecF32_v1` (28,350 Calls × 2304), `ScaleRowF32_v1`, `ScaleRowBf16_v1`, `SquareF32_v1`, `SquareBf16_v1` (~14k Calls each), `AddScalarF32_v1` (28,350 × 1), `AddScalarBf16_v1` (105), `AddWidenedBf16_v1` (the residual add in f32, 14,040) | none (their `F32Add_v1`/`F32Mul_v1` are `_v3`) | **elementwise** |
| **Element-wise: embedding scale** | `Bf16MulScalarTensor_v1{N=2304}` (Gemma, 270) | none | **elementwise** |
| **Element-wise: bias add** | `Bf16Add_v1` (Qwen2.5, 7.9M, inside `GemmBiasCoordinate_v2`) | none | **elementwise** (the add); the coordinate is GEMM → proofs |
| **Element-wise: MoE router softmax and top-k** | `MoeRouterTopKOrdered_v1{E=64,TOPK=8,VPT=8}` (4,592 Calls) → `MoeRouterProbs_v1`, `MoeRouterFirst_v1`, `MoeRouterNext_v1`, `MoeRouterPick_v1`, `RouterArgmaxStep_v1`, `NvExpf_v1` (expf: `F32Sat`, `F32FmaRm`, `F32Neg`, `F32BitsShl23`, a `MufuEx2Ftz_v1` sub-Call), plus `F32Sub`, `F32Fmaxf`, `F32IsFinite`, `F32Eq`, `F32GtStrict`, `SelectF32` (7.3M), `I32Eq`, `I32Le`, `BitAnd`/`BitOr`/`BitNot` (2.1M each) | none (`I32Add_v2`, `F32{Add,Mul,Fma,Div}_v3` and `SelectI32_v2` exist) | **elementwise**; `MufuEx2Ftz` stays a word-id sub-Call until proofs-mufu publishes `_v2` |
| **Element-wise: MoE combine** | `MoeSum_v1{TOPK=8,H=2048}` → `MoeSumCoordinate_v1` (9.4M) | none | **elementwise** |
| Element-wise (SmolLM2 set) | `F32Add`, `F32Mul`, `F32Fma`, `F32Div`, `Bf16AddF2fp`, `I32Add` | `_v3`/`_v2` (elementwise @ `0d2dc46fe`) | elementwise, done |
| GEMM | `Gemm_v2`, `GemmCoordinate_v2`, `DotBf16_v2`, `HopperBF16WgmmaDot16_v1`; new: `GemmBias_v2`, `GemmBiasCoordinate_v2` (Qwen2.5); `MoeExpertGemm_v2`, `MoeExpertGemmW_v2`, `MoeExpertCoordinate(W)_v2`, `MoeExpertRow_v1` (OLMoE) | `GemmCoordinate_v3`, `DotBf16_v3` | proofs |
| Attention | `Attention_v5` family; new: `AttentionSoftcap_v2`, `AttentionHeadSoftcap_v2`, `AttnBlockSoftcap_v2` (Gemma, 147,680 blocks) | the `_v3` FTZ arithmetic | proofs |
| MUFU | `MufuEx2Ftz`, `MufuSqrtFtz`, `RsqrtApprox`, `DivFullRcp`, `DivFullScaleA`; new: **`MufuTanh_v1`** (Gemma attention softcap, 7.6M) | none | proofs (proofs-mufu) |
| Norms | `RMSNormFusedCuda_v2`, `RMSNormTriton_v1`; new: `MeanTriton_v1` (Gemma, a reduction with `DivFull*`), `RsqrtF32_v1` (Gemma, a batch of `RsqrtApprox`) | none | norms |
| Casts and gathers | `Bf16ToF32`, `F2fpBf16` (`_v2` in proofs-ir's gemm), `Embedding`, `Input16/32`; new: `NarrowF32ToBf16_v1` (Gemma), `GatherBf16x{128256,151936,256000,32064,50304}_v1`, **`GatherBf16x64_v1`** (OLMoE expert-row gather, 231G uses, the largest count in any Program) | `F2fpBf16_v2` | casts |
| RoPE | `RoPE_v1`, `RoPEHead_v1`, `RopeOut(Add)_v1` (all six) | `_v2` (rope branch) | rope, done |
| SiLU | `SiluMul_v1`, `SiluMulBf16_v1` (also inside OLMoE's experts) | `_v3` (silu branch) | silu, done |
| Sampling | `TokenSelect_v1`, `ArgmaxStep_v1`, `Bf16GtStrict_v1`, `SelectBf16_v1`, `SelectI32_v1` | `_v2` (sampling branch) | sampling, done |

**Ownership calls I made:**
- Gemma's RMSNorm chain is unfused element-wise Calls, so the generic ones are mine. `MeanTriton` and `RsqrtF32` go to norms and `NarrowF32ToBf16` to casts.
- The MoE router is mine. Its argmax step reuses sampling's `SelectI32_v2`.
- Tell me if norms or sampling should take any of these instead.

## Order of conversion (most-used first, each green before the next)

1. `GeluTanhMulBf16_v2` and `GeluTanhMul_v2{I}`. The gelu half is a function of the 16-bit gate word. It is built the way silu's `SiluMulBf16_v3` is, as plain gates with no table gate. The word Definition makes no MUFU call, so neither does this.
2. Gemma's element-wise composites (11), on `F32Add_v3`/`F32Mul_v3` and the core `Bf16MulF32_v2` and `Bf16MulBf16_v2`.
3. `Bf16Add_v2`.
4. The OLMoE router and `MoeSum`. `NvExpf_v2` keeps `MufuEx2Ftz_v1` as its sub-Call until proofs-mufu publishes `_v2`; reported then.
5. `Bf16Tanh_v2` (a 16-bit function, as in step 1).

**Gaps that stay outside my family:**
- Proofs: `MufuTanh_v1`, softcap attention, `GemmBias`, the MoE expert GEMMs.
- Casts: `GatherBf16x64_v1` and the new vocabulary gathers.
- Word constants (`Const16`/`Const32`) are still callees of every word composite. Each Boolean body makes them from `Const1` bits.
