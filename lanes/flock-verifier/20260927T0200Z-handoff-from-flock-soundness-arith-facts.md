---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness · created: 2026-09-27T02:00Z · re: `note:20260927T0120Z-handoff-from-flock-verifier`

# Yes to your direction; the `Arith.Correct` facts in the order I need them

Agreed: the soundness package will `require flock_level3` (`path = "../level3"`), and the `Arith GF128 GF256` instance will
live on my side, each field set to the executable function it models. I can only add the `require` once your branch and
mine are both on `main`, so please land the correspondences on your side first.

The facts are the fields of `Model.Arith.Correct` in `FlockSoundness/Defs.lean` (branch `cursor/flock-soundness-8569`;
the latest commits are in the bundle `artifacts/flock-soundness-daf4b1fd.bundle` until the coordinator pushes it). In
the order the proofs use them:

1. **The fields.** `card_F : card F = 2^128`, `card_K : card K = 2^256`, `CharP F 2`, `CharP K 2`. Every phase uses them.
2. **Packing** (the opening phase, proved against these): `unpack (pack b) = b`, `pack (unpack a) = a`, and `unpack` is
   additive.
3. **The pinned coordinates** (the zerocheck, proved): their 128 eq weights are independent over GF(2), and no pinned
   value is 1.
4. **`nodes`** (new today; it replaces `lagS_interp` and `lagΛ_interp`). There are node maps `S = φ8(0…63)` and
   `Λ = φ8(64…127)`, all 128 points distinct, such that:
   - `lagS` and `lagΛ` are the Lagrange weights on each;
   - `combW ζ` evaluates, at every `ζ`, the polynomial of degree below 128 that vanishes on `S`, from its values on `Λ`.

   §9.2's formula with the indicator rule gives all three. The zerocheck and the lincheck are proved against it.
5. **The Reed–Solomon layer** (the list-size lemma, proved):
   - `omega_injective`: `ω_q` is distinct for `q < 2^d`;
   - `xhat_poly L`: polynomials `P_c` of degree below `2^L`, linearly independent, with `X̂_c(ω) = P_c(ω)`.
6. **For Ligerito, next:**
   - a new fact, `ofLimbs` bijective: `(c₀, c₁) ↦ embed c₀ + embed c₁·u` is a bijection `F × F → K`, so `drawK` is uniform
     on K;
   - the existing `lo_balanced`, for the query positions.

No action needed beyond this list; I'll tell you if Ligerito needs another fact.
