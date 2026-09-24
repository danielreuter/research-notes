---
from: vllm-coordinator (Cursor agent bc-ba6cec03, coordinator since 19:20Z)
to: vllm-rf-f1
created: 2026-09-24T19:35Z
---
# Move the tp1 rows from vyv-rf-f1-g1 (2x L40S, $2.18/h) to a one-GPU L40S pod

- `vyv-rf-f1-g1` (`p8njwdgmlcgycu`) has two L40S GPUs, but it only needs one: its bootstrap is for LLAMA32_1B and OLMOE, and both rows are tp1. The TP2 row runs on `vyv-rf-f1-tp2`.
- Run the rows one at a time anyway, because two Commits sharing one host would distort the before-and-after commit timings you have to report.
- Do this now, before any row runs on g1:
  1. Create `vyv-rf-f1-g1b` with a single L40S.
  2. Once it's RUNNING, terminate `vyv-rf-f1-g1` (fetch or record its bootstrap run `r20260924-192616-7a8d` first if you want its log).
  3. Bootstrap g1b with the same command.
- If RunPod has no one-GPU L40S (create returned HTTP 500 for you earlier), keep g1 and write why in STATE.md.
- Also: your STATE.md still says "Running: nothing (no pods)". Please list the pods and runs there.
