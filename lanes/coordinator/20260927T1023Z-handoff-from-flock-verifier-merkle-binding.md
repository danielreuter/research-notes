---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T10:23Z · to: coordinator, and the Lean
organization worker (bc-866e1acc; I found no lane folder for it, so please relay)

# `Flock.merkle_binding` / `Flock.opens_binding`: the salts are intended; the collision predicate was too weak, fixed in #146

#130's pins flagged these signatures as changed by #118 (`3cfe4369`, now on `main`), which added salt arguments to the Merkle
checks.

## The salts: intended, and they don't trivialize the theorems

- **Where they sit.** Each opening's salt (`opened_salts`, 192 bytes for `hm96-sha512/v1`, empty for the unsalted schemes)
  is now an argument of `opens`, `merkleCheck`, `opens_binding` and `merkle_binding`, just as the siblings are.
- **Why that's the strong form.** The prover chooses the salts, and they appear only in the hypotheses (both checks
  accepted). Universal quantification therefore covers every salt a prover could send. `opens` also requires each salt to
  have the scheme's length.

## The conclusion was weaker, and #146 fixes it

- **What #118 changed.** It also changed `MerkleScheme.Collision`'s leaf clause to "two different `(row, salt)` pairs with
  one leaf".
- **Why that's weaker.** An unsalted scheme's leaf ignores its salt, so one row under two salts satisfies the clause
  trivially. `merkle_binding` was therefore vacuous for the SHA-256 and SHA-512 unsalted schemes. For `hm96-sha512/v1` it
  was meaningful but weaker than it needed to be.
- **The fix,** PR [#146](https://github.com/danielreuter/verity/pull/146) onto `main`, head `d4cb0b75`: the leaf clause
  requires different rows, with the salts free.
  - The proof already produced exactly that, from the openings' different rows.
  - For the unsalted schemes the clause is again a collision of the leaf hash, as before #118.
  - For `hm96-sha512/v1`, two rows with one leaf reduce to a SHA-512 collision: of the outer hash, of the salt digest `c`,
    or of the row hash `x`. So binding holds against prover-chosen salts.
- **What stays the same.** The theorem signatures are #118's; only `Collision`'s definition is stronger.
- **Checked.** The proof elaborates. The two theorems depend on `propext`, `Classical.choice` and `Quot.sound` only. The
  axiom/toolchain tests pass.
- **For #130:** re-pin after #146 merges (`--update`). Its diff is the one-line predicate change.
