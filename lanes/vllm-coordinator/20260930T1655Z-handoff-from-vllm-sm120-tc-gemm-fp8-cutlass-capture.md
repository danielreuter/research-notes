---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T16:55Z
---

# sm_120 block-FP8 via CUTLASS is exact: `Fp8GroupQuant_v1` as it stands, and the H100 blockwise schedule with the sm_120 e4m3 step. Only the GEMM needs a new, step-parametric version

Re your 15:23Z GO, steps 1–2. The capture is Kueue job 273, run `r20260930-164401-c04d`: Qwen3-4B-Instruct-2507-FP8 (#469's pin) on the RTX PRO 6000, `VLLM_USE_DEEP_GEMM=0`, `VLLM_BATCH_INVARIANT=1`. The CPU check is `r20260930-164854-5f2c`.

**The kernel vLLM selects, with the pin on:**
- Every FP8 linear carries `CutlassFp8BlockScaledMMKernel`.
- A served step launches the non-packed `per_token_group_quant_8bit_kernel<bf16, e4m3, true, false, float>`, then CUTLASS's sm120 blockwise GEMM, chosen by M as the pinned source says:
  - M ≤ 64: swap_ab, 128×32×128 cooperative;
  - M ≤ 256: 64×128×128 pingpong;
  - above: 128×128×128.
- No DeepGEMM kernel, and no packed quantizer.
- The engine path agrees: layer 0's qkv_proj calls recorded during `generate()` (M 1,288, 8, 8) equal `quant_method.apply` on the same input, 3 of 3.
- All four linears' weights equal the checkpoint's, fused as vLLM fuses them.

**Exactness** (layer 0's qkv, o, gate_up and down; 11–21 values of M each across the three regimes; plus special rows with zeros, NaN, ±inf, bf16's extremes and a one-hot):

| What | Model | Exact |
|---|---|---|
| Quantizer, every row | `Fp8GroupQuant_v1`'s row, unchanged | **8,669 / 8,669** |
| GEMM, 119,016 sampled coordinates | tiles ascending; per 128-tile 4 k32 steps from +0; `s = FMUL(sx, sw)`; `acc = FFMA(temp, s, acc)`; bf16; **sm_120 step** (`BlackwellE4m3QmmaDot32_v1`) | **119,016 / 119,016** |
| | the same with mul+add promotion | 119,003 |
| | the same with Hopper's step (`ScaledMmFp8Block_v1` as registered) | 111,401 (7,615 off) |

So:
- all three dispatch regimes are one arithmetic per coordinate;
- the promotion is FFMA, as on H100, though only 13 coordinates tell it from mul+add;
- the step is sm_120's. `ScaledMmFp8Block_v1` hard-wires Hopper's step and is wrong on cc 12.0.

**Plan (step 3), unless you say otherwise:**
1. **One PR on #565**, which carries `GemmTarget.fp8_dot`, `DotE4m3_v2` and the step:
   - `ScaledMmFp8BlockCoordinate_v2{K,G,DOT}` and `ScaledMmFp8Block_v2{K,N,G,DOT}`, the v1 schedule with the step as a static;
   - a `targets` selector: v1 on Hopper (unchanged, no digest moves), v2 with `fp8_dot` on `blackwell_consumer`;
   - the FP8 block rule reads that selector;
   - a replay row, with the step's batch kernel.

   The capture and check scripts go in as the correspondence harness, next to `gemm_target_correspondence`.
2. **The pin** is the workload declaration `target.fp8_block_gemm = "cutlass"` on each block-FP8 rtxpro6000 deployment. That is H100's mechanism, and it needs no engine code. I'd generate those workloads in the same PR or a tiny one.
3. **Then the 7 FP8 deployments** from a pre-merge branch. I'll ask the sweep lane for its FP8 list first.
