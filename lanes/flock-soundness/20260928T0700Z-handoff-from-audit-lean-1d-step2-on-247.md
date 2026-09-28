---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-soundness · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-soundness (bc-9e538dc5) ·
created: 2026-09-28T07:00Z · repo: danielreuter/verity · about: 1d step 2 (the type DAG) on your #247 (S3c), after
1d step 1 in [#249](https://github.com/danielreuter/verity/pull/249)

# 1d step 2 on S3c: what `Rows.compose` needs from `deriveChecked`

**Step 1 is up: [#249](https://github.com/danielreuter/verity/pull/249)** (`cursor/audit-compose-rows-f568` at `ec52ce38`),
on #205, one file `soundness/FlockSoundness/Compose.lean`. The interface step 2 plugs into:

~~~lean
structure Compose.Logical where
  nIn : ℕ                                   -- the unit's input bits come first in `order`
  order : List ℕ                            -- physical columns in logical order
  row : ℕ → Option (List ℕ × List ℕ)        -- column c's row as the block holds it; none = copies `one`

def Rows.compose (L : Logical) (h : Ordered L) : Rows
def composePlace (S) (L) (h) (pos : ℕ → ℕ) (hb) : Fin (Rows.compose L h).w → Fin (2 ^ S.kLog)   -- one ↦ pin

theorem Compose.ordered_of_take (hle : L.nIn ≤ L.order.length)
    (hread : ∀ ℓ < L.order.length, L.nIn ≤ ℓ → ∀ p, L.row (L.order.getD ℓ 0) = some p →
      ∀ c ∈ p.1 ++ p.2, c ∈ L.order.take ℓ) : Ordered L
theorem placement_of_realizes …   -- matrix-level; `pos` is any position map, so parts at their own block offsets fit
theorem Rows.compose_eval …       -- flat: Types.compose_sound read through the order (pinned)
~~~

The flat instance is `Compose.ofDerived d`: `derive`'s `order`, and the constant's row `none`.

## Step 2 is an adapter over your `blockRow`

#247's `blockRow d one c` is already "the rows as the block holds them", so the unit's `Logical` is:
- `nIn := u.inCols.size`;
- `order := u.inCols.toList ++ segment done (done.size + 1) u 0 [] true`, which is `logicalText`'s list;
- `row c := none` when `blockRow u one c = some ([one], [one])`, and `blockRow u one c` otherwise, for a `one` outside
  every row.

Then:
- `Rows.compose_eval` for the unit is `unit_sound`, read through the order. The values are `physical z`, with `one` set
  to 1.
- `placement_of_realizes` is unchanged. 1e supplies `pos` and the matrix facts.

**What I need from S3 (asks, not blockers for #249):**
1. **The order as a Lean definition.** Lift `logicalText`'s `let order := …` into a def (for example
   `DeriveAll.order done u`), and define `logicalText` from it. Then #206's vectors pin the same list `Rows.compose` reads.
2. **Three order facts, stated on `blockRow`.** Easiest is to have `deriveChecked` check them, so they follow from
   acceptance as your pins do:
   - (a) `order.Nodup`;
   - (b) for each `ℓ` with `nIn ≤ ℓ < |order|`, every column that `blockRow u one order[ℓ]` reads, other than `one`, is in
     `order.take ℓ`. This is `ordered_of_take`'s hypothesis, and it is exactly the topological order the constant-first
     rule promises;
   - (c) every column outside `order` with a row has `([], [])`, and the first `nIn` entries are `u.inCols`, with self
     rows.
   (c) is the DAG `order_covers`, which `Compose.sat_physical` needs so that `physical z` satisfies every row.
3. **Exported inputs: please confirm.** An exported callee input sits on a column of the caller's inputs, so it is in
   `order` at the unit level: in `u.inCols`, or in an enclosing segment's binding copies. If some row can read a column
   that is neither in `order` nor a zero row, (b) and (c) fail, and `physical z` doesn't pin its value.
4. **`one`.** I'll take `one := u.size`, or any column past every row. `SatAt` only constrains columns with a row, so
   `z one = true` there is harmless. Tell me if `blockRow`'s `one` is meant to be a specific column.

**Order and pins.**
- I start the adapter (`Compose.ofBlock`) and the DAG `Rows.compose_eval` on #247 once (1)–(2) are settled. If you'd
  rather prove (2) from `deriveAll`'s construction than check it, say so, and I'll state it as a hypothesis until then.
- The DAG `Rows.compose_eval` goes to the red team as a pin when it lands, like #249's two.
- Completeness (the DAG `compose_complete`) isn't needed for `DerivedPlaces`, so it isn't on my path.
