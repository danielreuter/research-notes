---
id: proofs/20261008T2338Z-finding-recursive-sound-statement-list
campaign: proofs
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs), answering Daniel's conditions on the fork form (top, 1791502303.401289)
---

# `RecursiveSound`'s fork form: every statement that changes, and which table each one reads

Read at main `9c8323458`. This answers condition 3 of Daniel's approval of the fork form
(`note:proofs/20261008T1805Z-finding-rec-thm-compiled-inner`). Nothing has been edited yet. Condition 4, the premises
sweep, follows as its own note.

## The contradiction Daniel read, stated plainly

On main today, `RecursiveSound` takes **one** `I : Inner`, and two hypotheses read it: V*'s bridge `_hbr : VBridge …`
(whose `VDecodes` reads `I`'s round messages) and the inner soundness `_hin : InnerSound I εin`. No choice of `I` makes
both hold for the real system with `εin < 1`:

- **`I` = the compiled table** (`InnerAccepts`, `Recursive/Target.lean:121`). Each round's message is that round's proof
  messages and Merkle tops, which is exactly what the firewall commits and V* registers. So `VBridge` holds, and G
  proves it. But `InnerSound I εin` holds only for `εin` close to 1. A strategy that hard-codes a SHA-512 collision at a
  top commits to two tables under one top and picks one after the coin. In Lean's math such a strategy exists.
- **`I` = the interactive table** (`flockInner`, `Target.lean:193`). Round 0's message is the whole level-0 table.
  `InnerSound` holds at `2^-205` (`flock_inner_sound_fast100`). But `VBridge` fails for the real V*. V* commits only salted
  tree tops and reads opened rows, so `VDecodes` would have to decode a whole table from 64-byte commitments. Two trees
  under one top then break `Recursion.VBridge`.

The memo described this problem, then proposed the fix. It never proposed that V* commit whole tables. **Today's
statement is a theorem whose hypotheses can't all hold with a bound below 1**, and it belongs on condition 4's list as
well.

## Which table `VDecodes` is read against

| case | `VBridge` / `VDecodes` read | `InnerSound` reads | holds for the real system |
|---|---|---|---|
| main today | the one `I` | the same `I` | no `I` makes both true with `εin < 1` |
| after the edit | the **compiled** table only. Round `i`'s message is its proof messages and Merkle tops, which the firewall commits (`firewallLeaf`) and V* registers at `Sk i` (`VCommits`). | nothing: the hypothesis goes. The interactive table appears only inside the proof (compile lemma, then `flock_inner_sound_fast100`) and in the statement as the number `tableError` (`2^-205` for `22 ≤ m ≤ 33`). | yes |

V* never commits a whole table, in either case.

## VBridge E (#1568) is stated at the right level

- E's four headline theorems conclude that the checks of the verifier of record pass on the proof's messages, at the
  rep's coins:
  - `zerocheck_checks`: `Piop.lean:84` and `:98`.
  - `lincheck_checks`.
  - `ringSwitch_checks`.
  - `ligerito_checks`: `FinalOK`, `Ligerito.lean:227` and `:274`.
- Those messages (`Algebra/Structure.lean:199`, `Messages`) are the sumcheck rounds, the finals, the OOD values,
  Ligerito's messages and `yr`. The compiled proof sends all of these in the clear.
- E reads no table at all. Tables enter only through the Merkle openings against committed tops (`sound_recOpen`, A–C),
  which are compiled-level.
- So E feeds `InnerAccepts` as it stands, and nothing in E changes. E would be at the wrong level only if G had to
  conclude at the interactive table, which Daniel's approval rules out.

## Every statement the edit changes

1. **`Flock.Guarantees.RecursiveSound`** (`Security/Proofs/Flock/Recursive/Statements.lean:54`).
   - Remove `q` and `_hCR`, the fork finders' `cr/sha-512`, and the terms `(Σ_pos κ_i)·√(q_i²/2^513)`.
   - Remove `{εin} (_hin : InnerSound I εin)`. Fix `I` to C-Flock's compiled table on the class (item 4). The inner term
     becomes the number `tableError` (the Security page: "state the actual number", and `InnerSound` is no named premise).
   - For every `σ`, the conclusion becomes one of:
     - **a round fork:** two continuations of `σ` that agree through round `i`'s commitment, and hash `x ≠ y` to one
       SHA-512 digest along their paths to it (the firewall leaf, then the tree climb from the opened rows);
     - **a session fork:** two continuations of the strategy `σ` names for V*'s session `j` that share one of that
       session's own commitments (its Ligerito tops, its record and registered paths' roots), likewise;
     - the probability bound, with statistical terms only.

     Both forks range over `σ`'s own continuations, and every `∃` is bounded by membership in what those runs hashed
     (condition 1).
   - `_hS`, `_hA3`, `_hr`, `_hk`, `_hRw`, `_hM`, `_hρ` and `_ht'` don't change in this edit. The sweep classifies them.
2. **`ZkOuter.boundCR`** (`Recursive/Flock.lean:159`) **and `ZkOuter.slackCR`** (`Recursive/Stage.lean:181`). These are
   definitions `RecursiveSound` reads, and the lock records them.
   - The `if zo.CR … then … else 1` split goes.
   - The binding terms that depend on `qF`, `qS`, `qW` and `qR` leave the bound and become the session fork: the knowledge
     finders' part of `ksAvgStrictZ`, `regTermZC`'s part, and `qR²/2^513`.
   - What stays is statistical: the law's miss at one bad unit, and the drawn units' table and link errors. The exact
     split gets itemized in the edit.
3. **`Flock.Assumptions.VBridge`** (`Soundness/Assumptions/Recursive.lean:48`). Its text is generic in `I` and doesn't
   change. `RecursiveSound` instantiates it at the compiled table, so G concludes `VBridge …` at item 4's `Inner`.
4. **New: the compiled `Inner`** beside `flockInner` in `Recursive/Target.lean`: messages are `Game.Msg`, coins
   `Array W`, `accepts` is `InnerAccepts`, `holds` is the same as `flockInner`'s. The statement reads it.
5. **Unchanged:** `RecursiveZK`, `flockInner`, `flock_inner_sound_fast100`, E, and A–D.
   - `hidden_sound` (`Target.lean:104`, compiled with `CompiledCRL … hCR`) is a theorem, not a guarantee. The compile
     lemma supersedes it.

## The bound (condition 2)

The memo called the result "tighter than today's". That's wrong, and it's withdrawn:

- For a strategy that never collides on a fork, the bound is exact.
- For a strategy that collides on even one pair, it says nothing, and that's what a real attacker looks like.

The next step after the edit is the quantitative forking version: if a strategy beats the bound by δ, two runs from the
same commitment find a collision with probability about δ². Then the guarantee carries a number against a real
attacker.
