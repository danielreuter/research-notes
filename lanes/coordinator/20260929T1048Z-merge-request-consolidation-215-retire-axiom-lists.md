---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc flock verifier (bc-8e519ca0)
created: 2026-09-29T10:48Z
---

# Merge request: #215, retire the old `#print axioms` lists (Lean organization §7 item 2)

- **PR:** [#215](https://github.com/danielreuter/verity/pull/215), branch `cursor/retire-axiom-lists-ac68`, head **`fd0fd672780042a736ba0e04a78478a32fa51c45`**, with `main` `d7a58582` merged in. Ready.
- **Contents:**
  - deletes `CheckAxioms.lean`, `level3/CheckAxioms.lean` and `FlockSoundness/Check.lean`, their `exempt` entries, and the two `check_axioms` tests;
  - the docs that cited them now point at `lean-audit.json` and `tools/lean/audit.py`.
  - 11 files, +6/−518.
- **No pin or `reads` record changes:**
  - In all three `lean-audit.json` files, `exempt` is the only key that differs from `main`, and each loses exactly the deleted file's entry.
  - The executable package's audit passes without `--update`: 3,835 declarations, 14 pins.
  - Soundness's `Soundness.lean` changes only inside its `/-! -/` module docstring. `check`'s Lean audit confirms `level3` and `soundness`.
- **Tests (`suites.py --fresh`):** `repository`, `verity-lean-audit` and `verity-flock -k lean_verifier` pass.
- **Why it's ready now:** of the Lean PRs that edited these files, #154, #187 and #207 merged, #177's code landed in train T1 (`e1ac9466`), and #205 was closed.
- **#202:** its only edit here adds three `#print axioms` lines to `level3/CheckAxioms.lean`. After this lands, #202 gets a modify/delete conflict there; resolve it with `git rm`. The audit covers those three theorems anyway.
