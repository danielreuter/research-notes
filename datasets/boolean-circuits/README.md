# Boolean circuits of the served rows

A derived export for the website visualizer, laid out beside `../program-graphs/`. It covers all 13 rows. Each leaf template of a row's program graph is lowered to AND, XOR and NOT gates by C-Flock's IR lowering (`verity_flock.ir_lower`, pieces in `verity_flock.fp`). The export uses total semantics throughout: the tensor-core steps are the generic `fp.tc_dot16` (every encoding, NaN/Inf included), not the finite-only census unit. It is not a proof statement, and it is regenerated from the program graphs (see "Regenerate").

## Files

| file | what |
| --- | --- |
| `index.json` | rows, file names, totals, the verification summary, and everything not yet lowered |
| `<row_key>.boolean.json` | one row: its program-graph nodes (one per group), each pointing at a template; the program graph's edges |
| `templates.json` | `templates`: every leaf template (by id); `definitions`: the Definition trees the walker built (by id) |
| `subcircuits.json` | every named subcircuit (by id), shared across templates and rows |
| `gates/<root id>.json.gz` | full gate lists for subcircuits of at most about 20,000 gates (`gate_limit`) and for the tensor-core k-steps, one bundle per circuit root (a proof unit or a piece): `{"lists": {<subcircuit id>: <gate list>}}` |

## Hierarchy

Program-graph node → template → (Definition tree →) Boolean-circuit root (a proof unit or a piece) → named subcircuits → gates.

- **Program-graph node** (`nodes[]` in a row file): `id` (`<row>:<group>`), `name` (the module), `kind` `program-node`, `template` (a template id), `instances`, `calls`, `definition`. A group whose key count varies (attention) also has `varying.T` and `instances_per_T`. Each node also has:
  - `params`: the Call's parameters in order, each with:
    - `name` and `bits` (a `[min, max]` range when the size varies with T);
    - `roles`: `activations` (another Call's output), `constant` (a constant Call's output), `weights`, `prompt`, `seed`, `splits` (the sampler's split count) or `peers` (a tensor-parallel rank's values received from its peers);
    - `from_calls` (`{group: words}`) and `from_inputs` (`{input: words}`), the sources the roles come from;
  - `inputs`: the prescribed inputs the Call reads (`weights:<tensor>`, `prompt`, `seed`, …), with their role and read count;
  - `param_roles_complete`: whether every parameter's roles are known.

  The roles come from the program graph, never from a parameter's name. A parameter fed by another Call is exact, from the graph's `edges[].ports`. Which parameter reads each of `inputs` needs the graph's `param_inputs` (verity PR #94), which the current program graphs lack. Until they are regenerated with it, such parameters have `roles` null, and a parameter that reads both kinds lists only `activations`. For example, Embedding's `tok` reads the prompt on prefill Calls and the sampled token on decode Calls. `param_roles_complete` is false on every Call where this can happen.
- **Template** (`templates.json` `templates`): `id`, `name`, `kind`, `params`, `and` / `xor` / `not` / `not_yet_lowered` per instance, `in_bits` / `out_bits`, and `children`.
  - `kind` is `template` (lowered), `constant`, or `not-yet-lowered`.
  - Attention's circuit depends on T: `per_key_count[T]` gives each T's Definition and counts; the top-level `children` are the maximum T's (`children_at`).
  - `note` explains a template walked instead of unit-lowered.
- **Definition** (`templates.json` `definitions`): `id`, `name` (the IR Definition id, e.g. `AttnBlock_v3{D=64,NVIS=5,FIRST=true,BN=128}`), `kind` `definition`, the counts, `in_bits` / `out_bits`, and `children`.
- **Children** (of a template or a Definition), each one of:
  - `{"def": <definition id>, "count": n}`: a sub-Definition (a `call` once, a `batch` / `scan` n times);
  - `{"ref": <subcircuit id>, "count": n, "proof_unit": true}`: a proof unit under the committed cut (a C-Flock unit, or a tensor-core k-step);
  - `{"ref": ..., "count": n, "proof_unit": false}`: a primitive outside the units, lowered with its `ir_lower` piece;
  - `{"not_yet_lowered": <primitive>, "count": n, "in_bits", "out_bits", "reason"}`: a primitive with no Boolean lowering yet.
- **Subcircuit** (`subcircuits.json` `nodes`): its fields are:
  - `id`: a structural hash, stable across runs;
  - `name`: the display name, which can be renamed freely;
  - `kind` and `function` (the `fp` / `gf2` / `unit` function or IR primitive it is);
  - `and` / `xor` / `not`: its own gates plus its children's;
  - `own`: its own gates only;
  - `in_bits` / `out_bits`;
  - `in_ports` / `out_ports` (`[[name, width], …]`): the function's argument and result names in bit order, summing to `in_bits` / `out_bits`;
  - `children` (`[{"ref", "count"}]`): each distinct child once, with its instance count;
  - `parts` and `wiring`, set when it has children (see "Wiring");
  - `proof_units`: the unit roots whose trees contain it;
  - `outside_units`: whether it also appears outside the units;
  - `gates`: `{"file", "key"}`, set when it has a gate list.

  The named subcircuits follow `fp.py` / `gf2.py`: bf16→f32, unpack, integer multiply, align (shift right, sticky), integer add, carry-save compress, leading-zero count / normalize, round, specials (NaN/Inf), f32→bf16 (round), table lookup and one-hot decode, and the tensor-core k-step with its group sums.

## How each template is lowered

- **C-Flock units:** RoPE, SiLU·mul, and the RMSNorms at shapes with one warp unit. The template's proof units come from `ir_lower.units()` with the template module's cut, and its tail primitives are lowered with their pieces.
- **The Definition walker:** everything else, using the program graphs' stored Definitions. That covers:
  - GEMM coordinates, both Ampere `GemmCoordinate_v1` and Hopper `GemmCoordinate_v2`;
  - attention per T: FA2 `AttentionHead_v3`, FA3 on Hopper `AttentionHead_v2`, and gemma's `AttentionSoftcap_v1`;
  - MoE expert GEMMs, routers and sums;
  - TP collectives;
  - `TokenSelect`;
  - fp8 quant and block matmul;
  - gemma's elementwise ops and `BiasAdd`;
  - the RMSNorm shapes whose warps differ, so that there is no single unit (Triton at N = 128, 576, 1536 and 2560; fused at N = 1536 and 2560).
- **Tensor-core k-steps** are the proof unit wherever they occur:

  | step | ANDs | semantics |
  | --- | --- | --- |
  | `AmpereBF16TcDot16_v1` | 8,623 | `tc_dot16` with groups (8, 8), W 25, F −132 |
  | `HopperBF16WgmmaDot16_v1` | 8,233 | `tc_dot16` with groups (16,), W 26, F −133 |

  The Hopper parameters are `verity.ml.tc.models.HOPPER_BF16_WGMMA_K16`; that lowering matches the IR primitive on 60,000 special-heavy vectors with 0 mismatches.
- **What the walker counts:** every node of the Definition, including any that the evaluator's liveness pass would drop. For example, attention at T = 1 lists 72 unlowered primitive instances where the unit lowering has 71. Constants that a primitive reads directly from a `Const` node are propagated into its piece; otherwise a primitive is lowered once per operand signature.

## Counting

`gf2` commits only ANDs; XOR and NOT are linear forms that R1CS gets for free. Here they are real gates, counted as the lowering performs them:
- every live XOR or NOT operation counts once, in the subcircuit that ran it;
- a linear form built without recorded operations (`fp.lookup`'s table sums over decoded minterms) counts as a chain of |terms| − 1 XORs where it is used. That is why table lookups (SiLU) have many XORs.

AND counts are the ANDs live in the unit, so a C-Flock unit's `and` equals the committed ANDs of its pinned expanded circuit:

| unit | ANDs |
| --- | --- |
| RoPE pair | 5,996 |
| SiLU·mul element | 2,699 |
| RMSNorm fused warp, N = 2048 | 317,334 |
| RMSNorm Triton warp, N = 2048 | 1,132,502 |

Identical subcircuits (the same canonical structure after constant propagation) are one node, referenced with instance counts. The same holds for Definitions: attention's full `AttnBlock`s are shared across T.

## Wiring (the part graph)

A subcircuit with children also has the following, at every level down to the leaf functions, including inside the million-gate warp units:
- `parts`: its child calls in the order the lowering made them. Each entry is an index into `children`, so a child used 16 times appears 16 times.
- `wiring`: the dataflow between the parts, as edges `[src_part, src_port, dst_part, dst_port, width]`. Source bits `src_port + i` feed destination bits `dst_port + i` for i < `width`. A port is a bit position in the part's `out_ports` (as a source) or `in_ports` (as a destination).

Part numbers in an edge:

| part | meaning |
| --- | --- |
| 0, 1, … | `parts[i]` |
| −1 | the subcircuit itself: its inputs as a source, its outputs as a destination |
| −2 | a constant; the port is its value (0 or 1), or −1 when the value differs between instances of the type |
| −3 | the subcircuit's own gates (`own`); ports are not numbered (−1). An edge into −3 is a bit they read; an edge out of −3 is a bit they make |

An edge never spans two ports on either side, so each edge lies within one named port of its source and one of its destination. For `{from, to, bits}` bundles, sum `width` over the edges of each (`src_part`, `dst_part`) pair.

Every input bit of every part, and every output bit, has exactly one incoming edge. A bit that is exactly a parent input or an earlier part's output comes straight from it; any other bit comes out of the own gates. Every instance of a subcircuit type was checked to have its type's wiring (`index.json` `wiring_verification`). The one allowed difference is the value of a constant input that the counted structure does not depend on (a few leading-zero counts inside `F32Fma_v1` pieces); it is shown as constant port −1.

The wiring shows every bit a call makes, but the counts hold only the gates live in the unit, and a table sum's XOR chain is counted where it is used. So the own-gates part can appear even when `own` is zero, for example for integer subtract's borrow-out, which the unit never uses.

## Gate lists

A subcircuit's `gates` gives the bundle `file` and its `key` there. Each gate list has:
- `inputs`: the input wire count;
- `input_origin`: `["arg", i]` for the subcircuit's i-th argument bit, `["ext", …]` / `["form", …]` for other values made outside it;
- `gates`: a flat `[op, a, b, …]`, with op 0 AND, 1 XOR, 2 NOT (b = −1). Wires 0 .. inputs−1 are the inputs; each gate appends one wire; −1 and −2 are the constants 0 and 1;
- `outputs`: wire ids;
- `tag_scopes`: the subcircuit's tree of calls in preorder, each `[subcircuit id, parent scope, part index]`. Scope 0 is the subcircuit itself (parent −1); a scope's part index is its position in its parent's `parts`;
- `tags`: one scope per gate, the innermost named subcircuit that made it. A chain for a table sum takes the scope of the gate that uses it; chains for the outputs take scope 0;
- `counts`: the gates in the list.

To highlight a named part inside its parent's list, even one with no list of its own (for example `RopeOut_v1` inside the RoPE pair unit), take its scope and every scope below it, and select the gates tagged with any of them.

A list is written for each subcircuit of at most `gate_limit` gates whose parent is larger. The tensor-core k-step units also get one whatever their size, as do their k-step subcircuits: Ampere 25,992 gates, Hopper 24,690. A list contains every gate the subcircuit's outputs need, so its `counts` can exceed the tree's counts, which include only gates live in the unit (likewise a scope's tagged ANDs; `index.json` counts the scopes where they differ). Every list was evaluated against its circuit (bit-sliced, 64 random vectors) before it was written.

## Not yet lowered

Marked explicitly: nothing here is evaluated by anyone. `index.json` `not_yet_lowered` lists each one, with the templates and Definitions it occurs in:
- **Whole templates:** `Embedding_v1` and `EmbeddingShard_v1` (row gathers), and `GumbelTopPTokenSelect_v1` (Gumbel noise, the top-p word, the sampling carries).
- **Attention's softmax:** `F32Max`, the FTZ f32 ops, `MufuEx2Ftz`, `GuardNegInfZero`, `Fa2InvSum`, `Fa3InvSum`, and for gemma `MufuTanh` / `TanhF32Rn`.
- **The RMSNorm row scalars:** `RsqrtApprox`, `MufuSqrtFtz`, `DivFullScaleA`, `DivFullRcp`. Also `F32Div` by a non-power-of-two constant, such as `/ N` at N = 576.
- **The rest, primitives without a piece yet:**
  - comparisons, selects and integer ops (MoE routing, `TokenSelect` argmax);
  - `F32Neg` / `F32Sub` / `F32Fabs` / `F32Fmaxf` / `F32Fminf` / `F32Sat` / `F32IsFinite` / `F32BitsShl23` / `F32FmaRm`;
  - the gathers `GatherBf16x64` / `x128`;
  - `GeluTanhMulBf16`;
  - the fp8 `F32ToE4m3Sat` and `HopperE4m3QgmmaDot32`.

## Regenerate

~~~sh
PYTHONPATH=packages/verity/src:backends/numerical/python:backends/flock/python:integrations/vllm \
  python -m verity_flock.boolean_export --program-graph ../program-graphs/<row>.program.json [--program-graph ...] --out .
~~~

The Definition walker reads `definitions/` beside the first program graph. The generator is on verity branch `cursor/flock-ir-lowering-c78f`, in `backends/flock/python/verity_flock/boolean_export.py`.
