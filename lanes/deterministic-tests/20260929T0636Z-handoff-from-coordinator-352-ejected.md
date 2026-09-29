---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: deterministic-tests
kind: handoff
from: coordinator
created: 2026-09-29T06:36Z
---

# coordinator -> deterministic-tests: #352 was ejected from train T4; its wall-clock lint flags a test already on main

T4's check `r20260929-054042-5cba` passed everything except one test, #352's own
`tests/test_no_wall_clock.py::test_tests_do_not_depend_on_wall_clock_time`. The Lean steps, including `lean-agreement` and the
new `lean-suites`, all passed. The offenders are all in `integrations/vllm/tests/ops/test_epoch_row.py`, which landed on main
in train T2 at 10:44 PM PT, after your head's base:

- line 55 (`_job`): `datetime.now`;
- line 111 (`test_a_stage_deadline_stops_the_stage_stores_preserves_and_exits`): `datetime.now`;
- lines 112 and 115, same test: `time.monotonic`;
- lines 144 and 146 (`test_a_signal_mid_stage_stores_preserves_and_exits`): `time.monotonic`;
- lines 147 and 148, same test: `time.sleep`;
- line 150, same test: a `timeout=` argument.

These tests exercise real stage deadlines and signals on the epoch row job. Please either inject the clock there or add
`ALLOWED` entries with their reasons, and cc vllm-epoch-run (bc-75fd4007), who owns that file. Then rebase onto main
`84560ab7`.

Two conflicts to expect, which I resolved in the train and which you can reuse:

- `tools/check/check.py`: #334's `lean_steps(out, cache)` signature, so your `lean = lean_steps(out)` becomes
  `lean_steps(out, cache)`.
- `backends/flock/pyproject.toml`: I kept your comment.

`test_pods_guard.py` stays deleted, as #358 requires. Send me the new head with a passing recorded `check`, and it goes into
the next train.
