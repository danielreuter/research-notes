---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T09:40Z

**45 cells labelled.** On sm_120 (`2847317c`) 6 pass 460/460: SmolLM2-135M, TinyLlama, Llama-3.2-1B, SmolLM2-360M, Phi-3-mini and Mistral-7B.
- **Top-p fails the word check at V=49152 as well as at 128256** (SmolLM2 top-p, `r20260930-092532-f168`). By your rule I labelled the top-p cells of SmolLM2-360M, Qwen3-4B, Qwen2.5-1.5B, OLMoE and Qwen3-30B-A3B `fail` without running them. TinyLlama top-p (V=32000) is running as the probe for Mistral and Phi-3 (32k).
- **New unsupported:** Gemma-2-2B (`attention_softcap` has no FA2 variant on blackwell_consumer) and Qwen3-4B-FP8 (the Build finds no rule for `_C.per_token_group_fp8_quant_packed`).
- **Run branch `7b33718d` is on origin:** main `cc0f4688` plus #483 and #501, with `targets.py` resolved as a union (`gemm_bias_spec`, `gemv_bias_spec` and the #486 `attention_spec`). The two Qwen2.5 twins re-run there under the prefix `pre-merge #486 #481 #469 #487 #502 #483 #501 @ 7b33718d`.
