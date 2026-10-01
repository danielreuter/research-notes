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
- **Context:** its B1 sibling p047 passes 460/460, and so do the head_dim-64 TP2 B8 rows p004 (Llama-3.2-1B) and p016 (TinyLlama). The first
  head_dim > 64 B8 to land shows it. Phi-3-mini TP2 B8 (p028) is building and should show whether it's general.
- **Log:** on vy-nebius-1, `/workspace/jobs/cov/cov-p051-3/<row>/commit.log`, lines 84-85 and 216-266.
