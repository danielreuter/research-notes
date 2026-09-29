---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: plan · from: flock-soundness (bc-9e538dc5) · created: 2026-09-28T01:05Z · repo: danielreuter/verity ·
about: general L1 and IR-to-gates (Daniel's redirect) · for: the research coordinator, and the design lane writing
`docs/verified-lowering-design.md`

# flock-soundness: PR plan for general L1

**Status: a plan only. Nothing below is started.** I'm holding all implementation until
`docs/verified-lowering-design.md` lands, then I'll re-cut these PRs to its shape. Where the plan depends on a choice
that document may make differently, it says so (marked **design:**).

**Done meanwhile** (small, and clearly useful):
- **#187 is at `0e308ef6`.** On top of the red-team-granted `3ac26fd9`, it adds two commits:
  - `0e935dcb`, the review's docs sentence;
  - `0e308ef6`, the generator's limit checks: at most 512 runs, digits below 2^22 (the reviewer's (8191, 511) case),
    operands below 2^17, and every code decoded back as the Lean decoders do.

  Both are docs or Python only, so no pin changes. Merge order is unchanged: #180, then #187.
- **Per-template L1 is stopped.** SiLU is skipped. The generic per-template checks are parked at `922b400a` on
  `cursor/flock-silu-lowering-8569`, with no PR. Item 2 below supersedes them unless the design wants per-instance
  kernel checks back.

## The ground

- **Flat L1 exists** (#187). `GateRows.rows` derives a unit's rows from a flat gate circuit by the v2 rule, and
  `rows_sound` proves that satisfied derived rows compute the circuit, for every circuit and layout. `rows` is already
  an ordinary computable Lean function. #187 runs it through the kernel for one instance, RoPE, as the regression test.
- **The audit side exists for flat rows.**
  - In `Lowering.lean`: `Rows`, `Rows.Sat`, `IsRowsUnit`, `Placement`, `lowering_sound`, `UnitPlace`, `Prog.snoc` and
    `Prog.isRowsUnit`.
  - Open: #154 (the verifier's parse as `Rows`, and `Rows.stack`), #177 (`placement_of_setupH`) and #156
    (`placedA`/`placedB`).
- **Where the pipeline's rows come from.** `ir_lower.layout` makes them from the `gf2` construction, and
  `ir_lower.netlist` writes them as `flock-ir-unit/v2`. M0's prover, [#192](https://github.com/danielreuter/verity/pull/192)
  (`adcf38bf`, table reads now inline rows), parses that format, and so does `Flock/Net.lean`. The Boolean export
  materializes the same `gf2` construction as AND/XOR/NOT gates.
- **The composed format** is `constant-api-public.md` §2.2 and #191's `verity/circuit-type/v1`. A type's items are an
  AND of two linear forms, a call on input forms, or a table read. Its outputs are forms. XOR and NOT are free.
  §2.8 names the composition pieces: `Rows.compose`, `placement_compose` (audit-lean), W6 (mine) and the truth-table
  lemma.

**design:** I'd state the general spec over #191's circuit types, not over the Boolean export. They're the canonical
object: forms rather than one association of XOR chains, one type per Definition. They're also what the layouts,
the docs site and the export's modules share. The export then becomes a derived flattening, with one lemma tying the
two.

## Item 1: composed circuits, one theorem per rule

**PR A (flock-soundness), `FlockSoundness/Types.lean` next to `GateRows`.**
- **The object.**
  - `Ty` mirrors `circuit-type/v1`: input and output ports, items, and outputs as forms.
  - A program is a DAG of types listed callees first.
  - `Ty.eval` is its semantics, by recursion over that list: an AND of forms, a callee's `eval` on its input forms,
    and a table's entry for a read.
- **The derivation.** `Ty.rows`, in §2.8's `Rows.compose` order:
  1. the type's inputs;
  2. its own rows before each call point;
  3. the callee's input copies, rows `[src]·[src]` (an exported input stays an input);
  4. the callee's constant copy;
  5. the callee's composed rows;
  6. its remaining own rows;
  7. the constant, last.

  A read's rows are the `table/v2` generator's.
- **The theorems, each proved once:**

  | Rule | Theorem | What it says |
  |---|---|---|
  | own rows (flat) | `own_sound` | a type's AND rows over forms compute its items. `rows_sound` becomes its instance whose forms come from XOR chains |
  | a call | `call_sound` | if the callee's rows compute its `eval`, the input and constant copies plus the callee's rows force the callee's outputs to `eval` of the caller's input forms |
  | tail stages | `tail_sound` | rows after a call point that read the callee's output columns compute their items. This is `own_sound` with those columns in scope |
  | an exported input | `export_sound` | an input exported to the level above is bound there, exactly once |
  | a read | `read_sound` | the truth-table lemma: given index bits `x` and the constant 1, the generated rows force the output to `table[x]` |
  | the whole DAG | `compose_sound` | by induction over the DAG from the rules above: satisfied composed rows carry `Ty.eval` on the outputs |
  | flattening | `flatten_eval` | `Ty.eval` equals the flattened gate circuit's `Circ.eval`, so L1's wording ("in the program's Boolean circuit") still holds |

- **The conditions the rules need** are the constant design's checks, not new ones: every callee input bound exactly
  once, no cycles, and a caller reading only callee outputs after the call point. They'll be one hypothesis,
  `WellFormed`, shared with #154/#177's `Circuit.WellFormed`.
  **design:** whether that predicate lives in the soundness package or in the verifier.
- **Tests.**
  - RoPE's type has no calls, so `compose_sound` on it must restate `rope_sound`. #187's chunked kernel check stays
    as the regression test.
  - Small hand-made types in `decide` examples: a call, an exported input and one 8-bit read.
- **Size:** about 600–900 lines of Lean. No pods.

**PR B (audit-lean, bc-a0c5a22f, with me).** The audit's side, as in §2.8:
- `Rows.compose` as a unit's `Rows`, with `compose_topo`;
- `placement_compose`, from the accept step through `WellFormed`;
- W6, `IsRowsUnit u (Rows.compose …)`, which is mine.

It needs #154 and #177 merged. PR A's `compose_sound` is its L1 input.

## Item 2: the pipeline's rows are the Lean derivation

**PR C, the executable derivation.**
- `Ty.rowsExec`: an `Array`/hash-map implementation of `Ty.rows`, with one theorem, `rowsExec_eq : rowsExec = rows`.
- Compiled as ordinary Lean (`lake exe flock-rows`), with no kernel check per instance.
- It writes exactly what M0's prover consumes:
  - today, `flock-ir-unit/v2` per unit;
  - after the constant rollout's step 2, §2.2's layouts.
- **The check that the layout is what M0 consumes:** a byte-for-byte test of `flock-rows` against `ir_lower.netlist`
  for every template's unit and input set. It must reproduce the pinned hashes: RoPE's `933c4ef8…`, and every pin in
  #192's list.

**PR D, the statement builder uses it.** `circuit.compose` (#192) takes its rows from `flock-rows` instead of
`ir_lower.layout`, or, during the transition, checks the two equal. This is the M0 lane's code, so the M0 lane decides
how, with me (question 3).

**PR E, the public verifier recomputes and compares.**
- The Lean verifier holds every type by content (§2.7), recomputes `Ty.rows` for each, and refuses a statement whose
  rows differ.
- One theorem: accept implies rows = `Ty.rows` of the types. With PR A and PR B, L1 is then a theorem for every
  accepted statement, and the named hypothesis goes.
- Owner: the verifier lane (bc-8e519ca0), with me.

**PR F, the private-track form. A specification only, until Φ exists.**
- It's the same predicate, `RowsOf c : ∀ t ∈ types c, rows t = Ty.rows t`, proved at registration by Φ, as Φ proves
  `Circuit.WellFormed` (constant-api-private §5).
- Written into `PROTOCOL.md` and `DESIGN.md`. There's no code until the private track builds Φ.

**Questions for M0 (bc-ff572e70) and the constant rollout (bc-613ddf45),** which I'll send once the design lands:
1. **The layout policy.** If `calls/v1` inlines callees and runs CSE (§4, question 2), the derivation must implement
   that policy exactly. Otherwise rows are not a function of the type alone. Is the policy fixed and specified
   enough to put in Lean, or should the rows be derived before the policy runs?
2. **The unit layout.** Is the v2 unit layout fixed in the hierarchical format: input words, the ANDs, the output
   words, the constant last?
3. **Where the derivation runs.** Can the staging path call a Lean executable, which needs lake and the toolchain on
   the pod? If not, `ir_lower` keeps producing the rows, and PR E's recomputation is the soundness link: the builder's
   output is checked, not trusted.
4. **The `table/v2` generator.** Its `lo_bits` and its constant-bit drop for library tables must be the same function
   in Lean, Rust and Python. Who owns the one specification?

## Item 3: the gate circuit computes the IR (a plan, to send you before starting)

- **The inventory.**
  - `ir_lower.PIECES` maps 14 primitive ids to pieces today: `Bf16ToF32`, `F2fpBf16`, `F32ToBf16Rn`, `F32Add`,
    `F32Mul`, `F32Fma`, `F32Div` (constant divisor), `Bf16Add`, `Bf16AddF2fp`, `RopeOut`, `RopeOutAdd`, `SiluMulBf16`,
    `AmpereBF16TcDot16` and `HopperBF16WgmmaDot16`.
  - They're built from `fp.py`'s sub-pieces (align, normalize, round, pack and so on) and the tail pieces and reads.
  - The first step lists the leaf kinds exactly (your "about 32") and what each is built from.
- **The specification side is the real work.** Each primitive needs a Lean statement of its IR semantics. Today those
  exist only as Python: the IR evaluator, and `verity.ml.tc`'s exact hardware semantics.
  - Each port needs review, like a pin.
  - Table-backed primitives are specified by their pinned table.
- **The proofs, per leaf piece.** The piece's type computes its spec on every input:
  - parametric proofs where the piece is uniform in its width, such as adders, shifters and normalizers;
  - exhaustive `decide` where the domain is small (16-bit pieces, and 8-bit reads).
  - 32-bit pieces need structure, since the kernel can't enumerate 2^64 inputs. `bv_decide` is out, like
    `native_decide`: on this toolchain its proofs add a native-evaluation axiom. I checked this: a one-line
    `bv_decide` theorem depends on `…._native.bv_decide.ax_1_5`.
- **Composition.** A unit's types mirror its IR Definition's call structure, one type per Definition. So
  `compose_sound`, plus one proof per leaf kind, gives "the unit's rows compute the IR primitive" by the same
  induction as item 1, with no per-template work.
- **Sequencing.** It starts only after you confirm. It can run beside items 1 and 2, because it needs only `Ty.eval`
  from PR A.

## Order and dependencies

| PR | Owner | Needs | Merges before |
|---|---|---|---|
| A: `Ty`, `Ty.rows`, the rule theorems, `compose_sound`, `flatten_eval` | flock-soundness | the design; #187 as regression | B, C |
| B: `Rows.compose`, `placement_compose`, W6 | audit-lean, with me | #154, #177, A | E |
| C: `rowsExec`, `flock-rows`, the byte-for-byte test | flock-soundness | A; questions 1–2 answered | D, E |
| D: the statement builder uses it | M0 lane, with me | C, #192 | |
| E: the verifier recomputes and compares | verifier lane, with me | A, C, the constant rollout's step 4 (parser) | |
| F: the private-track predicate, specified | flock-soundness, with the private-track lane | A | |
| item 3: the leaf-piece gadget proofs | flock-soundness | A, your go | |

All of it runs on CPU. The kernel only ever checks the general theorems. Instances are checked by running the compiled
derivation and, in the verifier, by comparing, never by `decide` per instance.
