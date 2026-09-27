---
cursor:
  subagentId: "bc-39e42308-29c4-59bb-b889-029025de6eb8"
---

# Re-record 13 vLLM regression rows (read-only playbook)

Sources: `/workspace-wt/epoch/integrations/vllm/{tests/regression,verity_vllm/ops}`; lane notes under `internal/lanes/vllm-rf-{c4irb,b1*,b4*,b2v*,f1,f56}/`.

## 1. Row list (`tests/regression/fixtures.toml`, 13 keys)

| # | class | tp | GPU | MoE | key |
|---|---|---|---|---|---|
| 4 | FAIL | 1 | l40s | no | `smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager` |
| 11 | GREEN | 1 | l40s | no | `llama32-1b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager` |
| 23 | GREEN | 1 | l40s | no | `llama32-1b__bf16__l40s__tp1__b64__i1024__o128__mixed__greedy__bi-eager` |
| 39 | GREEN | 1 | l40s | no | `qwen25-15b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager` |
| 57 | FAIL | 1 | l40s | no | `gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager` |
| 60 | GREEN | 1 | l40s | no | `mistral-7b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager` |
| 67 | GREEN | 1 | l40s | **yes** (OLMoE) | `olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager` |
| 68 | GREEN | 1 | l40s | **yes** | `olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed-arrivals__greedy__bi-eager` |
| 70 | FAIL | **2** | l40s | **yes** | `olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager` |
| 73 | GREEN | 1 | **h100** | no | `qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager` |
| 74 | GREEN | 1 | **h100** | no | `qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager` |
| 75 | FAIL | **2** | l40s | **yes** (Qwen3-30B-A3B) | `qwen3-30b-a3b__bf16__l40s__tp2__b2__i1024__o128__mixed__greedy__bi-eager` |
| 101 | GREEN | 1 | l40s | no | `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager` |

GPU is encoded in the key (`__l40s__` / `__h100__`). Roles for `row_pod`/`tp_stage` (from `manifests/checkpoints.json` / bootstrap aliases): B0, LLAMA32_1B, B1 (→ Qwen2.5-1.5B), GEMMA2_2B, MISTRAL7B, OLMOE, QWEN3_4B, QWEN3_4B_FP8, QWEN3_30B_A3B.

## 2. One row on a pod: Build → Match → Commit

**TP1** (`verity_vllm/ops/row_pod.sh`):

```bash
bash verity_vllm/ops/row_pod.sh <row-id> <ROLE> <hf-repo> <revision> [stages=build,match,commit]
```

**TP≥2** (`tp_stage.sh`; `row_pod.sh` execs it when `WORLD>1`):

```bash
WORLD=N NCCL_P2P_DISABLE=1 bash verity_vllm/ops/tp_stage.sh <row-id> <ROLE> <hf-repo> <revision> [stages=build,match,commit]
```

**Inputs:** `workloads/<row>.json`; `manifests/checkpoints.json` → local HF snapshot under `HF_HOME` (default `/workspace/hf`, `HF_HUB_OFFLINE=1`); venv `/workspace/venv312` from `pod_bootstrap.sh`; optional `HIDDEN_SO` (FA2 matReq `.so`).

**Env (common):** `PY`/`PY312`, `SWEEP_DIR` (default `/workspace/cp/sweep`), `GPU_UTIL`, `PAIRS` (default 3), `MATCH_IMPL=fast`, `MATCH_PIPELINE=shared`, timeouts, `RESEARCH_RUN_DIR` → `result.json`. TP: `COMMIT_GPU_UTIL`, `REPLAY_WORKERS`, `FOLD_PROFILE`, `VERITY_WINDOW_*`.

**Evidence layout:** `$SWEEP_DIR/<row>/` — `stages.txt`, `row.log`, `timeline.jsonl`, `build_*` / `build/rank<r>/`, `match/`, `manifest.json`, `commit/`, `verdict.json`. Exit: 0 all PASS; 10/11/12 Build/Match/Commit FAIL; 3 precheck.

**Example (#101, b4c `tools/g1.sh`):**

```bash
cd integrations/vllm
bash verity_vllm/ops/pod_bootstrap.sh --cases B0,LLAMA32_1B --out "$OUT/bootstrap"
export HIDDEN_SO=/workspace/cp/fa2/build/matReq/verity_fa2_matReq.so SWEEP_DIR=$OUT/sweep
PAIRS=1 bash verity_vllm/ops/row_pod.sh \
  llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager \
  LLAMA32_1B unsloth/Llama-3.2-1B 9535bd9b1d1dea6acafbdc4813b728796aeb28da build,match,commit
```

**Bootstrap:**

```bash
research run --on <machine> --project verity --source <verity checkout> -- \
  bash -c 'cd integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh [--cases B0[,OLMOE]] [--out DIR] [--gpu|--cpu]'
```

(Exact f56: `research run --on vyv-rf-f56-tp2 --project verity --campaign vllm-rf-f56 --source <worktree> --stage bootstrap --cwd source/integrations/vllm -- bash verity_vllm/ops/pod_bootstrap.sh --cases OLMOE --out /workspace/bootstrap --gpu`)

## 3. `rebaseline.py` CLI

From `integrations/vllm`:

```bash
python -m tests.regression.rebaseline run   --record DIR [--oracle expected|frozen] [--tier T0,T1,T2] [-- <pytest args>]
python -m tests.regression.rebaseline table --record DIR
python -m tests.regression.rebaseline write --record DIR --commit SHA --branch B --release R [--run-id ID ...] [--force] [--dry-run]
```

**`--record DIR` layout:** `DIR/<row-key>/<check>.json` with schema `verity-vllm/regression-result/v1` (`expected`, `actual`, `problems`, `matched`, …); `run` also writes `DIR/junit.xml`.

**Where fixtures come from:** `tests/regression/fixtures.toml` (index) + `expected/<row>.json`. Resolver loads bytes via `$VERITY_REGRESSION_ROWS_ROOT/<row>/`, `[rows.*.local.*]`, then store `art:` ids in `[rows.*.artifacts]` / top-level `[artifacts]` (`store_io.fetch`). `run` does **not** need live GPU — it pytest-recomputes against those fixtures.

**`write`:** merges passing recorded `actual` into `expected/<row>.json` (shape preserved; failures refuse unless `--force`); sets `reference` to the v2 tree (`--commit/--branch/--release`); keeps prior v1 under `reference.frozen`. `--dry-run` prints only.

## 4. How prior lanes ran GPU rows

**Pod create (`create_cuda.py`):** not in repo; lane copies under `tools/` / `/tmp/…`. = `research pods create` + RunPod REST `allowedCudaVersions: ["12.9","13.0"]` (CLI has no flag). Default image otherwise: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04` (`tools/research/.../runpod.py`). Driver on good pods: **580.x / CUDA 13.0**; driver 550 + CUDA 12.4 → `BOOTSTRAP_FAIL_CUDA`. c4irb g1: “`tools/create_cuda.py` 12.9,13.0, b2v's”; f56: `/tmp/rff56/create_cuda.py` → 2×L40S, driver 580.159.04. H100 rows need **`NVIDIA H100 80GB HBM3` (SXM, 132 SMs)** — PCIe 114 SMs fails after Build (`b4` READY).

**Launch pattern (WAVE2 / c4irb / b4c):**

```bash
research run --on <pod> --project verity --custody-r2 --source <clean worktree> --cwd source -- <script or bash …>
```

Inner row: `row_pod.sh` / `tp_stage.sh` as above (older chains used `run_row_v2.sh stage build|match|commit … --retain host --sweep-dir /workspace/sweep`).

**Wall-clock (documented):**

| Row | Shape | Wall (approx) |
|---|---|---|
| #101 | 1×L40S, PAIRS=1 | Build ~2.5 min (c4irb 150 s); Commit ~191–295 s |
| #67 | 1×L40S MoE | f1: Build ~47–83 min, Match ~66 min; Commit PAIRS=3 ~2h26; PAIRS=1 Commit ~65–100 min/arm; b1c: Build 9739 s, Match 2510 s |
| #70 | 2×L40S MoE TP2 | Build ~21–23 min; Match ~20 min; Commit PAIRS=3 ~84–85 min (5062–5085 s); PAIRS=1 ~59 min (3538–3439 s) |
| #75 | 2×L40S Qwen3-30B-A3B | TP2 long; GPU_UTIL 0.92 / Commit 0.80 |

## 5. Long poles

- **#67** is the MoE TP1 long pole (Build+Match+Commit many hours; sampled replay dominates; needs ≥~180 GB for Commit).
- **#70** is the TP2 MoE long pole (~1h50 PAIRS=1 full chain; ~2.5 h with bootstrap).
- **#75** is the other TP2 MoE (larger shard).
- Gate (a) T1 `replay_partition` on B=1 rows needs **120–250 GB** (not a GPU-row re-record, but fleet long pole).
- f1: “MoE row of record is #70 … cheapest MoE by Commit cost: **84 min vs 146 min**” (#70 vs #67).
