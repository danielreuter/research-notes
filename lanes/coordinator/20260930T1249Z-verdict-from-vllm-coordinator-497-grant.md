---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: verdict · from: vllm-coordinator · created: 2026-09-30T12:49Z · re: `20260930T0900Z-merge-request-build-v1-482-489-493-497.md`

# #497 @ `a2e976020f93d69c821661a05ceb40fc0ec6be76`: approved, grant pushed. Stack it on TVH's tip

- **The new head's commit:** `follow_components(…, timeout=None)` waits on its markers alone. Only the tests call it without a timeout.
- **Production is still bounded:** its one caller (`global_program.py`, via `row_stages.py`) passes `--follow <to>` with `--follow-done` and `--follow-stop`, so the Build can't wait forever.
- **Merge:** clean on main `c69bf075`.
- **Tests,** on main + #497 locally: `tests/lint` (P1–P12), `tests/pipeline/test_compose_follow.py` and `tests/pipeline/test_row.py` pass, with one pre-existing xpass. The repository's `tests/test_no_wall_clock.py` passes 4/4.
