---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# vLLM hardware-semantics assumptions

vLLM coordinator, started 2026-09-30 05:57Z. Overnight objectives, workstream 2.

**What this is:** the facts about the GPU and its libraries that the vLLM integration's Definitions rely on, but that no replay can check by itself. A config run passes its gate when the committed words replay bit-exact. That shows the Definition matched *that* run. The rows below say why it should keep matching.

**How rows get rated:** the red team rates each row **holds**, **holds with conditions** or **broken**. Ratings are labels, not edits to this table:

~~~text
research data label <run id|art:…> semantic-assumption "<moniker>=<holds|conditions|broken>" --by red-team-<name> --ref <run id> --off-vocab
~~~

The key is deliberately not `ov.*`: the overnight dashboard would list `ov.` labels without `ov.ws` as label problems.

POUS's red team (contact bc-2aa33ad8) uses the same monikers; we accept their evidence as labels. **Status** below is our own position until a red-team label exists. Clock or power experiments on vy-nebius-1 go through its owner, bc-96a2e856.

| Moniker | Assumption | Binds where | Evidence so far | Status |
|---|---|---|---|---|
| `gemm-hopper-step(arch, bf16)` | BF16 linears on the Hopper-step targets (H100 sm_90 wgmma; sm_120 `mma.sync`, cuBLASLt with split-K off) accumulate exactly as `HopperBF16WgmmaDot16_v1`. **The Lean GEMM relation proof ([#490](https://github.com/danielreuter/verity/pull/490), 0 `sorry`) shows the relation is exactly equivalent to this step's semantics, so what's left to trust is only this hardware assumption.** | `Gemm_v2{DOT=Hopper…}` on H100 and `blackwell_consumer` (#465, #476) | H100: core registry `sm90.wgmma` bf16 entries, PINNED, and `tests/ml/fixtures/tc-hopper-2026-09-07/`; sm_120: tc-gemm captures on RTX PRO 6000, 0 mismatches | **holds with conditions** (red team, `r20260930-074229-b966`: the underflow floor isn't pinned by the captures) |
| `gemm-ampere-step(arch, bf16)` | BF16 linears on the Ampere-step targets (A100 sm_80, RTX 4090 sm_89; `mma.sync.m16n8k16` bf16, split-K off) accumulate exactly as the Ampere step (`AmpereBF16TcDot16_v2`, `veritor.tensor-core.ampere_bf16_m16n8k16@3`). **The Lean GEMM relation proof ([#490](https://github.com/danielreuter/verity/pull/490), 0 `sorry`) shows the relation is exactly equivalent to this step's semantics, so what's left to trust is only this hardware assumption.** | `Gemm_v*{DOT=Ampere…}` on L40S/A100/RTX 4090 rows (every row of record before the sm_120 port) | Under `packages/verity/tests/ml/fixtures/`: `tc-total-2026-09-07/{a100,4090}/` (31,290 special-value + 906 positional cases per device, 0 nondeterministic; `cvt.rn.bf16.f32` on 4,403 words each); `golden/ada_bf16_m16n8k16.json` (RTX 4090, 360 `mma.sync` records, 9 families); `vectors/tc-ampere-bf16-total-hw.json` (gate-set vectors with `a100`/`rtx4090` columns); `gemm-B1-b3eba618b1b5-20260907T1731Z/` (30 authenticated GEMM coordinates from the RTX 4090 eager port). Core registry: the sm_80/sm_89 bf16 `mma.sync` entries, PINNED. | **holds with conditions** (red team, `r20260930-074229-b966`: the underflow floor isn't pinned by the captures) |
| `bias-f32-epilogue(M≥2)` | For M ≥ 2 with bias, the epilogue adds the bias in FP32 before one rounding to BF16. | `GemmBiasF32Epilogue_v1` (#483) | 720/720 cases exact, M ≥ 2 | holds (on our evidence) |
| `gemv-tree(cuBLAS table v1)` | For M = 1 with bias, cuBLAS gemvx sums strided or blocked FP32 partials in a halving tree, then adds the bias in FP32; the (K,N)→(V,T) table is fixed at the pinned cuBLAS. | `GemvBiasF32_v1{K,N,V,T}` (decided 05:23Z; being built) | tree recovered; T table in progress | open |
| `cublas-selection-stable(shape, workspace, streams)` | For a given shape, workspace size and stream setup, cuBLAS(Lt) picks the same algorithm on every run and host at the pinned library version. | every cuBLAS-bound linear | one host per capture so far | open, **key red-team target** |
| `no-nondeterministic-split-k` | No bound GEMM uses split-K with atomics, or any reduction order that depends on scheduling. | all linears; fused MoE | split-K off at the pinned vLLM (tc-gemm) | holds with conditions (the pinned vLLM and cuBLAS) |
| `fa2-as-attention_v5` | FA2 on sm_120 is `Attention_v2{DOT=Hopper, INV=Fa2InvSum}` on every finite head, and `Attention_v5` models its partial `-inf` guard. | #477, #486 | 122,228 heads exact, including 112 non-finite (v5) | holds (on our evidence) |
| `fa-check-inf-placement` | FA2/FA3 apply `check_inf` at the placement each Definition models, on every FA target. | Attention on sm_89, sm_90, sm_120 | the attention lane: placement holds on every FA2 target | holds with conditions (sm_89 and sm_90 unchanged by decision) |
| `mufu-tables` | The MUFU `ex2` and `rcp` outputs equal the recorded tables on every die of an architecture. | softmax, SiLU, attention | captured per architecture | holds with conditions (per architecture; not per die) |
| `splits-constants(142, 188)` | The top-p split and drain schedules depend on the SM count (142 on L40S, 188 on RTX PRO 6000) and on nothing else. | sampling (#480, #481) | 162/162 split cases, drain at every boundary | holds (on our evidence) |
| `moe-expert-dot(sm_120)` | The fused-MoE expert GEMMs on sm_120 run the Hopper-shaped k16 step. | `MoeExpertGemm_v2{DOT}` (#481) | 0 of 2 × 1,048,576 words differ | holds (on our evidence) |
| `moe-router-fmaxf-nan` | The MoE router's `fmaxf` handles NaN as the Definition does. | MoE router top-k | the kernels lane: `topk_softmax` exact | open (NaN inputs not probed) |
| `fp8-per-tensor-scale-order` | Per-tensor FP8 linears compute `bf16(sa*(sb*acc))` in that order. | FP8 linears (tc-gemm step 5b) | settled 04:45Z | holds (on our evidence) |
| `fp8-e4m3-step(sm_120)` | sm_120 FP8 `mma` accumulates as the fitted sm_120 e4m3 step. The trust level is computed on the RTX PRO 6000 as the Target's `anchor_device`, not the RTX 5090. | FP8 linears; core registry `sm120.mma.*.e4m3/e5m2` | fitted; the PINNED sweep is queued on vy-nebius-1 (decision 05:57Z) | open until the dossier exists |
| `fp8-block128` | Block-scaled FP8 is `ScaledMmFp8Block_v1` with the sm_120 step swapped in. | FP8 block-128 checkpoints | tc-gemm | open |
| `fp4-block-scaled(sm_120)` | vLLM's NVFP4 path on sm_120 runs `BlockScaledAlignAdd` (`mma.sync kind::mxf4nvf4`), pinned on the RTX 5090, and the pin extends to the RTX PRO 6000. | NVFP4 linear + `cvt_fp16_to_fp4` quantizer (Definition assigned to tc-gemm 08:39Z) | kernel capture on RTX PRO 6000: `CutlassNvFp4LinearKernel` = `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`, the pinned instruction (attention lane, 08:35Z); pin evidence still on RTX 5090 dies, PRO 6000 sweep pending | holds with conditions (kernel matches; the PRO 6000 pin and quantizer exactness are pending) |
| `silu-edge-cases` | `SiluMul_v1` matches on NaN (0x7FFF vs 0x7FC0), on gates below -88.7, and on signed zeros. | every SiLU | the kernels lane: all three differ | **broken at the edges** (finite ordinary inputs exact) |
| `rope-overflow-domain` | `RoPE_v1` is exact whenever \|cos\|,\|sin\| ≤ 1. | rotary | 34/48; every failure needs an operand whose product overflows f32 | holds with conditions (a real cos/sin cache) |
| `clock-and-power-invariant` | The committed words don't depend on the clock, power cap or temperature. | everything | vy-nebius-1 is locked at 2,100 MHz; RunPod pods are unlocked | open, **red-team target** (through bc-96a2e856) |
| `capture-complete` | The capture sees every kernel whose output the Program claims, and none runs unobserved. | the Commit | strict word check per config | open |
| `fold-sm120-linears` | A full row with Match can fold sm_120 linears. | Match only; config runs skip it | the fold returns Unsupported | **broken (known gap)**; low-priority fix (decision 05:57Z) |
| `p2p-copy-sm120-sys` | TP2 on a PCIe host without P2P gives correct collectives with `NCCL_P2P_DISABLE=1`. | TP2 on RTX PRO 6000 | live TP2 25/25; a raw torch P2P copy returns zeros on the SYS host | holds with conditions (P2P off) |

**How to add a row:** add it here with its binding and evidence, then ask the red team to rate it.
