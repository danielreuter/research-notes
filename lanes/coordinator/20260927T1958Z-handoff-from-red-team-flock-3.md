---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-27T19:58Z
---

# M0's lookup slots (#83 @ 73a273d4) are plain gates: GRANT. Reads inside units (the planned stacked PR): GRANT WITH CONDITIONS C1, C2

Asked for directly (19:44Z, with Daniel suspicious). The review is a new section at the end of the store's
`private/red-team-reviews/m0-statement/review.md`. The numbers are in a new `lookup_numbers.txt` beside it. CPU only, $0.

- **Equivalence.** A lookup slot is AND rows like any unit: decoders, products and outputs, all forced by the index bits and
  the pinned constant. So it proves exactly `out = table[index]`, no weaker.
- **The table.** Only the verifier's four pinned MUFU tables are accepted, hash-checked in both the Rust and the Lean
  verifiers. The prover can't touch the table or its fold.
- **The fold.** It's computed once per table type, by an exact identity. It comes after the commitment, and every read
  keeps its own constraints.
- **Coverage.**
  - The soundness stack covers slot types generically.
  - Our Lean verifier builds them, and level 3 proves its fast fold.
  - Only the lemma "these rows compute `table[index]`" is unproved.
- **Numbers.** ex2 and rcp take 41,308 ANDs per read, and rsq and sqrt 49,576. XOR terms per read are 153.7 M for ex2 and
  309.4 M for sqrt: one per set table bit. Index widths are 23 and 24 bits, and outputs are 31 bits.
- **Conditions for reads inside units:**
  - **C1:** both verifiers refuse a circuit in which any late-input or index bit lacks exactly one wire.
  - **C2:** a negative test that flips one read's value, plus IR agreement on the new classes.
