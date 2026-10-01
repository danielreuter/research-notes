---
id: 20261001T1640Z-report-from-circuits-epoch-audit-counts
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-epoch-audit (bc-dab39801)
---

9:40 AM PDT, every failed coverage deployment named and labelled (`ov.cause --by circuits-epoch-audit`, 111 labels, art:a01112d9b090ac2cb041cef843e0c37f7611ceb69fa0aca1789a450ae161f7a9). Node 1's vllm-epoch-run failed attempts (cov-gm* excluded) number 76, not 83, and 38 of them are superseded by a later pass: TP2 world-2 rejected by vLLM 18, replay task with no bundle 12, Qwen2.5-7B bootstrap rc 3 10, Pythia-160m rotary refusal 7, TP2 Commit illegal memory access 6, Commit watchdog stop 6, EOS-stopped request 3, TP B8 staging 3, word-check gate guard 3, compose timeout 2, OLMoE TP all-gathers 2, splits unbound at top_p=1 1, W1 OLMoE weights 1, TP2 MoE blocks 1, Gemma-2 TP2 softcap 1. Node 1's n2-build keys: 2 (disk-emergency cancel 1, watchdog 1). Node 2's failed coverage fills: 14 (model not staged 9, Pythia 2, withdrawn 2, uv.toml config error 1). A further 52 keys have no end record: 49 withdrawn or stopped, all named, and 3 still running. Table: internal/circuits/epoch-failures-named.md in the Project store.
