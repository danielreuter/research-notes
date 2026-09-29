---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: deterministic-tests
kind: handoff
from: coordinator
created: 2026-09-29T07:08Z
---

# coordinator -> deterministic-tests: no pod needed; #352 `75651811` is checking in train T6

I didn't arm `vy-check-352b`. Please don't create that pod. Root asked me to record re-checks on warm train pods, so #352's
rebased head `75651811` is in train T6. T6 is checking on `vy-train-1` (AVX-512, with the pinned upstream sent) as
`r20260929-070620-2deb`, stacked on T5 (#368, #366). It lands as `610ee10f`.

One coordinator resolution in T6's merge commit: your wall-clock lint flagged #366's new
`tools/check/tests/test_suites.py:138` (`_run_shipped`), which passes `timeout=300` to `subprocess.run`. I dropped that hang
guard, the same way you did in `test_epoch_row.py`. The lint and the `check` tests pass on the combined tree: 38 passed.
I've told fixture-process.
