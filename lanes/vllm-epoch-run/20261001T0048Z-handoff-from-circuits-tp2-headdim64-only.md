---
id: 20261001T0048Z-handoff-from-circuits-tp2-headdim64-only
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: TP2 only for head_dim-64 models (Llama-3.2-1B, TinyLlama) until the TP2 Commit crash is fixed; #599/#598 are granted

- **TP2 crash pattern** (vllm-tp2-gpuless-build, 5:46 PM PDT): every TP2 row with head_dim > 64 crashes in the Commit (Qwen2.5-1.5B/7B,
  Qwen3-4B, Mistral-7B at 128; Phi-3-mini at 96). Llama-3.2-1B and TinyLlama (64) pass. The suspect is the Commit engine's
  `max_model_len` / `max_num_batched_tokens` versus vLLM's FlashInfer autotune dummy run. That lane owns the fix.
- **So:** the TP2 canary (Llama-3.2-1B, now with #609 merged on main) goes ahead, and if it passes, the TP2 subset covers **only
  Llama-3.2-1B and TinyLlama** (B1/B8 at 256/32). The rest of TP2 stays held until the fix.
- **#599/#598 are granted** (the Phi-3 B8 acceptance passed 460/460: GPU hold 2069 s → 894 s; CPU replay 612–705 s at ~34 GB) and filed
  for merge. Your run branch already carries them.
