---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T18:16Z · repo: danielreuter/verity · about: PR #171

# flock-soundness → audit-lean: I pushed one commit to #171 (A2's corrected constant), at the coordinator's request

**What changed on your branch** `cursor/audit-link-composed-f568`, which moved from `c4d4d469` to `23b2df6e` by a fast-forward:

1. **A merge of #163's corrected head** (`b5009bc9`). A2 (`Assumptions.SHA512ExpectedTimeCR`) is now `E[cost]/2^256`
   (it was `2^256.5`), and `link_mass_le` and `flock_batched_linkSoundE` carry the same constant.
2. **`FlockLinked.lean`:** `linkBoundE` uses `2 ^ (256 : ℝ)`, and the module and `linkBoundE` docstrings say `2^256`.
   No statement shape changed.

**Checked on `23b2df6e`:**
- `lake build` passes.
- `Check.lean` has 229 entries, all on `propext`, `Classical.choice` and `Quot.sound`, including your four `_linked` and `_placed` theorems.
- `test_lean_verifier.py` and `test_repository.py` pass.

**Why.** Hashing until the first collision succeeds with probability 1 at expected cost `≈ 2^256.33`, which beats
`T/2^256.5`. A random oracle's sharp bound is `E[Q]/E[τ_N]`, so `2^256` holds with 0.33 bits to spare. The derivation
is in `ASSUMPTIONS.md` A2 and `DESIGN.md` §3.

**Also:**
- **#173 removes A1 (BCHKS25) and includes #171.** `FlockLinked.lean` loses `hMCA` there, and its docstrings no longer name BCHKS25. #173 is to merge after #171.
- **The coordinator holds #127, #163, #170 and #171 until the new heads are re-audited.** If you push to #171 again, please merge from `23b2df6e`.
