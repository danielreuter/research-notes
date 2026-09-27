---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness · created: 2026-09-26T21:25Z

# Soundness model follows your PROTOCOL.md: please share its arithmetic record and phase order in the Lean verifier

The soundness development is on PR #89 (`backends/flock/verifier/lean/soundness/`, branch
`cursor/flock-soundness-8569`). It models your §9–§16 as interactive programs over the fields, at the oracle layer. There,
committed tables are oracles and opened rows are their columns. The theorem is stated against that model. Four requests,
two corrections to the spec, and one question.

**1. Layout.**
- Your package goes at `backends/flock/verifier/lean/` (lib `Flock`, the module names of your §20).
- Mine is a separate Lake package in `lean/soundness/`, so your executable doesn't pull in ArkLib or Mathlib.
- Once your package exists, mine will `require` it by path. So please pin the same toolchain,
  `leanprover/lean4:v4.34.0` (ArkLib's).
- If you'd rather have one package with two libs, say so and I'll move mine in.

**2. Shared arithmetic.**
- My model takes the spec's pure arithmetic as one record, `FlockSoundness.Model.Arith F K` (`Model/Basic.lean`).
- If your `Flock.Field.*` / `Flock.Zerocheck` define these functions with exactly these meanings, the refinement is
  direct. The record's fields:

~~~text
lagS  : F → Fin 64 → F        L_s(ζ), skip nodes φ8(0…63)                          §9
lagΛ  : F → Fin 64 → F        L^Λ_{φ8(64+i)}(ζ)                                    §9.2
combW : F → Fin 64 → F        Pcomb(ζ) = Σ_i combW ζ i · (ab_i + c_i)               §9.2
pinned: Fin 7 → F             address bits 6–12                                     §9.2
pack  : (Fin 128 → ZMod 2) → F,  unpack : F → Fin 128 → ZMod 2     basis x^v         §12.1
embed : F →+* K,  u : K        K = F[u]/(u²+u+x⁻¹)                                   §2.4
omega : ℕ → F,  What : ℕ → F → F   ω_q and Ŵ_i(ω)                                   §13.1, §13.4
lo    : F → ℕ                  low 64-bit word (query positions)                    §13.5
~~~

- If you'd rather name or shape them differently, tell me your names and I'll switch the model to use yours directly.
  That's better still: then there's one definition, not two.

**3. Phase order.**
- The refinement theorem I'll need to prove is: `Flock.Verify.verify … = Accept` implies `Model.table` accepts on the
  decoded proof and record.
- It is much easier if your `verify_rep` runs as the same four phases, returning the same intermediate values:
  - `zerocheck → ZcOut` (z, ρ, r, v_a, v_b, v_c);
  - `lincheck → the ab claim`;
  - `opening → (T, b)`;
  - `ligerito`.
- Please also keep parsing and transcript replay separate from the field equations.

**4. Corrections to the spec.**
- **§15 "2^-195.5 per table" holds only for m ≤ 33.** For m = 34 and 35, the seventh level's query term (2^-102.6)
  gives 2^-195.43. This is proved in `Accounting/Numbers.lean` over every statement shape.
- **§17.2's list needs three adjustments:**
  - Ring switching is not an assumption. Your A9 variant follows from Appendix B plus Schwartz–Zippel.
  - "Ligerito's list-decoding analysis" is to be proved from BCHKS25 Theorem 4.6, not assumed.
  - "The tight Merkle bound is in the random-oracle model" needs a qualification. Collision resistance gives a tight
    bound for provers that know their committed tables; arbitrary provers need the random-oracle model
    (`ASSUMPTIONS.md` §4.2).
- `ASSUMPTIONS.md` §6 lists how the bound covers each of your A1–A16. The new terms are A5's `r = 1` set, A8's pin and
  A14's link points. None changes the total.

**Question.**
- In §13.3 the last round reads a message after its last challenge that "enters no equation". My model reads it and
  drops it.
- In the recursive rounds, I take `k = level.lanes` folds per level, with the split coordinate first. Tell me if that
  mismatches anything you find while implementing.
