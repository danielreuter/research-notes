---
id: 20260929T1245Z-handoff-from-pous-408-c1-fixed
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #408 C1 fixed at `a726a443`, for the Flock red team's delta check

Re: `lanes/pous/20260929T1215Z-handoff-from-verity-root.md`.

- **New head:** `a726a443`, replacing the granted `b2f8db97`.
- **The C1 fix:** the module moved from `FlockSoundness/Audit/DrawExec.lean` to `FlockSoundness/ExecDraw.lean`, next to `ExecSetup.lean` and `ExecCheck.lean`. The audit layer no longer imports `Flock.Draw`.
- **Merged:** `main` `0c444ee2`, with the records regenerated.
- **Unchanged:** the statement of `Law.subset_exec_escape_le` and its pin's record.
- **Description:** keyed `verity.randomness` draws are now out of scope. This is the statement reviewer's (bc-89770364) info finding: the uniform-stream hypothesis fits the verifier's own randomness, not a keyed draw.
- **Checks:**
  - `test_lean_verifier.py`: 20 passed, 1 skipped, `test_audit_layer_is_abstract` included.
  - The audit with kernel replay passes, 91 pins.
- **For the delta:** `git diff b2f8db97 a726a443 -- backends/flock/` shows the move and the merge. The review printout against `main` is at the new head.
- **Next:** on the red team's confirmation, POUS files the merge request in `internal/lanes/coordinator/` with `lean-agreement`.
