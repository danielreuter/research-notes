---
lane: coordinator
kind: handoff
from: reaper-resume-guard
created: 2026-09-25T14:49Z
---

# MERGE-READY reaper-resume-guard: lane/reaper-resume-guard @ c69ec9de (PR #24), base main@2c92b9e3

- PR: https://github.com/danielreuter/verity/pull/24 (reaper change only; render_lines untouched, #23 owns that)
- Change: `reap_lines` (FINAL-lane pods) skips pods whose createdAt/lastStartedAt is after done_ts (or unknown) and runs
  `reap_custody` (run_custody_r2 under `watch --custody-r2`) before terminating. `--keep-pod` and `stale_reap_lines` unchanged.
- New log lines:
  - `HH:MMZ RESUMED-POD <lane> <pod> <id> (created HH:MMZ, after FINAL HH:MMZ): not reaped` (once per pod)
  - `HH:MMZ REAP-BLOCKED <lane> <pod>: <why>` (re-checked every 30 min, state key `reap_final`)
  - `HH:MMZ REAPED <lane> <pod> <id> $X/h (final Nm ago); custody: <why>`
- Behaviour change: with --reap, REAP-FAILED is retried every 30 min, not every pass.
- Tests: test_notes.py 59/59. Full tools/research suite: 436 pass. These fail on main too: test_pods_connect rsync,
  test_pythonpath, test_store_honing evict, test_telemetry d6. test_remote_local exclusive is flaky (passes on rerun).
- After merging: restart the steward (`research notes watch --reap` on vy-control-verity).
- No pods, $0 spent.
