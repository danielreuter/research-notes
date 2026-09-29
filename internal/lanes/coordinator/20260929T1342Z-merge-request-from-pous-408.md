---
id: 20260929T1342Z-merge-request-from-pous-408
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: merge request for #408 at `a726a443` (Lean train, needs `lean-agreement`)

- **PR:** [#408](https://github.com/danielreuter/verity/pull/408) at `a726a443`.
- **The new pin:** `Law.subset_exec_escape_le`. The verifier's executable `Flock.Draw.subset` misses B with probability ≤ C(n−|B|,k)/C(n,k), which is the first tier-3 pin.
- **Also changed:**
  - `Flock.Draw` goes under `meaning`, so the records of `workRule_eq_draw` and `countRule_eq_draw` grow (accepted by both reviewers);
  - the module is `FlockSoundness/ExecDraw.lean`.
- **Grants:**
  - POUS's statement reviewer, at `b2f8db97`;
  - the Flock red team, at `b2f8db97`, then its delta confirmation at `a726a443` (`lanes/pous/20260929T1325Z-handoff-from-verity-root.md`).
- **Checks at the head:**
  - `test_lean_verifier.py`: 20 passed, 1 skipped;
  - the soundness audit with kernel replay: 91 pins, standard axioms.
  - The head contains `main` `0c444ee2`. Per root, the train merges current `main` in and regenerates the records.
- **Heads:** fixed until the PR lands. Draft [#412](https://github.com/danielreuter/verity/pull/412) is stacked on it and is still in review, so it isn't part of this request.
