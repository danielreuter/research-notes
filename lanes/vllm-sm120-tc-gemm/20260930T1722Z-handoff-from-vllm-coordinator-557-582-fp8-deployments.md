---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: decisions · from: vllm-coordinator · created: 2026-09-30T17:22Z

**1. #557 @ `470cf59d`: granted** (17:20Z), with B1 and B8 at 460/460. It's clean on main `2e04ac50` and in RC's queue now.

**2. The workload-only pin `fp8_block_gemm: "cutlass"`: agreed**, on these conditions:
- the workload field is what sets `VLLM_USE_DEEP_GEMM=0` for that deployment's engine;
- it's recorded in the config record's engine facts;
- it's used only on sm_120 block-FP8 workloads.

No code change, and Daniel approved the setting at 15:22Z. If the field is new to the workload schema, the schema change is the code change: say so in #582's body.

**3. #582 (FP8 CUTLASS, `ScaledMmFp8Block_v2` over the sm_120 e4m3 step): not grantable yet.**
- It carries #515's core step (`packages/verity`, `backends/flock`) and #516. Those need their own core grants and `lean-agreement`, and go first.
- It conflicts with main `2e04ac50` and with #557.
- **Do:** once #557 is on main, merge main into #582. Send me the #515 → #516 → #582 stack heads in order. I'll grant the vLLM parts and file the core parts with RC for their owners.

**4. #546: parked.** Convert it back to draft (I can't from here) and leave it untrained. The DeepGEMM path isn't served.

**5. The 7 FP8 deployments** (rtxpro6000, TP1, B1, i256/o32, greedy, bi-eager, `fp8_block_gemm: "cutlass"`), one per family:
1. `LLAMA32_1B_FP8` (Llama)
2. `TINYLLAMA_FP8`
3. `PHI3_MINI_FP8` (Phi)
4. `MISTRAL7B_FP8` (Mistral)
5. the hub `Qwen3-4B-Instruct-2507-FP8` (Qwen3; your capture model)
6. `QWEN05_FP8` (Qwen2.5, biased linears: needs #557)
7. `GEMMA2_2B_FP8` (Gemma-2: needs #581 on top of main's #568/#569, and #569's MUFU move lands with #250)

- Run them from a pre-merge branch: main + #557 + #581 + #582's stack. Use `config-run-split`, campaign `overnight-sep30`.
- `ov.note "pre-merge … @ <commit>; VLLM_USE_DEEP_GEMM=0"`, and label each as it finishes.
- If Gemma-2 still refuses on something FP8-specific, label it `unsupported` with the cause, and don't chase it tonight.
- Tell the sweep lane (`lanes/vllm-epoch-run/`) which 7 you're running.
