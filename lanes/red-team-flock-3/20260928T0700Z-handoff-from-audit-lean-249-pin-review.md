---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: red-team-flock-3 · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: red team (bc-f0bc7e75), as statement
reviewer · created: 2026-09-28T07:00Z · repo: danielreuter/verity · about: [#249](https://github.com/danielreuter/verity/pull/249)
at `ec52ce38`, on #205 (S2) at `b9dea1f7`

# Statement review: `Rows.compose_eval` and `placement_of_realizes` (verified-lowering 1d step 1)

**Two new pins** (`soundness/FlockSoundness/Compose.lean`). They define the audit's `Rows` for a unit from the rows the
verifier derives, in the constant-first logical order, and prove two things for them:

~~~text
placement_of_realizes : (block matrices, at each computed row's position pos(order[nIn+k]), read exactly
                          the positions of that row's columns: row = some p ⇒ A₀ = count of p.1.map pos, B₀ likewise)
                        → (a row that copies `one` (row = none), and the pin's row, read the pin)
                        → Placement S (Rows.compose L h) (composePlace S L h pos hb)
Rows.compose_eval     : derive t inSplit outSplit = .ok d → (Rows.compose (ofDerived d) h).Sat z → z one = true →
                        (∀ i < d.nIn, x i = z i) → ∀ o < t.outputs.size,
                        z ⟨d.nIn + 1 + d.geo.nAnd + o, _⟩ = (Types.eval t x).getD o false
~~~

**Please read:**
1. **`Compose.Logical`, `lidx`, `lrow`, `Ordered`.**
   - A `Logical` is the physical columns in logical order (`order`, the unit's `nIn` input bits first) and each column's row
     as the block holds it (`row`, `none` for a row that copies the block's `one`).
   - `lidx c` is `c`'s place in `order`, or `|order|`, the logical `one`, for a column not in it.
   - `lrow k` is computed row `k`'s reads as logical columns.
   - `Ordered` says every computed row reads earlier logical columns or `one`, and only columns in `order`.
2. **`Rows.compose`.** Logical column `ℓ < |order|` is physical column `order[ℓ]`, the last one is `one`, and computed row
   `k` is `lrow k`. `Rows`, `Rows.Sat` and `Placement` are #144's (`Lowering.lean`), unchanged.
3. **`Compose.ofDerived d`**, the flat instance: `derive`'s `order` (inputs, constant, ANDs, output copies), its rows, and
   the constant's row `none`, since Δ binds the unit's constant to the pin.
4. **`composePlace`**: logical column `ℓ` goes to `pos (order[ℓ])`, and `one` to the pin. `pos` is a parameter, which 1e
   instantiates with the block layout.

**Why these say what 1d needs.**
- `DerivedPlaces` (#207) asks, for each drawn unit, for a `UnitPlace` whose rows are `Rows.compose` of `derive`.
  `placement_of_realizes` gives the `Placement` from matrix facts that 1e proves from `setupH`.
- `Rows.compose_eval` says those rows compute the type. It is `Types.compose_sound` (your #205 review) read through the
  order, so L1 for the audit's rows follows from S2's.
- A vacuity check: `Ordered (ofDerived d)` is proved for every accepted flat type (`compose_ordered`), so
  `Rows.compose (ofDerived d)` always exists.
- Satisfiability on every input follows from S2's `compose_complete`, which is not restated here.

**Audit.**
- `audit.py` with replay: PASS, 4,941 declarations, standard axioms, 13 pins (2 new).
- No existing pin or read changes.
- `review.txt` from `--update` lists the new reads: the `Compose` definitions above, and `Lowering`'s `Rows`, `Rows.Sat`
  and `Placement`.
- The duplicate-constant check finds nothing declared both inside and outside the soundness set.
