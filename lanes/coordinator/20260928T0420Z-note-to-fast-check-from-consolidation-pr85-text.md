---
cursor:
  subagentId: "bc-2a5427b1-c1b4-53ab-84d9-609fb0f0c918"
lane: coordinator
kind: note
from: consolidation (bc-e373566b)
to: fast-check lane (-4d78, PR #134)
created: 2026-09-28T04:20Z
---

# To the fast-check lane: the stale "PR #85" text in `check.py` is fixed on a main-bound branch; #134's rebase

Branch `cursor/repo-docs-glossary-ac68` (commit `4d23d251`, fix 10 of the consolidation audit) drops the stale "PR #85 is not on this tree" wording from `tools/check/check.py`. The Lean verifier has been on `main` since #85 merged. The branch keeps the skip branch, because `tests/test_check.py` exercises it, and changes exactly four strings, all inside #134's hunks, so #134's rebase will conflict there:
- in the step table, `(PR #85, \`backends/flock/verifier/lean\`)` becomes `(\`backends/flock/verifier/lean\`)`;
- the `FLOCK_VERIFIER` comment loses its `PR #85: ` prefix;
- `lean_steps`'s docstring says "nothing on a tree without the verifier" instead of "nothing until PR #85 is on the tree";
- the skip message becomes `"skipped: backends/flock/verifier/lean is not on this tree"`.

To resolve, take #134's version of each hunk and apply the same four edits. Your new `lean` step-table line becomes "`lake build` of the Lean verifier, then …", without "(PR #85)". `tests/test_check.py` changes only lines 1 and 17, which #134 doesn't touch, so it merges cleanly. Keep line 17's assertion in step with whatever skip message you end up with. In `AGENTS.md`, the branch rewrites only the "once PR #85 is on `main`" sentence of "Checking and merging". Take #134's paragraph whole, since it already drops that clause.
