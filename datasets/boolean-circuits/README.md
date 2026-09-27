# Boolean circuits of the served rows

A derived export for the website visualizer, laid out beside `../program-graphs/`. It covers all 13 rows. Each leaf template of a row's program graph is lowered to AND, XOR and NOT gates by C-Flock's IR lowering (`verity_flock.ir_lower`, pieces in `verity_flock.fp`). The export uses total semantics throughout: the tensor-core steps are the generic `fp.tc_dot16` (every encoding, NaN/Inf included), not the finite-only census unit. It is not a proof statement, and it is regenerated from the program graphs (see "Regenerate").

## Files

| file | what |
| --- | --- |
| `index.json` | rows, file names, totals, the verification summary, and everything not yet lowered |
| `<row_key>.boolean.json` | one row: its program-graph nodes (one per group), each pointing at a template; the program graph's edges |
| `templates.json` | `templates`: every leaf template (by id); `definitions`: the Definition trees the walker built (by id) |
| `subcircuits.json` | every named subcircuit (by id), shared across templates and rows |
| `gates/<root id>.json.gz` | full gate lists for subcircuits of at most about 20,000 gates (`gate_limit`) and for the tensor-core k-steps, one bundle per circuit root (a C-Flock unit, a tensor-core k-step or a piece): `{"lists": {<subcircuit id>: <gate list>}}` |
| `commitments.json` | each Call's cut under the no-recompute partition, by the Call's Definition id (see "Commitment marks") |

## Hierarchy

Program-graph node → template → (Definition tree →) Boolean-circuit root (a C-Flock unit, a tensor-core k-step or a piece) → named subcircuits → gates. The commitment marks sit beside this tree, at the Calls (see "Commitment marks").

- **Program-graph node** (`nodes[]` in a row file): `id` (`<row>:<group>`), `name` (the module), `kind` `program-node`, `template` (a template id), `instances`, `calls`, `definition`. A group whose key count varies (attention) also has `varying.T` and `instances_per_T`. Each node also has:
  - `params`: the Call's parameters in order, each with:
    - `name` and `bits` (a `[min, max]` range when the size varies with T);
    - `roles`: `activations` (another Call's output), `constant` (a constant Call's output), `weights`, `prompt`, `seed`, `splits` (the sampler's split count) or `peers` (a tensor-parallel rank's values received from its peers);
    - `from_calls` (`{group: words}`) and `from_inputs` (`{input: words}`), the sources the roles come from;
  - `inputs`: the prescribed inputs the Call reads (`weights:<tensor>`, `prompt`, `seed`, …), with their role and read count;
  - `param_roles_complete`: whether every parameter's roles are known;
  - `commitment`: the id of the Call's record in `commitments.json`. A group whose T varies has `commitment_by_T` (`{T: id}`) and `commitment_partitioned_at` instead. Constant Calls have neither.

  The roles come from the program graph, never from a parameter's name. A parameter fed by another Call is exact, from the graph's `edges[].ports`. Which parameter reads each of `inputs` comes from the graph's `param_inputs` (verity PR #94), which all 13 graphs carry. A parameter can have two roles: for example, Embedding's `tok` reads the prompt on prefill Calls and the sampled token on decode Calls. `param_roles_complete` is false only on a Call whose graph lacks `param_inputs`.
- **Template** (`templates.json` `templates`): `id`, `name`, `kind`, `params`, `and` / `xor` / `not` / `not_yet_lowered` per instance, `in_bits` / `out_bits`, and `children`.
  - `kind` is `template` (lowered), `constant`, `commitment-opening` (the embedding: checked by opening the committed table, not a circuit), or `not-yet-lowered`.
  - Attention's circuit depends on T: `per_key_count[T]` gives each T's Definition and counts; the top-level `children` are the maximum T's (`children_at`).
  - `note` explains a template walked instead of unit-lowered.
- **Definition** (`templates.json` `definitions`): `id`, `name` (the IR Definition id, e.g. `AttnBlock_v3{D=64,NVIS=5,FIRST=true,BN=128}`), `kind` `definition`, the counts, `in_bits` / `out_bits`, and `children`.
- **Children** (of a template or a Definition), each one of:
  - `{"def": <definition id>, "count": n}`: a sub-Definition (a `call` once, a `batch` / `scan` n times);
  - `{"ref": <subcircuit id>, "count": n, "c_flock_unit": true}`: the C-Flock unit a RoPE, SiLU·mul or one-warp RMSNorm template is lowered as. This is the lowering's grouping, not a commitment;
  - `{"ref": <subcircuit id>, "count": n}`: a primitive lowered with its `ir_lower` piece (a tensor-core step is its k-step circuit);
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
  - `gates`: `{"file", "key"}`, set when it has a gate list.

  The named subcircuits follow `fp.py` / `gf2.py`: bf16→f32, unpack, integer multiply, align (shift right, sticky), integer add, carry-save compress, leading-zero count / normalize, round, specials (NaN/Inf), f32→bf16 (round), table lookup and one-hot decode, and the tensor-core k-step with its group sums.

## How each template is lowered

- **C-Flock units:** RoPE, SiLU·mul, and the RMSNorms at shapes with one warp unit. The template's units come from `ir_lower.units()` with the template module's cut, and its tail primitives are lowered with their pieces. These units are C-Flock's grouping of the circuit, not the commitment cut.
- **The Definition walker:** everything else, using the program graphs' stored Definitions. That covers:
  - GEMM coordinates, both Ampere `GemmCoordinate_v1` and Hopper `GemmCoordinate_v2`;
  - attention per T: FA2 `AttentionHead_v3`, FA3 on Hopper `AttentionHead_v2`, and gemma's `AttentionSoftcap_v1`;
  - MoE expert GEMMs, routers and sums;
  - TP collectives;
  - `TokenSelect`;
  - fp8 quant and block matmul;
  - gemma's elementwise ops and `BiasAdd`;
  - the RMSNorm shapes whose warps differ, so that there is no single unit (Triton at N = 128, 576, 1536 and 2560; fused at N = 1536 and 2560).
  - the sampler, `GumbelTopPTokenSelect_v1`, whose primitives now have pieces (see "Tail primitives").

- **Tensor-core k-steps** are one circuit root each, wherever they occur:

  | step | ANDs | semantics |
  | --- | --- | --- |
  | `AmpereBF16TcDot16_v1` | 8,260 | `tc_dot16` with groups (8, 8), W 25, F −132 |
  | `HopperBF16WgmmaDot16_v1` | 7,872 | `tc_dot16` with groups (16,), W 26, F −133 |

  The Hopper parameters are `verity.ml.tc.models.HOPPER_BF16_WGMMA_K16`; that lowering matches the IR primitive on 60,000 special-heavy vectors with 0 mismatches.
- **What the walker counts:** every node of the Definition, including any that the evaluator's liveness pass would drop. For example, attention at T = 1 lists 72 unlowered primitive instances where the unit lowering has 71. Constants that a primitive reads directly from a `Const` node are propagated into its piece; otherwise a primitive is lowered once per operand signature.

## Tail primitives

The primitives a template's units leave outside now have circuits (`verity_flock.tail_pieces`). Each is its IR primitive bit for bit, checked by C-Flock's exact-bits piece test and by circuit-check (verity PR #100): 20,000 vectors per primitive, 0 mismatches.
- **Attention's softmax:** `F32AddFtz`, `F32SubFtz`, `F32MulFtz`, `F32FmaFtz`, `F32FmaSubFtz`, `F32Max`, `GuardNegInfZero`, `MufuEx2Ftz` and `Fa2InvSum`.
- **The norms' row scalars:** `RsqrtApprox`, `MufuSqrtFtz`, `DivFullRcp` and `DivFullScaleA`. The circuits around their table reads are M0's (`verity_flock.tail`, verity PR #83).
- **The sampler:**
  - `GumbelStreamKey` (Philox4x32-10, 9,282 ANDs);
  - `GumbelNoiseLane` (Philox, the uniform draw, libdevice `log1pf` with its true toward-zero add, and `logf`: 102,837 ANDs);
  - `BitAtx{W}` (a mux tree, 128,282 ANDs at W = 128,256);
  - `F32GtStrict`, `F32Eq`, `SelectF32`, `SelectI32`, `I32Add`, `BitOr` and `BitNot`.

`MufuEx2Ftz` reproduces the IR exactly, including one quirk: for |x| < 2⁻⁶³ the IR's model (`fa2_model.cpp`) shifts a 64-bit word by 64 or more. C++ leaves that undefined and x86 wraps the count modulo 64, so the IR returns, for example, 1.0083 for ex2(6.5 × 10⁻²²) where the hardware gives 1.0.

### Table reads (lookup slots)

A MUFU operation (EX2, RCP, RSQ, SQRT) reads a pinned 2²³- or 2²⁴-entry table (`ir_lower.TABLES`). Its piece computes the table index with gates, reads the table, and finishes the result with gates.
- **The read** is a subcircuit of kind `lookup-slot`, with `table`, `table_sha256`, `index_bits`, `value_bits` and `built_by`. It stands for M0's lookup slot (`live/src/lookup.rs`):
  - one-hot decoders of the index's low and high bits, each minterm the AND of two half minterms;
  - per value bit and high minterm, one AND of that minterm with the XOR of the low minterms whose table word has the bit set;
  - each value bit, the XOR of its products.
- **Its counts** come from that structure over the actual table: 41,308 ANDs for the 2²³ tables, 49,576 for 2²⁴. Its XOR counts are large (144–289 million), because they are the trees behind the slot's linear sums; in Flock's R1CS those are free. The slot has no gate list.
- **In gate lists,** a read's value bits are inputs with `input_origin` `["lookup", <table>, <bit>, <id>]`. A list that computes the read's index also has `lookups`: `[{"table", "index": [wires], "value": [[bit, input wire], ...]}]`. Every list's index wires and values were checked against the circuit.

## Counting

`gf2` commits only ANDs (and a table read's value bits); XOR and NOT are linear forms that R1CS gets for free. Here they are real gates, counted as the lowering performs them:
- every live XOR or NOT operation counts once, in the subcircuit that ran it;
- a linear form built without recorded operations (`fp.lookup`'s table sums over decoded minterms) counts as a chain of |terms| − 1 XORs where it is used. That is why table lookups (SiLU) have many XORs.

AND counts are the ANDs live in the unit, so a C-Flock unit's `and` equals the committed ANDs of its pinned expanded circuit:

| unit | ANDs |
| --- | --- |
| RoPE pair | 5,828 |
| SiLU·mul element | 2,606 |
| RMSNorm fused warp, N = 2048 | 308,358 |
| RMSNorm Triton warp, N = 2048 | 1,114,422 |

These are the hash-consed circuits (verity PR #104): an AND of two forms already ANDed reuses that bit.

Identical subcircuits (the same canonical structure after constant propagation) are one node, referenced with instance counts. The same holds for Definitions: attention's full `AttnBlock`s are shared across T.

## Commitment marks

The commitment marks follow the no-recompute partition of verity PR #92 (`verity_vllm.query.word`, `Q_word_v1{X=16,W=32,R=no-recompute}`, at the verity commit named in `commitments.json` `code`). Each Call's circuit is cut into units:
- every gate and every value is computed in exactly one unit;
- a value read across units is committed once, and so are the Call's outputs and its inputs;
- a unit's committed outputs are at most 16 bits, or one value of at most 32 bits;
- constants and wiring (`Bf16ToF32`, `F32BitsShl23`, `F32Fabs`: bit rearrangement) are structure, in no unit and never committed.

The export computes each Call's cut with that code on the Call's Definition. It checks the cut against the program graph's own `q_word_v1` summary (units, gates, structure gates and committed interior words per Call), with the result in `index.json` `commitments`. These marks replace the earlier `proof_unit`, `proof_units`, `outside_units` and `placement` fields, which recorded C-Flock's prover grouping.

A record in `commitments.json` `records` has:
- `id`: the Call's Definition id;
- `word_gates`, `structure_gates`, `redundant_gates`, `units_per_call`, `by_kind` (`output`, `committed`, `dead`), `committed_interior_words`;
- `scopes`: the Definition ids that `scope` and `part_nodes` index;
- `units`: the unit classes, grouped as `word.unit_rule` does. Each has `kind`, `head` (the primitive of its first committed value), `scope`, `count` (units per Call), `word_gates`, `out_bits`, `out_gates`, `ok`, and `nodes` (every primitive of one unit). It also has the unit's `and` / `xor` / `not` from the pieces, with constant operands propagated, and `not_yet_lowered` (primitives with no piece, left out of those counts);
- `constants_not_propagated` (when present): gates of the unit lowered with their primitive's generic piece. A record lowers at most 8 constant-operand variants of one primitive, and an unrolled scan gives every lane its own constant index; #101's Gumbel select has 384,743 such gates of 1.41 million;
- a unit of at most 4,096 word gates also has a part graph, of one representative unit:
  - `parts`: its word gates in layout order, each an index into the record's `pieces` (`{"ref": <subcircuit id>}`, `{"not_yet_lowered": <primitive>}` or `{"commitment_opening": <primitive>}`);
  - `part_nodes`: each part's `[scope, body node]`;
  - `wiring`: `[src part, dst part, bits]` inside the unit. A read through wiring stands for a read of its source;
  - `reads`: `[unit class, dst part, bits]` for a value another unit commits, or `[-1, dst part, bits, parameter]` for the Call's inputs;
  - `outputs`: the parts whose value the unit commits;
- `committed`: `[scope, body node, kind, values]`, every value the cut commits, counted at the Definition body node that computes it; kind indexes `mark_kinds` (`output`, `committed`);
- `structure`: gates by primitive, in no unit;
- `violations`.

A separable Definition, such as a Gemm's coordinates or attention's heads, is its members' cuts. Its record lists `separable` (`[[member id, members]]`) instead of `committed` and `pieces`, and each unit class names the record holding its part graph (`graph`).

Attention is partitioned at the program graph's own points: every T up to a few hundred (all 287 for #101), else the key-block boundaries and their neighbours. Other T values have no record, and their marks are not interpolated.

In brief, what the cut changes from the earlier marks:
- a GEMM unit is a whole output coordinate (the k-step chain plus the round, committing only the bf16 output), not one k-step;
- RoPE's `RopeOut` and `RopeOutAdd` are separate units;
- an RMSNorm has one unit per output element plus one committed row-scale unit;
- attention commits its S and P values and its row values;
- nothing is "outside the units" but structure.

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
| −4 | a bit computed outside the subcircuit and not among its inputs: an AND the hash-consed lowering reused from an earlier subcircuit (port −1) |

A source port of −1 on a part means a bit computed inside that part but not one of its outputs, which the lowering reused the same way.

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

A list is written for each subcircuit of at most `gate_limit` gates whose parent is larger. The tensor-core k-step units also get one whatever their size, as do their k-step subcircuits: Ampere 25,625 gates, Hopper 24,327. A list contains every gate the subcircuit's outputs need, so its `counts` can exceed the tree's counts, which include only gates live in the unit (likewise a scope's tagged ANDs; `index.json` counts the scopes where they differ). Every list was evaluated against its circuit (bit-sliced, 64 random vectors) before it was written.

## Checked by opening

The embedding (`Embedding_v1`, `EmbeddingShard_v1`) gathers one row of the committed weight table at the token id. That gather is checked by opening the committed table at that row (`census/subcircuits.json` `commitment_opening`), not as a circuit. Its templates have `kind` `commitment-opening`, its gather pieces in `commitments.json` are `{"commitment_opening": <primitive>}`, and `index.json` `commitment_openings` lists them.

## Not yet lowered

Marked explicitly: nothing here is evaluated by anyone. `index.json` `not_yet_lowered` lists each one, with the templates and Definitions it occurs in.
- **Row #101:** only the sampler's top-p keep word `TopPMaskWordx{V}`. It is the whole row's split pipeline, and it is partial: it raises unless `splits` is 1, 2, 4, 8, 16 or 32 (circuit-checks' finding 2, verity PR #100). Its owner is the vLLM sampler.
- **Other rows:**
  - FA3's `Fa3InvSum` (Hopper rows);
  - gemma's `MufuTanh`, `TanhF32Rn` and `GeluTanhMulBf16`;
  - FP8's `F32ToE4m3Sat` and `HopperE4m3QgmmaDot32`;
  - greedy selection and MoE routing: `Bf16GtStrict`, `SelectBf16`, `I32Eq`, `F32Neg`, `F32Sub`, `F32Sat`, `F32IsFinite`, `F32FmaRm`, `F32Fmaxf`, `F32Fminf`;
  - `F32Div` by a constant that is not a power of two, such as `/ N` at N = 576;
  - the gathers `GatherBf16x64` / `x128`;
  - the bit rearrangements `F32BitsShl23` and `F32Fabs`, which the commitment cut treats as structure.

## Regenerate

~~~sh
PYTHONPATH=packages/verity/src:backends/numerical/python:backends/flock/python:integrations/vllm \
  python -m verity_flock.boolean_export --program-graph ../program-graphs/<row>.program.json [--program-graph ...] --out .
~~~

The Definition walker reads `definitions/` beside the first program graph. The generator is `backends/flock/python/verity_flock/boolean_export.py`. This export ran from branch `cursor/flock-tail-pieces-c78f`: verity `main` at `fa662029`, plus PR #104 (bit-exact NaNs in `F32Add` / `F32Mul`, an IR lowering with no redundant ANDs), plus the tail primitives. `commitments.json` `code` names the commit. The program graphs are the 13 rows regenerated by lane vllm-cross-call-check (`art:c74deac4…`), with rows #4 and #101 rebuilt from their record Builds (`art:983c79f8…`, which carry their Definitions inline and no word rules). Every row therefore has `param_inputs`, but rows #4 and #101 have no `q_word_v1` to cross-check the cuts against.
