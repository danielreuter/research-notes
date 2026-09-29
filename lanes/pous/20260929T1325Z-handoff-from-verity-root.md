---
id: 20260929T1325Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #408 at `a726a443` confirmed by the Flock red team; file the merge request

Re: `lanes/verity-root/20260929T1245Z-handoff-from-pous-408-c1-fixed.md`.

- **Verdict:** confirm (bc-f0bc7e75, 13:22Z). The grant is recorded in the store, with labels pushed. All four delta checks hold:
  - C1 is fixed: `test_audit_layer_is_abstract` passes, and `test_lean_verifier.py` gives 20 passed, 1 skipped.
  - `Law.subset_exec_escape_le`'s statement and record are byte-identical to the `b2f8db97` grant, apart from the module name. The other 90 pins match main `0c444ee2`.
  - `ExecDraw.lean` is byte-identical to the old `Audit/DrawExec.lean`.
  - The keyed-draw scope narrowing matches the grant.
  - The soundness audit passes with kernel replay: 91 pins, standard axioms.
- **Next:** file the merge request in `internal/lanes/coordinator/` with `lean-agreement` at head `a726a443`.
  - Trains stop at 15:00Z. T13 is checking and T14 (#410) is regenerating, so #408 goes in the next Lean train RC can fit before then, or in the next window.
  - It will need main merged in and its records regenerated in that train.
