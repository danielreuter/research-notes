---
id: 20261001T0215Z-handoff-from-e6a46970-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-e6a46970 (GPU 0, FP8 tensor-core capture on sm_120, node 2 vy-nebius-2); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff: GPU 0, the FP8 tensor-core capture on sm_120 (bc-e6a46970), 7:15 PM PDT, 30 Sep

What I do: measure and check the sm_120 FP8 tensor-core step (E4M3, E5M2, mixed, chains, 2:4 sparse) against the registered
models, and price instructions in W1 units (`w1.py`) for the theory lane. My status file, with every result, run line and lesson,
is `internal/pouw/rtx-pro/workers/0-fp8-capture.md` in the top-level store `bc-b729c175…`. Every path below is node 2's unless it
says the store.

## 1. Branches and PRs

- **#492, `cursor/sm120-fp8-capture-75d4`, head `7aa3abf63`** (pushed; origin matches). Open draft. No recorded `check` of this
  head. 36 commits ahead of `main`, 608 behind; 27 files, about 11,400 lines, nearly all under `tools/tc_probe_fp4/`:
  - `w1.py` and `w1_prices.cu`: the W1 price microbenchmarks;
  - `fp8.py`: the step, chain, sparse, mixed, cvt and fadd rows, each split into a GPU phase and a CPU phase;
  - `fp8_check.cu` and `fp8_gpucheck.py`: the step model on the GPU, with its gate and fill phases;
  - `tool_fp8.py`: the tool declarations (`W1_PRICES`, `TC_PROBE_FP8`, `TC_PROBE_FP8_GPUCHECK`);
  - the tests, including `tests/test_fp8_gpucheck.py` (13 tests, passing at `7aa3abf6`).
- **Its base is dead.** #492 stacks on #487 (`cursor/vllm-sm120-fp8-probe-422d`), which is **closed, unmerged** (head `7cef262f`,
  "the sm_120 FP8 target moves to the registry PR"). That registry PR, #502 (`cursor/sm120-fp8-registry-422d`), is closed too.
  `main` has no `BLACKWELL_SM120_E4M3_M16N8K32`, and #492's code and tests import it. The open #630
  (`cursor/proofs-fp-defs-95d4`, "sm_120 FP8 / FP4 step Definitions … in one PR") looks like where the models live now. I haven't
  checked that it carries the same names.
- **What's left:**
  1. Retarget #492 onto `main` once the models land (rebase onto #630, or carry #487's model commits).
  2. `uv run python tools/check/check.py --record --on vy-nebius-2`.
  3. A merge train.

  Optionally, split it into three PRs: W1 prices, the `fp8.py` rows, and the GPU check. The backlog's view is "keep: the evidence
  behind γ and the divisor".

## 2. Runs and jobs in flight

**No research run is in flight.** All 34 recorded runs my status file cites on node 2 have custody (`.custody`
`"preserved": true`). These include today's gate, `r20260930-221543-8564` (`art:64ca059f…`), and its failed first try,
`r20260930-221312-3234`. The two runs `r20260930-060217-6c89` and `r20260930-060227-9825` were compile-only runs on my VM (CUDA
12.9), and my VM has since been reset. They are superseded by the preserved `r20260930-062059-dc4d`.

**Fill jobs.** All are mine (owner `bc-e6a46970-b6ef-5738-af64-182b143075d4`), all were queued before the ruling, and nothing of
mine is running now.

| jobs | what | state at 02:06Z | ends | outputs (node 2) | custody |
|---|---|---|---|---|---|
| `fp8gc-die0.sh` … `fp8gc-die7.sh` (`gpus=1 on=<d> prio=10 max_min=8`) | the GPU check's GPU half: 5 units per die (E4M3, floor-aimed E4M3, E5M2, mixed E4M3×E5M2, K = 2^20 chains), fresh seeds 20264000 + 100d + k | **done**, all exit 0, 23:39Z–00:26Z; 60 chunks, **5.11 GPU-h** (Measured, the runner's minutes) | – | `/workspace/pouw/fill-out/fp8-gpucheck/die<d>/<unit>/L_*.npz` (78 launch files per die, 98 GB in all), `plan.json`, `gpu.log`, `gpu.done` | none: fill outputs. Node 2's hourly backup of `/workspace/pouw/` (per bc-2aa33ad8's handoff), unchecked at 98 GB |
| `fp8gcver-die<d>-<unit>.sh`, 40 jobs (`gpus=0 max_min=30 cpus=4 mem_gb=48`) | the CPU re-check of each unit: kept set = hash sample + flagged tiles; the operand port; per-tile counts; flags; the negative control | **queued, none started** (0 `V_*.json` anywhere) | Estimated about 17 CPU core-hours in all (93 CPU-s per 1.07e9-tile launch, Measured on my VM). 4 workers per job, so about 4.3 slot-hours: about 1–1.5 h of wall with all 4 pous CPU slots, much longer at one slot | the same unit dirs: `V_<launch>.json`, `unit_verify.json`, `verify.log` | none: small JSON, preserve by hand once passed |
| `fp8ver2-die0.sh` … `-die7.sh` (`gpus=0 max_min=20`) | the second fill's step-capture CPU verify; 107 of 128 units have passed | queued; each requeues with 99 after about 7 min | Estimated about 8 min of work per die left | `/workspace/pouw/fill-out/fp8-capture2/die<d>/<unit>/probe_results.json` | none |
| `fp8chainver-die2.sh` … `-die7.sh` (`gpus=0 max_min=30`) | the second fill's chain CPU verify (die 0 and 1 passed) | queued | about 28 min per die (Measured on dies 0 and 1) | `/workspace/pouw/fill-out/fp8-chain/die<d>/*/probe_results.json` | none |

- These 54 CPU jobs are most of the 64 CPU jobs queued at 02:05Z. None of mine has started since 21:39Z.
- I start nothing new. Whether the queued ones may still run is the successor's call. To stop them, move them from
  `/workspace/pouw/fill/queue/` to `withdrawn/`.
- The GPU check's gate already compared the GPU model with the CPU model bit for bit on all 159 units of the second fill, with 0
  mismatches. So those 14 old verify jobs add the CPU's own verdict, not a new check of the model.

## 3. Half-done state a successor needs

- **My VM:** it was reset to `main` before 02:04Z, so nothing exists only there. The fill's job generator survives as
  `/workspace/pouw/fill-out/fp8-gpucheck/jobs/mkjobs.py`, with the verify jobs' 4 workers and 48 GB. The status file is in the
  store.
- **Node 2:**
  - `/workspace/pouw/fill-out/fp8-gpucheck/build/`: the gated `libfp8_check_sm_120a.so` (sha256 `d70ec7fb…`), with
    `SHA256SUMS`, `PROVENANCE` and the SASS dump.
  - `/workspace/pouw/fill-out/fp8-gpucheck/jobs/`: the 8 GPU jobs, the 40 verify jobs, `mkjobs.py` and `plan_summary.json`
    (per-unit sizes and estimates). `fp8gc-canary-die2.sh` is withdrawn; it ran on my VM instead and passed.
  - `/workspace/pouw/fill-out/{fp8-capture,fp8-capture2,fp8-chain}/`: the earlier fills' outputs.
  - The source trees the jobs `cd` into: `/workspace/research/src/7aa3abf638bc…` (the GPU check), `bf77c948…` (the chains) and
    `9d5abb09…` (the step captures). **Keep them until the verify jobs finish.**
  - The gate run's dir, `/workspace/research/runs/r20260930-221543-8564/`, holds `timing.json` and the smoke launches.
- **The store:** `internal/pouw/rtx-pro/workers/0-fp8-capture.md` is mine. Its 22:55Z checkpoint, the Results entry "The FP8 step
  check on the GPU" and the "Fill jobs (third fill)" section are current. Its header and Needs predate the GPU half's end, which
  this file supersedes.

## 4. Next step per kept item, and what I'd stop

- **#492 (kept: the evidence behind γ and the divisor):** retarget onto `main`, then record `check`, then a train (section 1).
- **The GPU check's fill (5.11 GPU-h done):**
  1. Let the 40 verify jobs run.
  2. Read each unit's `unit_verify.json`. A pass means `validation` is `passed`, `primary_gated_beyond_control` is 0, and
     `negative_controls_flagged` equals `negative_controls`.
  3. Sum the totals: about 7.8e11 tiles (1.0e14 words) were checked on the GPU, and 1.67e8 kept tiles (2.1e10 words) are
     re-checked on the CPU.
  4. Put the results in the status file's Results, labelled Measured.
  5. Preserve the small files of every unit (`plan.json`, `V_*.json`, `unit_verify.json`, `gpu.log`) with
     `research data put --tree … --preserve`.

  After a pass, the 98 GB of launch files could be deleted; that's the successor's call.
- **The second fill's verifies:** let them finish, then record 128/128 step and 31/31 chain units in Results.
- **Stop:**
  - Don't queue more FP8 GPU fill until the CPU half catches up. At this sample, each GPU-hour costs about 3.3 CPU core-hours to
    re-check (Estimated), and pous has 4 CPU slots.
  - Don't port `cvt` and `fadd` onto the GPU check unless asked.
  - Treat the Fill candidates table in the status file as optional.

## 5. Traps

- **#492's base PR is closed** (section 1). Its tests fail on `main` until the sm_120 FP8 models are there.
- **Pous CPU is 4 slots on cores 96–127, at nice 19.** The runner picks by `prio`, then by how many jobs the owner has running,
  then by the oldest file. So my old `fp8ver2` jobs go before the 40 new ones, and a `prio=10` CPU job from anyone goes before
  all of them. CPU jobs don't start while a timed window is on.
- **Fill-verify memory:** one worker peaked at 6.1 GB on a 261,193-tile launch (Measured). E5M2's launches keep 1.6× as many
  tiles (about 9.5 GB, Estimated). The runner's `MemoryMax` is `mem_gb`, so keep workers × peak under it.
- **`research run` passes argv without a shell,** so `--out '$RESEARCH_RUN_DIR'` arrives literally. `fp8.py`, `w1.py` and
  `fp8_gpucheck.py` (since `7aa3abf6`) expand it themselves.
- **Never pass `--timeout`** (it extends the machine's lease). Never probe or flock `/run/gpu-lease/*.lock`; read `status.txt`
  and the `.owner` files instead. Never build with `-ftz=true` or `--use_fast_math`: the SASS gates reject `.FTZ`.
- **A fill job that exits anything but 0, 99, 75, 124 or 143 is retried once.** So a lease child writes its exit status to a file
  and the job exits 0 (`w1.fill_lease`). A chunk that exits 99 is requeued immediately.
- **"Fresh seeds" are fresh draws from fixed tables:** the operand code tables are pinned at `TABLE_SEED` 20261001 per (kind,
  family).
- **After a VM reset:**
  - There is no `~/.research`. Clone `danielreuter/research-notes` to `~/.research/notes`; then the workspace venv's
    `research pods ssh vy-nebius-2` works, resolving the machine from the clone's `machines.d/`, with `RUNPOD_SSH_KEY_B64` in
    the environment.
  - `/cursor/stores/self` may point at the agent's own empty store, not `bc-b729c175…`.
  - The store mount returns "Resource temporarily unavailable" for minutes at a time; retry.
- **A notes push gets a 403 that names `cursor[bot]`.** The VM's `~/.gitconfig` rewrites `https://github.com/` URLs to the bot's
  credential (`url.….insteadOf`), and the bot can't write to `research-notes`. Push to `https://x-access-token@github.com/danielreuter/research-notes.git`,
  which isn't rewritten, with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=credential.helper` and a helper that prints
  `password=$RESEARCH_NOTES_TOKEN`. That keeps the token out of every config file and log.
- **`TC_PROBE_FP8_GPUCHECK` isn't in the shared tools registry.** Runs load it by import path
  (`--tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8_GPUCHECK`).
