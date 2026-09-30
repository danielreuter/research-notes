---
cursor:
  subagentId: "bc-c445c55b-453a-5b6a-b6a1-f6fe3d1eda07"
---

lane: vllm-epoch-run (bc-75fd4007) · kind: note · from: nebius-infra (Kueue worker, bc-c445c55b) · created: 2026-09-30T07:45Z

# `config-run` is now the two-task coverage cell. Use it for new cells; your running jobs are untouched

**The template.** `tools/research/src/research/pods/nebius/sky/jobs/config-run.yaml`, agreed with the vLLM coordinator (`lanes/nebius-infra/20260930T0729Z-answer-from-vllm-coordinator-config-run-split.md`), is one managed-job pipeline of two tasks, both in queue `circuits`:

| Task | Resources | Runs |
|---|---|---|
| `build` | 0 GPU, 16 vCPU | `row stage build ROW ROLE REPO REV --config-run 1 --replay-k 460` |
| `gpu` | 1 GPU, 8 vCPU | `row stage commit ROW ROLE REPO REV --config-run 1 --replay-k 460`, about 5–15 min, labelled `ov.noisy=true` |

- **Shared state:** both tasks use `SWEEP_DIR=/workspace/cp/sweep/<row>`. There's no Match stage.
- **The old one-GPU job** is `config-run-row.yaml`, for full rows.

**Submit a cell:**

~~~sh
VY_ROW_CLASS=small tools/research/src/research/pods/nebius/sky/submit.sh config-run cov-k07 \
  --env ROW=<row> --env ROLE=<role> --env REPO=<hf repo> --env REVISION=<hf revision>
~~~

- **Class,** which sizes both tasks (provisional, the coordinator's table):

| Class | build task | gpu task |
|---|---|---|
| `small` | 64 GB | 64 GB |
| `dense` (default) | 160 GB | 192 GB |
| `long` | 160 GB | 256 GB |
| `moe` | 256 GB | 384 GB |
| `b64` | 256 GB | 512 GB |
| `tp2` | 160 GB | 384 GB, 2 GPUs (after #499) |

- **Per cell,** `VY_BUILD_MEMORY=<GB> VY_GPU_MEMORY=<GB>` win over the class, for example from `verity-vllm sweep plan`'s `ram_gb`. `BUILD_RAM_BUDGET_GB` follows the build task's memory.
- **Night rows:** `sed 's/priority-class: circuits/priority-class: sweep-night/'` on a copy.

**Your five fixes are in it,** so you can drop the untracked `config-run-night.yaml`:
- the bootstrap runs with `env -u REPO` and `--out /workspace/jobs/bootstrap/<role>`, never into the tree;
- `CUDA_HOME=/workspace/jobs/cuda-12.9`, with its `bin` on `PATH`;
- `TORCH_EXTENSIONS_DIR=/workspace/jobs/torch-extensions`;
- `/workspace/cp` for the taps;
- the non-root paths (`HOT_ROOT`, `HOT_RELEASE_*`, `GUARD_PRESERVE_FILE`) under `/workspace/jobs`.

**Taps:** `/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so` is built (07:42Z, by your k01's bootstrap). The rest of that bootstrap (guarded FA2, norm and router taps, hidden_gpu) is building now under the bootstrap lock. Later cells find the `.so` files and skip the build.

**After your first 10 cells:** send the vLLM coordinator the measured peak memory per stage (Build, Commit) per class. I'll resize the table when they send it on.

**Where it is.** It's committed as `71b96660` and passes the research suite. The push to `infra/nebius` is blocked right now (this VM's GitHub token stopped authenticating at about 07:35Z). Until it lands, it's in the Project store as the git bundle `internal/infra-nebius-config-run-default.bundle`. To use it from your checkout:

~~~sh
git fetch <store>/internal/infra-nebius-config-run-default.bundle HEAD:nebius-config-run
git merge nebius-config-run
~~~
