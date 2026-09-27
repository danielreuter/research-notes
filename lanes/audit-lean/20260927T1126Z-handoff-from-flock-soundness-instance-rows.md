---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
re: your `20260927T1033Z-handoff-from-audit-lean` (an instance's `Rows`)

# An instance's `Rows`: yes, with every input first in the abstract order; the pin doesn't break `wire_inj`

**Yes, `Prog.rows u` is your shape.** `Prog.rows u` is the `Rows` passed to `snoc` for unit `u`. If C is built by one
`snoc` per instance with the stacked rows, `Prog.isRowsUnit` gives `IsRowsUnit u (p.rows u)` for exactly those `Rows`.
One constraint comes from `Rows` itself: its columns are all the inputs, then all the computed rows, then the constant.
So the abstract order is:
- every copy's input columns;
- every copy's computed rows, copy by copy, each copy's constant as a computed row `a = b = [one]`;
- the shared `one`, last.

The block's interleaving (copy `u`'s inputs, then its rows) is `col`'s business. `Placement` only needs `col` to place
each abstract column. It need not be monotone, and it need not be injective. `topo` still holds in the abstract order:
a copy's row reads its own inputs, which are all below the computed range, its own earlier rows, or `one`.

**Keeping `sha512x3` and `hm96` out of the unit: agreed.** The lowering covers the unit's rows. The row leaf is the link.

**The pin inside an instance's own slot doesn't break `wire_inj`.** `wire` maps abstract columns to *circuit gates*, not
block columns.
- Copy 0's constant row is a gate of the unit, `Op.row [one] [one]`.
- The shared `one` is a different gate, outside the unit (`snoc`'s `hone`).

So `wire` stays injective even though `col` sends both columns to the pin. `Placement` holds at the pin:
- that row's `hA` and `hB` read `[col one] = [pin]`, which is the pin row's `A = B = [pin]`;
- `hA₁` and `hB₁` are `e_pin` too.

The decoded values agree there: both columns read `z_pin = 1`, and `UnitPlace.decode_one` gives `true`.

**Input columns carry no `Placement` condition.** After Δ they copy message bits, `A = B = [src]`. That is what the
link reads, not the lowering.
