---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T05:19Z
---

# Merge request: the research vocabulary accepts C-Flock and D-SP1 as candidates

- **Branch:** `cursor/research-vocab-ac68`, head **`b832b21e`**, into `main`. PR: [#235](https://github.com/danielreuter/verity/pull/235). Ready, $0.
- **Change:** a new `BACKEND_FAMILIES` (A-GKR, B-Ligero, C-Flock, D-SP1), checked against `bench.views.FAMILY_NAMES`. `CANDIDATES` gains `C-Flock` and `D-SP1`. Nothing is removed, and no spelling becomes an old spelling.
- **Recorded labels:** all still validate. A test replays the frozen ledger's import and the red-team verdicts: 3,615 labels, 0 off the vocabulary. `vocab-check --strict` stays clean.
- **Tests:** research `-k "vocab or label or store"`: 158 passed. `test_store_tables.py`, the tables label test and `tests/test_repository.py`: 15 passed.
- **Overlaps:** none that conflict. #210 and #224 edit other lines of the same files.
- **Epoch:** moves no digest.

Once it lands, C-Flock's Attempts, including M0's cells under #189's row, can carry `candidate C-Flock`.
