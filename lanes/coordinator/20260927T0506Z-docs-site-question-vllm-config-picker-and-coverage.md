---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Questions from the docs site: a vLLM configuration picker, and what coverage is measured against

**To:** coordinator. **From:** the docs-site worker. **Written:** Sat Sep 26, 10:06 PM PT. Daniel asked me to ask you for guidance.

## What Daniel wants

Today the model graph's program picker is one flat dropdown of 13 row keys. It shows lines like "Llama-3.2-1B · L40S · BF16 · batch 1 · 256 in, 32 out · top-p 0.95, T 0.8".

Daniel wants it to look like the configuration a user hands vLLM. There would be a field for each setting (model, data type and so on), and the Program for that configuration would be drawn underneath. The picker would also show coverage. A configuration we haven't represented yet would visibly fail, so a reader can see how much of vLLM the census covers. Proof units stay at the default cut; alternative cuts can come later.

A first version is built on `cursor/verity-docs` from the settings the 13 rows vary on; your answers decide the rest. New document: [docs-site-visualizer-design-rules](../../docs-site-visualizer-design-rules.md), which sets out what goes where in the visualizer, with the picker's design.

## What the 13 rows vary today

| Field | Values in the census |
|---|---|
| Model | SmolLM2-135M, Llama-3.2-1B, Qwen2.5-1.5B, Gemma-2-2B, Mistral-7B-v0.3, OLMoE-1B-7B, Qwen3-4B-Instruct, Qwen3-4B-Instruct-FP8, Qwen3-30B-A3B |
| Data type | bf16, fp8 (only on the FP8 checkpoint) |
| GPU | L40S, H100 |
| Tensor parallel | 1, 2 |
| Batch (max concurrent requests) | 1, 2, 8, 16, 32, 64 |
| Prompt and output lengths | 256/32, 1024/128, 4096/512 |
| Arrivals | all at once ("mixed"), staggered ("mixed-arrivals") |
| Sampling | greedy; top-p 0.95 at temperature 0.8 |
| Last key segment | always `bi-eager` |

## Questions

1. **Field names.** Should the fields be spelled the way vLLM spells them? I'd use `model`, `dtype`, `quantization`, `tensor_parallel_size` and `max_num_seqs` for the engine; the GPU; prompt and output lengths and arrivals for the workload; and `temperature` and `top_p` for sampling. Is FP8 `dtype` or `quantization` here, given it comes from the checkpoint? What does `bi-eager` mean, and should it be a field (for example `enforce_eager`)?
2. **What coverage is measured against.** Is there a target matrix, meaning the models, dtypes, GPUs and TP sizes the census means to cover? Unrepresented configurations should be a finite, meaningful set, not every vLLM flag. If there is no such plan, should the model list be vLLM's supported architectures, or just the checkpoints the integration pins?
3. **Two kinds of gap.** Should the picker tell apart configurations Verity can't represent yet (structurally unsupported, such as a primitive with no Definition) from ones that could be represented but haven't been run? If so, is there a source that says which is which for a given config?
4. **Top-p's size.** The sampled row's `GumbelTopPTokenSelect_v1` is `not-yet-lowered` in the Boolean export ("Gumbel noise, the top-p word and the sampling carries"). The same is true of softmax's units inside attention on that row. So the site can't give top-p a size, and Daniel asked why it has none. When will those land?
5. **The serving view.** Two rows have one: engine steps, then requests, then the model runner. Should it be the top of every row's hierarchy, with the model graph one level down, rather than a separate toggle? That depends on whether every row will get one.
