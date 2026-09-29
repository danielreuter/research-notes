---
id: 20260929T1431Z-merge-request-from-pous-412
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: merge request for #412 at `da1e703a` (Lean train with #408, needs `lean-agreement`)

- **PR:** [#412](https://github.com/danielreuter/verity/pull/412) at `da1e703a`, stacked on #408 `a726a443` (merge request `20260929T1342Z-merge-request-from-pous-408`). Root retargets it to main before it lands.
- **What it adds:** the rest of the Lean-only tier-3 chain. Four new pins:
  - `stratified_exec_escape_le`;
  - `flock_e2e_drawn_exec`;
  - `flock_e2e_count_exec`;
  - `execStratified_escape_le`.

  None carries a named assumption. `ExecStrata` is an explicit hypothesis. Nothing in the Python call path changes.
- **Grants:**
  - POUS's statement reviewer: `e1081cc5` in full, then `da1e703a` (Phase 19q), where the only delta is the `execStratified_escape_le` pin it asked for;
  - the Flock red team: `e1081cc5` (`lanes/pous/20260929T1412Z-handoff-from-verity-root.md`). **Its delta check on the added pin at `da1e703a` is pending** (requested in `lanes/verity-root/20260929T1426Z-handoff-from-pous-412-delta-414.md`). Hold this request until it confirms.
- **Checks at the head:**
  - `test_lean_verifier.py`: 20 passed, 1 skipped;
  - the soundness audit with kernel replay passes with standard axioms: 94 pins at `e1081cc5`, plus the one added pin. #408's 91 records are byte-identical.
- **Changed prose, outside the pins:** the exhausted-stream sentence in the PR description, and one docstring sentence naming the new pin.
- **For the re-merge:** `main` `1766d522` removed `Check.lean`, so the merge drops the new pin's `#print axioms` line. Nothing else in the delta touches it.
- **Heads:** fixed until the PR lands.
