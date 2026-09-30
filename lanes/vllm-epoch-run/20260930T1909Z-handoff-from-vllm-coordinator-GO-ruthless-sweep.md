---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: GO (supersedes my 18:56Z order) · from: vllm-coordinator · created: 2026-09-30T19:09Z · Daniel 19:06Z: "sweep the shit out of different vLLM configs … I want to know this thing works"

# Maximum vLLM deployment coverage, and no GPU idle. In this order, now

**1. #594's proof, NOW, from the pre-merge branch.** Don't wait for the train.
- Merge `cursor/warmup-seeded-plans-c646` @ `6a7ff652` into your run branch.
- Re-run **two failing stochastic B8 deployments from two different models**.
- **If both pass 460/460, release all 130 held deployments at once** from that branch.
- Their Builds are done (they failed at the Commit), so these are Commit-only jobs that fill the GPUs immediately. Use `config-run` with the existing Build dirs, or `row stage commit` reusing the Build.
- If either proof fails, stop and send me the runs.

**2. Grow the grid to about 740 deployments** (from about 250 today: done, held and remaining). Generate the workloads (`verity-vllm workload`, as the GEMM lane did) and commit them to the run branch. Don't leave them untracked.

| Block | Axes | Count |
|---|---|---:|
| BF16 TP1 | every cached model (16) × batch 1/8/16/32/64 × context 256/32, 1k/128, 4k/512 × greedy, top-p 0.95, Gumbel; less infeasible (memory, weights, context) | ~540 |
| TP2 (#499 is on main) | the 8 models ≥ 1B, plus OLMoE and Qwen3-30B-A3B × batch 1/8/32 × context 256/32, 1k/128 × greedy, top-p | ~96 |
| FP8 | handled by the GEMM lane: the 7 families × batch 1/8/32 × context 256/32, 1k/128 × greedy, top-p | ~84 |
| Serving variants | chunked prefill on, all 16 models, B8 1k/128 greedy | 16 |
| **Unsupported, label now without running** | prefix caching (the engine is built with it off by design), top-k (no Definition), TP4 | named |

**Order:** breadth first, meaning every model at B1 and B8 before B16+, and 4k last. The 4k deployments wait for build-optimization's request-derive fix; they're `unsupported: build timeout` until then.

**3. Keep node 1's GPU queue full at all times:** at least **8 Commit-ready deployments queued ahead** of the 4 GPUs. Order Commits by engine key, so the hot worker serves a model's deployments back to back (the TP2 lane's hot-safety change is in PR A). Top-up rule: when the Commit-ready queue drops below 8, submit the next Builds, CPU permitting.

**4. Deferred replay:** as soon as PR A and B are on a branch you can merge (the TP2 lane), switch submissions to the three-task template (the steward), so GPUs aren't held during replay.

**Checkpoints:** one line every 30 min in your folder: labelled, pass/fail/unsupported, GPU queue depth, Build queue depth.
