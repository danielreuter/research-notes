---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T15:05Z

**I cannot fetch #561 (`cursor/jit-tree-invariant-sources-3847` @ `e0c56cb4`): GitHub auth refuses it, and it is neither in vy-nebius-1's repo nor in `artifacts/`.** A bundle in `artifacts/` would unblock it; until then cells keep running from `2f5d600b` without #561, which only makes them slower. New passes: Mistral-7B top-p (`r20260930-144204-0e06`, 460/460, MAX_GATES 30M). TinyLlama at 4k is `unsupported` (vLLM refuses max_model_len 4608 against max_position_embeddings=2048). Gemma-2-2B keeps its `fail` from the Build's call-boundaries check (the norm add), a cause earlier than the missing replay evaluator.
