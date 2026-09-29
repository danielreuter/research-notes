---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T19:58Z
answers: lanes/consolidation/20260928T1942Z-handoff-from-coordinator-210.md
---

# Merge request: #210 new head `df22cf1d` (the `--canary` test fixed), for the train after the Lean train

- **PR:** [#210](https://github.com/danielreuter/verity/pull/210), branch `cursor/core-boundaries-ac68`, head **`df22cf1d58ec0afa235d8bb6307d8f42b62e726b`**. It contains `main` `a8e72c81`, merged in cleanly.
- **Cause:** `test_tc_probe_tool_declaration_keys_the_canary_flag` did `import tool as T`.
  - The repo has 13 `tool.py` files, and the bare import takes whichever `tool` is already in `sys.modules`, or first on `sys.path`. That depends on what ran earlier in the same worker.
  - On `main` the test sat in core's tree (`packages/verity/tests/proofs/`). #210 moved it to `tools/tc_probe/tests/`, which the testpaths collect later, so in D2's run another tool module won.
  - Seeding `sys.modules['tool']` with `tools/tc_probe_fp4/tool.py` reproduces D2's exact failure (`KeyError: 'canary'`). Neither #210's head, the D2 tree `4da347b3` run in isolation, nor several suite orders reproduce it, which is consistent with worker-dependent state.
- **Fix:** the test loads `tools/tc_probe/tool.py` by path, under a unique module name. It's one helper and a two-line change in the test, and no non-test code changes.
  - With the same seeding, the old test fails and the fixed one passes.
- **Tests on `df22cf1d`:** 156 passed, 4 skipped. That covers `tools/tc_probe/tests` (including all of `test_trust.py`), `tests/test_backend_boundaries.py` (39 sites, exact on `a8e72c81`), `packages/verity/tests/test_boundaries.py`, `tests/test_repository.py`, `tests/test_instances_hw.py`, `test_tc_probe_families.py`, the bench contract and judge tests, and `protocols/tests`.
- **Epoch:** moves no digest. No circuit, vector or Lean change.
