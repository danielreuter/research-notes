---
lane: tables-switch
kind: report
created: 2026-09-25T18:55Z
status: final
---

CHECKPOINT 25a26e3b (19:12Z) [final] merge-ready 25a26e3b (PR #33): parity --take-snapshot --record, published=views, bench.switch digest, CHANGELOG; parity ok 15/15 art:af3ddc98; handoffs to coordinator + flock-backend; no pods, $0
CHECKPOINT 25a26e3b (19:11Z) [final] merge-ready 25a26e3b (PR #33): parity --take-snapshot --record, published=views, bench.switch digest, CHANGELOG; parity ok 15/15 on R2 store; handoffs to coordinator + flock-backend; no pods, $0
CHECKPOINT a0a0091b (19:02Z) [open] a0a0091b pushed: views --parity --take-snapshot --record, --published, steward published="views" + tests; refreshed R2 store to VM; next: real parity run, switch digest, changelog, kb
CHECKPOINT f6524716 (18:55Z) [open] started 1900Z; branch lane/tables-switch on PR #32 tip f6524716 (Flock column from #32, not duplicated); next: parity cmd, steward published=views option, digest, changelog; agent bc-a6473c97

## FINAL

~~~text
tip: lane/tables-switch @ 25a26e3b (base origin/main@a1ccdecd, merged; started on PR #32 f6524716)   merge-with: none (PR #33)
known-failures: test_notes.py::test_relaunch_saves_the_work_supersedes_binds_the_successor_and_prints_its_launch_message; tests/test_repository.py size caps (all on main a1ccdecd too)    pod: none; $0
artifacts: art:af3ddc98 (tables-parity/v1, ok 15/15) art:23049a6d (snapshot tables-2026-09-25), both from the R2-refreshed store at 19:10Z; the control-pod run is the one to cite at the switch
~~~

Deliverables are in the merge-ready handoff `lanes/coordinator/20260925T1915Z-handoff-from-tables-switch.md` (parity command, steward.toml edit, 6 PM recipe, digest). The record contract went to `lanes/flock-backend/20260925T1912Z-handoff-from-tables-switch.md`. kb/TABLES.md was edited in place. Evidence: `evidence/switch-digest-vm-1909Z.md`, `evidence/parity-vm-1909Z.json`. Handoffs received: `20260925T1905Z-handoff-from-coordinator.md` (PR #32 merged, don't duplicate): done, merged origin/main a1ccdecd (a merge rather than a rebase, since there's no force-push), and no Flock column added.
