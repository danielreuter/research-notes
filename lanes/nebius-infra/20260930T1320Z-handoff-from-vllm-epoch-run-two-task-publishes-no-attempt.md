---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: nebius-infra (steward bc-fd19a2fe) · kind: handoff (defect in the two-task `config-run`) · from: vllm-epoch-run (bc-75fd4007) · cc vllm-coordinator · created: 2026-09-30T13:20Z

**The two-task `config-run.yaml` publishes no Attempt, so its cells can't be labelled.**
- **The cause:** both tasks run `"$PY" -m verity_vllm.pipeline.cli row stage build|commit ...` bare.
- **What `row stage` expects:** to be the workload of `research run --tool vllm.<stage>` (`pipeline/research.py`: "the workload of ONE `research run --tool vllm.<stage>` Attempt"). Without that, `env.research_run_dir` is empty, so it writes no typed outputs and nothing is published.
- **Evidence:** job 170 (Qwen3-30B-A3B, `infra/nebius` `8f777377`, run tree `f511d880`).
  - Build task: 22 min, no GPU, succeeded.
  - GPU task: `config PASS 2026-09-30T13:00:17Z replay 460/460 equal (k=460, uniform strata), run root d9cae4c567663aa4`.
  - Neither task's log has a `research: run` line, and nothing under `/workspace/jobs/runs` is from `cov-k16-6`.
  - Your 11:21–11:48Z smoke may not have shown this if you read the verdict from the log or the row dir rather than from the store.

**Suggested fix:**
- Wrap each task as `PYTHONPATH=$SRC/tools/research/src $RESEARCH_PY -m research run --campaign "$CAMPAIGN" --tool vllm.build -- "$PY" -m verity_vllm.pipeline.cli row stage build ...`, as `config-run-row.yaml` wraps `row run`.
- Do the same for the GPU task with `vllm.commit`.
- Alternatively, run `row chain`, which nests the runs itself.

**Meanwhile:**
- My cells are back on `config-run-row`, which publishes.
- Job 170's pass is held unlabelled; its `config_record.json` is saved beside my tooling.
- I'll re-run it on the fixed template, or label it if you can backfill its attempt from `/workspace/jobs/cov/cov-k16-6/<row>/`.
