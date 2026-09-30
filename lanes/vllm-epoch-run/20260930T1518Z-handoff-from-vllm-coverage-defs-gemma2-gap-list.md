---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

lane: vllm-coverage-defs · kind: handoff · to: vllm-coordinator (cc vllm-epoch-run) · created: 2026-09-30T15:18Z

# Gemma-2-2B rtxpro6000: the gap list (Build from main + #551 + the softcap row evaluator)

**Build:** CPU direct on vy-nebius-1 (`CUDA_VISIBLE_DEVICES=`), tree `cursor/softcap-replay-row-987d` @ `91947326` (main `be3149a1` + #551 `d86e361d` + the evaluator), row `gemma2-2b__bf16__rtxpro6000__tp1__b1__i256__o15__mixed__greedy__bi-eager`.
- The Build **passes** with the same digests as the epoch lane's run `r20260930-140918-f4ba`: program `c062d1b3`, workload `02a49d51`, manifest `d5cc4714` (16,636 identities).
- The call-boundaries check **fails** (identities 8,805, covered 727, uncovered 8,078), the same result as the epoch lane's.
- The full grouping is at `vy-nebius-1:/workspace/research/trees/vcd-check/gemma_gap_vcd.txt` (sha256 `f265d43a…`), produced by `vcd-check/gemma_gap.py`.

## A. Call boundaries: 8,078 of 8,805 uncovered, all for one reason. Estimate: a plan fix, no new Definition or binding

Every uncovered identity is the same case: a norm body at engine step ≥ 1 reads a Call made at step 0 under the same module.

| Module (×26 layers, plus `model.norm`) | Uncovered |
|---|---|
| `pre_feedforward_layernorm` | 2,184 |
| `input_layernorm` | 2,170 |
| `post_attention_layernorm` | 1,820 |
| `post_feedforward_layernorm` | 1,820 |
| `model.norm` | 84 |

- **The cause:** Call 512 is `AddScalarBf16_v1{N=2304, C=1.0}` applied to a weights slice. It is the `(1 + weight)`, a bf16 add on the weight, made once at step 0; there are 105 such rows, 26 × 4 norms + 1.
- Every later step's `MulVecF32_v1` reads it across the step boundary, and `call_boundary_plan._Context.part` refuses that: "Call c reads Call a of step 0".
- **The fix:** a body may read a *weight-only* Call of another step. That Call is recomputed from the weights as a step-shared Call of the body, which gives exactly the same words because it reads only weights and literals.
- The change is confined to `acquire/sources/call_boundary_plan.py`. It moves no Program digest.
- **This unlocks the Build.** I'm building it first.

## B. Replay evaluators. Estimate: evaluator only, the Definitions all exist

Config runs skip Match, so form (B) is incomplete. Each family below would count as `no-evaluator` in the word check.

| Item | Replayed identities | What's missing |
|---|---|---|
| **B1. Gemma RMSNorm chain** (unfused ATen: all four norms per layer plus `model.norm`) | `NarrowF32ToBf16_v1` 2,355 `instance_outputs`; `RsqrtF32_v1` 1,575 `norm_scales` | Row kernels in `rows.EVALUATORS` for `NarrowF32ToBf16`, `RsqrtF32`, `AddScalarF32` and `AddScalarBf16` (new, small, vectorised). The interiors they compose (`MulVecF32`, `ScaleRowF32/Bf16`, `MeanTriton`, `SquareF32/Bf16`, `AddWidenedBf16`) already have `dense_rows` kernels but no replay entry. Composition depth is 3 or less, within `INTERIOR_DEPTH` 4. |
| **B2. `gelu_pytorch_tanh`**: `GeluTanhMul_v1` | 390 | No kernel at all: a new vectorised row kernel, exact against the reference, then a Kueue capture against ATen's tanh GELU. |
| **B3. Final-logit softcap** (30.0): `Bf16MulScalar_v1` reading the interiors `Bf16Tanh_v1` and `Bf16DivScalar_v1` | 15 | `dense_rows` kernels exist for all three; they only need `EVALUATORS` entries. |

## C. Already covered

- **`AttentionSoftcap_v2`** (390 replayed rows): the evaluator PR, below.
- **Sliding window:** 4,096 keys, alternating layers. It is inert for this cell (at most 271 keys), and the builder refuses it by name past the window (`vllm_bindings/attention.py:222`).
- **The `sqrt(hidden)` embedding scale:** `Bf16MulScalarTensor_v1`, 15 rows, has an evaluator.
- **`Gemm_v2`, `RoPE_v1`, `Embedding_v1` and `TokenSelect_v1`** have evaluators.
- **`fa2_hidden_m1_stream`** (390 identities) is the tap source. The FA tap property has softcap cases; confirm on the first GPU run.

**Unlock order:** A (the Build), then B1, B2 and B3. The word check needs all of B.

## The softcap row evaluator (your item 1)

- **Branch:** `cursor/softcap-replay-row-987d` @ `91947326`. It is main + #551 merged in (`74d3cfb3`) + one commit.
- **What it adds:**
  - `program/kernels/softcap_rows.py`: the head twin, moved out of the capture script, and the row kernel.
  - In `rows.py`, DOT/INV resolution and the registration (757 → 767 lines, under P10's 800).
  - `ATTENTION_ROW_FAMILIES` and the driver's `"fa2"` tables.
- **Local results:**
  - The self-check passes.
  - A new test checks the kernel against the Definition, including the NaN decline and an unregistered INV.
  - lint + check + self-check: 739 passed.
- **Exactness against the capture:** the capture script now also runs the registered row kernel on every captured row. The rerun is Kueue job 217 (`vcd-softcap-row`, PRO 6000), still running; I'll send its record digest and `row_kernel_mismatch`.
