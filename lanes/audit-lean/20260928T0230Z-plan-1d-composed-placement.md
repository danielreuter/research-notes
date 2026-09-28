---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: audit-lean · kind: plan · created: 2026-09-28T02:30Z · repo: danielreuter/verity · about: verified-lowering phase 1,
item 1d (`docs/verified-lowering-design.md` §3; the soundness lane's `lanes/coordinator/20260928T0156Z-plan-from-flock-soundness-phase1-prs.md`)

# 1d: the placement of composed rows, planned against #154, #156, #177 and S3

**Status: a plan. Nothing is started.** The interface questions went to flock-soundness (bc-9e538dc5) and flock-verifier
(bc-8e519ca0) at the same time (`lanes/flock-soundness/20260928T0230Z-handoff-from-audit-lean-1d-interface.md`,
`lanes/flock-verifier/20260928T0230Z-handoff-from-audit-lean-147-lookuprows-1e.md`). CPU only, $0.

## 1. What 1d proves

For a statement in the hierarchical format, 1d proves #144's `Placement` for each unit's composed rows. The rows are
placed in the model statement of the matrices the verifier folds. This gives `UnitPlace` for every drawn unit, which
feeds `loweringSoundB_of_place` and #171's `_placed` forms. With S2/S3's `compose_sound`, L1 then holds for that unit.

| Piece | Statement | What it replaces |
|---|---|---|
| `Rows.compose` | a unit's `Rows` in logical order, built from `derive`'s output for its layout | `Rows.stack (Rows.ofNet h) upv` (#154), its special case |
| `compose_topo` | every computed row of `Rows.compose` reads earlier columns or `one` | `Rows.ofOrdered`'s `topo` from the parser's check |
| `composePlace` | each logical column's block column: the physical placement of `derive`'s rows, for instance `g` | `stackPlace` |
| `placement_of_realizes` | if the block matrices, at every logical row's physical column, read exactly the physical images of its reads, and the pin's row reads the pin, then `Placement S (Rows.compose …) composePlace` | `placement_stack` |
| `placement_compose` | `WellFormed` and "the block is `derive`'s rows placed, plus Δ" give that realization | #177's `Layout.placement` |
| `unitPlace_compose` | the `UnitPlace` that #171's `_placed` forms take, given W6's `inst` | `unitPlace_of_setupH` |

`Rows`, `Placement`, `lowering_sound`, `UnitPlace` and the audit layer don't change (constant design §2.8). #177's
theorems stay as they are for the old tags, since old cells keep old statements.

## 2. How it is built

**One source for both orders.** `derive` produces the physical rows the verifier folds. `Rows.compose` must read the same
rows in logical order, and #144's `Placement` asks that the two agree row for row. So `Rows.compose` is *defined from*
`derive`'s output, not written beside it. I've asked the soundness lane (§4, Q1) to have `derive` produce, or expose, its
rows as one list in logical (call-point) order with each row's physical column. Then:
- the folded matrix is that list placed;
- `Rows.compose` is the same list, with each read translated from a physical column to its logical index;
- `composePlace` is the physical column;
- `placement_of_realizes` is close to definitional.

The work is then in two places:
- **`compose_topo`:** each row reads only inputs, earlier rows or the constant. This follows from the type format (a form
  reads earlier wires; a caller reads a callee's outputs only after its call point) and from `derive`'s order. Proved by
  induction over the DAG with the type's column map monotone.
- **The geometry, from `WellFormed`:** an instance's rows have distinct physical columns, inside their layouts' ranges,
  and no other row, instance or range writes at those columns. This generalizes #177's argument:
  - pairwise-apart spans at the block level: #177's `rangesEntry_of_covers`, `Apart`, `lastCover`;
  - aligned, disjoint callee ranges inside the caller's range, clear of its own region. These are the placement clauses
    of `WellFormed`, which the constant rollout is adding beside #194's type clauses;
  - Δ's pairs at the instance's columns: the unit-level binding copies become one more form of #177's `delta_split` and
    `DeltaIn`, beside the slot constants and the leaf maps.

**What the proof no longer has to walk.** #177 walked `HmRow.check` to get the layout facts. With #194's pattern, the
parser decides `WellFormed` and `check_ok` states that acceptance implies it. So the new layout facts come from one
theorem, not a walk. The setup walk stays (1e): the `extract_lets` technique from #177's `ExecCircuit.lean` carries over.

## 3. Milestones, dependencies and sizes

| Step | Contents | Needs | Lean lines |
|---|---|---|---|
| 1d-0 | Agree the interface: `derive`'s output (Q1), the logical order (Q2), binding and constant rows (Q3, Q4), the unit-level slots (Q5) | this note's questions answered | none |
| 1d-1 | `Rows.compose`, `compose_topo`, `composePlace` and `placement_of_realizes` for flat and inlined types: a unit with no placed callee. Includes `Rows.compose` = `Rows.ofNet` on a flat type, and the old `Rows.stack` as `upv` placed calls with no bindings | S1 (`derive` for flat types) | 300–400 |
| 1d-2 | Placed callees and reads: `Rows.compose` over the DAG, `compose_topo` by induction, the geometry lemmas from `WellFormed`'s placement clauses, and `placement_compose` at the matrix level | S3; the placement clauses of `WellFormed` (constant rollout) | 500–700 |
| 1d-3 | From the accept step: `placement_compose` from `setupH` (new tags), and `unitPlace_compose` for #171's `_placed` forms | 1e's theorem that an accepted `setupH` folds `derive`'s rows placed, plus Δ; flock-verifier's recursive `placedA`/`placedB` | 200–400 |

That totals 1,000–1,500 lines, the design's estimate.

**How the 1d/1e cycle breaks.** The design has 1d needing 1b and 1e needing 1d. 1d-1 and 1d-2 are stated at the matrix
level, under a hypothesis of the form "the level-0 matrices are `derive`'s rows placed, plus Δ". 1e discharges that
hypothesis from its new `Stmt.setup`. 1d-3 is then the composition of the two. It lands in whichever of 1e or 1d-3 lands
last; it is a few lines.

**Order.**
- 1d-1 can start as soon as S1's `derive` has a stable type.
- `Rows.compose`'s definition should land before S4, since W6 (`IsRowsUnit u (Rows.compose …)`) is stated over it.
- 1d-2 follows S3.
- 1d-3 follows 1e.

## 4. The questions that fix the interface

The first four went to flock-soundness. The fifth, with the Δ binding shape and the pin rule, went to flock-verifier.

1. **`derive`'s output.** Can `derive` produce, or expose through one lemma, its rows as a list in logical order, each row
   with its physical column? If `Ty.rows` is a map from position to row, 1d needs the inverse map and its injectivity,
   which is the same fact the geometry proves.
2. **The logical order.** Constant design §2.8 puts a type's constant last. For `topo`, a type's constant row has to come
   *first* in its segment:
   - a placed callee's constant copies its caller's constant (§2.2), so the caller's constant must be earlier;
   - the root's constant row reads `one` (the pin), as #154's `Rows.stack` has each copy's constant first.

   Proposed order, per type, from its call point:
   1. its constant copy;
   2. its binding copies, one per non-exported callee input bit;
   3. its own rows and calls in item order, where a placed call is that callee's segment, recursively, and an inline call
      or read is own rows;
   4. its output copy rows.

   The unit's inputs, exported bits included, come first, and `one` comes last. S4's W6 and S2's statement have to use
   the same order.
3. **Binding copies.** §2.2 now says a binding copy is `form · 1`, which is `a = form, b = [const]` in `Rows`. The unit
   level binds through Δ, and Δ today writes the same pairs to A and B. That makes the row `form · form`: the same
   Boolean value, but a different row. Which does each level use? `Rows.compose` must mirror it exactly (§4 Q5).
4. **Which constant a constant copy reads.**
   - Inner callees: their caller's constant column.
   - Callees placed by the unit's layout, in their own block ranges: Δ's first loop wires each slot's constant to the
     pin, as today.

   Is that right? The two give different logical reads.
5. **For flock-verifier (1e): the unit-level slots and the pin.**
   - Which slot of each block range does instance `g` occupy? This generalizes `instOf`'s `ur.slot (g·upv + u)`.
   - Are the unit's own-region bindings and its callees' input bindings Δ entries, with `da = db`?
   - Is the pin still the first non-mask range's first slot constant, with a count of at least 1?
   - How will the recursive `placedA`/`placedB` express nesting: per range, or per type with shifts?

## 5. What carries over, and what goes

**Carries over:**
- from #154: `Rows.ofNet`, `ofRows_row`, `Rows.stack` (as the special case), `placement_stack`'s proof pattern;
- from #156: `placedA`/`placedB`'s range-and-Δ structure, which needs its recursive form;
- from #177:
  - `spanH`, `Apart`, `rangesEntry_of_covers`, `lastCover`;
  - `delta_split`, `DeltaIn`, `InBit` (extended with the binding form);
  - `Layout.model`;
  - the walk technique (`extract_lets`, `loop_inv`).

**Goes, for new tags:** reading rows from `Net.parse` (`parse_facts`' text-net branch), because `derive` produces the rows.
The lookup slot's facts become `table/v2`'s (`build_computes_v2`, the constant rollout's).

## 6. Status of #154, #156 and #177 (02:30Z)

- **#154** (`e0dd3323`), now based on `main`: merged `main` and #147 `ec162ac8`.
  - The `ASSUMPTIONS.md` edits moved to `README.md` §1.5 after #180's split.
  - `parse_checkOrder` steps over #147's new `Net.parse` check.
  - A separate commit fixes #185's `LookupRows.build_spec`, which #147's `Lookup.build` change breaks on `main` (handed to
    flock-verifier for #147).
  - Checks: 255 of 255 on standard axioms; the flock tests pass.
- **#177** (`81552896`): merged #154 and #156 `40b78fde`.
  - The docs moved into #180's layout.
  - `setupH_spec` steps over `main`'s new stratified-draw check.
  - Checks: 277 of 277 on standard axioms; `tools/lean/audit.py --no-replay` passes on the soundness, executable and
    level3 packages (level3 with all 50 pins); the flock tests pass.
- **#156** (flock-verifier's): conflicts with `main` in `level3/FlockLevel3.lean`, on the import lines, where it and #185
  both add one. #177 carries the union.
- **Merge order:** #147, then #156, then #154, then #177. All four are drafts, and none has had the independent Lean
  audit.
