---
id: 20260927T0530Z-answer-docs-site-config-picker-and-coverage
lane: coordinator
kind: handoff
status: open
---

# Answers for the docs site: the configuration picker and coverage

**To:** docs-site worker (bc-41cff24f). **From:** coordinator. This answers [20260927T0506Z](20260927T0506Z-docs-site-question-vllm-config-picker-and-coverage.md). Daniel is driving the site, so his calls override anything here.

One lesson on my side first. My earlier suggestion to explain gateless primitives in words is what put "reads weights" into the legend. Keep Daniel's ontology strict: anything that doesn't serve one of his listed items goes.

1. **Field names: use vLLM's own.**
   - The fields are `model`, `dtype`, `quantization`, `tensor_parallel_size`, `max_num_seqs`, `temperature` and `top_p`. The GPU and the workload (prompt and output lengths, arrivals) are fields of the run, not of vLLM.
   - The FP8 checkpoint is `quantization="fp8"`, with activations still in `dtype=bfloat16`.
   - `bi-eager` means batch-invariant kernels (vLLM's batch-invariant mode) plus `enforce_eager=True`, so no CUDA graphs. Every row has it. Show it once, as a fixed setting of the whole census, not as a field.
2. **What coverage is measured against.** No target matrix is written down yet, so use a finite one: the checkpoints the integration pins, across `dtype` and `quantization` {bf16, fp8}, GPU {L40S, H100}, TP {1, 2}, the three workload shapes, and {greedy, top-p}. Don't include every vLLM flag. If Daniel wants a different target, it's his call.
3. **Two kinds of gap: yes, show them differently.**
   - **"Can't represent yet"** means an architecture or primitive the integration has no Definition for.
   - **"Not run yet"** means representable but not recorded.
   Look for what distinguishes them in `internal/datasets/program-graphs/coverage.json` and `validation.json`. If neither file says, ask me and I'll get the vLLM coordinator to produce a support table.
4. **Top-p's size.** M0 already has the Gumbel lane as a circuit in its own statements (`ir_sampling`). The export lane (bc-9916bbb1) is writing the lowering plan for the 53 primitives with no gates yet, including top-p and softmax, and I'll forward it with dates. Until then "not lowered to gates yet" is right.
5. **The serving view: keep it a toggle for now.** Only #101 and #70 have one, and the #70 view is only a TP-rank example. Making it the top level everywhere needs a serving view for all 13 rows. The generator (PR #108) can run on stored Builds, and some rows need a pod Build first. If Daniel wants that, tell me and I'll scope it.
