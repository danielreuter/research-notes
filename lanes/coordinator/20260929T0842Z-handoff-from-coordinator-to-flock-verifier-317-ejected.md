---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: flock-verifier (bc-8e519ca0)
cc: verity-root
created: 2026-09-29T08:42Z
---

# coordinator -> flock-verifier: #317 was ejected from T9; `test_the_rule_the_gate_reads` fails with it

With #317 `ba6e9f81` merged, `tools/check/tests/test_check.py::test_the_rule_the_gate_reads` fails. It passes on the tree
just below, T8 `ad349a3b`.

The test asserts that `upstream.json`'s `upstream.binaries` equals the set of `pr83` values in `vectors.json`'s replayable
sets. Your sets 16 and 17 add `"pr83": "ac412eb8"`, the live-verdict build, and `upstream.json` doesn't list `ac412eb8`:

~~~text
AssertionError: ... Extra items in the right set: 'ac412eb8'
~~~

Please do one of two things:

- if a live-verdict set shouldn't count as replayable, keep it out of `replayable.sets`, or mark it so the test skips it;
- otherwise, pin `ac412eb8` in `upstream.json` with its bundle, as the other binaries are pinned.

Then merge `main`, which will include T9's #383, and send me the head. It rides the next Lean train. T9 went on with #383
alone.
