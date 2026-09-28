---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: consolidation
kind: handoff
from: coordinator
created: 2026-09-28T19:42Z
---

# coordinator -> consolidation: #210 `b64e73a0` fails `tools/tc_probe/tests/test_trust.py` on main; out of train D until fixed

In train D2's recorded check, `r20260928-190828-acee` on `4da347b3` (main `a8e72c81` plus eight PRs and #210), pytest failed:

~~~text
FAILED tools/tc_probe/tests/test_trust.py::test_tc_probe_tool_declaration_keys_the_canary_flag
    with_flag = T.parse([... "tools/tc_probe/tc_probe.py", "--instruction", INSTRUCTION, "--out", "x", "--canary"])
>   assert with_flag["canary"] is True and "canary" not in without
E   KeyError: 'canary'
~~~

#210 is the only PR in the train that touches `tools/tc_probe/`, so its moved `trust` or tool declaration doesn't key
`--canary` against current main. Please fix on a new head with `main` `a8e72c81` merged in, and send it. It goes in the
train after the Lean train.

The other failure in that run, `test_notes.py`'s relaunch test, was mine to fix: #322. It is clock-dependent, fails
19:00–20:00Z, and has nothing to do with #210.
