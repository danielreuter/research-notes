---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
follows `20260927T0740Z-handoff-from-flock-soundness-compiled-shapes` · branch `cursor/flock-session-8569` (stacked on
#127 → #124, and it merges #122 for `table_value_sound`)

# The session theorem is proved: its exact form

`FlockSoundness/Session.lean`, no `sorry`. `Check.lean` shows only `propext`, `Classical.choice` and `Quot.sound`
(145 of 145).

**The session after `Commit`** is `sessAfter A H E S sch hm ptLocal mPts pre post cap₀ : Game (List (OutC F D))`. It is
one link-point draw, then `batch (pre.map (· pts) ++ tableAfter … cap₀ pts :: post.map (· pts))`.

- The table sits at position `pre.length`, with its level-0 cap fixed by `Commit`.
- `pre` and `post` are any games reading the link points, such as the other tables.
- `Game.batch` is in `Game/Batch.lean`. It is the same definition as your `Audit.batch`. Once you import the session,
  use one or the other, or `batch` becomes ambiguous under `open Game`.

~~~lean
theorem session_knowledge_sound … (pre post : List ((Fin 2 → Fin mPts → F) → Game (OutC F D)))
    (cap₀ : Cap D) (σ : Strategy (sessAfter A H E S sch hm ptLocal mPts pre post cap₀)) (Kr : ℕ) (hK : 1 ≤ Kr) :
    expectN (sessAfter …) σ Kr (fun bs => expect (ind fun outs =>
        (outs.getD pre.length dfltOut).accepted = true ∧
          ¬ Committed A S sch (extractTableS H E sch pre.length cap₀ bs)) (sessAfter …) σ) ≤
      epsS … σ + (Kr * adv₀S … σ + 2 ^ l₀.logLen / (Real.exp 1 * Kr))
~~~

- **`extractTableS`** fills the table from the table's openings in the `Kr` reruns of everything after `Commit`.
- **`epsS`** is `tableError` plus the table's rep-cap fork terms (`advRS`) plus its self-clash, all in the session.
- **`adv₀S`** is its level-0 finder in the session. All three are prover-dependent, as §2 of my last handoff says.
- **The table's acceptance** is the event. The session's acceptance implies it, so your `ks` for a unit in the table is
  at most this left side.
- **`session_sound_of_table`** is the compiled bound for any level-0 table in the session. The oracle prover plays the
  whole session, and `orcSess_value_le` bounds it by the table's value.
- **Your `session S R`** for the compiled Flock audit would be `send (caps) → sessAfter …` with the plan's tables, and a
  unit's table taken at its position. Splitting `List.ofFn` at `j` into `pre ++ x :: post` is the only glue.

**Still open with you:** the three questions in my 0740Z handoff (number form, prover-dependent bound, one table or
several per unit). Only then can `cover` be written, and that also needs the canonical values.
