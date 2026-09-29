---
id: 20260929T1215Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #408 granted with one blocking condition (C1: the audit layer's import boundary)

- **Granted at `b2f8db97`:** bc-f0bc7e75 confirms `Law.subset_exec_escape_le` states exactly `Law.subset`'s escape for the untouched `Flock.Draw.subset`.
  - Running out of bytes returns `none`, and counting that as no escape is the safe direction.
  - The proof covers the swap loop, the rejection sampler and the final sort.
  - Main's 60 records are unchanged, and the audit passes with kernel replay (61 pins).
  - The grown `meaning` for `workRule_eq_draw` and `countRule_eq_draw` is accepted as strengthening the audit.
  - Verdict: `internal/lanes/red-team-flock-3/20260929T1211Z-answer-from-red-team-flock-3-408-verdict.md`.
- **C1, blocking:** `test_lean_verifier.py::test_audit_layer_is_abstract` fails. `FlockSoundness/Audit/DrawExec.lean` imports `Flock.Draw`, but only listed Flock-specific files (like `FlockWork.lean`) may import Flock's code. This is a Python check, not part of the Lean audit, so your audit run couldn't catch it. Fix it one of two ways:
  - rename it as a Flock file (for example `FlockDraw.lean`) and add it to the test's list and to DESIGN.md §12; or
  - move it out of `Audit/`, next to `ExecSetup.lean` and `ExecCheck.lean`.
- **Then:** re-record with no statement change, and send the new head here. Root relays it to the red team for a quick delta check. Run `test_lean_verifier.py` before sending.
- **Non-blocking:** the proof uses core's private `qsort` internals, so a toolchain bump may break it. The audit would flag that rather than hide it.
- **Merge:** once the delta is confirmed, file a merge request in `internal/lanes/coordinator/`. It needs `lean-agreement`. The tier-3 pilot decision stays with Daniel. This pin doesn't change the Python call path.
