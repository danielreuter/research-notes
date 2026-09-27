---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Request from the docs site: export each served row's Program as a graph

**To:** coordinator, for vllm-vu-export. **From:** the docs-site worker. **Written:** Fri Sep 25, 7:45 PM PT.

## Why

Daniel wants the site's model graphs to come straight from the circuit: integration, then circuit, then visualization.

Today Census › Models draws Llama-3.2-1B's module tree from `data/models.ts`, which I wrote by hand:

- **Module names:** from the site bundle's sample op paths. Those are genuine: they're `named_modules()` of the export wrapper, which `Q_module_body_v1` partitions by.
- **Nesting and order:** mine.
- **Which Definition each module runs:** inferred by matching shapes to `vus_by_spec` keys, for example `Gemm_v1{K=2048,N=3072}` for `qkv_proj`.
- **Edges:** a sequential chain I drew.

`gate_up_proj` and `embed_tokens` never appear in the samples; I filled them in by convention.

## What would let the site render the Program as it is

A `program.json` per served row in the site bundle (`internal/datasets/…/`):

- **Modules:** every module body of the Program, with:
  - its path, as the correspondence names it;
  - its parent;
  - its order among its siblings.
- **Calls:** each module's Calls, in order, with:
  - the Definition and its statics (the spec, as in `vus_by_spec`);
  - the subcircuit it decomposes into: template and bound parameters, as in the template files;
  - its verification units and inputs in the run.
- **Dataflow:** producer-to-consumer edges between Calls or modules, from the Values they read and write. That would replace the site's drawn sequential chain with the real graph, residual adds included.
- **Repeats:** a structural hash per module body, so the site can fold identical siblings (`layers.0` … `layers.15`). It shouldn't guess from names.
- **Row identity:** the row's serving config, as in `rows.json`'s `serving` block, and its Program digest.

A second row with a different template mix, for example OLMoE with its MoE Calls, would show the format generalizes. The site would then replace `data/models.ts` and render every served config's graph from these files.
