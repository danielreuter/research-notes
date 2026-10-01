---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-tp2-gpuless-build, cc @circuits · created: 2026-10-01T04:25Z

# Qwen3-4B TP2 B8 (cov-p051-3) fails in bounded staging: warm-up step 0's plan wasn't pre-learned and is over the host budget

- **The row:** `qwen3-4b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__greedy__bi-eager`, tree `5bab849b` (with `b642a4a4b`). The attempt is
  `r20261001-040850-7a22`. The GPU-less 2-rank Build passed (step `659c2c47…`/`871a0ea4…`).
- **What happened:** both ranks logged `[collector] worker failed on windowed step 0: RuntimeError('bounded staging: learning step 0 exceeds the
  transient host budget 4096 MiB at window 16 (4352 MiB): its plan was not pre-learned (warm-up learn-only pass)'`. vLLM's worker then died, and the
  engine raised `RuntimeError: cancelled`, 130 s in. That was in the warm-up (`req_id=warmup-0-…`), before the instrumented run.
- **Context:** its B1 sibling p047 passes 460/460. At TP2 B8, these pass:
  - p004 (Llama-3.2-1B) and p016 (TinyLlama), head_dim 64;
  - p028 (Phi-3-mini, head_dim 96, `r20261001-042330-7745`) and p096 (Qwen2.5-1.5B, head_dim 128, `r20261001-043153-da65`).
- **Update 04:45Z:** p108 (Qwen2.5-7B TP2 B8, `r20261001-042845-6293`) fails the same way, at 4352 MiB against 4096 MiB on both ranks. So it isn't
  head_dim. So far it's Qwen3-4B and Qwen2.5-7B at B8.
- **Update 05:10Z:** p040 (Mistral-7B TP2 B8, `r20261001-044017-9ba5`) fails the same way too, at 4352 MiB against 4096 MiB on both ranks.
  - Failing at TP2 B8: Qwen3-4B, Qwen2.5-7B and Mistral-7B.
  - Passing: Phi-3-mini, Qwen2.5-1.5B, Llama-3.2-1B and TinyLlama.
  - p085 (Qwen3-30B-A3B TP2 B8) is the last B8 in the subset.
- **Log:** on vy-nebius-1, `/workspace/jobs/cov/cov-p051-3/<row>/commit.log`, lines 84-85 and 216-266.
