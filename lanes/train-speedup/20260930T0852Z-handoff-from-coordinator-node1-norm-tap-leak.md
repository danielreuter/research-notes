---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: train-speedup
kind: handoff
from: coordinator
created: 2026-09-30T08:52Z
---

# Node 1 fails a third host-leak test: the vLLM norm-tap `.so`

TLN's node-1 check `r20260930-080725-e6b6` (slot c, with #495 and #504) passed every Lean step, `lean-agreement` included. Only pytest failed, on one test:

- `integrations/vllm/tests/pipeline/test_row.py::test_a_dense_tp1_row_attaches_the_norm_tap_only`
- It expects `row_records.missing_tap_build(["norm_tap"], env)` to say the tap `.so` is missing. On node 1 the default `env.norm_tap_so` path exists (a lane built the tap there), so it returns `""`.
- The same test passes on RunPod: TVF passed on t7.

The fix would be the same as #495 and #504: the test should point `norm_tap_so` / `router_tap_so` at a tmp path. Until that lands, I'm sending vLLM-suite trains to RunPod. TIN (#508 #512 #509) is checking on t7 now: `r20260930-084944-cf10`, expected merge `0db15c41`.
