---
id: 20261001T1218Z-handoff-from-circuits-predict-repin-557
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-predict
---

#664 is ready to retrain, 5:18 AM PDT. `cursor/vllm-predictor-8c79` head `0612c9664` is pushed. It merges origin/main `d88650921` and #557's prep head `0522c86f6`, the one train `c0097b93b` merged. Two pins are re-derived from #557's `GemmBias_v2` binding and none loosened: the Qwen2.5-0.5B step moves `312cae23…` → `421d0b9a…`, cov-k03-8's traced Build; the biased-linear rule test now has rtxpro6000 → `GemmBias_v2`, asserting exactly one kind. Tests pass: `tests/predict` + `tests/lint` 89, slow tests included; the vLLM invariants 8; the repository 33. Re-score on this head: 1606 of 1610 freshly predicted small units exact (99.75%), and 4139 of 4151 composed (99.71%), art:e5e7ddf09cd9.
