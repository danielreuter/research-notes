---
id: proofs/20261009T1718Z-report-rec-universal-class
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: cursor/rec-universal-class-95d4
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
