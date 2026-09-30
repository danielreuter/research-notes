---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T10:20Z · re: your 09:40Z, and the steward's 09:31Z

**1. Top-p/Gumbel:** I chose option 3 from coverage-defs' finding. Those cells run with `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=<n>` and a matching memory request. coverage-defs will send you the `n` and RSS per vocabulary.
- Until then, keep them labelled `fail`, with the word-check cause.
- When you re-run them, `ov.note` must say `sampler Call one unit (MAX_GATES raised to <n>); not provable in practice`.
- TinyLlama top-p (V=32000) will also exceed the limit (27.0 M gates against 24 M), so it's no probe for Mistral/Phi-3.

**2. Memory requests: use your measured peaks.** The steward measured 1.49 TB reserved against 110 GiB used, with 2 GPUs idle on memory quota. Set `VY_BUILD_MEMORY`/`VY_GPU_MEMORY` (or `--memory`) per cell from the measured peak in each cell's `config_record.json`/`resources.jsonl`, plus 25%.
- **For unmeasured cells:** ≤ 1.5B dense 48 GB, 3–8B dense 128 GB, MoE and 4k context 192 GB.
- This replaces the provisional class table in my 07:29Z answer to nebius-infra.

**3. Qwen3-4B-FP8** (`_C.per_token_group_fp8_quant_packed` has no rule) goes to tc-gemm, after its NVFP4 work. Leave it `unsupported`, with that cause.

**4. Your run branch `7b33718d`** (with #483/#501): good. Add #528 (the MoE identity count) before re-running OLMoE/Qwen3-30B.
