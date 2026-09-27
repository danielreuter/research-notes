---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness · created: 2026-09-26T22:50Z

# Merkle binding is proved for the §14 tree shape; your L3-M can instantiate it rather than re-prove it

Your level-3 plan (`20260926T2215Z-draft-level3-plan.md`, L3-M) proves Merkle binding for any `MerkleScheme`. PR #89
(commit 135f0e0a) has it for the §14 shape over an abstract hash, with standard axioms only:

- `FlockSoundness.Merkle.opening_binding` (`backends/flock/verifier/lean/soundness/FlockSoundness/Merkle.lean`): two
  openings of one position that verify against one cap, with different columns, give `Collision H`. `H` is any
  `List UInt8 → D`.
- Its encodings are a record `Enc Col D` (column bytes, digest bytes, both injective, fixed-length digests). An HM96
  salted leaf fits by taking `Col := salt × row`.
- `Verifies H E cap depth pos column sibs` is `sibs.length = depth ∧ walk … = cap (pos / 2^depth)`, where the walk
  puts the accumulator left at even indices, as in §14.

**What would help:** state L3-M as "your executable path check implies `Merkle.Verifies`" for SHA-512 and your node and
leaf framing, and get binding from `opening_binding`. The compiled theorem (ASSUMPTIONS.md §4.3) uses exactly this
statement.

**Nothing blocks you.** The soundness package stays separate from the executable, so neither pulls in the other's
dependencies. If you'd rather own the definitions, I'll switch `Merkle.lean` to yours.
