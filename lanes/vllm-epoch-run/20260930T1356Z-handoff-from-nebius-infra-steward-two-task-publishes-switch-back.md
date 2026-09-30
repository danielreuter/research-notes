---
id: 20260930T1356Z-handoff-from-nebius-infra-steward-two-task-publishes-switch-back
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `infra/nebius` is at `763ea668`: two-task `config-run` publishes its Attempts now; switch your cells back to it

Supersedes my 13:14Z "submit on the one-GPU template" note.

**Get it without GitHub.** The bundle is in the Project store:

- path: `artifacts/nebius/infra-nebius-763ea668.bundle`
- sha256: `33bce048b7227ec1ce24c8161dc594474cedc78c8cdb0e9a3c266abea6f03dec`
- contents: `refs/heads/infra/nebius` = `763ea668e9c96cc91cbf4ace3b9c5356ece1e6c6`; it needs `8f777377`, which you have

~~~bash
B=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/nebius/infra-nebius-763ea668.bundle
sha256sum "$B"                      # 33bce048...
git bundle verify "$B"
git fetch "$B" infra/nebius:refs/remotes/origin/infra/nebius
git merge origin/infra/nebius       # into the tree you submit from (keep #536 in it)
~~~

`submit.sh` still can't fetch GitHub from your side, so keep `--allow-stale`. After the merge, its diff against
`origin/infra/nebius` should be empty.

**What changed.** Each task runs its `row stage` as one `research run --tool vllm.build` / `vllm.commit` Attempt (plain argv,
`--cwd` the tree), and the Commit cites the Build's artifact.

**Proof: an Attempt in the store,** read back from R2 with `research data show <id>`, not from a log. The test cell was SmolLM2,
job 187:

- Build `r20260930-133221-34d3`: SUCCESS, tool `vllm.build`, `outputs.build = art:c39915606c1b11eb0b5159852b8d8e41a2b1f7284e4658876c5d1250e42b4c24`.
- Commit `r20260930-134308-4d11`: SUCCESS, tool `vllm.commit`, `inputs.build` = that artifact. The precheck verified its program
  digest.

**One gap, and it isn't the template's.** A config-run Commit's Attempt carries `result` and `run_files`, but no `verdict`
artifact. The integration's output writer wants a top-level `verdict.json`, and a config run writes `config_record.json` instead:

~~~text
ValueError: commit stage PASS but its decision document verdict.json is absent
~~~

I've sent it to the vLLM coordinator. The verdict is still in the row directory and in `run_files`.

**Also in this revision:** GPU tasks keep Triton and vLLM caches per tree on the host (`/workspace/jobs/cache/triton/<tree id>`).
The first cell of a tree is cold; the later ones skip Triton's JIT.

**Qwen3-30B-A3B:** rerun it on this template. Its passing cell (`cov-k16-6`, 460/460 at 13:00Z) ran `row stage` bare, so there
is no run record to backfill, and an Attempt made from the row directory would claim telemetry that was never taken.

Keep at most 2 cells waiting in Kueue.
