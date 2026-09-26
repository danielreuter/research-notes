---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Hierarchical VU store: layout and extraction query (design note, lane vllm-vu-export, 2026-09-26 02:30Z)

This note answers Daniel's request 2: store the exported inputs inside the circuit they came from, and make flat sets the output of a query. PR [#42](https://github.com/danielreuter/verity/pull/42) doesn't implement it, because it's larger than a PR #42 addendum (see "Why a follow-up" below). The flat sets that #42 writes today would become the output of `extract` with the default decomposition, byte for byte.

## Layout: one store per run, keyed by Program digest

~~~text
vu-store/<run_root>/                          one committed run (the commitment root is the run's name)
  run.json                                    row, model, serving config, run id, run root, source {commit, dirty, branch}, epoch,
                                              manifest digest, weights-of-record root, query id (Q_module_body_v1), selection rule
  programs/<program_digest>/
    program.ref.json                          the Program by reference: store art of the Build's descriptor.json.gz + instances.json.gz
                                              (already registered per row as the `programs` fixture), correspondence digest
    modules.json                              the hierarchy actually sampled: module op_path -> {invocations, calls: [i, ...]}
    units.jsonl                               one line per sampled VU (a Call under Q_module_body_v1):
                                              {i, spec, module, request, step, engine_step, row, phase, stratum, replay: PASS,
                                               evaluations: [{call i (interior producers too), family, statics,
                                                              args: [value ref ...], outs: {member: value ref}}]}
    values/<sha256>.<u8|u16|u32|u64>          content-addressed committed words (each opened against the run root at export)
    weights.json                              weight operands by reference: {field, range, sha256 of the slice} with the
                                              weights-of-record per-field digest; plus a materialised row cache (below)
    weights/<sha256>.u16                      the weight rows the default decomposition selected (GEMM coordinates' w rows)
~~~

- **Hierarchy.** The chain is Program (digest) → module (op_path plus invocation, from the correspondence) → Call (instance row `i`) → VU (the Call's `Q_module_body_v1` unit) → evaluation (the VU's own Call plus any composed interior producers). That's exactly what `replay_vu` walks today; the exporter's evaluation tap already sees every level.
- **Values** are stored once and referenced by hash. A GEMM row's activation `x` is shared by all its coordinates, and a K/V history is shared by every head that reads it. For #101 that's roughly 186 MB flat, versus a fraction of it deduplicated (the attention K/V histories dominate).
- **Weights** are registered inputs, not committed values. They're referenced by field and range and pinned by the weights-of-record digests. Only the rows that the default query sampled are materialised. A full GEMM weight is N×K (the #101 lm_head alone is 525 MB), so storing whole weights per sampled VU would store the model several times.

## Extraction: the IR query machinery

`extract(store, query, template=None, limits)` → flat sets in today's `vllm-vu-set/v1` format:

1. Load the Program from `program.ref.json` (a `verity.ir` Program from the descriptor).
2. Evaluate the query with `verity.ir.query` / `query_ast.evaluate(program, q)`. For a template: `where(instances(//Gemm_v1{K=2048,*}))`. For a node: `instances(//model.layers.3.mlp)`, or `each(instances(//...), nodes(...))`. The result is a `Family` of GateSets.
3. Intersect it with the stored units. A unit's gate interval comes from its instance row `i`, through the row → root-gate map the replay's `vu_query` planner already computes, so the query's GateSets select stored units without expanding the Program.
4. Run each selected unit's evaluations through `vu_export.decompose` (unchanged: coordinates, heads, rows), re-evaluate each instance under its relation, and write the flat set. Weight rows outside the materialised cache come from the checkpoint by reference, or the instance is skipped by name when no checkpoint is present (the laptop case).

Today's flat sets are `extract(store, default_query)`. The docs-site bundle (`internal/datasets/vllm-101/`) is a small extraction too.

## Why a follow-up and not PR #42

- Step 3's unit ↔ GateSet map needs the descriptor Program loaded next to the instance rows. `vu_query` does that mapping for the replay's own tier; wiring it for stored units is new code, plus tests on the small replay Programs.
- The weights question below changes what the pod must write, and it should be settled before #4 and the default-on rows produce data in the new form.
- PR #42 now carries default-on export for every passing row, and it should merge on its own merits.

**Follow-up scope:**
- `vu_export` writes `vu-store/` (units, values, weights refs plus the row cache) instead of `sets/`.
- `extract()` plus `verify()` over the store.
- Test that `extract(default)` equals today's sets byte for byte on the replay test Programs.
- Re-express the #101 and #4 exports. Their `vus.jsonl` already carries every unit's operand identities; the values are in the registered sets.

## Open question for Daniel

For on-demand extraction of GEMM coordinates at arbitrary `n`, the weight row must come from somewhere. The options:

- **(a)** Reference the checkpoint: exact and pinned, but the site builder then needs the HF snapshot.
- **(b)** Materialise a fixed number of rows per sampled GEMM VU (today 32 per row, about 16 MB at K = 8192 for 60 rows).
- **(c)** Materialise every weight row the sampled VUs touch. That's the model's linear weights: GBs per row, and no good.

The proposal is (a) plus (b): the store holds (b), and (a) is the fallback when a checkpoint is present.
