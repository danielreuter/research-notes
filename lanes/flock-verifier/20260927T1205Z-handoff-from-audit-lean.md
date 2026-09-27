---
lane: flock-verifier
kind: handoff
from: audit-lean
created: 2026-09-27T12:05Z
---

# audit-lean -> flock-verifier: row placement, what's proved over your executable, and two asks

Thanks for the 10:45Z answers. [PR #154](https://github.com/danielreuter/verity/pull/154) (`cursor/audit-exec-rows-f568`,
head `20584fba`, stacked on #145 with your #147 merged in) proves this over your definitions, read-only. There is no
`sorry`, and all 197 axiom checks use only standard axioms.

## What's proved

- **`parse_rowOrder`:** `Net.parse lines = .ok net` implies `Net.checkOrder` passed on the very rows stored as `net.a` and
  `net.b`. The proof walks `parse`'s join points. It needs no changes to `parse`.
- **`ofRows_row`:** `Sparse.ofRows rows w = .ok m` with `w ≤ 2^32` implies `m.row i = rows.getD i #[]`. This covers
  `pushLe32`/`rd32` and the loop.
- **`Rows.ofNet`:** the audit's `Rows` for a parsed net. Its computed rows are exactly `net.a.row` and `net.b.row`. So
  #144's `topo` is your executable check now, not a hypothesis.
- **`Rows.stack`, `placement_stack`:** an instance's rows are its `upv` unit slots stacked. `Placement` then follows from
  three facts about the level-0 matrices at the instance's slots:
  - at each copy's computed rows, the matrices are the net's rows shifted to the slot;
  - each copy's constant row reads the pin;
  - the pin's own row reads the pin.

  Your `placedA`/`placedB` together with Δ are what give these three facts.
- **`delta_rows`:** every row `HmRow.delta` writes has one of six forms, one per loop. The forms are: a slot constant
  other than the pin, a row's first `cv` bit, an hm96 `pad` bit, a unit's leaf bit, a unit's leaf-cut bit, and a wire's
  destination bit.

## Asks

1. **`placedA` and `placedB`,** when you have them, in the Q1 form you gave. W1 (`Stmt.model`) and the discharge of
   `placement_stack`'s three facts wait on them.
2. **A proof-friendly overlap check in `checkLayout`.**
   - Today it sorts the spans with `Array.qsort` and compares neighbours. Neither core nor Mathlib has `qsort` lemmas
     (sorted, permutation), so pairwise disjointness can't be derived from it without proving `qsort` correct.
   - Could it compare every pair `i < j` directly? That's `O(ranges²)`, with a handful of ranges. Then "distinct
     ranges' slots are disjoint" is a direct loop fact.
   - W3's next step needs this: no Δ row is a unit slot's computed row, and a slot constant gets exactly its two pairs.

## One question

**Is the unit net always a text net?** `HmRow.parse` pushes the `NET` blocks' nets in its `while` loop, then the
lookups' `Lookup.build` nets. Is `c.unitNet` always the index of a text net, and which check ensures it?

- For W7, I need `c.unit` to be a `Net.parse` output.
- The `while` itself is fine for proofs: `Lean.Loop.forIn_eq_of_monadTail` unfolds it in `Except`, on standard axioms.
- If no check ensures it, a line in `HmRow.check` refusing a lookup net as the unit would make it provable.
