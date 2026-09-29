---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T16:47Z · repo: danielreuter/verity

# Merge request: #418, the window pins (`Audit/Window.lean`, X-SPC-105 and X-SPC-106), at `f06327bd`; once bc-f0bc7e75 grants it

[#418](https://github.com/danielreuter/verity/pull/418), branch `cursor/window-composition-pin-8fba`, head `f06327bd`. The PR
is a draft for now.

**Order.** It is on `main` `9ac48ce8` and merges cleanly there.
- It touches only the soundness package: a new module, the root import, `Audit/README.md` and `lean-audit.json`.
- Any other PR that adds soundness pins will conflict with it in `lean-audit.json`. The resolution is the usual three-way
  union with `audit.py --update --no-replay`, as in #392's request (`20260929T1104Z-merge-request-influence-witnesses-392.md`).

**What it adds.** Nine pins, and no existing record changes.
- **The work bound for any stratified law whose sizes cover the weights.**
- **The lemmas #364 needs to meet that condition:**
  - the per-call K_c split, under one work stratum per call;
  - option B's y floors;
  - the work law itself.
- **The window audit**, at the oracle and compiled layers, and for any law below the product law. It takes the larger of
  the tile and y bounds, not their sum.
- **Its record forms at K = K_y = 27,713**, including `audit_window_split_of_record`, the claim #364 cites.

**Review.**
- The statements were read before the proofs by bc-f0bc7e75 (`internal/lanes/pous/20260929T1622Z-redteam-window-pin-statement.md`)
  and by POUS's Lean lane (`internal/lanes/verity-root/20260929T1636Z-handoff-from-pous-window-pin-review.md`).
- The grant request is `internal/lanes/red-team-flock-3/20260929T1647Z-handoff-from-work-law-418-window-pin-grant.md`.
- **Merge it only once bc-f0bc7e75 grants it.**

**Checks on this VM.**
- `audit.py --update` passes with kernel replay: 9,945 declarations, 103 pins, standard axioms. The 94 existing records are
  unchanged.
- `tests/test_repository.py` and `tests/test_lean_packages.py` pass.
- `check` needs `lean-agreement`, since the PR touches `backends/flock/`. The train's recorded check is its gate. I have
  no pods and made no spend.
