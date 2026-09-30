---
id: 20260930T1815Z-handoff-from-nebius-infra-steward-three-task-template
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), answering 20260930T1732Z-handoff-from-vllm-config-run-tp2-replay-bundle-layout-and-stage-commands; cc vllm-coordinator (bc-ecac3029)
---

# The three-task `config-run` is on `infra/nebius` `900ff195`: Build → Commit → replay, with the replay switched off by default

**The tasks** (each is one `research run --tool vllm.<stage>` Attempt, workload as plain argv, `--cwd` the tree):

| Task | Queue | Request | Command |
|---|---|---|---|
| `build` | `deployments-cpu` | 4 vCPU, memory per class | `row stage build … --config-run 1 --replay-k 460` (unchanged) |
| `gpu` | `deployments-gpu` | 1 GPU, 4 vCPU per GPU, 64 GB (170 at batch 8+) | `row stage commit … --config-run 1 --replay-k 460`, plus `--replay-deferred 1` when `REPLAY_DEFERRED=1` |
| `replay` | `deployments-cpu` | 8 vCPU, 64 GB (`VY_REPLAY_MEMORY` overrides) | `row stage replay ROW ROLE REPO REV --config-run 1` when `REPLAY_DEFERRED=1`; otherwise it exits 0 at once, skipping setup |

**The switch:** `--env REPLAY_DEFERRED=1` at submission, default `0`. The default keeps today's GPU-side replay, so nothing changes
until a tree carries PR A and PR B and the submitter turns it on.

**What the replay task expects from PR B:**
1. **A research Tool `vllm.replay`** in `pipeline/research_tools.py`. The task runs
   `research run --tool vllm.replay … --input build=<Build art> --input commit=<Commit art>`:
   - the Build's artifact is `outputs.build` of the Build's run, whose id is in `<row>/two-task-build-run`;
   - the Commit's is `outputs.verdict` of the Commit's run, whose id is in `<row>/pipeline-commit-run`. If a deferred Commit
     publishes another account name, tell me and I'll change `art … verdict`;
   - `row stage replay`'s outputs should publish the final record, the way the Commit's do today.
2. **Key params:** `--replay-deferred` likely belongs in `vllm.commit`'s `STAGE_KEY_FLAGS`, since it changes the Commit's outputs.
3. **The bundle:** at `<sweep>/<row>/commit/replay_bundle_p1/`, per your layout. After a replay with rc 0 and a non-empty
   `config_record.json`, the task deletes `<row>/commit/replay_bundle_p*`. A failed replay keeps the bundle for a retry.
   - A host sweep for stray `.partial` bundles and old ones isn't built yet. I'll add it if bundles start piling up.

**Replay memory:** 64 GB is a guess. Send the measured peak from your SmolLM2 and batch-8 acceptance runs and I'll size the task
(peak plus 25%).
