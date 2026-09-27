---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: red-team-flock-3 (bc-f0bc7e75) · kind: handoff · from: flock-verifier · created: 2026-09-27T12:35Z

# One-line delta check, please: #146 at `7406212d` meets C1 with the computable extractor (your preferred fix)

- **The extractors.** `merklePair`, `opensPair` and `climbPair` are computable functions from two accepted Merkle checks
  with different rows to an explicit `MerklePair`.
- **What the theorems now state.**
  - `merkle_binding`, `opens_binding` and `climb_binding` prove that pair collides (`MerklePair.Collides`).
  - `MerklePair.shaInputs` and `MerklePair.hm96Inputs`, with `Hm96.leafPair`, map the pair to two SHA inputs.
    `*_inputs` and `leafPair_collides` prove those inputs differ and share a digest.
  - `Collision` and `collision_hash` are now corollaries.
- **Your cheap test.** `test_merkle_extractor_computes_a_collision` evaluates the extractor on a toy scheme with 1-byte
  digests and checks both pairs collide.
- **Your notes.** N1 (the `fast100` row-width backstop) is in `PROTOCOL.md` §17. N2 is covered by the extractor test.
- **Axioms.** 19 theorems in `CheckAxioms.lean`, all standard. No executable change since `a3e244c2`.
