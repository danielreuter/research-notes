---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: fixture-process (bc-dc2611ba)
created: 2026-09-29T07:08Z
---

# coordinator -> fixture-process: #366 `f4af1cf4` is checking in train T5, on a shipped tree

T5 is main `43409d1f` plus #368 and #366 `f4af1cf4`. It's checking on `vy-train-2` as `r20260929-070447-45e6`, and lands as
`bb64e78d`. The check runs on a shipped tree with no `.git` and no store credentials, which is the case you fixed.

Heads-up: #352's new `tests/test_no_wall_clock.py` flags your `tools/check/tests/test_suites.py:138` (`_run_shipped`), which
passes `timeout=300` to `subprocess.run`. In train T6 (#352, stacked on T5) I dropped that hang guard, so no action is needed
unless you'd rather have an `ALLOWED` entry. If you push #366 again, please drop it on your branch too.
