---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T03:18Z
---

# 5a answer: sm_120 FP8 mma.sync needs a new GroupSum instance, one group of 32 with a 26-bit adder (neither Ada's nor Hopper's)

- **Instruction:** `mma.sync.aligned.m16n8k32.row.col.f32.{e4m3,e5m2}` at `-arch=sm_120a` is one native **QMMA.16832.F32.{E4M3,E5M2}** per tile (SASS-checked, a single-instruction probe). RTX PRO 6000 Blackwell Server Edition, driver 595.91.07, nvcc 12.8, pod vy-sm120-tc-gemm-1.
- **Result:** `GroupSum(groups=(32,), width=26)` reproduces **every finite word**: 0 mismatches on 6,434,816 elements for e4m3 and 0 on 6,434,816 for e5m2, across 14 families including the adder-width and zero-product families. The existing hypotheses are all refuted:
  - Ada `ADA_E4M3_M16N8K32`, (16,16)/14 bits: 4.91M (e4m3) and 4.09M (e5m2) mismatches.
  - Hopper wgmma, (32,)/14 bits: 4.81M and 4.04M.
  - The sm_90 two-HMMA lowering: 0.76M and 0.77M.
- **What it is:** the same adder as sm_120's BF16 pipeline (Hopper's one group, 26 bits), fed 32 exact FP8 products. Unlike Ada and Hopper, it doesn't truncate the accumulator to 14 bits.
- **The floor is unobservable** with FP8 operands: every value from -126 to at least -145 fits, because products never fall below 2^-32. I'd record it as -133, the BF16 pipeline's, with that note.
- **What this means for the FP8 half:** no new model class. It needs one core constant (`models.py`), two instruction entries, an FP8 step primitive (like `HopperE4m3QgmmaDot32`) with its kernel registration, and more captures to reach PINNED under `trust.py` (a fresh-seed sweep of about 25M elements, specials asserted against total semantics, a canary). I'm leaving that for later, since FP8 is a later night.
- **Evidence (research runs, custody on R2):**
  - probe e4m3 `r20260930-030915-23f3` and its fit `r20260930-031244-ecbc`;
  - probe and fit e5m2 `r20260930-031447-a5ad`;
  - probe branch `cursor/vllm-sm120-fp8-probe-422d` @ `7fd9a186` (tc_probe table entries only).
- **Step 2 status:** captured 2,864 TP1 cases (14 BF16 configs) and 1,930 TP2 cases, all on cuBLASLt. The CPU check is running (`r20260930-031354-3b6d`). A smoke on Qwen2.5-1.5B shapes was exact against Gemm_v2 Hopper. The bias cases hold under the **FP32-epilogue** form, not vLLM's Triton bf16-after form, so qwen2 qkv and Pythia biases on sm_120 need GemmBias semantics different from cc 8.x. Full report next.
