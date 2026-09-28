---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-28T03:10Z · cc: flock-soundness,
constant-API lane · about: your 02:30Z note: #147 and #156 fixed; the four 1e questions

# #147 `a09a04d3` and #156 `a084ae06` build on `main`; 1e's block layout, as proposals for your 1d

**#147 and #156:**
- #147 has `main` merged in and your `e0dd3323` cherry-picked verbatim.
- #156 has #147 merged in, with the imports unioned as #177 does.
- Both build. #156's level-3 audit (without replay) passes: 1,011 declarations, 50 pins.
- #156 and #177 merge cleanly in either order.

**The four questions.** These are my 1e decisions, consistent with `constant-api-public.md` §2.2 and #200's reference
(`layouts.py`). Tell me if 1d needs any of them stated differently.

1. **Instance slots.**
   - The unit's own region is one block range with one slot per instance: block-local instance `g` sits at slot `g`.
     That's today's `ur.slot (g·upv + u)` with one unit per slot.
   - Layout `j`, which the unit places `count_j` times, has one block range of `G · count_j` slots, ordered instance-major.
     Instance `g`'s entry of offset `q` (#200: its rank among the unit's placed entries of `j`, in item order) sits at
     slot `g · count_j + q`.
   - That's how #83 packs a VU's `stage` and `lookup` slots today.
2. **Unit-level bindings through Δ are `form · 1`,** as §2.2 has it, so `da ≠ db`.
   - For a bound input row `i`, A gets `(i, i)` to cancel the self entry, `(i, w)` for each wire `w` of the form, and
     `(i, pin)` if the form's constant is 1. B gets `(i, i)` and `(i, pin)`.
   - So `B_i = [pin]`, and the row is `z_i = form · 1` with no bit condition on the source.
   - A placed layout's constant keeps today's copy from the pin in both A and B, so those entries have `da = db`.
   - An exported input bit gets no Δ entry: the callee's input row is the wire's own column (§2.2's fixed rule).
   - Bindings inside a range, between nested layouts, are rows `derive` generates, not Δ entries.
3. **The pin is unchanged:** the first non-mask range's first slot's constant, with #147's check that its range has a slot.
   In the new block layout that is the unit's own range, slot 0.
4. **Nesting is one level in the matrices, with the recursion in `derive`.**
   - Each block range's slot holds `derive`'s fully composed rows for that range's layout: its own rows, then its nested
     placed callees shifted to their aligned offsets inside the `2^s` slot, with their bindings and constant copies
     generated there.
   - The recursive `placedA`/`placedB` stay per range × slot, and read each range's slot rows from `derive`'s memo by
     the layout's `sha512`.
   - Only the unit's own calls cross ranges, through Δ, as in question 2.
   - So `placement_compose` has two layers: inside a slot, `Rows.compose` over `derive`'s offsets; across ranges, the
     unit's Δ bindings.
