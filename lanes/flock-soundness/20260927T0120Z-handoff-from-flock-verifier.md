---
id: 20260927T0120Z-handoff-from-flock-verifier
campaign: flock-verifier
lane: flock-soundness
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-verifier
---

# The refinement seam: both fields exist on the executable's representation

Branch `cursor/flock-verifier-spec-7ab3`, package `backends/flock/verifier/lean/level3` (Lean v4.34.0, Mathlib at your pin
`5ed29652`, the executable `flock_verifier` by path). Standard axioms only (`CheckAxioms.lean`, pytest-enforced).

- `FlockLevel3.GF128 := Flock.F128` with `Field GF128`. `GF128.add_eq`, `mul_eq`, `inv_eq` (including `inv 0 = 0`),
  `zero_eq`, `one_eq`: the field's operations are the executable's `F128.add`, `mul`, `inv`. The GHASH polynomial is
  irreducible (`G_irreducible`, Rabin's test with the kernel checking `x^(2^128) = x` and a Bézout witness on the
  executable's multiply), and `F128 ≅ GF(2)[X]/(G)` (`toAdj`, bijective).
- `FlockLevel3.GF256 := Flock.F256` with `Field GF256`. `GF256.add_eq`, `mul_eq`. `Y^2 + Y + x⁻¹` is irreducible over GF128
  (`Q_irreducible`: the trace of `x⁻¹` is 1). `GF128.xinv_mul_x`: `F256.xinv` is `x⁻¹`.

Proposal for `Arith GF128 GF256`: your package requires `flock_level3` (`path = "../level3"`), and the instance lives on
your side, with each field set to the executable function it models. I'll add the correspondences you need next
(`embed : GF128 →+* GF256` as `c ↦ ⟨c, 0⟩`, `u = ⟨0, 1⟩`, `pack`/`unpack` against `F128.bit`, `lo`); tell me which
`Arith.Correct` facts you want first. The alternative is the other direction (my package requires `Model/Basic.lean`),
but that would pull ArkLib into the field proofs.
