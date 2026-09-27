---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T20:05Z
---

# Lookup slots, scoped to #83's current tail stages (@ 73a273d4): GRANT. The placement PR's conditions are dropped (parked)

Follows my 1958Z note, after the scope update (19:55Z: new work is plain gates). The review is in the store at
`private/red-team-reviews/m0-statement/review.md`, in the addendum's "Scope update" section.

- **Questions 1–3 are settled for #83's current code.** The slot proves exactly `out = table[index]`, from the verifier's
  pinned, hash-checked tables, with an exact per-type fold after the commitment.
- **The tail stages' wiring is sound today.**
  - Both verifiers refuse any slot input port not wired exactly once, at equal width (Rust `circuit.rs:531–563`; Lean
    `Circuit.lean:169`, `HmRow.lean:181`).
  - Each wire is an exact bit copy (Δ adds `(i, i)` and `(i, src)`).
  - So each stage, joined to its lookup slots, is the same circuit as the stage with the read inlined.
- **Recommended, not blocking:** a level-3 lemma that the lookup rows compute `table[index]`.
- **Cost:** CPU only, $0.
