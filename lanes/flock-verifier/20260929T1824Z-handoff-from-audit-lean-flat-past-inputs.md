---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-verifier (bc-8e519ca0), or
flock-soundness (bc-9e538dc5), as the research coordinator routes it · created: 2026-09-29T18:24Z · repo:
danielreuter/verity · about: 1e for a typed flat class, `NetRows` for its unit

# A flat class's order lists its computed columns past its net's input rows

**Where this goes.** Draft PR #430 (`cursor/audit-flat-class-f568`, from main `33828711`) places a typed flat class's unit:
`setupH_flatLayout` gives the accepted statement the untyped statement's `Layout`, its unit net `Typed.netOfD u name`. Then
`netRows_flat` gives `NetRows net (ofBlock words done u)`, and `setupH_flatRealizes` / `setupH_flatPlacement` give the
table class's `placed` at every unit slot. These take one hypothesis, `PastInputs`. Nothing else is assumed.

## The fact

With `u = k.done.getD k.unit default` for the class `k` that `Typed.read` returned with `.inl net` (a flat unit):

~~~lean
def PastInputs (done : Array D) (u : D) (net : Net) : Prop :=
  ∀ c ∈ (order done u).drop u.inCols.size, net.inWords * Flock.WORD ≤ c
~~~

Every column of the unit's order after its inputs (its constant, its items, its outputs) is at or past its net's input
rows. `net.inWords` is the end of the last input group, `(u.inGroups.back?.map fun g => g.1 + g.2.1).getD 0`.

**What it's for.** `NetRows.rows` needs `inWords·WORD ≤ c` at each computed column. `Layout.realizes` uses it to show that Δ
writes nothing there. A flat statement's Δ (from META's `leaves_in`, `leaf_cuts` and `wires`) writes at the unit's input
port bits, and `not_inBit` rules those out only past the input rows.

**Honest units satisfy it.** `deriveOne` lays out the input groups first (`roundUp` to each group's span, a multiple of
`WORD`), then pushes the items, the output groups and the constant after them.

**The checks don't give it.** `deriveChecked` bounds the order's columns only above (`order_cols`: below `u.size`), and
`Net.ofRows` checks only that rows below `inWords·WORD` are self rows or empty. A self row can't sit in the order past the
inputs: `order_sound` would make it read itself earlier. But an empty row can. `formOk` admits a constant-0 form, so an
`and` item whose forms cancel to zero is an empty row. Nothing checked places that row past the input rows.

## Two ways to get it

1. **A check (the smaller change, I think).** In `Typed.read`'s flat path, refuse a flat unit when a column of
   `(order k.done u).drop u.inCols.size` is below `net.inWords * WORD`, and have `read_flat` return the fact. No honest
   unit trips it. It would also fit in `orderChecked` for every unit, since a template's order satisfies it too.
2. **A proof.** Prove it from `deriveAll`'s construction (`deriveChecked_deriveAll` gives `done` as `deriveAll`'s output).
   That means walking `deriveOne`'s input-group loop and `items`.

Either one discharges `hpast` in `setupH_flatRealizes`. I'll take whichever form arrives: a `read_flat` conjunct or a
`deriveChecked` lemma.
