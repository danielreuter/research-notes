---
lane: circuits-predict
kind: report
created: 2026-09-30T23:57Z
status: open
---

CHECKPOINT 8962d0ee5 (01:03Z) [open] 8962d0ee5: vocabulary now also covers Qwen2 q/k/v bias, Qwen3 per-head q/k norm, Phi-3 inert sliding window; digest-exact step+request+workload vs near-main traces: Qwen2.5-0.5B (cov-k03-7), Phi-3-mini (cov-k07-3), Qwen3-4B (cov-g242), SmolLM2 stoch B1/B8 (cov-k17, cov-g230); score pass ~2/3 done; next: rerun plan with new families, divergences, store
CHECKPOINT 418b32712 (00:46Z) [open] 418b32712: predictor now emits the seeded top-p select (derived splits Input or single-request const S); SmolLM2 stoch B1+B8 step/request/workload all digest-exact vs cov-k17/cov-g230; full score pass restarted incl. ~1100 stoch units (663 tasks left, 3 workers); next: divergences, store score by 7:40 PM
CHECKPOINT 286377017 (00:33Z) [open] lint ratchets green (286377017: model facts via FAMILY_FACTS, capture-era scheduler dropped, tests/predict 14 pass); scoring pass 1 resumed from cache: so far 476 step/request units exact, 2 differ (older-tree traces cov-k01-9/cov-k04-6), ~377 pending; next: finish pass, divergences, store score
CHECKPOINT 73387739c (00:17Z) [open] 5:17 PM PDT: predict score running over all 251 traced rows (73387739c+); interim: 155 step/request units exact, 2 differ (older-tree traces, Attention_v2 vs v5), Llama-3.2-1B/TinyLlama/SmolLM2-360M/Mistral-7B exact too. Next: finish pass, divergences, art: put.
CHECKPOINT da63ea0c1 (23:57Z) [open] 5:05 PM PDT: predictor restored (verity_vllm/predict, da63ea0c1); SmolLM2-135M rtxpro6000 B1 256/32 greedy step+request digests EQUAL traced (53aa6ed2, 6ea7c413). Next: workload Program, scorer over all traced rows, Llama-3.2-1B/TinyLlama.
