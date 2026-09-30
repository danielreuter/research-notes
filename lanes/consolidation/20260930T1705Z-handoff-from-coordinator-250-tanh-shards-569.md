---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: consolidation
kind: handoff
from: coordinator
created: 2026-09-30T17:05Z
---

# #250 at `da4261e5` still breaks the softcap tests, this time #569's

- **What I ran:** #228 `b8a27ef8` + #250 `da4261e5`, stacked on TVN's tip `a522f206`, whose TVM part carries #569 (the softcap replay row evaluator).
  - `integrations/vllm/tests/program/test_fa2_softcap.py` fails 3 tests there: `test_the_replay_row_kernel_is_the_definition[0]`, `[2]` and `test_the_capture_compare_accepts_the_definitions_own_rows`.
  - The error: `AttributeError: module 'verity_vllm.program.registry.prims' has no attribute '_tanh_shards'`.
  - The same tests pass on `a522f206` without #250 (19 passed).
- **Why:** your rebase fixed #551's uses of the moved name. #569 added new ones after it.
- **Please:** rebase onto `main` once TVM lands (`2e04ac50`), or onto TVN's tip `a522f206` now, and point #569's uses at the core location too. Then re-grant (vLLM + red team) and send a bundle.
- **Meanwhile:** TVO (#574, #575, #579) takes the next slot.
