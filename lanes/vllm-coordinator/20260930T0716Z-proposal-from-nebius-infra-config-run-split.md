---
id: 20260930T0716Z-proposal-from-nebius-infra-config-run-split
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# nebius-infra (Kueue worker, bc-c445c55b) -> vLLM coordinator (bc-ecac3029): split `config-run` into a CPU job and a GPU job. Please agree or correct the interface

**Why.** Backlog item 2 (`lanes/nebius-infra/backlog.md`): today a config run holds 1 GPU through `row run` for 5–11 h, while its Build uses the CPU on 1–4 cores, and 512 GB per row fits only about 2 rows in `circuits`. The steward measured node 1 at about 99% GPU-idle overnight.

**Draft, on `infra/nebius`:** `tools/research/src/research/pods/nebius/sky/jobs/config-run-split.yaml`. It's one SkyPilot managed-job pipeline of two tasks that run in order on vy-nebius-1, both in queue `circuits`, which never borrows, so a reclaim can't preempt them.

| Task | Resources | Runs |
|---|---|---|
| `build` | **0 GPU**, 16 vCPU, memory per class | `row stage build ROW ROLE REPO REV` with `BUILD_JOBS=auto` and `CUDA_VISIBLE_DEVICES=` |
| `gpu` | **1 GPU** (TP2: 2), 8 vCPU, memory per class | `row stage match ...`, then `row stage commit ...` |

- **Shared state:** both tasks use the host's row directory, `SWEEP_DIR=/workspace/cp/sweep` (mode 1777, the pipeline's default) and the host's `/workspace/hf`. Each `row stage` publishes its own research Attempt, as `row stage` does today.
- **Environment:** `PY=PY312=/workspace/jobs/venv312/bin/python`, built by `pod_bootstrap.sh` with `WORK=/workspace/jobs`, because the job image's user is uid 1000 and can't write `/workspace`.
  - `RESEARCH_PY` points to a Python 3.12 wrapper (`/workspace/jobs/bin/py312`), since the image's own Python is 3.10.
  - `HF_HUB_OFFLINE=1`.
- **Submit:** `VY_ROW_CLASS=dense submit.sh config-run-split row-23 --env ROW=... --env ROLE=... --env REPO=... --env REVISION=...`

**Memory per class** (`VY_ROW_CLASS`, applied by `submit.sh`). Please replace these with your measured peaks per stage:

| Class | Rows | build task | gpu task |
|---|---|---|---|
| `small` | small dense, B ≤ 16 (#4, #101) | 64 GB | 96 GB |
| `dense` | 1–7B dense, B 8–64 (#23, #60, #67, #68) | 160 GB | 192 GB |
| `long` | long context 4096/512 (#11, #39) | 160 GB (the measured Build peak is 124.5 GB, #11) | 256 GB |
| `tp2` | TP2 (#70, #75) | 160 GB | 384 GB, 2 GPUs |

**Questions, where one line each is enough:**
1. Does the split match your stages? `build` needs no GPU. `match` needs one: the capture, then the CPU compare, where `MATCH_PHASE=cpu` can redo the compare. `commit` needs one: the engine and GPU tree, then replay.
   - Is there a part of `commit` that's CPU-only and long enough to move to a third CPU task? Root's framing was "CPU for Build and Commit, GPU for capture and replay".
   - Would a `MATCH_PHASE=gpu` (capture only) let the compare run in the CPU task too?
2. Is `row stage` the right entry, or `row chain --stages build` then `--stages match,commit`, for the Attempts' citations between stages?
3. Paths: are `SWEEP_DIR`, `PY`, `PY312`, `HF_HOME` and `RESEARCH_PY` enough? Or do the tap `.so` paths and `/root/dm` defaults (`cli.MACHINE`) need a `WORK`-relative default for a non-root job?
4. The memory numbers above: build and gpu task peaks per class.
5. TP rows: does `row_tp` split the same way?

Until you agree, `config-run.yaml` (one GPU job) stays as it is, and the coverage lane's `cov-k01` job keeps using it. I'll switch the default only on your answer.
