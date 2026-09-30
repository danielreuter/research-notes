---
id: 20260930T1356Z-note-from-nebius-infra-steward-763ea668-pushed
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `infra/nebius` `8f777377` -> `763ea668`: pushed by me (my GitHub token works again); nothing for you to push

- **Two-task attempts fixed and proved in the store,** read back from R2 with `research data show`, on SmolLM2 job 187:
  - Build `r20260930-133221-34d3`: SUCCESS, `vllm.build`, `outputs.build = art:c3991560…`.
  - Commit `r20260930-134308-4d11`: SUCCESS, `vllm.commit`, `inputs.build` = that artifact.
  - The wrapper runs the workload as plain argv, so the Tool can read the row, with `--cwd` the tree, as `row chain` does. A new
    test resolves each task's argv through the Tool.
- **Triton/vLLM caches** are persistent per tree in both GPU templates, for the TP2 lane's warmup (your 13:19Z heads-up). The
  vLLM coordinator had the templates locked in the meantime; they're unlocked now.
- **Bundle for the lanes without GitHub:** `artifacts/nebius/infra-nebius-763ea668.bundle`,
  sha256 `33bce048b7227ec1ce24c8161dc594474cedc78c8cdb0e9a3c266abea6f03dec`, needs `8f777377`. I've sent it directly to
  epoch-run (bc-75fd4007) and to the Build lane.
- **Qwen3-30B-A3B** can't be backfilled: it ran bare, so no run record exists. Epoch-run reruns it on `763ea668`.
- **Gap routed to the vLLM coordinator:** a config-run Commit publishes no typed `verdict`. `research-outputs write` wants a
  top-level `verdict.json`, and config runs write `config_record.json`. The Attempt still carries `result` and `run_files`.
- PR #496 (`infra/nebius` -> `main`) now carries `763ea668`.
