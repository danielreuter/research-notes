---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T15:35Z · re: postmortem action 4c

**The whole remaining sm_120 BF16 grid is queued behind a feeder,** on the #561 tree `e6627dbc` (prefix `pre-merge #481 #487 #502 #483 #501 #551 #561 @ e6627dbc`), two-task `config-run`.
- **What the feeder does:** it runs in tmux `cov-feed` every 2 min, keeping 4 cells waiting, largest Build first. It labels cells as they end and generates each cell's workload just before submitting it (untracked in the run tree and deterministic in the row id).
- **The grid:** 9 models (SmolLM2-135M/360M, TinyLlama, Llama-3.2-1B, Phi-3-mini, Qwen3-4B, Mistral-7B, OLMoE, Qwen3-30B-A3B) × B 1/8/16/32/64 × ctx 256/32, 1k/128, 4k/512 × greedy/top-p/Gumbel. Top-p/Gumbel use coverage-defs' MAX_GATES.
- **The count:** 253 cells to run (g001–g253); 4 are submitted. 44 context cells are labelled `unsupported` (vLLM's max_model_len > max_position_embeddings: TinyLlama, Phi-3 and OLMoE at 4k).
- **Not queued:** 81 cells whose estimated memory passes what one cell may ask (Build > 500 or Commit > 700 GiB, from measured peaks + 25%). Most are B32/B64 at 4k, and Qwen3-4B, Mistral and Qwen3-30B at B≥32. They are unlabelled; the list is `grid_memory_infeasible` in my `coverage/cells.json`.
- **Excluded:** Gemma-2 (softcap row evaluator), Qwen2.5 (#535) and top-k.
