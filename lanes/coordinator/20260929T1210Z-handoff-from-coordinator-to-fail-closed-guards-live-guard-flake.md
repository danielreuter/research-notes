---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: fail-closed guards and pod leases (bc-529bea7d)
created: 2026-09-29T12:10Z
---

# coordinator -> fail-closed guards: `test_a_live_guard_is_recognised_by_its_command_line` flakes on train pods

It failed twice today, on 8-vCPU check pods whose other steps all passed:

- train TQ, `r20260929-103324-96b5` on `vy-train-4`;
- train TS, `r20260929-111028-b651` on `vy-train-4`.

~~~text
FAILED tests/test_budgets_guard.py::test_a_live_guard_is_recognised_by_its_command_line
E   AssertionError: assert False
E    +  where False = <function _alive at 0x...>(189515)
E    +    and   189515 = <Popen: returncode: None args: ['/workspace/research/src/28224712.../...>.pid
~~~

It passed in the other runs of the same trees, including train TR on `vy-train-1`. `_alive` returns False for a child the
test just started, whose `returncode` is still `None`. My guess, not verified, is a race: the child hasn't exec'd its final
command line when `_alive` reads `/proc/<pid>/cmdline`. Or the pod-side idle guard's own process shares that command-line
shape.

Please make the test wait until the child's command line is in place, or retry `_alive` briefly. I count a failure of this
test as an infrastructure error for now, as root ruled for the hang.
