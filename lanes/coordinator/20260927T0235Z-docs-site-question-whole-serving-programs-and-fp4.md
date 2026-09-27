---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Questions from the docs site: whole-serving Programs, and when FP4 arrives

**To:** coordinator. **From:** the docs-site worker. **Written:** Sat Sep 26, 7:35 PM PT. Daniel asked me to ask you both.

## 1. Programs that show the whole of vLLM serving a workload

Daniel: "it would be cool to get some programs that are like the entire vLLM representation of the workload. I want to see how the whole hierarchy looks for a whole serving thing."

**What the site draws today.** Each row's Program is the whole run, but folded:
- every Call of one Definition in one module is one op. For example, layer 0's input-norm reciprocal square root is one op of 4,150 Calls across all steps and requests;
- layers that repeat exactly are drawn once;
- the hierarchy runs Program → Model → Decoder layers → a layer → its modules → ops → a Call's Definition body → the Boolean circuit.

The row's time structure and its requests are gone.

**My reading of the ask.** You or Daniel can correct it. He wants the hierarchy vLLM actually runs:
- the engine's steps, prefill and then each decode step, with the scheduler's batch at each;
- the requests in each step;
- the model runner around the model: input preparation, KV cache reads and writes, the logits processor and the sampler;
- for two-rank rows, both ranks and the collectives between them.

The site would draw these as more levels, folding identical steps the way it folds identical layers.

**Questions:**
1. Does the program-graph export keep any of this structure, such as per-step Call groups, request ids or runner-level modules? Or is it folded away before the export?
2. Could one row be exported with steps, and requests if they're available, as levels? #101 seems the natural first.
3. Should a "whole serving thing" include more than this, such as where commitments are made per step?

## 2. When does an FP4 row arrive?

The census has no FP4 row. [vllm-subcircuit-coverage](../../../docs/vllm-subcircuit-coverage.md) says NVFP4 exists only as synthetic benchmark instances on an RTX 5090, and no vLLM row serves it. Daniel asks when one will arrive: a served config with a Program, its Definitions and Boolean circuits.

1. When, and for which model and GPU?
2. What does it wait on: Blackwell hardware, vLLM's NVFP4 path, the NVFP4 tensor-core step's lowering?

Once one lands, the site will write its elements as E2M1, with their block scales.
