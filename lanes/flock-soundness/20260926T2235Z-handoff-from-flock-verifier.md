---
lane: flock-soundness
kind: handoff
from: flock-verifier
created: 2026-09-26T22:35Z
---

# I read your branch: my package moves to Lean v4.34.0 to match your Mathlib/ArkLib pin; stage 2 is a refinement of your Model by my executable, via `Arith`

Your package, `backends/flock/verifier/lean/soundness/` on `cursor/flock-soundness-8569`, supersedes the layout I proposed at
22:15Z. Keep it where it is.

**Toolchain.**
- Your ArkLib and Mathlib pin `leanprover/lean4:v4.34.0`. My executable package, `backends/flock/verifier/lean/`, was
  on v4.34.1.
- I have moved it to v4.34.0 (next push on PR #85). It builds, and every component test passes (field, SHA-256, SHA-512,
  BLAKE3, Merkle, HM96).
- Your lakefile can now `require flock_verifier from ".."`, and one build covers both.
- My package stays dependency-free (a test enforces it). My source checks skip `soundness/`.

**Stage 2, the bridge.** Your `Model` is written from PROTOCOL.md, with `Arith` as the seam. What I propose to prove:
1. **An `Arith` instance from my executable**, with its `Arith.Correct` (my L3-F): `lagS`, `lagΛ`, `combW`, `pinned`,
   `pack` and the embedding. They come from `Flock.skipWeights`, `lagrange`, `pinned`, `F128.mul`, `F256`, and are proved
   against GF(2)[x]/(g).
2. **A refinement lemma per phase.**
   - If `Flock.bindAndZerocheck`, `lincheck`, `ringSwitch` and `ligerito` succeed on a replay transcript, then your model's
     phase checks hold on the corresponding values.
   - Then `Flock.verify … = .ok ()` implies `Model` accepts.
   - Arrays become `Fin n →` functions at the boundary.

   The lemma is stated about the running code, so your rep and link soundness theorems transfer to it.
3. **What refinement needs from your side:** your phase predicates in terms I can match.
   - Is `Model.Piop`'s zerocheck check over the `(G(1), G(∞))` encoding with `G(0)` derived, as in §9.2?
   - Is the lincheck fold stated as `α·A_0ᵀe + B_0ᵀe` on the tensor `lw ⊗ eq(ρ_in)`?
   - Tell me where yours differs; I would rather adapt the executable's shape than add a second refinement.

**What changed in my definitions since 22:15Z:**
- Lookup slots are implemented (`Flock.Lookup`).
- `Tags` gains `name` and `pinnedLeafScheme`; the final PR #83 format is `fd02e847`.
- `MerkleScheme` supports SHA-512 with 64-byte digests. I saw your `2e7fc65c` (SHA-256 never clears 2^-128 under
  rewinding); Daniel has since made SHA-512 the target on every commitment path.
