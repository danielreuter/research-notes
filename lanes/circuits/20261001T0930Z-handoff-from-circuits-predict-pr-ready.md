---
id: 20261001T0930Z-handoff-from-circuits-predict-pr-ready
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-predict
---

# circuits-predict -> @circuits (2:30 AM PDT, head updated 2:35): the predictor PR is ready at `cursor/vllm-predictor-8c79` `d34b7a58d`, in time for the 3:30–4:00 slot

- **Head.** `d34b7a58d` (pushed): origin/main at `aac153709` merged in, plus the scorer's code-versioned cache. A cached result carries
  the predictor's code version and is reused only by that code, or by a version `--reuse-code` names. The code's own result for a key
  always wins, then the reused versions in the order named.
- **Title and body.** In the Project store at `internal/circuits/predictor-pr-body.md`.
- **Tests at that head.**
  - `integrations/vllm` `tests/predict`, `tests/lint` and the top-level invariants: 97 passed.
  - The repository's `tests/`: 33 passed.
- **Records.** Predicted Programs never enter one. No record-path module imports the predictor, and `inputs_trace` forbids the
  package. All 3669 construction manifests of the scored Builds record `forbidden_hits: []`. The scorer refuses to write inside a
  rows root.
- **No circuit change**, so there is no circuit-check report. `check` has not run on this head.
- **#557 preview.** On this head with #557's `2fdd11053` merged, coverage-v1 Qwen2.5 traces become exact (cov-k03-8, cov-n111). The
  pre-#557 main-tree trace cov-k03-7 starts to differ, as expected. The full Qwen2.5 pre-run on that tree is r20261001-092331-b782.
  The landed number follows at 4:50.
