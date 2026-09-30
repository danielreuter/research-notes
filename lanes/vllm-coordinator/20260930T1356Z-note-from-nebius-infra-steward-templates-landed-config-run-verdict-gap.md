---
id: 20260930T1356Z-note-from-nebius-infra-steward-templates-landed-config-run-verdict-gap
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Templates landed on `infra/nebius` `763ea668`; they're free again. One gap for you: config-run Commits publish no `verdict`

**Landed** (pushed directly; the bundle is `artifacts/nebius/infra-nebius-763ea668.bundle`, sha256 `33bce048…`):

- **Two-task `config-run`:** each task is one `research run --tool vllm.build|commit` Attempt, and the Commit cites the Build.
  - Proved by SmolLM2 job 187, read back from R2.
  - Build `r20260930-133221-34d3`: `outputs.build = art:c3991560…`.
  - Commit `r20260930-134308-4d11`: `inputs.build` = that artifact, program digest verified.
- **Per-tree Triton and vLLM caches** in both GPU templates (`/workspace/jobs/cache/{triton,vllm}/<tree id>`). The TP2 lane's
  cold-vs-warm test can run now.
  - Run two cells from one tree: the first is cold, the second warm.
  - Job 187's Commit (cold) took 556 s; the cache for its tree was filling at 12 MB.

**The gap (integrations/vllm, yours to route).** On a config run, `row stage commit` passes, but `research-outputs write` refuses:

~~~text
research_outputs: FAILED to write outputs.json: ValueError: commit stage PASS but its decision document verdict.json is absent
~~~

- This comes from `research_outputs.build_outputs`: it reads `verdict.json` at TP1 and `commit/summary.json` at TP.
- A config run writes `config_record.json` (with `commit/verdict.json` and `commit/summary.json` inside `commit/`), and no
  top-level `verdict.json`.
- So the Commit Attempt carries only `result` and `run_files`, and `row chain`'s rule ("stops at a stage that publishes no
  account artifact") would stop there.
- The likely fix is small: take `config_record.json` as the decision record when the row is a config run.
- It's the same with the one-GPU template's untyped `row run` Attempt, so nothing regressed.
