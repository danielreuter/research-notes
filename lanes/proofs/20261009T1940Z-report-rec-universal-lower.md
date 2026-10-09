---
id: proofs/20261009T1940Z-report-rec-universal-lower
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-66706a46-5939-5be0-a84f-7c0f0ac0b97f
---


# The universal unit's class of private circuits, in Lean

For proofs (bc-8416bc72), on Daniel's decision 3 (9 Oct, 16:01Z) and circuits' semantics (16:06Z). No PR, no Slack.
Branch `cursor/rec-universal-class-95d4`, head `c94bb5ec9`: my commit `6b347d636` (off `cursor/rec-gaps-4-7-2261` at
`efc84f720`), then a merge of that branch's new head `99d7a5b27` (rec-thm's `VStarU2`), whose only conflict was the
import list and docstring of `Recursive.lean`. Against `99d7a5b27` the branch is one new file,
`Security/Proofs/Flock/Recursive/UniversalClass.lean` (478 lines), and its import in `Recursive.lean`. `Universal.lean`,
`Property.lean` and `Audit.lean` are untouched.

## Outcome

**The class of decision 3 is defined and proved in Lean, and the file builds on node 1** (`r20261009-163826-5bab` on
`6b347d636`, and `r20261009-171008-52a7` on the merged head `c94bb5ec9`; `lean_changed --records Security/Proofs`):
`Built Proofs.Flock.Recursive.UniversalClass (4.0s)`, no warnings from it, and none of its declarations uses `sorryAx`.
The audit's FAIL is the branch's inherited `sorry`s only (ten, all in `Compile`, `Audit` and `Universal`).

The class is stated as decided: a description is any bit string of the unit's width, read in gate order, and the class
is every such string. Decoding is total with no hypothesis, the class depends on `{G, N_IN, N_OUT}` alone, and the layout
and interpretation agree with `universal.py` on vectors checked by the kernel. On rec-thm's question, `HClass.ofStmt` is
not this class: at no hidden entries it is one statement, the executable's own, and with hidden entries it is larger
than the universal unit (details under "Answer to (3)").

**A correction to the assignment's parameters.** The real class is `UniversalUnit_v1{G = 8090, N_IN = 64, N_OUT = 32}`,
not `{N_IN, G, N_OUT} = {8090, 64, 32}`: `universal.and_count(8090, 64, 32) = 66,841,560`, the staged class's AND count;
`and_count(64, 8090, 32)` is 1,301,006. So `W = 8154`, `K = 13`, and a description is 226,936 bits
(`real_width`, by `decide`).

## What is defined and proved

All in `FlockSoundness.Discharge.Recursion.UniversalClass` unless noted.

- **Parameters.** `Params` (`g`, `nIn`, `nOut`), `w = nIn + g`, `k = max 1 (bitLength (w − 1))` (Python's
  `index_bits`, with `bitLength` as Python's `int.bit_length`), `width = 2G + 2G·K + N_OUT·K`. `w_le_two_pow_k`: every
  wire has an index.
- **Layout.** `layout p : Place p ≃ Fin p.width`, an equivalence between the places (an op bit `(g, t)`, bit `j` of
  source `s` of gate `g`, bit `j` of output `i`) and the positions. `layout_op`: `2g + t`; `layout_src`:
  `2G + (2g + s)·K + j`; `layout_out`: `2G + 2G·K + i·K + j`. That is `universal.arguments`' order: op, then src, then
  out, gate-major, source `a` before `b`, each index least significant bit first. Op bit 0 picks AND over XOR and bit 1
  negates (`gateFn`), so the four values are XOR, AND, XNOR, NAND.
- **Interpretation.** `Desc p := Fin p.width → Bool`. `Desc.wiresTo` grows the wire list one gate at a time; a source
  index reads the list with default `0`, and `Desc.eval` reads each output index from the final list with default `0`.
  Its defining equations are circuits' semantics word for word:
  - `wire_input`: wire `i < N_IN` is `x_i`;
  - `wire_gate`: wire `N_IN + g` is `op_g (src a_g) (src b_g)`, where `srcVal g i` is wire `i` if `i < N_IN + g`, else
    `0`;
  - `eval_eq`: output `j` is wire `out_j` if `out_j < W`, else `0`;
  - `wire_of_le`: every index `≥ W` reads `0`.
- **Decoding.** `Circ p` is a private circuit of the class, acyclic by its type: gate `g`'s sources are
  `Option (Fin (N_IN + g))` (`none` is the constant `0`), its outputs `Option (Fin W)`, and `Circ.eval` evaluates gates in
  order (`Fin.snoc`). `decode : Desc p → Circ p` is a total function (no well-formedness hypothesis: an index past the
  gate's wires decodes to `none`). `eval_decode`: every description runs exactly as its decoded circuit. `encode`,
  `decode_encode` and `decode_surjective`: every circuit of the class is some description's, provided its outputs are all
  wires or `W < 2^K` (the constant-`0` output needs an index `≥ W`; at `W = 2^K` none exists. The real class has
  `8154 < 8192`).
- **The class.** `uclass p := Set.univ`. `mem_uclass`: every description is a member. `mem_uclass_iff`: membership is
  the same for any two descriptions, so the class reveals `p` and nothing else about a private circuit.
  `card_desc`: there are `2^width` descriptions.
- **Vectors against Python (`decide`, in the kernel).** `k_vectors`: `index_bits` on 13 `(G, N_IN)` pairs, including
  `(8090, 64)` and `(64, 8090)`. `real_width`. `eval_vectors_111`: all 32 descriptions of `{1, 1, 1}` on both inputs (one
  64-bit table). `eval_vectors_322`: six random descriptions of `{3, 2, 2}` (`W = 5`, `K = 3`, width 30) on all four
  inputs; these include forward reads and outputs past `W`.
- **The bridge** (in `FlockSoundness.Discharge.Recursion`): `Hidden.tmpl_of_nnz_zero`, `Hidden.side_of_nnz_zero` (a
  class with no hidden entries hides nothing: every hidden statement's sides are the public part),
  `HClass.ofStmt_toStatement` (at `nnz = 0`, every hidden statement of `HClass.ofStmt st …` is `Refine.stmtOf st` at its
  regions), and `Hidden.exists_side_ne` (with `0 < nnz` and a unit slot inside the block, one value-1 entry at the slot's
  corner gives a statement whose `A₀` is not the public one; that hidden statement is canonical).

**How the Python was checked.** `/tmp/ucl-vectors.py` (scratch, run from the checkout) decodes bit strings with the
layout above, asserts `arguments(net, x)`'s three leaves concatenated equal the input bits (so the layout is
`arguments`' order), and records `interpret`'s outputs. The vectors in the file are its outputs; changing one bit of a
vector makes `decide` fail (checked). Python's own tests hold the unit to `interpret`
(`test_boolean_universal.py`, random private circuits in range and not). Axioms: `propext`,
`Classical.choice`, `Quot.sound` only (scratch `#print axioms` on `eval_vectors_322`, `decode_encode`, `eval_decode`,
then the audit in the build). No `maxHeartbeats` change; the kernel `decide`s take about a second.

## Build

`r20261009-163826-5bab` on vy-nebius-1, tree `6b347d636`, through the node's Lean audit slot (queued behind
`r20261009-155056-c3ba`; the build itself took 17.7 s, two files changed, 102 s with the audit). Result:

- `Build completed successfully (5429 jobs)`; `✔ Built Proofs.Flock.Recursive.UniversalClass (4.0s)`, then
  `Proofs.Flock.Recursive` and `Proofs.Flock`. No warning names `UniversalClass.lean`.
- `AUDIT … Security/Proofs: FAIL`, 62,073 declarations in 967 modules. The offenders (`facts.json`) are exactly the
  ten inherited ones: `flock_inner_sound_compiled`, `…_fast100`, `…_plain`, `recursive_sound_compiled`, `…_fast100`,
  `zk_sessions_recursive_fork_inner` (`Compile`), `Flock.SecurityProofs.RecursiveAudit` (`Audit`),
  `compiledForkSound_ofStmt`, `…_of_fast100`, `…_ofSchedule` (`Universal`). No escapes.
- On the merged head, `r20261009-171008-52a7` (17:10Z): `Build completed successfully (5430 jobs)`, 62,232
  declarations in 968 modules (`UniversalClass` and `VStarU2` both audited), the same ten offenders, no escapes.
- Both are `lean-fast/v1` results (no kernel replay of every declaration). The `decide` vectors are kernel-checked when
  the file elaborates, and the scratch build printed only the three allowed axioms for them.

The bridge lemmas could not be built locally (their closure is 476 local modules and ArkLib); before this build I
checked them against stand-ins with the real definitions' shapes, and this build compiles them against the real ones.

## Answer to (3): is `HClass.ofStmt` this class?

**No, not by itself, and it shouldn't be.** `HClass` models hiding as up to `nnz` secret entries added to the public
matrices at unit slots. `HClass.ofStmt` takes the public part to be `Refine.matA/matB st`, and for the universal design
those already are the unit's lowering at every slot: they depend only on `{G, N_IN, N_OUT}` and the instance count. The
private circuit is not in the matrices. It is a runtime input: the description is in the witness rows, bound by the
registration, whose commitments are the regions' commit strings in the public file. So:

- **At `nnz = 0` the class is one statement.** `HClass.ofStmt_toStatement`: every hidden statement is
  `Refine.stmtOf st hwf regs`. In `RecursiveAudit` at this class, `Hidden cls` has one element, so the hidden statement
  `stmt` and its `x` are constant, and `_hx` says nothing. The private circuit is bound inside satisfiability, through
  the witness rows that the in-circuit row hash ties to their public commitments, not by the class. That is the right
  reading for the universal design, which hides nothing in its matrices. It also means `HClass` doesn't express what is
  hidden here (the rows and the registration's openings); that is the ZK property's and the commitments' job.
- **At `nnz > 0` the class is larger than the universal unit.** `Hidden.exists_side_ne`: with a unit slot inside the
  block, the class contains a canonical hidden statement whose `A₀` differs from the unit's lowering at that slot, so it
  is a statement of some other circuit. The all-pad hidden statement is still `stmtOf st`, so the class is strictly
  larger. That is the `Private.lean` model (the circuit hidden in the matrices), not this design.

**The gap between `HClass.ofStmt st … 0` and `uclass p`:**

1. **The unit's lowering in Lean.** Nothing in Lean lowers `UniversalUnit_v1` to its level-3 matrices, so no theorem
   says that `stmtOf st`'s satisfying witnesses for an instance are exactly the pairs `(d, x)` with outputs
   `Desc.eval d x`. That theorem is what would turn "the statement is satisfiable" into "some `d ∈ uclass p` gives these
   outputs".
2. **The row hash to the regions.** M0's statement hashes each instance's input rows in the circuit
   (`hm96-sha512/row/v1`, `class_statement.py`) and makes their `b ‖ c` public; that is what binds `d` to the registered
   description. The circuit enforces it and Lean checks the reads open their roots, but no lemma in this model states it.
3. **The unit, `interpret` and `Desc.eval`.** The unit against `interpret` is tested in Python; `interpret` against
   `Desc.eval` is the kernel vectors here. Neither is a proof at the real width.
4. **The regions per private circuit.** `RecursiveAudit` fixes `regs` per class, but the regions carry the
   registration's commit strings, which differ from one private circuit to the next. Rec-thm's gap 4 part (a)
   (`execClassAt`, the regions as a function of the statement) is where that dependence would go.

The short bridge is `HClass.ofStmt_toStatement` itself: at the universal unit's class, `RecursiveAudit`'s hidden
statement is `stmtOf st`, and the class of private circuits lives in the witness, as `uclass p`.

## Closing finding (b) (the paragraph appended to `internal/private-circuit/rec-private.md`)

Finding (b) is closed by decision 3 (Daniel, 9 Oct, 16:01Z): the class of `UniversalUnit_v1{G, N_IN, N_OUT}` is every
description of its width, read in gate order. The "outside" description of (b), a gate reading a wire computed after it,
is therefore a member, and accepting it is the right verdict, not a miss. Circuits pinned the reading (16:06Z): before
gate `g` there are `N_IN + g` wires, and a source index at or past that reads `0`; an output index at or past
`W = N_IN + G` reads `0`; all four ops (XOR, AND, XNOR, NAND) are meaningful. So (b)'s description is the member whose
forward read is the constant `0`; its 33 (small) and 3 (large) output differences were differences from a reading the
class does not use. `Security/Proofs/Flock/Recursive/UniversalClass.lean` (branch `cursor/rec-universal-class-95d4`,
`6b347d636`, built in `r20261009-163826-5bab` with no `sorry` of its own) states this class: the layout
(`universal.arguments`' order), the interpretation by exactly those equations (`wire_gate`, `eval_eq`), a decode to
gate-ordered circuits that is total with no well-formedness hypothesis (`eval_decode`), and the class as all `2^width`
descriptions, whose membership reveals only `{G, N_IN, N_OUT}` (`uclass`, `mem_uclass_iff`). Kernel-checked vectors
against `interpret` include forward reads and outputs past `W`. No format change and no rerun. What stays open is the
link from the unit's statement to this class. Nothing in Lean lowers `UniversalUnit_v1`, so no theorem yet says that the
statement's satisfying witnesses are the pairs `(d, x)` with outputs `Desc.eval d x`; until then that link rests on
Python's tests of the unit against `interpret` and on these vectors. In `RecursiveAudit` terms, the universal unit's
`HClass` is `HClass.ofStmt st … 0`, whose one hidden statement is `Refine.stmtOf st` (`HClass.ofStmt_toStatement`):
the private circuit is in the witness, and the class of private circuits is `uclass p`.

## Gap 4: the unit's lowering in Lean (assignment of 17:19Z)

This is item 1 of the gap list above, "the unit's lowering in Lean"; item numbers below refer to that list.

Branch `cursor/rec-universal-lower-95d4`, off `c94bb5ec9`, head `c86ccc9e1` (commits `3c1861c1a`, `32aba75f2`,
`8b484d12b`, `ac7e7779d`, `12bf1e4c2`, `c86ccc9e1`). It adds one file, `Security/Proofs/Flock/Recursive/UniversalLower.lean`
(892 lines, namespace `FlockSoundness.Discharge.Recursion.UniversalLower`), imports it in `Recursive.lean` (one line of
the docstring as well), and adds one test to `verity/ml/flock/tests/test_circuit_types.py`. `Universal.lean`,
`Property.lean` and `Audit.lean` are untouched. No PR, no Slack.

### Outcome

**Yes for the unit's lowering, generically in the parameters.** `uu_rows_iff` says, for every `{G, N_IN, N_OUT}`: once
`derive` lays out the unit's type, outputs `y` are carried by an assignment that satisfies the rows (constant at 1,
description columns `d`, data columns `x`) exactly when `y = Desc.eval d x`. No width is enumerated, so it covers
`{8090, 64, 32}` with the same proof as `{1, 1, 1}`.

The soundness half also holds on a typed statement's own unit rows. `uu_unit_sound` says that when `deriveChecked` (the
verifier's derivation for a staged statement) accepts and the unit's type is `uuType p`, the unit's rows as the block
holds them, Δ applied, carry `Desc.eval`. This also settles item 3 for the type `build` makes: `eval_uuType` relates
the unit to `Desc.eval` directly at every width, so `interpret` and the vectors are no longer in that chain.

Two conditions remain on what it covers:

1. **It is the type `universal.build` makes, not yet the staged one.** Lean's type is byte-identical to
   `circuit_types.from_gf2(universal.build)` over the four argument ports (six digests pinned on both sides). The type
   that `class_statement` stages for the typed statement is the same circuit with its wires renamed and its ANDs
   reordered, not the same bytes. Its registered rows also hold the description in a different bit order. Closing this
   is a staging change that needs a ruling (below).
2. **The derivation's success is a hypothesis.** The verifier checks it at run time (`derive`, or `deriveChecked` on
   a staged statement), so this costs soundness nothing. `flatOk_uuType` proves `derive`'s first check for every `p`,
   and it is also what `uu_unit_sound` needs. `derive`'s geometry check (`geoOk`) is checked only at the six pinned
   classes, by evaluation.

### What Lean had, and the design

Lean had nothing for this unit: no lowering of `UniversalUnit_v1` and no lemma about `gather`. What it had in general is
the flat-type semantics in `Proofs/Flock/Soundness/Types/Flat.lean`: `eval` of a `Flock.CircuitType` of AND items over
XOR forms, and `compose_sound` / `compose_complete`, which turn `eval` into a statement about the rows `derive` lays
out, for any flat type `derive` accepts.

So I wrote **a Lean builder of the unit as a flat `CircuitType`** and proved its `eval`, rather than proving the
semantics of the circuit file the staging writes. The reasons:

- The builder is a recursion in the parameters, so one induction covers every width.
- A file is a fixed object: 66.8 M ANDs at the real class. Its semantics would need either a proof about the Python that
  writes it, or a checker run at that width.
- The verifier's rows are `derive` of a type in exactly this format, so the theorems land where `compose_sound` already
  reaches.

The builder follows `universal.build` and `forms` step by step:

- **Forms** are ascending wire lists with constant 0. `symm` is their XOR (a sorted merge that drops common wires), and
  `xorSum_symm` proves it.
- **The pieces.** `andL` appends an AND item and returns its wire. `muxL`, `levelL` and `gatherL` are `forms.mux` and
  `gather.gather`. `gateL` is `build`'s gate: `s = a ⊕ b`, output `s ⊕ AND(t, AND(a, b) ⊕ s) ⊕ n`. `gatesL` and `outsL`
  are the gate loop and the outputs.
- **The type.** `uuType p` has inputs `(op, src, out, x)` as ports `(1, 2G)`, `(1, 2G·K)`, `(1, N_OUT·K)`, `(1, N_IN)`,
  which is `UniversalClass.layout`'s order, and one output port `(1, N_OUT)`.
- **The specs.** Each piece has a spec: the items only grow (`Ext`), the result reads only wires that exist (`Good`),
  and its value under `run` is the value-level function.

What is proved (all in the new namespace; scratch `#print axioms` shows only `propext`, `Classical.choice` and
`Quot.sound`):

- **The gather lemma, once** (`gatherB_eq`, `gatherB_lt`, `gatherB_ge`, with `getD_levelB` for one level). Whenever the
  words fit the index (`cur.length ≤ 2^|idx|`), the multiplexer tree is `cur[idx]` for an index below the length, and
  `0` at or past it. `gatherL_spec` reduces the builder's tree to `gatherB`. The sources use the lemma at
  `cur = Desc.wiresTo` (`gatesL_spec`), and so do the outputs (`outsAll_spec`).
- **What the type computes** (`eval_uuType`): for all input bits `x`,
  `eval (uuType p) x = List.ofFn ((descOf x).eval (dataOf x))`, so the outputs are `UniversalClass`'s `Desc.eval` of
  the description those bits hold on the data they hold.
- **Flat at every width** (`flatOk_uuType`): every item is an AND of two forms whose wires ascend below its own, and the
  `N_OUT` outputs' wires ascend below the last.
- **Its rows** (`uu_sound`, `uu_rows_iff`). Given `derive (uuType p) inSplit outSplit = .ok dd`:
  - `uu_sound`: any `z` that satisfies the rows with the constant at 1 has `z (dd.outCol i) = Desc.eval (description
    columns) (data columns) i`.
  - `uu_rows_iff`: the "exactly when" form, with `compose_complete` for the converse.
- **On a typed statement's unit rows** (`uu_unit_sound`). Given `deriveChecked types ls info words unit = .ok done` and
  `(ls.getD unit default).type.bind types = some (uuType p)`: any `z` that satisfies the unit's block rows
  (`blockRow`, Δ applied) with `one` at 1 has each output column equal to `Desc.eval` of the description columns on the
  data columns. It is `Dag.unit_sound` composed with `Dag.evalT_flat` (which needs `flatOk_uuType`) and
  `eval_uuType`, five lines.

### The tie to Python

- **Digests.** At six classes, `{1,1,1}`, `{2,2,1}`, `{3,2,2}`, `{5,3,4}`, `{7,9,3}` and `{16,16,8}`, the file's
  `#guard`s check that `uuType`'s SHA-512 digest (`Flock.CircuitType.digest`) is the one `from_gf2(universal.build)`
  gives over the same four ports. They also check that its item count is `universal.and_count`. These guards run
  Lean's evaluator when the file elaborates; they are checks, not theorems, and add no declarations.
- **The Python test.** `test_the_universal_unit_is_the_lean_builders_type` reads the six pins out of the `.lean` file and
  recomputes them in Python. The flock suite's inputs include `Security`, so a change on either side fails `check`. The
  file's 9 tests pass on `12bf1e4c2` through `suites.py flock` (which also checks that no test reads outside the
  suite's inputs), and on `c86ccc9e1` under pytest.
- **Acceptance.** `accepted` runs `CircuitType.check` (the format's rules) and `derive t [] []` at the six classes.
- **Why the real class is the same construction.** Both builders are the same recursion in `{G, N_IN, N_OUT}`.
  Python's `forms` folds no AND of this unit for any parameters: an index bit never occurs in a form, and every gathered
  value and gate output holds a fresh AND wire. `from_gf2` keeps every AND, since each feeds a later gather or an
  output's. So both make `and_count` ANDs in one order at every width (66,841,560 at `{8090, 64, 32}`).

### The staging gap (needs a ruling)

The typed statement's unit type is `from_gf2` of `partition_units.lower_class` over the traced Definition. It differs
from `uuType` in three ways:

- Its inputs are one-bit ports per leaf, in the order the trace first reads them, not `(op, src, out, x)`.
- Its ANDs are in `trace.emit`'s `(depth, kind, index)` order.
- `class_statement.sources` lays out each source's row in the same first-read order. Measured at eight classes up to
  `{16, 16, 8}`, the `op` row is in leaf order, but the `src`, `out` and `x` rows are not, and the rows themselves come
  in first-read order (`x, src, out, op` at most classes).

The benchmark (`benchmarks/private_circuit/universal.py`) stages through exactly this path with `packed=True`, so the
registered `src` and `out` rows hold the description's bits in an order that only the trace defines.

As evidence that it is the same circuit, the staged type computes the same function as `uuType` under the leaf renaming,
with the same AND count, at seven classes up to `{16, 16, 8}` (256 random vectors each). That check and the row-order
check are `art:44c20ac843726eaa098b94a59a8dcfd5080ef1c9be38024e43f70390c5bb7e7c` (scripts and output).

Options:

- **(a) Recommended: stage the universal unit in argument order.** The unit type would be `from_gf2(build)` in creation
  order with leaves in argument order (for the universal unit, or for every traced Definition), and each source's row in
  leaf order. Then the type tie is byte equality, which the six pins already check, plus one staging test. The row tie
  becomes plain arithmetic, generic in `p`: with `packed=True`, bit `j` of a source is bit `j mod 16` of the row's u16
  leaf `⌊j/16⌋`. This changes staged digests and the bit layout of registered rows, which is why it needs a ruling.
- **(b) Keep the staging and prove the renaming.** A generic Lean lemma (`eval` is invariant under a permutation of
  inputs and a reordering of items that respects dependencies), plus a certificate checked against both types at real
  width (66.8 M items through Lean's evaluator). The row order would also need the trace's first-read order stated in
  Lean, which it isn't. This is much heavier than (a).

### The row hash (the second part)

What exists:

- **The assumption.** `HmRowComputes` (`Soundness/Assumptions.lean`, "phase 2i") is a named `Prop`. The binding
  theorems take it for the rows the drawn units' tables read (`Binding/Rows.lean`'s `registered (hHm : rs.Computes)`).
- **Discharges on the untyped path only.**
  - `row_bc_setupH` (`Discharge/Hm/Bc.lean`): `tags.typed = false`, v1 rows.
  - `row_bc_tgt` (`Hidden/Wide/RowBc.lean`): rows of `16·words` bits.
  - `keyedRowsOuts_computes` (`Hm/Site.lean`): `HmRowComputes` at e2e-layout rows, given v1 ports, one input group and
    `outNet = unitNet`. It is used by `ZkReg/Bind` and `Composed/DefsJ`.
- **On the typed path, one result with open hypotheses.** `row_bc_of_sat` (`Discharge/Hm/Accept.lean`) is my correction
  to item 2 above, which said no lemma states the row hash. For an accepted template statement (`deriveChecked`,
  `TemplateLayout`), port `p`'s `b ‖ c` at its `hm96` slot is the commit string of the row prefix, the `2·words` row
  bytes at `Typed.msgCol`, and the salt. Its hypotheses: the port is unsegmented, its words fill its chunks
  (`2·words = 128·chunks`, a v1 row padded to whole blocks), and four copies of Δ hold (the first `cv` is the prefix's
  midstate, the chain between compressions, the `hm96` slot's `cv`, and the padding block). Nothing uses it yet. The
  copies are discharged only without a typed template (`Hm/Flat.lean`, `Hm/Copies.lean`; `delta_flat_eq`).
- **Registration binding.** `Verifier/Registered.lean` (`check_ok`, `opensLeaf_binding`), `regRowCommit_binding`
  (`Recursive/Private.lean`) and `RecursiveRanRegistered`'s `_hbind`.
- **Row formats.** The universal unit's rows are v1 (`hm96-sha512/row/v1`). `FLOCK_CORE_ROWS` applies only to FP GEMM
  coordinates (`element_rows` refuses anything else), so v2 rows are not needed here.

What's missing for the universal unit:

1. **Δ's copies on the typed path.** Discharge `row_bc_of_sat`'s four copy hypotheses from `HmRow.delta` for a typed
   template (`ExecTyped.lean` already describes that `HmRow.delta`). That gives a typed `Computes` for the class's rows.
2. **The layout tie.** Map unit input column `j` to its row byte and bit at `Typed.msgCol`. Under option (a) this is the
   `j mod 16` / `⌊j/16⌋` arithmetic; under (b) it is the trace's order.
3. **The composition.** An accepted statement, through the row hash, `registered` and `regRowCommit_binding`, makes the
   description columns the registered description's bits. `uu_unit_sound`, at each instance, then makes the outputs
   `Desc.eval` of that description.

### Builds (node 1, `lean_changed --records Security/Proofs`)

- `r20261009-175959-60ad`, tree `ac7e7779d` (the builder, `eval_uuType`, `uu_sound`, `uu_rows_iff`, the pins and
  `accepted`; not yet `flatOk_uuType` or `uu_unit_sound`), done 18:53Z:
  - `Build completed successfully (5431 jobs)`, with `✔ Built Proofs.Flock.Recursive.UniversalLower (5.1s)`. A
    failing `#guard` is an error, so the six digest pins and the `accepted` guard held. No warning names the file.
  - `AUDIT … Security/Proofs: FAIL`, 62,461 declarations in 969 modules (`UniversalLower` among them). The offenders
    (`facts.json`) are exactly the ten inherited `sorry`s listed under Build above, with no escapes.
  - Build time was 1,931 s, because 49 files differed from the node's warm tree (the other lane's). It is a
    `lean-fast/v1` result.
- `r20261009-182754-647e`, tree `c86ccc9e1` (the head), queued 18:27Z, has no result yet. At 19:36Z it was still
  waiting for the slot, behind two other lanes' runs: `r20261009-181827-0b24` held it from 18:51Z to about 19:25Z, and
  `r20261009-181906-0809` has held it since. Each of those builds took about 30 minutes, so `647e` should finish after
  20:00Z; `research fetch r20261009-182754-647e --all` will have it. Its tree differs from `60ad`'s only in
  `UniversalLower.lean`. The head's two new theorems, `flatOk_uuType`
  and `uu_unit_sound`, compiled in the scratch package against the real `Types/Flat.lean` and `Types/Dag.lean`, and
  `#print axioms` shows only `propext`, `Classical.choice` and `Quot.sound`.
- Cancelled while waiting for the slot, each covered by a later tree: `r20261009-175517-5ae9` (`32aba75f2`) and
  `r20261009-180928-8cd6` (`12bf1e4c2`).
- `5ae9` and `60ad` queued behind another lane's run, `r20261009-174634-cf8b` (`cursor/salted-hiding-reduction-95d4`),
  which held node 1's Lean slot from 17:46Z to about 18:17Z.
- Locally, the file elaborates in about 3 s against copies of its imports in a scratch package (`Flock/`, built
  `Types/Flat.lean` and `Types/Dag.lean`, `Audit/Circuit.lean`, `UniversalClass.lean`), with no warnings. No
  `maxHeartbeats` change.

### What's left

In order along the path, with the work each takes:

1. **The staging ruling, then the change.** Python only: `class_statement` / `partition_units` for the universal unit
   (or for every traced Definition), plus one test that the staged type's digest is `from_gf2(build)`'s and that each
   row is in leaf order. Lean needs nothing beyond the existing pins. It changes staged digests, so the benchmark and
   any recorded sessions are restaged. Small once ruled.
2. **From the unit's block rows to the statement's instances.** `uu_unit_sound` covers the unit's rows as the block
   holds them. What remains is to place each drawn instance at its slot with `setupH_flatTableClass` and
   `Placed/Typed.lean`'s `ProgPlaces`, so that an accepted statement's satisfying witness gives `uu_unit_sound`'s `z`
   at every instance. The completeness direction on the typed path would be `compose_complete`'s analogue for
   `deriveChecked`, which isn't needed for soundness. Small to moderate: `Placed/Typed.lean` already places the
   drawn units of flat table classes, so this is mostly wiring.
3. **The typed row hash** (missing item 1 under the row hash). This is the largest item: the untyped discharge took
   several files (`Hm/Delta`, `Hm/Copy`, `Hm/Copies`, `Hm/Flat`), and the typed `HmRow.delta` adds the template's
   entries.
4. **The layout tie** (missing item 2). Small under (a); under (b) it needs the trace's order stated in Lean.
5. **The registration composition** (missing item 3). Moderate, mostly composing existing `Binding` and `Private`
   lemmas. The `op`, `src` and `out` rows are committed once and opened by every instance, which is M0's shared rows.
6. **The regions per private circuit** (item 4 above, `execClassAt`), unchanged by this work.

Items 1 and 4 are small once ruled, item 2 is mostly wiring, item 5 is moderate, and item 3 dominates. `uu_unit_sound`
carries `ht`, the statement's unit type being `uuType p`; item 1 is what discharges it, as byte equality.
