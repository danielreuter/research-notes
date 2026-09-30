---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T08:39Z · from root 08:38Z

**1. HOLD the labels of any cell whose attempt was published from inside a Kueue container** until nebius-infra confirms those attempts reached the store.
- Why: the attention lane's `port-capture` job's attempt never arrived, and nebius-infra is checking the custody gap.
- Keep the cells running. Record each cell's run id and outcome in your checkpoint, and label them all as soon as custody is confirmed.
- Labels on attempts you can already see in the store (`research data` shows them on the remote) may go ahead.

**2. FP4 cells** (a stretch row, after BF16/FP8 breadth):
- The NVFP4 verdict is a match: `CutlassNvFp4LinearKernel` = core's pinned FP4 step. The tc-gemm lane now owns the NVFP4 Definition and quantizer.
- Until that merges, NVFP4 cells are `unsupported`, with `ov.note "NVFP4 Definition pending (tc-gemm)"`. Label them now, without running them, like the TP rows.
- **Checkpoint choice:** `RedHatAI/Qwen3-8B-NVFP4` (e391349c) keeps a **bf16 KV cache**, so use it first. `nvidia/Qwen3-8B-FP4` (ModelOpt, ccd10a89) declares an **FP8 KV cache**, which is its own axis with no Definition. Label its cells `unsupported`, `ov.note "FP8 KV cache (kv_cache_dtype=fp8) has no Definition"`.
