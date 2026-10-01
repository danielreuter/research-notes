---
lane: circuits-predict
kind: report
created: 2026-09-30T23:57Z
status: open
---

CHECKPOINT 286377017 (00:33Z) [open] lint ratchets green (286377017: model facts via FAMILY_FACTS, capture-era scheduler dropped, tests/predict 14 pass); scoring pass 1 resumed from cache: so far 476 step/request units exact, 2 differ (older-tree traces cov-k01-9/cov-k04-6), ~377 pending; next: finish pass, divergences, store score
CHECKPOINT 73387739c (00:17Z) [open] 5:17 PM PDT: predict score running over all 251 traced rows (73387739c+); interim: 155 step/request units exact, 2 differ (older-tree traces, Attention_v2 vs v5), Llama-3.2-1B/TinyLlama/SmolLM2-360M/Mistral-7B exact too. Next: finish pass, divergences, art: put.
CHECKPOINT da63ea0c1 (23:57Z) [open] 5:05 PM PDT: predictor restored (verity_vllm/predict, da63ea0c1); SmolLM2-135M rtxpro6000 B1 256/32 greedy step+request digests EQUAL traced (53aa6ed2, 6ea7c413). Next: workload Program, scorer over all traced rows, Llama-3.2-1B/TinyLlama.
