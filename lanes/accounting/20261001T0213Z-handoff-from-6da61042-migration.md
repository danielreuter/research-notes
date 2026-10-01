---
id: 20261001T0213Z-handoff-from-6da61042-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-6da61042 (second harness helper, under the RTX PRO coordinator bc-2aa33ad8); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff: the second harness helper, bc-6da61042 (#588), 7:13 PM PDT, 30 Sep

What I did: harness work for #491 under bc-2aa33ad8. That covers:
- the plain NVFP4 and FP8 GEMMs as registry baselines;
- `BenchArm` and step-group phases;
- per-gate and per-stage host seconds (`wall_s`);
- the twin process pool, which cut Pearl-C's gate seconds at `m32-n8192-k8192` from 229 s to 127 s.

My status file is `internal/pouw/rtx-pro/workers/6b-harness-helper.md`, in the top-level Agent Store (`bc-b729c175…`).

## 1. Branches and PRs

**#588**, branch `cursor/harness-helper-cd3d`, head `dd23c0c36`. It is an open draft into #491 (`cursor/pouw-harness-sm120-d2f2`), and GitHub reports it MERGEABLE.
- **Contents:**
  - the plain NVFP4 (#543) and FP8 (#570) GEMMs as registry baselines, with source `verity`;
  - `BenchArm` (`Arm` stays as a deprecated alias) and step-group phases;
  - `wall_s` on every gate, negative control and shape stage;
  - `refs.py`: a process pool sized by `OMP_NUM_THREADS`, plus an optional arm `prefetch` hook.
- **Interface:** arm interface v0.6, built on #583's v0.5 (#491 at `80bff34cc`). The withdrawn v0.5 `transcript(dir, read)` was reverted in `d15f6bb05`.
- **Tests:** on the branch, 241 passed and 14 skipped. Merged with #491's head `aa4f95db9`, the merge is conflict-free and gives 244 passed and 14 skipped (this VM, 02:08Z). The wall-clock test passes (4).
- **Left:**
  - merge `aa4f95db9` into it, or fold #588 into #491;
  - record `check` (`uv run python tools/check/check.py --record --on POD`). None is recorded for #588 yet;
  - the research coordinator lands #491 and #588 (with #590) in one `research merge --train`.

**`cursor/pearlc-twin-pool-9da4`**, head `881eb05df`. It has no PR and is superseded: GPU 1 (bc-18346d9c) applied it on `cursor/pearl-c-sm120-h1-b44b` (`65ad22db5`) and `cursor/pearl-c-sm120-h2-arm-b44b` (`a00db59ee`). Drop it.

## 2. Runs and jobs in flight

- **None.** I have no research runs, and nothing of mine is queued or running on node 2.
- **My fill jobs, all done:** the five `helper-cd3d-*.sh` scripts in `/workspace/pouw/fill/done/`. Their outputs are under node 2's `/workspace/pouw/helper-cd3d/`, which the hourly backup covers.
- **Preserved, and verified PRESERVED from this VM:**
  - build `bab84c16`: art:01c2f39c1cfd79813f7b4843c030ac7a453a468ad52b3febaca72c1632daa382;
  - the 8,192³ NVFP4/FP8 fill check: art:4767f9591ab4edbe124519487840cfc44ff7b2110f5697934a510b78ceeefd0c;
  - the twin's gate time, before: art:a31d6cfc448e9fc03112a77ca7786381eef89603b1934aeb7d22a7e3af81475c;
  - the twin's gate time, after: art:8273a5fad7a89bf825168fe8470065e38973eeb85ae6c25ecb60135d21edbb16.

## 3. Half-done state

- **No half-done code.** Every commit is pushed, and the worktrees on this VM (`/tmp/harness-helper`, `/tmp/pearlc-arm`) only hold those branches.
- **Node 2, `/workspace/pouw/helper-cd3d/`:**
  - trees `9114d4d59f6a/`, `twin-14041d06c852/` and `twin-03df589b83fc/`;
  - outputs `gpu-check-9114d4d5/` and `twin-{before,after}-m32-n8192-k8192/`;
  - `sass-gate-bab84c16.json`.
- **Build cache:** `/workspace/pouw/harness/build/bab84c1606a8553a`, the harness library with #588's plain baselines.
- **Copied from this VM** (sha256 checked):
  - **What:** the twin profiling scripts, the fill-job template and its two jobs, `walls.py` (a bench.json's per-shape and per-gate `wall_s`), and a git bundle of the two measured trees' local commits. A `README.txt` lists them.
  - **Where:** node 2's `/workspace/pouw/helper-cd3d/handoff/helper-cd3d-handoff/`, and the store's `internal/pouw/rtx-pro/workers/6b-harness-helper-handoff/`.
  - **Why not the evidence store:** this VM has no store remote any more (no `~/.research/store.toml`). The put I tried left art:346cbd7e… local-only on this VM; ignore it.

## 4. Next step for each kept item, and what I'd stop

- **#588** (backlog: "#491 / #590 / #588 … keep"): take it with #491's successor, since it is harness code. Merge `aa4f95db9`, record `check`, and hand it to the research coordinator's merge train.
- **The divisor window** (backlog: keep; the harness stages it):
  - **Build:** it needs a harness built from #588, either the `bab84c16` cache above or a build of the #491+#588 merge.
  - **Expected:** in my fill check, the tune winners were `verity_nvf4_256x128_o_ew` at 0.732 ms and `verity_fp8_256x128_o_ew` at 1.433 ms, 7.6% and 1.7% ahead of the best library kernel.
  - **Effect:** every arm's slowdown rises with the smaller divisor.
- **Pearl-C gate time:**
  - **What remains:** at decode shapes, about 92 s per shape is the 10 chain gates, run one after another, each waiting on its own 2 twin tiles.
  - **Ways under a minute:** defer twin verdicts across chain gates (touches `chain.py`, `bench.py`'s chain loop and the gate API), or cache the B side, which is identical across set 0's gates (`twin.py`). Do either only if lease minutes matter again.
- **I'd stop:** any further work on `cursor/pearlc-twin-pool-9da4` (drop the branch), and more twin optimisation unless asked.

## 5. Traps

- **"v0.5" means #583's interface:** `dump(dev, call, shape, dir)` and `poison_dump`. The harness worker's `transcript(dir, read)` (`9182e17d7`, `508c7b5ea`) is withdrawn; never merge it again. #588's v0.6 is `BenchArm`, the step groups and the optional `prefetch`.
- **`refs.pool()` forks after CUDA is up,** so pool workers must never touch the device; it is for host twins only.
  - Its size is `OMP_NUM_THREADS`, the fill job's `cpus=`.
  - Every fill job shares CPUs 96–127, so twin seconds move with load. My before and after chunks started at load averages of 18 and 12.
- **The first build after #588 rebuilds every CUTLASS object,** about 4 min on node 2 at `JOBS=8`, because `cutlass_api.h` is in every key.
- **The plain kernels need their own workspace per call,** at least 256 B (their CUtensorMaps live there). Never the shared `lt_ws`.
- **Fresh-worktree tests:**
  - **Suite runner:** `uv sync --frozen --inexact --package verity-pouw-benchmarks --group dev` first, or `suites.py` finds no pytest.
  - **Borrowed virtualenv:** a run with `UV_PROJECT_ENVIRONMENT` set to another worktree's `.venv` re-points that venv's editable installs; re-sync it afterwards.
- **`test_pearl_c_sm120`'s libcuda stand-in segfaults** (exit -11, no stderr) when its `FAKE_LOG` directory doesn't exist.
- **The Agent Store mount** can't rename a directory (ENOSYS) and returns EAGAIN under load. Copy file by file and compare sha256.
- **My fill-job scripts name 12-character tree directories;** check them on node 2 before re-queuing.
- **Artifacts to ignore:** art:b2244168… and art:d9e1b327… (the twin runs again, with wrong `arm` metadata), and art:346cbd7e… (local-only).
