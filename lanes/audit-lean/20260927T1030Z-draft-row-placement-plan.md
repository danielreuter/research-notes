---
id: audit-lean/20260927T1030Z-draft-row-placement-plan
campaign: verity
lane: audit-lean
kind: draft
status: open (progress 12:05Z below)
repo: danielreuter/verity
origin: audit-lean
---

# Plan: discharge the row-placement hypothesis from the executable verifier

**The goal.** When `flock-verify` accepts a statement, the parsed statement gives a `Placement` for every drawn instance.
So [#145](https://github.com/danielreuter/verity/pull/145)'s `loweringSoundB_of_place` gets its `UnitPlace`s from what the
verifier accepted, and the audit bound applies to exactly that, the way [#114](https://github.com/danielreuter/verity/pull/114)
linked the arithmetic.

**Verdict for tonight: too large to finish at the no-`sorry` bar, so this is the scoped plan.**
- The placement proof itself is small.
- It needs a definition that doesn't exist yet: the statement's level-0 matrices as the verifier builds them (L3-A,
  flock-verifier's).
- It needs loop-invariant proofs over two executable functions, and a choice of what one template instance's `Rows` are.
- The questions for flock-verifier (bc-8e519ca0) are in `lanes/flock-verifier/20260927T1032Z-handoff-from-audit-lean.md`.

## The theorem to prove

Stated over the executable's accept step for `hm96-sha512/row/v1` statements: `Stmt.setupH`, `Main.buildStmt`'s branch,
which is the `Stmt` that `verify` checks proofs against.

~~~lean
theorem placement_of_setupH
    (h : Flock.Stmt.setupH tags circuitB pubB coins tables draw partition program = .ok st)
    (b : Fin (2 ^ st.nbl)) (g : Fin st.c.g) (hi : st.c.instOf st.n b g = some i) :
    Placement st.model (instRows st) (instCol st g)
~~~

- `st.model : Model.Statement`: the statement the soundness theorems are about, built from `st` (W1).
- `instRows st : Rows`: one template instance's rows, which are the VU's `upv` unit-net slots stacked (W2).
- `instCol st g`: the instance's columns in the block. Copy `u`'s column `c` is `ur.slot (g·upv + u) + c`, and the
  shared constant is `st.pin` (W4).

Then `place S R u := ⟨instRows, inst, b, instCol, placement_of_setupH …⟩` for #145. The `inst` comes from the circuit side
(W6).

## What is already there (heads as of 10:30Z)

- **The consumer.** #145 (`07e63e39`) has `LoweringSoundB` and `loweringSoundB_of_place`. #144 (`084f8478`) has
  `Placement S R col`:
  - `hA`, `hB`: the level-0 rows at the computed columns read exactly the placed columns;
  - `hA₁`, `hB₁`: the constant's rows read the pin.
- **What the parser already guarantees** (`Flock/Net.lean`, `Net.parse`):
  - input rows are `A = B = [i]` or empty;
  - the constant is the last useful column, with `A = B = [const]`.
- **What the parser doesn't check:**
  - that computed rows read only earlier columns or the constant (#144's `Rows.topo`). A Python test covers it,
    `test_pinned_rows_read_earlier_columns`.
  - column bounds below `useful`. `Sparse.ofRows` bounds them only by `2^unitLog`.
- **The layout checks** (`Circuit.checkLayout`, run by `parse`; `HmRow.check`):
  - ranges are aligned and don't overlap;
  - wires stay inside their slots' ports, and none goes into a unit's leaf port;
  - leaf maps are per unit.
- **Δ** (`HmRow.delta`) is a pure function with six loop nests:
  - every slot constant `k ≠ pin` gets `(k, k)` and `(k, pin)`;
  - the SHA chain's `cv` and `pad` bits get `(i, i)` and `(i, src)`;
  - each unit's leaf bits and leaf-cut ports, and every wire's destination, likewise.
- **Consequence for placement.** Every Δ row is either a slot constant or an input-port column of a net slot. So Δ never
  touches a unit's computed rows, and it turns each unit slot's constant row into `A = B = [pin]`. The row at `pin` itself
  stays `[pin]`.
- **The fold, partly done in L3-A** (`level3/FlockLevel3/FoldStmt.lean`): `fold_get`, `slot_term`, `baseOf_get`. A
  successful fold's entry is the last covering range's slot base, plus Δ. What's missing is the explicit matrices and
  "fold = α·Aᵀe + Bᵀe over them", which flock-verifier's level-3 plan names as L3-A's goal.
- **#142** (`712ae5f7`, `shared_rows`) changes only `HmRow.lean`'s public-file reading, `Public.lean` and `Tags.lean`
  (commit `e3eb5019`). It changes neither Δ nor any slot's rows, so it bears on the input binding (the link), not on
  placement.
- **The instance map.** Instance `i = b·c.g + g` (`Circuit.instOf`), in VU `g` of block `b`. Its units are unit-range
  slots `g·upv + u` for `u < upv`, with leaf maps `leavesIn[u]`.

## Work items

| # | Item | Owner | Package | Size and difficulty |
|---|---|---|---|---|
| W1 | The level-0 matrices as the verifier builds them. `placedA st r j` = the count, mod 2, of `j` in the net row of the last range covering `r` (shifted by its slot base), plus `(r, j)` in `st.da`; likewise `B`. `st.model` adds `m`, `kLog`, `pin : Fin (2^kLog)` with its bound, and `regions` | flock-verifier: the matrices, as L3-A needs them for the fold theorem. Me: `Stmt.model` in soundness, which alone has `Model.Statement` | `level3` (matrices), `soundness` (model) | Definitions plus the bounds from `setupH`'s checks. Small, but it has to be agreed first, because W3 and W4 are stated over it |
| W2 | `Rows.ofNet` (`nIn = inWords·128`, computed rows `nIn … constPos−1`, constant `constPos`) and `instRows` (`upv` copies stacked, each copy's constant a computed row reading the shared constant). Needs `topo` and the column bounds | Me. The `topo` check in the executable is flock-verifier's call (Q2) | `soundness` | A definition and stacking lemmas, moderate. `parse = .ok → topo` is a loop invariant over `Net.parse`'s row loop. If the executable doesn't check `topo`, it stays a named hypothesis next to L1 |
| W3 | Characterizing Δ: every pair of `HmRow.delta c pin` has its row at a slot constant `≠ pin` (with exactly `(k, k)`, `(k, pin)` once) or at an input-port column of some net slot. With the layout checks, no Δ row is a unit slot's computed column | Me | `soundness`, over `Flock.HmRow.delta` | **The long pole.** Six `Id` for-loops over `Std.Range`, pushing into an array; invariants by `forIn` over `List.range'`. The layout facts come from `checkLayout`'s success, which is itself a loop over ranges |
| W4 | `placement_of_setupH`: from W1, W3 and non-overlap, the row at `instCol (comp i)` is the net row shifted, with no Δ, so `hA`/`hB`; the constant rows are `[pin]`, so `hA₁`/`hB₁` | Me | `soundness` | Small once W1–W3 exist |
| W5 | The partition's drawn unit to `(b, g)`: through `HmRow.drawn`, `unitsEntry` and `deriveTemplateUnits`, the global unit index is an instance of this statement; with #145's `tab S R u` | Me, with flock-verifier on the functions | `soundness` | Moderate: JSON-level functions (`drawn` reads the draw). Can be stated over `pub.header.units` first |
| W6 | The circuit side: `inst : IsRowsUnit u (instRows st)` for C = `Prog.circuit`, built from the registration's program and the parsed nets, so that `p.rows u = instRows` | flock-soundness (#144's `Prog`) | `soundness` | Depends on how C's `Prog` is built from the program. Out of this plan's scope, but W2's `Rows` shape must match it |
| W7 | Assembly: `setupH = .ok st` gives `place` for every drawn unit, then `loweringSoundB_of_place`, then #145's `flock_batched_count` over `st.model` | Me | `soundness` | Small |

**What makes the audit apply to "exactly what the verifier accepted"** is W1 plus L3-A's fold theorem, which says the
verifier's lincheck is `st.model`'s lincheck. That is flock-verifier's L3-A. Placement (W2–W4) is mine, and it holds over
W1's definition independently.

## Order and stacking

1. Agree W1's signature with flock-verifier (the handoff).
2. Me: W2 and W3, on a branch stacked on #145 with #142 merged in. #142 doesn't change the functions W3 reads, but it is
   the verifier head this should state over.
3. W4, then W7.
4. Then W5 and W6, with flock-soundness.

Each step keeps the bar: no `sorry`, standard axioms in `Check.lean`, and the theorems importing the running definitions
(`Flock.*`, through `level3`), as `Instance.lean` does.

## Risks

- **`Rows` for an instance.** Stacking `upv` copies of the unit net with per-copy constants as rows reading the shared
  constant must match #144's `Rows` and `Prog` (W6). If the pin column falls inside an instance's own slot, `instCol` is
  not injective. `Placement` doesn't need injectivity, but `IsRowsUnit.wire_inj` does, on the circuit side.
- **Other nets in a VU** (`sha512x3`, `hm96`) are the row-leaf hashing. They're not part of the audit unit, so
  placement covers the unit net's slots only. Their correctness is the link and the row leaf's binding.
- **Reasoning about imperative loops is laborious.** `level3` has the pattern (`placeSlot_get`), but `HmRow.delta` is
  bigger.

## Progress, 12:05Z

[PR #154](https://github.com/danielreuter/verity/pull/154) is at `20584fba`, stacked on #145 with #147 merged in. There is
no `sorry`, and all 197 axiom checks use only standard axioms.

**W2 is done:**
- `parse_rowOrder`: an accepted `Net.parse` passed #147's `Net.checkOrder` on the rows it stored;
- `ofRows_row`: `Sparse.ofRows` reads back its rows;
- `Rows.ofNet`: the audit's `Rows` for a parsed net, with `topo` proved;
- `Rows.stack`: an instance's rows, in the shape flock-soundness confirmed. The one refinement is that each copy's
  constant row comes first and the copy's rows read it.

**W4's core is done.** `placement_stack` reduces `Placement` to three facts about the level-0 matrices at the instance's
slots.

**W3 has started.** `delta_rows` gives every Δ row one of six forms. Next, from the layout checks: no form is a unit slot's
computed row, and a slot constant gets exactly its two pairs.

**Blocked, or needing more work:**
- **W1** waits on flock-verifier's `placedA`/`placedB`.
- **W3's layout step** needs pairwise disjoint ranges. `checkLayout` checks overlap after `Array.qsort`, and `qsort` has
  no lemmas, so I asked flock-verifier for a pairwise check (`lanes/flock-verifier/20260927T1205Z`).
- **W7** needs `c.unit` to be a `Net.parse` output through `HmRow.parse`'s `while` loop. That loop is provable with
  `Lean.Loop.forIn_eq_of_monadTail`, which uses standard axioms.
