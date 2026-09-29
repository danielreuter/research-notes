---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-epoch-run
kind: handoff
from: coordinator
created: 2026-09-29T05:43Z
---

# coordinator -> vllm-epoch-run: #342 was ejected from train T2; one census test fails with it

#342 rewrites `integrations/vllm/tests/regression/expected/qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json`.
With that change, `backends/numerical/tests/bench/test_census_data.py::test_workloads_are_the_regression_rows_template_mix`
fails: the census workload's `template_mix` no longer equals the expected file's mix, which has 17 more `Attention_v2{...}`
entries. The check that caught it was `r20260929-045525-44a6`, and it also reproduces locally: T2 with #342 fails, and T2
without #342 passes.

Please update the census workload, or the test's view of that row, in #342. Then send me the new head with a passing
recorded `check`, and it will ride the next non-Lean train. The rest of T2 is re-checking without it
(`r20260929-052928-f388`).
