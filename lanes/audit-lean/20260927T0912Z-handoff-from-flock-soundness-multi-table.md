---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
[PR #141](https://github.com/danielreuter/verity/pull/141) (branch `cursor/flock-session-batch-8569`, head `210babc8`,
stacked on #136)

# Several tables per session: the per-unit ks and link, in #133's shape

These are what your follow-up needs to drop the one-table-per-session restriction of `FlockCompiled.lean`. All are in
`FlockSoundness/SessionBatch.lean`, with no `sorry` and standard axioms (151 of 151).

**The session.**

- `sessionB A H E ts : Game (List (OutC F D))` is the protocol's batch (PROTOCOL.md §5). `Commit` sends every table's
  level-0 cap (`Fin ts.length → Cap D`), there is one link-point draw, and then every table runs concurrently.
- `acceptedB ts outs` holds when every table accepts.
- A table is a `TabSpec mPts`: your `FlockTableC`'s fields without `mPts`, which the session shares.

**The wiring I'd expect.**

- `plan : Finset (Fin n) → Reg → List (TabSpec mPts)`, for a fixed `mPts`.
- `tab S R : Fin n → Fin (plan S R).length`: the table that carries each unit.
- `session S R := (sessionB execArith H E (plan S R)).map fun outs => decide (acceptedB (plan S R) outs)`.
- With `τ₀ := Strategy.ofMap _ _ τ`:
  - `ksFail S R τ u := ENNReal.ofReal (failProbB execArith H E (plan S R) (tab S R u) Kr τ₀)`;
  - `linkFail S R τ u X := ENNReal.ofReal (extractProbB execArith H E (plan S R) (tab S R u) Kr τ₀ (LinkEv S R u X))`.
- `LinkEv S R u X` is your `LinkEvent`, taken as a predicate on the extracted table: replace
  `extractTable H E sch cap₀ bs` by its argument. The decoder is then per table, reading messages of table
  `tab S R u`'s shape.
- **`cover`** is `one_le_fail_add_B'` with `hG` from your lowering. Your current proof carries over: a committed table
  gives `LinkEv` for a wrong unit.
- **`KnowledgeSound`.** `prob_map` turns the verdict into `prob (acceptedB …) (sessionB …) τ₀`. Then
  `joint_le_B' … (tab S R u)` gives `≤ ENNReal.ofReal (ksBoundB … (tab S R u) Kr τ₀)`.
  - For a bound that doesn't depend on the target, take `εks R τ := avg_ω ⨆_j ENNReal.ofReal (ksBoundB … j Kr τ₀)`,
    or the sum over tables.
  - Each `ksBoundB` is table `j`'s `ε_c⁻ + K·Adv₀ + N₀/(eK)`, computed in the session and prover-dependent.
- **The lowering** becomes per table: a message packing a witness that satisfies table `tab S R u`'s statement decodes
  to values on which `u` is correct.

**One naming clash to watch.** `Game.batch` (in `Game/Batch.lean`, from #136) and your `Audit.batch` are the same
definition. Under `open Game` inside `namespace FlockSoundness.Audit`, `batch` becomes ambiguous once you import
`SessionBatch`. Qualify it, or use `Game.batch`.
