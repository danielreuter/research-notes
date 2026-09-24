# Phase 2 gate: `Q_module_body_v1` against the v1 manifests of record

Every reference row's required-value manifest, rebuilt from its request Programs (`instances.json.gz`, the Build's flat body) plus
the per-Call correspondence (owning module path, fx node, return-slot hint) by the query path, compared identity-for-identity to the
row's recorded v1 `manifest.json`.  No execution data, no model- or family-name table: `tests/query/test_lint.py`.

How a row is run (laptop, CPU; one row staged at a time under `/tmp/v2q/`):

~~~
python -m verity_vllm.query.cli build-global --fixture workloads/<row>.json --programs-root <row dir> \
        --workload-digest <build_summary.json: workload.workload_digest> --out manifest.v2.json
python -m verity_vllm.query.cli compare --v1 <row dir>/manifest.json --v2 manifest.v2.json --out compare.json
# or through the harness: VERITY_REGRESSION_ENGINE=v2 VERITY_REGRESSION=1 pytest tests/regression -m regression -k manifest_digest
~~~

The per-row records are `tests/query/gate/row<N>_*.json` (the `compare` summary + populations + residual counts).

## Rows

| row | model / shape | v1 identities (rows) | v2 identities (rows) | only_v1 | only_v2 | manifest_digest | build (laptop) |
|---|---|---|---|---|---|---|---|
| #57 | gemma2-2b bf16 L40S tp1 B8 | 160,010 (163,052) | 160,442 (163,484) | 0 | 432 | v1 + the labelled decision | 172 s |
| #60 | mistral-7b bf16 L40S tp1 B8 | 201,400 (205,144) | 201,400 (205,144) | 0 | 0 | EQUAL `085985ae…` | 274 s |
| #73 | qwen3-4b bf16 H100 tp1 B8 (FA3) | 243,115 (247,327) | 243,115 (247,327) | 0 | 0 | EQUAL `a2aaa282…` | 493 s |
| #74 | qwen3-4b-fp8 fp8 H100 tp1 B8 (FA3, blockwise FP8) | 258,637 (262,885) | 258,637 (262,885) | 0 | 0 | EQUAL `ecb28d4e…` | 492 s |
| #67 | olmoe-1b-7b bf16 L40S tp1 B32 (MoE) | 383,968 (385,504) | 404,896 (406,432) | 0 | 20,928 | v1 + `(layers.k.mlp.experts, out)` -- see below | 222 s |
| #68 | olmoe-1b-7b bf16 L40S tp1 B32 mixed-arrivals (MoE) | 380,250 (382,234) | 400,954 (402,938) | 0 | 20,704 | v1 + `(layers.k.mlp.experts, out)` = 16 x 1,294 | 295 s |

Not run on the laptop (this session): #23 (llama32-1b B64: 247 MB Programs +
222 MB manifest of record), #11 / #39 (B=1, 4096 x 512: one 922 MB / 1.6 GB Program each -- the flat body is ~10^7 Calls, past
what the laptop's 24 GB and the 5-hour budget allow), #70 / #75 (TP2 rank Programs: v1's TP encoding -- `tp_rank_partials` rows,
`tp_peer_binding`, the rank fold -- is a separate bridge not written here; #75 also has no manifest of record).

"identities" = distinct IDENTITY_KEY tuples; "rows" = manifest rows (a global manifest repeats one request-less hidden-stream key per
engine step; the harness digests rows with multiplicity, so both are compared).  `program_digest` equal on every row (the workload
digest of record).

### #57: the one difference, explained

`only_v2 = 432 x (model, out)`, spec `Bf16MulScalarTensor_v1`, one per (request, step): the decoder's own `embed * normalizer` Call.
v1's vocabulary classed the family interior (`_DENSE_INTERIOR`); its output is read by `layers.0.input_layernorm` and
`layers.0.pre_feedforward_layernorm` -- Calls of other module bodies -- so under `Q_module_body_v1` it is a boundary Value by
definition.  The row's labelled decision (`fixtures.toml`, F-r19-int-20, `expected = { identities = 163484, only_new = 432,
promoted_member = "model/out" }`) is met without a promotion pass: 163,484 rows, digest `d54d8efe…`, `complete = true`.

### #60: what TENSOR-RETURN is for

Before the TENSOR-RETURN policy the row read `only_v1 = 516 x model.norm/1` and 8 x `model.norm/0` range differences: the final
fused norm (`RMSNormFusedCuda_v2`, ports `0` normed / `1` residual, no recorded return slot) is unrolled to one Call per prompt row,
and the logits read one row of port `0`; v1 requires every row of both ports because the collector binds the two TENSORS the module
returns.  The policy states that: once any Value of an fx node's output at a step crosses the body boundary, every Value of that
node's output (all rows, all ports) is protocol-required.  With it the row is byte-equal; #57 is unchanged by it.

### #67: the one difference, explained (F-r19-int-20 class, MoE)

`only_v2 = 20,928 x (model.layers.<k>.mlp.experts, out)`, spec `MoeSum_v1` = 16 layers x 1,308 (request, step) pairs, one per MoE
block per step; `only_v1 = 0`, every v1 identity present (the 125,568 `moe_block_stream` plane rows included).  `MoeSum_v1` is the
last Call of the `mlp.experts` body (vLLM `FusedMoE.forward`'s returned `final_hidden_states`); its output is read by
`layers.<k+1>.input_layernorm` (the fused add+norm of the next layer) -- another module's body -- so it is a boundary Value.  v1's
vocabulary classed the family interior by name and covered the MoE block only through the kernel-side planes.  This is the same class
as #57's decision (a v1 by-name claim the dataflow contradicts), a candidate for a labelled decision on #67 / #68; not a v2 gap.

## Named residuals (v1 spellings the structure does not give)

Emitted in every manifest header (`query.named_residuals`) and counted per row (`query.residuals_applied`).

| family | structural member | v1 member | condition | why |
|---|---|---|---|---|
| `Gemm_v1`, `Gemm_v2`, `BiasAdd_v1`, `ScaledMmFp8Block_v1`, `AllReduce2_v1` | `out` | `0` | the Call reads a parameter registered under its own module | vLLM `LinearBase.forward` returns `(output, output_bias)`; the collector binds slot 0.  The Definition returns one array and the Build recorded no return slot |
| `RoPE_v1` | `query` (recorded hint) | `0` | -- | the Build records RoPE's return slots by keyword; v1 spells them as the tuple index of `RotaryEmbedding.forward -> (q, k)` |
| `RoPE_v1` | `key` | `1` | -- | as above |
| (encoding) | -- | `<consumer>/in` | -- | v1 encodes the token ids a module consumes as `input_token_ids` at the consuming module |
| (encoding) | -- | `runner.sampler/sampled_token_ids` | -- | the sampling event's output under a fixed path (the root body has no module path) |
| (encoding) | -- | `<field>/weight` | -- | a registered weight as `<field path>/weight`, open range, once per rank |
| (encoding) | -- | `fa2.m1/L<k>` / `fa3.m1/L<k>` geometry | -- | the attention M1 stream is a kernel-side stream; member = launch geometry (v1 `_fa2_geometry` / `_fa3_geometry`) |

Not residuals -- derived from structure: the member of every tuple-returning Definition (`0`/`1` of the fused norms, the
attention/MoE ports), `out` for a single-array Definition without a hint, the recorded hint otherwise; the owning module (correspondence);
the implementation path (suffix match of the Build's observed attention paths against the Program's module paths); shared module
instances (`op_path_aliases`: bodies reading the same registered parameter with the same body signature; canonical = the body the
parameter is registered under); the step (sampling events); the MoE and FA kernel geometry (v1's functions over the binding record).

## v1 by-name tables the path does not use

`_DENSE_INTERIOR`, `MEMBER_RULES`, `members_for`, `_LINEAR_LEAVES`, `FIRST_NORM_SUFFIX`, `FAMILY_OF_MODULE`, the width literals,
`is_epilogue_interior` / `epilogue_modules`, `is_aggregate_family` / `is_structure_family` / `_operand_family`, `alias_family` /
`shared_module_aliases` (replaced by `shared_instances`), and the promotion pass (`Traversal._promote`, `promote_interior_crossings`,
`PROMOTION_RULE`).  Imported from v1 as the encoding being bridged to: `SCHEMA`, `IDENTITY_KEY`, `_row_key`, `manifest_digest`,
`components_fold_digest`, `request_label`, the FA / MoE geometry functions (`_fa2_geometry`, `_fa3_geometry`, `mat_total_words`,
`moe_geometry`, `moe_identities`, `_layer_of`).
