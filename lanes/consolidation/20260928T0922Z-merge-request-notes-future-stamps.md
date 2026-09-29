---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: consolidation
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T09:22Z
---

# Merge request: `research notes sync` leaves out lane notes stamped more than 5 minutes ahead (the root's ask, low priority)

- **Branch:** `cursor/notes-future-stamps-ac68`, head **`0e91f584c62970ae9d2a87dcc178a355eee6912f`**, on `main` `3ba4d8b3`. PR: [#269](https://github.com/danielreuter/verity/pull/269). Ready, $0, off the epoch path.
- **What it does:**
  - `sync` leaves out any added or changed `lanes/**/*.md` whose filename stamp or `created:` is more than 5 minutes ahead of now. It syncs the rest, and prints `SYNC-REFUSED <path>: … use <date -u value>`.
  - A lane's own run exits 5.
  - In the steward's watch pass the refused notes appear as lines, and the pass keeps going.
  - `checkpoint`, `bind` and `relaunch` with `RESEARCH_NOTES_SYNC=1` go through the same check.
  - Committed notes are never re-checked.
- **Tests:** research `-k "notes or sync or checkpoint"`: 88 passed, 1 skipped. `tests/test_repository.py` and the no-`verity`-import test pass.
- **Merges:** clean with #216 and with #240, and the tests pass on both merged trees. #216 and #240 conflict with each other, independently of this.
- **Not covered:** the laptop watcher's `--snapshot` path commits without calling `sync`, so it isn't checked.
