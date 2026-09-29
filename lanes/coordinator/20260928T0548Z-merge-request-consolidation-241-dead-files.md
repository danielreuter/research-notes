---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc red team (bc-f0bc7e75)
created: 2026-09-28T05:48Z
---

# Merge request: PR #241, remove dead files (23)

- **PR:** [#241](https://github.com/danielreuter/verity/pull/241), branch `cursor/remove-dead-files-ac68`, head **`f9ca44603bfb0b3b61439eb9f30a37beec6b6f4e`**, into `main`. Ready, $0.
- **Deleted, each with a scan showing zero references:**
  - 9 stray `results_*` run outputs;
  - `research`'s 4 unapplied veritor telemetry `.diff` patches;
  - 10 unreferenced backend scripts and shims in frozen B-Ligero and A-GKR.
- **Gate:** `REPORT_GENRE` now also catches `results_*`/`result_*`. The six files that must stay are listed in `PINNED_EVIDENCE`.
- **Tool closures that change:** `bench_vu`, `bench_vu_fp8`, `bench_vu_fp4` and `a_gpu_prove` get a new source identity on their next Attempt.
- **Conflicts:** merges cleanly with #210, #216, #224, #228 and #235. #134 conflicts with `main` in `test_circuit_check.py` already; that isn't from this PR.
- **Tests:** repository passes. The ligerito and gkr suites match `main` (105 passed, 12 skipped, 11 torch-only errors). `tools/research/tests`: 467 passed.

**For the red team:** nothing of yours is deleted.
- `fixtures/redteam*` and the reproduction scripts in `backends/direct/ligero/redteam/` stay.
- The audit was wrong that `redteam-3/gpu_a_forge.json` is unread: `test_redteam_3_fixtures.py` reads it under `check`.
- `fixtures/redteam` is read only by battery gate scripts outside `check`. Whether those batteries should run in `check`, or the fixtures be retired, is your call.
