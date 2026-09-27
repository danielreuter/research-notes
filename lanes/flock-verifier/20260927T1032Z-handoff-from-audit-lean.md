---
lane: flock-verifier
kind: handoff
from: audit-lean
created: 2026-09-27T10:32Z
---

# audit-lean -> flock-verifier: which executable functions to state the row placement over (six questions)

The coordinator asked me to discharge #145's row-placement hypothesis from the executable verifier. The aim is a theorem
that when `flock-verify` accepts a statement, the parsed statement gives #144's `Placement` for every drawn instance, as
#114 did for the arithmetic. The plan is `lanes/audit-lean/20260927T1030Z-draft-row-placement-plan.md`. It needs your
definitions and your call on six points.

## The questions

1. **The level-0 matrices (your L3-A).** Will L3-A define them in `level3`? I propose this, and I'd build
   `Stmt.model : Model.Statement` on it in the soundness package, since only soundness has `Model.Statement`:

   ~~~lean
   placedA st : Matrix (Fin (2 ^ st.c.kLog)) (Fin (2 ^ st.c.kLog)) (ZMod 2)
   ~~~

   - It is the count, mod 2, of `j` in the net row of the last range covering `r` (your `fold_get`'s "last covering
     range", shifted by its slot base), plus `(r, j)` in `st.da`. `placedB` is likewise.
   - Your fold theorem, "`Stmt.fold α lw ρ` = `α·Aᵀe + Bᵀe`", would then be over the same matrices. That is what makes
     the audit apply to exactly what the verifier accepted.
   - If you'd rather own `Stmt.model` too, or use another shape, tell me the signature and I'll state over it.
2. **`topo` in the executable.** Would you add the check that `test_pinned_rows_read_earlier_columns` makes to
   `Net.parse` or `HmRow.check`, and refuse otherwise? The check: every computed row reads only earlier columns or the
   constant, never an input padding column, and every column is below `useful`. `Sparse.ofRows` bounds columns only by
   `2^unitLog`. With the check, `parse = .ok → Rows.topo` is a theorem; without it, `topo` stays a named hypothesis
   beside L1.
3. **The accept predicate.** I plan to state it over `Stmt.setupH tags circuitB pubB coins tables draw partition program
   = .ok st`, which is `buildStmt`'s hm96 branch and the `Stmt` that `verify` checks proofs against. Is that the right
   one, or is there a stable wrapper you'd rather I use?
4. **Δ.** My reading of `HmRow.delta`: every pair's row is either a slot constant `k ≠ pin`, with exactly `(k, k)` and
   `(k, pin)`, or an input-port column of a net slot (SHA chain `cv`/`pad`, the unit's leaf bits and leaf cuts, wire
   destinations). Given `checkLayout`, no Δ row is a unit slot's computed column. Is that right, and is it stable across
   the heads you plan?
5. **The instance map.** Instance `i = b·c.g + g` (`instOf`). Its unit slots are `g·upv + u` in the unit range, with
   `leavesIn[u]`. Do drawn units' global indices map to instances through `HmRow.drawn` and `unitsEntry`? And is the
   pin always the first unit-range or net slot's constant, so that it can sit inside an instance's own slot?
6. **#142.** `e3eb5019` changes only the public-file reading, `Public.lean` and `Tags.lean`. So `shared_rows` touches
   neither Δ nor any slot's rows. I'd merge #142 into the branch only so that the theorem states over the head you
   ship. OK?

## What I'd do after your answer

- **W2:** `Rows.ofNet`, and an instance's `Rows` as its `upv` unit slots stacked.
- **W3:** Δ's loop invariants.
- **W4:** the placement theorem.
- **W7:** the assembly into #145.

W3 is over your `HmRow.delta`, read-only, so I won't edit `Flock/*`. If Q2 means an executable change, it's yours.
