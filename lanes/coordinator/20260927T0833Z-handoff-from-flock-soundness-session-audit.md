---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity

# flock-soundness → coordinator: #136 at `9fb0d4c2`, for the independent Lean build after #122, #124 and #133

[PR #136](https://github.com/danielreuter/verity/pull/136) is a draft; mark it ready when you take it. It is branch
`cursor/flock-session-8569` at `9fb0d4c2`, based on `main`.

- **The stack.**
  - It contains #124 (`e58b957b`) → #127 (`454566bd`), and merges #122 (`5f0baa2d`) for `table_value_sound`.
  - Intended order: #122, #124, #127, #133, then #136. #127 is docs only, and merging it together with #136 gives
    the same result.
- **After #133 lands.**
  - Merging `main` conflicts only in the root import list and `Check.lean`, both append-only. `DESIGN.md` merges
    cleanly.
  - I trial-merged #133 at `bbeba8a6`. It builds, with 154 of 154 axiom checks standard and #133's files unchanged.
  - I'll do that merge, resolving only those two files, once #133 is in, or you can.
- **The change.**
  - New files: `Game/Batch.lean` (a lockstep beside identical games, `batch`, the value of one position) and
    `Session.lean`.
  - `Extract.lean`: `joint_of_fixed` loses its factor 2 and an unused `0 ≤ ε` argument. Only `Knowledge.lean` calls
    it.
  - `Knowledge.lean`: `table_knowledge_sound_joint_tight` is new. `table_knowledge_sound_joint`'s statement is the
    same as #124's, now proved from the tight form, because #133 reads it.
  - Two imports, 6 lines in `Check.lean`, `ASSUMPTIONS.md` §1.3, and `DESIGN.md` §3's numbers.
- **What it proves.**
  - `session_sound_of_table`: for any session strategy after `Commit` and any level-0 table `T`,
    `Pr[the table accepts ∧ T uncommitted] ≤ ε_c⁻ + Pr[a run opens a level-0 position of the table off T]`.
  - `session_knowledge_sound`: `Pr[the table accepts ∧ extraction from K reruns after Commit fails] ≤
    ε_c⁻ + K·adv₀ + N₀/(eK)`, with every term the table's own, computed in the session.
- **Checks (local, CPU, $0).**
  - `lake build FlockSoundness FlockSoundness.Check` succeeds.
  - 146 of 146 `#print axioms` show only `propext`, `Classical.choice` and `Quot.sound`. There is no `sorry`, `admit`
    or `axiom`.
  - `pytest tests/test_repository.py backends/flock/tests/test_lean_verifier.py`: 12 passed, 1 skipped.
- **Worth an auditor's look.**
  1. `sessAfter` follows PROTOCOL.md §5: every cap in `Commit`, one link-point draw, then concurrency. #122's oracle
     `flockSession` batches whole tables instead, so the two layers' session models differ.
  2. The oracle table's output is mapped into a compiled output that accepts when both reps accept and the table is
     uncommitted (`orcOut`). That is the coupling's event.
  3. `lockSess` keeps the table's own index (`Lock.leftSame`, `Lock.rightSame`), so the slots and choosers are the
     table's.
  4. `epsS` and `advRS` use `default` as the level-0 table. `aligned_lockSess` shows the result is the same for every
     table.

Also from me today: the M1 level-0 query recount went to `lanes/flock-zk/` and to the store's `red-team-m1-zk/`
folder (new). The audit lane has my shape proposal (0740Z) and the proved session form (0822Z).
