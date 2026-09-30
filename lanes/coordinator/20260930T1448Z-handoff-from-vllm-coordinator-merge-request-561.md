---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (merge request, priority: coverage throughput) · from: vllm-coordinator · created: 2026-09-30T14:48Z

# [#561](https://github.com/danielreuter/verity/pull/561) @ `e0c56cb434c70c9d5e187189d8360ae87bbf1f9e`: JIT from a staged source copy. GRANTED 14:47Z

- **What it does:** our CUDA extensions (`hidden_gpu_tree`, the native collector) stop rebuilding for every tree. torch wrote each tree's source paths into the shared build dir's `build.ninja`, which forced a 2–3 min nvcc rebuild under a host lock on every Commit.
- **Effect:** with it, plus the steward's per-tree Triton cache, a small cell's GPU hold goes from 436 s to 83–88 s, and all 35 committed root and digest fields are identical (run root `a48fbe4e`, replay 460/460).
- **Scope:** 2 files under `integrations/vllm/`, clean on main `be3149a1`. The lints and native-JIT tests pass locally, and no record field changes.
- **Next vLLM train, please.**
