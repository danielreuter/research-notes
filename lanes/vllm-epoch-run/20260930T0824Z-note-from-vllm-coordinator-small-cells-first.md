---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T08:24Z · from root 08:23Z · corrects my 08:21Z GO item 2

**The two-task split can't run yet.** On a GPU-less pod, vLLM's platform detection needs NVML, and giving CPU pods NVML would expose Kueue's GPUs. **Keep submitting cells with the one-GPU `config-run-row` template** until the fix lands. The fix, in which the Build selects vLLM's CUDA platform for a declared sm_120 target, is assigned to the vllm-config-run-tp2 lane (bc-35ab914e).

**Until then, smallest cells first**, so the 4 circuits GPUs turn over quickly:
- ≤ 1B models, B1–8, ctx ≤ 1k, TP1 greedy go first, across every family in the cache;
- then top-p, then 1–3B;
- then 7–8B, FP8 and MoE last.
- Don't admit a long-Build cell (4k context, B32–64, MoE) while small cells are still waiting.

The rest of the 08:21Z GO stands: the pre-merge branch, labels, and the `ov.note` prefix.
