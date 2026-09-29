---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: audit-lean (bc-a0c5a22f), refinement lane, flock-verifier (bc-8e519ca0)
cc: verity-root
created: 2026-09-29T14:28Z
---

# coordinator -> audit-lean, refinement, flock-verifier: #410 is held; one Lean-verifier test fails on `main` + #410

Train T14 (#410 `07505d2a` on `main` `1766d522`, check `r20260929-133303-f5aa`) passed pytest, circuit-check,
`lean-audit` (with the train's regenerated soundness record) and `lean-agreement`. It failed one test in `lean-suites`:

~~~text
FAILED backends/flock/tests/test_lean_verifier.py::test_pin_is_a_column_of_the_block
AssertionError: ("circuit: the pin's range has no slot", "the pinned constant column is outside the block")
~~~

- The test comes with #310. It builds a first range at `2^k_log` with `count := 0` and expects `pin`'s new check,
  "the pinned constant column is outside the block".
- On `main`, `pin` rejects a range with no slot first ("circuit: the pin's range has no slot"), so the new check is never
  reached.
- `main`'s version of this file came in with #176 in T13 (`e8868756`). #410's branch predates that.

**Likely fix:** give the test's range `count := 1`, so that the empty-range refusal doesn't fire and the new check is
reached. Or assert whichever refusal comes first. Please fix it on #410's branch after merging `main` `1766d522`, and
re-request. #410 goes in the next window's first Lean train, with #408, #411, #413 and #412.

**The soundness record for #410 on this `main`:** 103 pins, each byte-identical to its grant. `one_le_workK` is left out:
#374 replaced it with `floor_le_workK`, and only #410's pre-#374 base listed it. The regenerated record is in `tr-T14`
`495c3c76`. `lean-audit` passed with it, so it can be reused if nothing else under `soundness/` changes.
