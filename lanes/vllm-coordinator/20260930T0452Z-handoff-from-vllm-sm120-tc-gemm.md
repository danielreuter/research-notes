---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T04:52Z
---

# gemvx closed inside the time box: the M=1 bias linear is modelable exactly (strided or blocked FP32 partials, then a halving tree, then the bias in FP32); bias Definition PR #483 is up

- **The gemv time box closed in about 40 minutes of agent time and under 0.1 GPU-h.**
  - **Probe:** cancellation triplets at M = 1 with a bias (x = 1, bias = 0; a weight row has +2^25 at i, -2^25 at j, +1 at an anchor l). The "+1" survives only if i and j merge before either meets l, so the probe reads the reduction tree directly. Runs `r20260930-042955-f567` (3 shapes x 3 anchors) and `r20260930-044507-fe26` (the 14 bias shapes of the Qwen2 family and Pythia at TP1 and TP2).
  - **Structure (0 mismatches on every triplet, about 25M in all):** T threads per output; thread t sums the positions of chunks c with c % T == t (chunk width V) in ascending k, left-deep in FP32. The T partials then reduce by a halving tree (offsets T/2 ... 1, i.e. the warp butterfly), and the bias is added in FP32 before RNE to bf16.
  - **V and T are cuBLAS's choice per (K, N)** on this GPU and cuBLAS (torch 2.13 cu129):
    - V=1, T=32: (896,1152), (896,576), (1536,1024), (1536,768), (768,1152), (768,768), (768,1536), (384,768), (3072,768).
    - V=1, T=16: (1536,2048), (3584,4608), (3584,2304), (768,3072).
    - V=48, T=16 (contiguous blocks): (768,2304), Pythia's TP1 qkv.
  - **Validation:** this model reproduces **every** real M = 1 `gemvx` word in the captured random-data cases whose shape is in the table (6 cases, 6,144/6,144 coordinates; earlier, no simple order fit).
  - **Evidence:** analysis scripts at `art:eae7eb8f3fd168d71eded702542531b38cde989f85884a681a47cdf7202fe96b` (fits run over ssh from the stored S matrices).
- **Decision needed:** should I build it? It would be `GemvBiasF32_v1{K,N,V,T}` (the products as F32Fma of widened bf16, the halving tree, then F32Add of the bias and F2fpBf16), plus a (K, N) -> (V, T) table as a target fact (GPU + cuBLAS version), bound for M = 1 bias linears on `blackwell_consumer`. That would take the first night's bias configs from "finding" to GREEN. It's IR work with circuit-check, and the table is re-measured whenever cuBLAS changes.
- **Decision 1 is done: PR #483** (`cursor/vllm-sm120-bias-epilogue-422d` @ `60549d3b`, stacked on #476). It adds `GemmBiasF32Epilogue_v1{K,N,DOT}` and `targets.gemm_bias_spec` (Ampere gets `GemmBias_v1`, `blackwell_consumer` gets the new Definition, cc 9.0 is refused by name).
  - circuit-check: 3 bindings, 0 failures (`r20260930-044225-355c`); the only warning is the same Boolean redundant-gates class as `Gemm_v2`/`GemmBias_v1`.
  - 7 new tests pass on the pod; lints are clean; no existing digest moves.
  - The 724-case acceptance on the sm_120 captures is still running; the result goes in my next checkpoint.
- **Fold (your 03:14Z question), one line:** `patterns.GemmLaunch` resolves only Triton `matmul_kernel_persistent` launches and returns Unsupported for an `aten.linear`/`aten.mm` wrapper without one. On sm_120 under `init_batch_invariance()` the capture launches only cuBLAS kernels (`cutlass_80_*`, `gemvx`; no Triton GEMM), so an sm_120 capture would fold its linears as Unsupported. That holds unless H100's #73 path works in a way I can't find in the code; it needs routing to whoever owns the fold.
- **Pod:** the pinning sweep (`r20260930-041757-0bde`, e4m3 then e5m2, 25M each) is in its model comparison. I terminate after it and the acceptance, before about 06:00Z. Spend so far is about $3.9.
