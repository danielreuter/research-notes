---
id: 20261001T1010Z-report-from-circuits-bool-elementwise-done-gemma-olmoe-on-bits
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-elementwise
---

# @circuits: element-wise family done. Gemma-2's and OLMoE's element-wise rows and OLMoE's router are on bits, the softcap tanh went to silu, head `9366d8afc` (3:10 AM PDT)

Branch `cursor/bool-elementwise-8c79` at `9366d8afc`, pushed, no PR.

- **Base.** proofs-ir's frozen `46c768b2c`, plus proofs-mufu's final `3bf1b6d02` and `cursor/bool-trace-emit-f91f`, both merged.
- **circuit-check.** Green on all 45 of the lane's targets, with 0 warnings: `art:9257ee132724da9c0c594968becceab1cd769af5ce8136ca56cf74444b6398ee`.
- **Inventory.** `note:20261001T0700Z-report-from-circuits-bool-elementwise-inventory`.
- **Boolean-purity dry runs.** `art:9a147dacaf285a8a604a85ecf13be5b02be7a752a33fa64f48105716fcdac57b`.

## Converted

Each row is pinned in its test, by And/Xor/Not counts and standalone program digest, and in circuit-check's `pins.json`. Each
word view is the current word Definition at the same statics.

| Boolean Definition | Where | ANDs at the pinned binding |
|---|---|---|
| `GeluTanhMulBf16_v2`, `GeluTanhMul_v2{I}` | `boolean_dense` (Gemma-2 GeGLU) | 1,347; 10,776 at I = 8 |
| `SquareBf16_v2{N}`, `SquareF32_v2{N}` | `boolean_dense` (Gemma-2 RMSNorm chain) | 5,024; 15,824 at N = 8 (628, 1,978 per element) |
| `AddScalarF32_v2{N,C}`, `AddScalarBf16_v2{N,C}` | `boolean_dense` | 5,936 at C = 1e-6; 4,968 at C = 1.0 |
| `AddWidenedBf16_v2{N}` (the residual add in f32) | `boolean_dense` | 5,328 |
| `ScaleRowBf16_v2{N}`, `ScaleRowF32_v2{N}`, `MulVecF32_v2{N}` | `boolean_dense` | 9,138; 19,202; 19,440 |
| `Bf16DivScalar_v2{N,C}`, `Bf16MulScalar_v2{N,C}` (the logit softcap's divide and multiply) | `boolean_dense` | 6,920; 5,032 at C = 30 |
| `Bf16MulScalarTensor_v2{N}` (the embedding scale) | `boolean_dense` | 6,266 |
| `Bf16Add_v2` (Qwen2.5's bias add), `Bf16MulBf16_v2`, `Bf16MulF32_v2` | core `verity.ml.boolean.elementwise` | 717; 799; 1,220 |
| `MoeSumCoordinate_v2{TOPK}`, `MoeSum_v2{TOPK,H}` | `boolean_moe` (OLMoE combine) | 5,222; 41,776 at TOPK = 8, H = 8 |
| `NvExpf_v2` = `NvExpfIn_v1` + `MufuEx2Ftz_v2` + `NvExpfOut_v1` | `boolean_moe` (the router's expf) | 11,372 (9,556 + 1,073 + 743) |
| `MoeRouterTopKOrdered_v2{E,TOPK,VPT}` (`MoeRouterProbs_v2`, `MoeRouterShift_v1`, `MoeRouterNormalize_v1`, `MoeRouterSelect_v1`) | `boolean_moe` (OLMoE router) | 126,243 at {8, 2, 4}; served {64, 8, 8}: 1,066,321 |

The first task's six (`F32{Add,Mul,Fma,Div}_v3`, `Bf16AddF2fp_v2` and `I32Add_v2`) are unchanged.

**MUFU.** The router's expf has the one MUFU use its word Definition makes, a sub-Call to proofs' `MufuEx2Ftz_v2`. No other row
reads a MUFU.

**Exactness.** Each row matches its word Definition exactly on every input checked:
- Every one-word bf16 row: all 65,536 words.
- `NvExpf_v2`: 241,168 words (specials, every exponent edge, random words).
- The low byte of `fma.rm(sat, 252, 12582913)`, exhaustively over all 1,065,353,217 words in [+0, 1].
- The router: every row tested, at five shapes, the served one included.

**Partition.** Every root passes `Q_word_v1{X=16, W=32}` with no recomputed gate.

## Acted on since 2:05 AM PDT

- **Scope change** (`20261001T0716Z-handoff-from-circuits-activations-to-silu`, which I only saw at 3:00 AM PDT).
  - I retired my `Bf16Tanh_v2{N}` (443 ANDs per element) in `9366d8afc`. circuits-bool-silu's `boolean_activation` registers
    the same id at 391 ANDs per element.
  - GeLU stays in `boolean_dense`: silu retired its own copy as a duplicate of mine in `59b134051`. It is silu's from now on,
    whether it stays where it is or moves to `boolean_activation`.
- **Activations in the six Programs, for circuits-bool-silu:**
  - Gemma-2: `GeluTanhMul_v1{I=9216}` → `GeluTanhMulBf16_v1` (on bits, mine); `Bf16Tanh_v1{N=256000}` (silu's); and the
    attention softcap's `MufuTanh_v1`, inside `AttentionSoftcap_v2` (blocked on proofs, as silu reported).
  - Llama-3.2-1B, Qwen2.5-0.5B, Qwen3-4B, Phi-3-mini and OLMoE's experts: `SiluMul_v1` / `SiluMulBf16_v1` only (silu's `_v3`,
    done).
- **Import error in merged trees** (silu's report). `elementwise` imported `trace._body`, which `cursor/bool-trace-emit-f91f`
  renamed to `emit`. I merged that branch and use `emit` (`7e254313f`). The family's branches now merge without that error.
- **Same ids defined twice.** proofs-ir-attn's new core `verity.ml.boolean.scalar` (`1256f06fc`) defines `F32Add_v3`,
  `F32Mul_v3`, `F32Fma_v3` and `F32Div_v3` again. They are the same circuits (identical counts and program digests to my pins).
  A tree with both raises `registry already has a different definition`. Handoff to proofs-ir:
  `note:20261001T1006Z-handoff-from-circuits-bool-elementwise-f32-v3-ids-twice`.
  - The proposal: whichever branch lands second imports the four from the other's module.
  - No other collision. I scanned the ids every Boolean module defines on silu, switch, sampling, softcap-attn, norms, rope,
    casts and the proofs branches.
- **`on_bits` in core** (`94755e6a5`). `verity.ml.boolean.elementwise.on_bits` builds a Boolean composite whose word view is
  a word composite at the same statics. `boolean_dense` and `boolean_moe` had identical private copies of it; both now call the
  core one, with counts and digests unchanged.

## Checks at `9366d8afc`

- **Suites.** `suites.py --quick` passes for verity, verity-vllm, verity-circuit-check and repository.
  `tests/query/test_tp_moe_members.py` is left out: it runs out of memory on this 15 GiB VM, and it isn't mine.
- **AGENTS.md.** Its diff against the base is only the map line for `elementwise`.

## Still open

- **Rebase onto main** once proofs-ir lands (main is still `6c566874c`).
- **`targets.py` and `pins.json`** conflict between every pair of family branches. The union of both sides resolves them.
