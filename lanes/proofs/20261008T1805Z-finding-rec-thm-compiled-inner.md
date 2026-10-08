---
id: proofs/20261008T1805Z-finding-rec-thm-compiled-inner
campaign: proofs
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs, rec-thm's statement owner), answering note:lean/20261008T1756Z-finding-vbridge-g-inner
---

# rec-thm: G concludes at the compiled `Inner`, and `RecursiveSound`'s inner premise changes

Read at `339446a0e` (the move head). This answers lean's question in `note:lean/20261008T1756Z-finding-vbridge-g-inner`.

## lean's read is right

- `VDecodes` (at equality) and `VFull` require each round-`i` message to be a function of the values at V*'s commit
  strings `Sk i j`, and those wires to lie in fully drawn units.
- At `flockInner`, round 0's message is the whole level-0 table (`recv (Oracle F)`). The real V* commits salted tree tops
  (`firewallLeaf`) and opens rows against them (`RecOpen`'s climb), so the four conjuncts have no instance there.
- The vbridge plan meant the inner protocol to be the verifier of record on the decoded session
  (`note:proofs/20261005T2345Z-draft-vbridge-plan`, "G proves it at `I :=` C-Flock's verifier of record"), so the
  compiled table (`InnerAccepts`, messages are tops).
- The mismatch is rec-thm's: its finding (`note:proofs/20261006T0101Z-finding-rec-thm`) pointed `InnerSound` at
  `flock_inner_sound_fast100`. That theorem is the interactive table's soundness (oracles sent whole), not the
  compiled table's.

## Why `RecursiveSound` has to change

`InnerSound I ε` says one statistical `ε` holds for every strategy. That is false at a compiled `Inner`:

- A strategy that hard-codes a SHA-512 collision at a top commits to two tables with one top, and picks one after the
  coin. That at least doubles the error.
- With collisions at every node it picks among exponentially many tables, and the error goes to 1.

## A caveat for Daniel's form

The single-run reading, "soundness ∨ a collision among the inputs V* hashed in this run", is also false for a
commit-then-coin argument:

- In the counterexample, each run hashes only the chosen table's paths, so no run contains a collision, yet the prover
  cheats.
- The collision appears only between two continuations of the prover that share the commitment. That is #1497's form
  ("one from each opening's check", `∃ x ∈ coinHashed … o, ∃ y ∈ coinHashed … o'`) and the ruling's Merkle clause: two
  openings of one root.

So the run-tied disjunct here quantifies over two runs of `σ` (two leaves of its strategy tree) that agree through round
`i`'s commitment. It is bounded by membership: `x` is hashed along a path to that commitment in one run, and `y` along a
path to it in the other.

The disjunct is not vacuous. Where no such pair collides, all the paths to one root across `σ`'s continuations form one
tree (`opening_binding`, `walk_binding`, `hm96Leaf_bind`, and through the firewall leaf too). So the candidate inputs
are at most one tree's nodes, far fewer than 2^512, and pigeonhole forces nothing.

A single tree-wide set over every leaf of `σ` would be vacuous. Even an honest prover's later rounds, across 2^128
coins per round, hash more than 2^512 distinct inputs.

## Recommendation

1. Keep `Inner` and `InnerSound` at the interactive table. `flockInner` and `flock_inner_sound_fast100` are proved,
   statistical, and `2^-205` for `22 ≤ m ≤ 33`.
2. Put the compilation between the outer and inner protocols as one lemma.
   - **Hypothesis:** no round `i` has two continuations of `σ` that share its commitment and collide on what they hash
     along their paths to it.
   - **Conclusion:** the commitment determines one table, and `σ` induces an interactive-table prover holding that
     table. The table is the opened values across all continuations, a function of the prefix, padded where nothing is
     opened.
   - **Effect:** compiled acceptance implies interactive acceptance at the same coins.
   - **Missing proof:** lean's caveat, that the interactive verifier reads each oracle only at its queries.
3. Then `RecursiveSound` reads, for every `σ`, one of two things:
   - two continuations of `σ` that share a round's commitment hash two distinct inputs with one SHA-512 digest along
     their paths to it, or
   - `Pr[every session of V* accepts ∧ ¬ holds] ≤ E[Σ_j outer bound_j] + tableError`.
4. This removes:
   - `hCR`, the per-round fork finders' `cr/sha-512`;
   - the `(Σ κ)·√(q²/2^513)` terms;
   - any per-strategy inner `cr/sha-512`.

   The binding those carried becomes the disjunct.
5. The outer sessions' `boundCR` also takes `cr/sha-512` per strategy. It takes it as a case rather than a hypothesis:
   the bound is `1` wherever the session's finders fail `ZkOuter.CR` at budgets `qF qS qW qR`. Change it in the same
   statement edit to the same two-continuation disjunct over V*'s own commitments.

The remaining bound is statistical, with no square-root loss, and tighter than today's.

## Scope

- This is a statement change to a guarantee (claims), so it goes to Daniel through top before anyone builds it.
- Lean's items 1 and 2 (the algebra unit's check, pinned `(L, H)`) are needed under any answer, and lean has started
  them.
- G stays several thousand lines either way. The compile lemma adds work, but it replaces the forking argument rather
  than adding to it.
