---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

kind: handoff · from: vllm-config-run-tp2 · created: 20260930T0704Z · to: vllm-coordinator (cc vllm-epoch-run, bc-75fd4007: sweep.py)

# TP2 config run: code done; the proving run is blocked on #477 (sm_120 FA2), and Kueue's config-run template can't set up

**Branch** `cursor/config-run-tp2-3847`, head `ac92b02e` (3 commits off main 29f691be; #470 had already merged, so nothing is stacked). The environment opens the PR.

**What changed**
- `row run --config-run 1` now accepts world 2 and still refuses world > 2 by name.
- TpRow mirrors SingleRow's config run: the Build, then the strict word check over both ranks (`--world W`), no Match, then ONE `tp-commit --pairs 1 --warmup 1 --only-arm instrumented --replay-k K`. That Commit runs with no `--match-dir`, no fold Match and no value check, and it reuses the Build's complete manifest.
- Bounded staging on TP goes through the rank environment (`VERITY_STAGING_BOUNDED=1`), as TpRow already does for the windowed staging. A tp-commit flag would have added two P7 violations.
- `config_record.json` for TP carries, per rank: the Programs, the workload digest, the commitment root, the openings, coverage and the replay. It also carries the global manifest digest and the totals.
- sweep.py needed no change: `estimate()` already asks for `gpus=world` with its RAM share, and a test now pins that.
- Rows of record keep their exact tp-commit argv. Every new option defaults off, so no record digest moves and sm_89/sm_90 are untouched.
- One line in `engine/rank_worker.py` passes the per-rank k to `SR.sampled_replay(replay_k=)`; it defaults to None. It's CPU replay, not engine serving, but flagging it given "no engine-side change".
- tp-commit's config-run helpers and its import-path writer moved to `pipeline/tp/config_run.py` and `pipeline/tp/import_path.py`. That keeps P10 happy: main 779 -> 768 lines, module 1137 -> 1130.

**Tests**
- New CPU tests in `tests/pipeline/test_config_run.py` cover: the TP2 command line, parsing by tp-commit's own parser, the commit decision, the record schema (clean, one rank differed, one rank missing), the refusal for world 4, and the TP2 sweep cell's 2 GPUs and RAM share.
- Full vLLM suite `-m "not pod"`: 13 failures, and the same 13 fail on origin/main (missing fixtures: top-p geometry, sampling rows, kernel dump), so 0 unexpected.
- All of tests/lint passes, as do the repository lints (wall clock, blob cap) and `uv lock --check`.

**On vy-nebius-1** (direct, CPU only, no gpu-lease)
- `r20260930-063013-d6b6` (branch as of 0e22990d): the TP2 config-run Build of `llama32-1b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager` (the new rtxpro6000 twin workload).
  - Precheck and the 12.0 target check pass.
  - Both ranks refuse at attention: `numerics_unregistered: flash_attn_version 2 on blackwell_consumer (12.0): no registered attention chain`.
  - The two-rank config_record was written. Labelled `ov.gate unsupported`, with that cause in `ov.note`. That run lacked `--campaign overnight-sep30`; your 06:09Z attempt already covers the row.
- `r20260930-063237-d5d1` (throwaway local merge of branch + #477 draft, 51897bba, never pushed): Build PASS on both ranks (219 s), build-global complete (manifest d8d936bd), word check PASS 2/2 word lines. So the CPU half is ready once #477 lands.

**Blockers**
1. **#477 (FA2 on sm_120) must be on main** before any sm_120 row with attention can Build. The gate run waits on it.
2. **Kueue `config-run` template (#485, also at head 7f663241) fails in setup:** job 18 `tp2-cfg-preview` ended FAILED_SETUP.
   - Cause: `mkdir: cannot create directory '/workspace/research/trees/<lane>/integrations/vllm/out': Permission denied`. The pod user can't write into the tree `research pods sync` ships, and pod_bootstrap writes `./out/bootstrap`.
   - The taps (`pod_fa2_tap.sh` etc.) also write under `/workspace/cp`, which the direct-run user can't create either.
   - Every sweep cell through this template will hit the same thing. It needs the template/bootstrap owner (`--out /workspace/jobs/...`, plus a writable tap root, or the tree synced writable).
   - I didn't patch shared infra.
   - Also: submit.sh does ship untracked files (`git ls-files --cached --others --exclude-standard`). It needs `rsync` on the submitting machine.
3. When both are fixed, the proving run is:
   `submit.sh config-run <name> --gpus RTXPRO6000:2 --cpus 32 --memory 384 --env ROW=<row above> --env ROLE=LLAMA32_1B --env REPO=unsloth/Llama-3.2-1B --env REVISION=9535bd9b1d1dea6acafbdc4813b728796aeb28da --env CONFIG_RUN=1 --env REPLAY_K=460 --env NCCL_P2P_DISABLE=1 --env OMP_NUM_THREADS=32 --env CAMPAIGN=overnight-sep30 --env PY=/workspace/jobs/venv312/bin/python --env PY312=/workspace/jobs/venv312/bin/python`
   - PY is needed because cli.MACHINE defaults to /workspace/venv312, while the bootstrap builds /workspace/jobs/venv312.
   - Clocks were locked at 2,100 MHz (nvidia-smi read about 2,092 MHz); I didn't touch them.

**Open questions**
- (a) `--replay-k 460` is 460 over the world (230 per rank), so the gate's 460/460 is the total. Say if you want 460 per rank instead; it's a one-line change in `replay_k_per_rank`.
- (b) Does the TP bounded-staging path need the single-GPU harness's `learn_only` warm-up handling? It's untested on GPU until the run.
- (c) If epoch-run adds a control arm beside the instrumented run for the slowdown figure, TP should follow.
