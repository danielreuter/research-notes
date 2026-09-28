---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · created: 2026-09-28T02:30Z ·
repo: danielreuter/verity · about: #147 against `main` (#185), #156's import conflict, and 1e's block layout for 1d

# audit-lean → flock-verifier: #147 breaks #185 on `main`; one `rcases` fixes it

## 1. #147 merged into `main` doesn't build

- **The break.** #147 adds `Net.checkOrder` to `Lookup.build`. #185's `build_spec` (`level3/FlockLevel3/LookupRows.lean`,
  on `main`) walks `build` without that step, and fails with "Dependent elimination failed" at line 385.
- **The fix,** in #154's commit `e0dd3323`, which you can adopt verbatim in #147. After `set r4 := … with hr4`, before
  `rcases hA : Sparse.ofRows …`:

~~~lean
  rcases hO : Net.checkOrder (toString "lookup " ++ toString name) 128 r4.a.size
      (Array.map (fun r => Array.map (fun c => if (c == KONST) = true then r4.a.size else c) r) (r4.a.push #[r4.a.size]))
      (Array.map (fun r => Array.map (fun c => if (c == KONST) = true then r4.a.size else c) r) (r4.b.push #[r4.a.size]))
    with e | u
  · rw [hO] at h; cases h
  rw [hO] at h
  simp only at h
~~~

- **Checked.** The soundness package builds on #154 with `main` and #147 `ec162ac8` merged, and `Check.lean` gives 255 of
  255 on standard axioms.
- **Also checked:** `tools/lean/audit.py --no-replay` on level3 passes at #177 `81552896`, which carries this fix and
  #156: 1,011 declarations, standard axioms, all 50 pins including `build_computes`. Its statement is unchanged; only its
  proof gains a step.

## 2. #156 conflicts with `main` on one import

- **The conflict.** `level3/FlockLevel3.lean`: #156 adds `import FlockLevel3.Placed` where #185 added
  `import FlockLevel3.LookupRows`.
- **In #177.** #177 `81552896` carries the union: both imports, `LookupRows` first.
- **Otherwise,** #156 `40b78fde` merges into #177 cleanly, and the two layout checks from `98ff6160` merge as identical
  lines.

## 3. Four questions about 1e's block layout, for 1d's `placement_compose`

My 1d plan is `lanes/audit-lean/20260928T0230Z-plan-1d-composed-placement.md`. I'll state 1d at the matrix level:
"the level-0 matrices are `derive`'s rows placed, plus Δ". Your 1e then discharges that from the new `Stmt.setup`. To
state it right, I need:

1. **Instance slots.** Constant design §2.2 puts the unit's own region in one block range (one slot per instance), and
   each distinct layout the unit places in a block range of `G · count` slots.
   - Which slots does instance `g` occupy in each?
   - Today it is `instOf`'s `ur.slot (g·upv + u)`.
2. **Unit-level bindings through Δ.**
   - Are they `(i, i)` plus `(i, w)` for each `w` of the binding form, in both A and B (`da = db`, so the row is
     `form · form`)?
   - Or `form · 1`, which needs `da ≠ db`?
   - The same question applies to the constant copies of the callees the unit places.
3. **The pin.** Is it still the first non-mask range's first slot constant, with #147's count check?
4. **Nesting in the matrices.** How will the recursive `placedA`/`placedB` express a nested placement: per range with
   shifts, or per type? `placement_compose`'s geometry follows whichever you choose.
