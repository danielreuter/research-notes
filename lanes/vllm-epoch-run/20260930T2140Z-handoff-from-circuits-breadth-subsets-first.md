---
id: 20260930T2140Z-handoff-from-circuits-breadth-subsets-first
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: reorder the queue by served code path: breadth subsets first, the rest of each block as filler behind them

Daniel asked whether the GPU work advances research. With @old-circuits-and-proofs (2:39 PM PDT) the answer is yes if it runs by
*distinct served code path*: after a few passes on a path, more cells of it add little. Order the single-GPU queue like this, and
keep ≥12 GPU-h ready:

1. **The 29 Commit-ready, now** (skip any rerun of an already-passing deployment).
2. **Qwen2/2.5 on #557, ~15 first:** each size (0.5B, 1.5B, 7B) × B1/B8 × greedy and top-p.
3. **Top-p, ~25 first:** each model at B1, B8, B32.
4. **New paths as they unblock:** OLMoE and Qwen3-30B-A3B (MoE), Gumbel B8 when staging-bug's fix lands, Gemma-2 when coverage-defs'
   fix lands, one 4k per model when build-optimization's derive cut lands.
5. **Filler behind all of that:** the rest of each block (the other ~96 Qwen, the other top-p cells, the rest of the grid), so GPUs
   never idle.

- **Drop:** reruns of already-passing deployments (g218 has three passes).
- **TP2 stays held** (my 2:40 PM handoff). When it returns, the first subset is ~10 models × B1/B8 at 256/32, plus OLMoE and
  Qwen3-30B-A3B.
- **Node 2:** kueue-fold staged SmolLM2-360M, TinyLlama, Llama-3.2-1B, Qwen2.5-0.5B, Phi-3-mini, Mistral-7B, OLMoE and Pythia-160m
  there (2:34 PM). If infra turns on node-2 Commits as preemptible guests, each record must carry the driver, vLLM pin and clock state.

Put, in your next checkpoint, how many of steps 1–3 are queued and the GPU-h ready.
