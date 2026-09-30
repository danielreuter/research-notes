---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

20260930T1611Z: Daniel 16:05-16:07Z: 'cell' -> 'vLLM deployment' (handoffs to epoch-run, TP2, tc-gemm, coverage-defs, RC/backend sweep). GPU/CPU split GO (variant 3): TP2 lane builds --replay-deferred + replay bundle + `row stage replay` with per-slice weight-root openings (first: confirm the weights root supports openings); steward designs GPU commit-only queue ordered by engine key (hot worker reuse) + CPU queue for build/replay + 3-task template.
