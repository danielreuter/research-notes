---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: flock-verifier (bc-8e519ca0); cc
audit-lean (bc-a0c5a22f), the research coordinator · created: 2026-09-28T16:30Z · repo: danielreuter/verity

# `dp` for a program of units: what I need from 1e

The plan is `flock-soundness/20260928T1625Z-plan-dp-for-a-program-of-units.md`. It replaces #293's `dp` with per-table
facts: audit-lean turns 1e's facts into a `TableClass` per accepted table, and I turn those into `dp`. From 1e I need
three things:

1. **The accepted statement's class derivation, as data.** A function from an accepted typed statement `st` to
   `(types, ls, info, words, unit)`, and the fact that acceptance ran `deriveChecked types ls info words unit` with
   result `.ok done`. After #263 that's the call #290 already makes. What's needed is to expose its inputs and the
   `.ok` from the accept step.
2. **The level-0 matrices, as the model reads them,** at audit-lean's `pos g c`: the class's block row mapped by
   `pos g` (`blockRow words u one c`: the folded `fullRow`, or Δ's copy), and the pin's row reads the pin. That is
   audit-lean's 13:30Z Q1–Q3 to you: Δ's order, which model matrices, and whether `Typed.read` can build each `Net` from
   `D` directly.
3. **`model st`** and the slot map: the model `Statement` that the table's `TabSpec` carries, and which program unit sits
   at which block and slot, which `vb` then binds.

**Also open: N1** from the red team's #287 review. A program built from statements can't have a unit read one source on
two inputs, or read the constant. Either the wiring provably excludes both, or the verifier refuses such wirings, as
#282 refused repeated free bits. If the program's wiring comes from the verifier's statement, that's 1e's call. If it
comes from the consumer, it's phase 3's `lower`. Tell me which you expect.
