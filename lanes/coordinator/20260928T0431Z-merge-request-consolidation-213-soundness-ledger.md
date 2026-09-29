---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc soundness (bc-9e538dc5), audit theorems (bc-a0c5a22f), flock verifier (bc-8e519ca0), Lean organization (bc-866e1acc)
created: 2026-09-28T04:31Z
---

# Merge request: PR #213, the soundness ledger index true against `main` (plus two drafts that wait)

## #213, ready: please take it with #211

- **PR:** [#213](https://github.com/danielreuter/verity/pull/213), branch `cursor/soundness-ledger-docs-ac68`, head **`70586c11`**, into `main`. Docs only, $0.
- **Contents:**
  - `soundness/ASSUMPTIONS.md` gains a "What is pinned" section and an "Upstream status" section, the latter naming the watch entries and pointing at `upstream.py`;
  - A1 by its Lean name, "verifier" for "coin server", and the Table 1 ids as the renderer cites them;
  - `assumptions/trusted-components.md`: the reviewer reads `pins`/`reads`, and the `escapes` are named;
  - the `lean-proofs` skill's example is A2.
- **Pins and Lean:** no Lean file, no `lean-audit.json` and no pin changes, so no statement reviewer is needed.
- **Tests:** `tests/test_repository.py` and `tests/test_lean_packages.py` pass.
- **Conflicts:** merges cleanly with the open soundness PRs #207, #187 and #177.
- **Why now:** outside collaborators open this ledger first tomorrow.

## Two drafts, for later

- **[#215](https://github.com/danielreuter/verity/pull/215)** retires `CheckAxioms.lean`, `level3/CheckAxioms.lean` and `FlockSoundness/Check.lean`, their `exempt` entries and the `check_axioms` tests. `exempt` is the only `lean-audit.json` key it changes.
  - **Hold it until** the Lean lanes' PRs that still edit those files have landed: #154, #177, #187, #205, #207 and #202, and #199 for the `exempt` line.
  - After that, every conflict is a `git rm`. I'll mark it ready then.
- **[#214](https://github.com/danielreuter/verity/pull/214)** is the dependency escape-hatch scan (Lean organization §7 item 11), stacked on #149.
  - It merges after #149, then rebases onto `main`.
  - It changes no record: 27 tool tests pass, with 18 controls run for real on Lean v4.34.0.

## For you, as the renderer's owner

Table 1 tags C-Flock's interactive rows `statistical-soundness`. But the compiled theorem the rows cite is computational: it rests on SHA-512 collision resistance, A2. The ledger now avoids that id. The fix, retagging or splitting the property, is your call.

The superseded branch `cursor/soundness-ledger-index-ac68` holds both halves. It has no PR, and it becomes deletable once #213 and #215 are on `main`.
