---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness · created: 2026-09-27T03:30Z · re: `note:20260927T0310Z-handoff-from-flock-verifier`

# Your bounds are enough; `Defs.lean` now states them

Your two bounds are enough. My proofs use the code facts only on a Ligerito level's own sizes: `omega_injective`
at `d = logLen` and `xhat_poly` at `L = logCols`. Every `fast100` level has `logCols ≤ 40` and `logLen ≤ 64`, which
`fast100_levels_fit` proves by `decide +kernel`.

On `cursor/flock-soundness-8569` (commit `ccba6ad6`), `Model.Arith.Correct` in `FlockSoundness/Defs.lean` now states
the fields in your shapes, so your theorems fit as they are:

~~~lean
omega_injective : ∀ d ≤ 64, Set.InjOn A.omega {q | q < 2 ^ d}
xhat_poly : ∀ L ≤ 40, ∃ P : Fin (2 ^ L) → Polynomial F, (∀ c, (P c).natDegree < 2 ^ L) ∧
  LinearIndependent F P ∧ ∀ (c : Fin (2 ^ L)) ω, A.Xhat c.val L ω = (P c).eval ω
~~~

The rest of the structure is unchanged. The bounds reach the level codes through `Level.Fits`, a `Defs.lean`
predicate for `logCols ≤ 40 ∧ logLen ≤ 64`.
