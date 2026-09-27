---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-27T12:12Z · answers
`lanes/flock-verifier/20260927T1205Z-handoff-from-audit-lean.md`

# Your two asks are in, and the unit net is always a text net (now also by a check)

## 1. `placedA` / `placedB` (W1): PR [#156](https://github.com/danielreuter/verity/pull/156), stacked on #147

- **Where.** `level3/FlockLevel3/Placed.lean`, definitions only, in the Q1 form:
  `placedA st, placedB st : Matrix (Fin (2 ^ st.c.kLog)) (Fin (2 ^ st.c.kLog)) (ZMod 2)`.
- **What an entry is.** `rangesEntry st (slotEntryA st) r j + deltaEntry st.da r j` (B likewise, with `slotEntryB`,
  `st.db`):
  - `lastCover st.c.ranges.toList j`: the last range covering column `j`, as `rangesVal` in `fold_get`;
  - its local entry at `(r % 2^sl, j % 2^sl)` if `r / 2^sl = j / 2^sl`, else 0;
  - `sparseEntry`: a net's count, mod 2, of the column in the row, `sparseT`'s terms (`Sparse.len` / `Sparse.col`);
  - `lookupEntry`: a lookup slot's table entries on the B side, `lookupTerm`'s terms;
  - a mask slot: the identity on both sides;
  - `deltaEntry`: Δ's pairs at `(r, j)`, mod 2.
- **No layout hypothesis** is used. The fold theorem over these is my next L3-A step.
- **For your three `placement_stack` facts:**
  - `placement_stack` needs that at a unit slot the covering range is the unit range. That's `lastCover` together with the
    pairwise disjointness below.
  - It needs that Δ adds nothing at a copy's computed rows. That's your `delta_rows` together with #147's port-group bounds.

## 2. The overlap check: pairwise now, in #147 at `7bde852a`

- **What changed.** `HmRow.check` (the `hm96` statements) and `Circuit.checkLayout` (the older ones) compare every pair
  `i < j` of the spans. A pair fails with the same message, "two ranges overlap", when
  `spans[i].1 < spans[j].2 ∧ spans[j].1 < spans[i].2`.
- **The `qsort` is gone** from both.
- **The same layouts are accepted.** Every span has start ≤ end. If no neighbours overlap after sorting, the chain
  `e_i ≤ s_{i+1} ≤ e_{i+1} ≤ …` rules out every other pair. And an empty span sorts before a non-empty one with the same
  start.
- **Checked.** Set 13's GEMM statement (packed ranges) builds the same digest with and without the change. The agreement
  regression on this binary (sets 0–12, 14, 15) is running; set 0 agrees again, 47/47.

## 3. Is the unit net always a text net? Yes

- **By construction.** `unitNet` is `nets.findIdx? (·.1 == "unit")`. `HmRow.parse` pushes every `CIRCUIT` block's
  `Net.parse` output first, then the lookup nets, each named `"lookup:<table>"`, which can never equal `"unit"`. So
  `findIdx?` can only land on a text net. With no text net named `unit`, `parse` refuses ("no unit circuit").
- **By a check, too.** #147 at `7bde852a` adds `if c.unit.lookup.isSome then throw "the unit circuit is a lookup slot"` to
  `HmRow.check`. It never fires on a valid circuit.
  - `Net.parse` always returns `lookup := none`, and `Lookup.build` always returns `some`.
  - So `c.unit.lookup = none` separates the two kinds, without reasoning about `findIdx?` over the two loops' names.
