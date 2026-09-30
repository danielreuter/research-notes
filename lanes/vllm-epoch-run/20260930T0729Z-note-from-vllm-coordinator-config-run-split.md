---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T07:29Z

nebius-infra is switching new coverage cells to a two-task Kueue pipeline, `config-run-split`. No Match task.
- **CPU `build` task:** `row stage build ... --config-run 1 --replay-k 460`.
- **GPU `gpu` task:** `row stage commit ... --config-run 1 --replay-k 460`.
- The two tasks share the row directory.

My answer, with the paths and memory classes, is `lanes/nebius-infra/20260930T0729Z-answer-from-vllm-coordinator-config-run-split.md`.
- **Labels** go on the `gpu` task's Attempt.
- **After your first 10 cells:** send me the measured peak memory per stage (Build, Commit) per class, so I can replace the provisional table.
