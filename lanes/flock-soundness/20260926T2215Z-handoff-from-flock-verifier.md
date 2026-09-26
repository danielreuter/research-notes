---
lane: flock-soundness
kind: handoff
from: flock-verifier
created: 2026-09-26T22:15Z
---

# Level 3 plan aligned with a16z's stages; proposal: proofs in a Mathlib package `lean-proofs/` beside the dependency-free verifier

Daniel asked both lanes to follow the stage structure of a16z's zkVM security stages. Mine is in
`lanes/flock-verifier/20260926T2215Z-draft-level3-plan.md`, and PROTOCOL.md §17.4 (PR #85) has the maintained table.

**Split:**
- **Yours:** 1a (the PIOP), 1b for Ligerito, 1e (the glue).
- **Mine:** 1b for Merkle (a collision extractor, parametric in the hash), session binding in 1c's slot (coins are
  interactive, so there is no Fiat–Shamir), 1d (the lowering of every pinned circuit, and the fold, region and Δ lemmas),
  and 2 (field arithmetic, decoders).
- **Stage 3** (the prover) is out of scope.

**Proposal: package layout.**
- `backends/flock/verifier/lean/` stays dependency-free. It is the running binary's trust surface, and a test enforces it.
- A second package, `backends/flock/verifier/lean-proofs/`, requires Mathlib at a pinned revision and `flock_verifier` by
  path.
- Both lanes' theorems live there, importing the executable definitions. Libraries could be `FlockProofs.Level3` and
  `FlockProofs.Soundness`; name yours as you like.
- Please confirm, or propose another layout. If you have already picked a Mathlib revision, I will pin the same one.

**Definitions that changed since my last handoff** (branch tip 9605a77d and later):
- `verify` and `verifyRep` now take the proof's Merkle scheme from `Setup.merkle` (`MerkleScheme`: digest width, node,
  leaf, `PcsParams` index). SHA-512 with 64-byte siblings is supported; Daniel's target is SHA-512 on every commitment
  path.
- `ligerito` and `queryLevel` take the scheme as their first argument.
- `merkleCheck` moved to `Flock/Merkle.lean`.
- `CircuitFold.fold` takes the tensor factors `(α, lw, ρ_in)` instead of a materialised `e`.
- A transcript `Round` may carry the framed bytes the coin server retained. `squeeze` then compares them exactly instead of
  their SHA-256. With retained bytes, R2 needs no collision resistance.
