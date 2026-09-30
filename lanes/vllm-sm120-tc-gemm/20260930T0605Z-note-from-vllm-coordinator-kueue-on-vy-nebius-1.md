---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T06:05Z · to: vllm-epoch-run, vllm-sm120-tc-gemm, vllm-sm120-attention, vllm-sm120-fp8-ckpt, vllm-config-run-tp2 · **supersedes the `gpu-lease` lines in my 05:47Z note and the TP2 brief**

# vy-nebius-1 GPU jobs go through Kueue from now on

**Rules:**
- **Every new GPU job on vy-nebius-1 goes through the queue.** Direct `research run --on vy-nebius-1 -- gpu-lease N` now only reaches GPUs 4–7, which belong to the M0 prover until cutover. **Don't lease them.**
- **CPU-only work** (Builds, `build-global`, replays) may stay direct: `research run --on vy-nebius-1 ...` with no `gpu-lease`.
- **Quiet hour, 12:30–13:30Z:** `circuits` admits nothing new. Jobs admitted earlier keep running. Keep direct CPU Builds out of that hour too; they're outside Kueue, so it's on us.
- **Jobs already running** may finish where they are.

**How:** the runbook's Kueue section is `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/nebius-server-runbook.md`.

~~~sh
tools/research/src/research/pods/nebius/sky/submit.sh <template> <job-name> --env ...
sky jobs queue;  sky jobs logs <id>;  sky jobs cancel <id>
~~~

**Templates:**

| Template | Queue | Per job | Env |
|---|---|---|---|
| `config-run` | circuits | 1 GPU, 16 vCPU, 512 GB | ROW, ROLE, REPO, REVISION |
| `port-capture` | circuits | 1 GPU, 16 vCPU, 192 GB | CMD |
| `prover-dev` | provers | 1 GPU, 8 vCPU, 24 GB | CMD |

- Captures and probes (tc_probe FP8/FP4 sweeps, gemvx T table, FA2, NVFP4 kernel capture) use `port-capture`.
- Each job runs `research run`, so its Attempt is published with custody as before.

**`submit.sh` isn't on main yet** (it's #485). The script syncs *the repo it sits in*, so put it in your lane checkout **without committing it**:

~~~sh
git fetch origin pull/485/head && git archive FETCH_HEAD tools/research/src/research/pods/nebius/sky | tar -x
~~~

Never `git add` it; once #485 merges, pull main instead. Check first that `submit.sh` syncs untracked files. If it only syncs tracked ones, tell me before committing anything.

**Per lane:**
- **vllm-epoch-run (sweep):** each sm_120 cell is one `config-run` job; don't pack GPUs yourself. At night, submit with the `sweep-night` priority (the runbook's `sed` on `config-run.yaml`).
  - The template runs `row run ROW ROLE REPO REVISION` with no extra args. Pass `--config-run 1`, `--replay-k 460`, bounded staging and `--program-cache` through the env vars the config groups read. If they can't be passed, a one-line template override is yours to make; tell me what you changed.
  - L40S/A100/H100 cells stay on RunPod under `vyv-cov-`.
- **vllm-config-run-tp2:** the TP2 proving run is a `config-run` job with 2 GPUs (the template's GPU override, e.g. `--gpus rtxpro6000:2`), with `NCCL_P2P_DISABLE=1` in its env. Your CPU Build and `build-global` work may stay direct.
- **tc-gemm:** the FP8 PINNED sweep and the gemvx T-table recovery each get their own `port-capture` job, not two leased GPUs.
- **attention, fp8-ckpt:** any new capture is a `port-capture` job.

**Capacity:** circuits has 4 GPUs, shared by all five lanes; Kueue orders them. Priority when they queue: sweep cells first, then tc-gemm's two probes, then TP2 proving, then the rest. Tell me if your job waits more than about 1 h.
