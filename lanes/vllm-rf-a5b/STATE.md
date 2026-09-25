---
id: vllm-rf-a5b/state
lane: vllm-rf-a5b
kind: state
updated: 2026-09-25T14:25Z
---
# a5b (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-a5b`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

**a5b succeeds a5** (agent bc-95dc5f40, hung at the 12:30Z host disconnect). Agent bc-a9b686f7; coordinator bc-ba6cec03.
Start commit **`09511c5f`** (`origin/wip/vllm-rf-a5-0705` = a5's pushed head `1452248c` + its two uncommitted test edits).
Worktree `~/projects/verity-wt/rf-a5b`, branch `lane/vllm-rf-a5b` (pushed). **a4 base: 10996616** (a4 not in main at 14:10Z).
Budget: what remains of a5's $35 (a5 spent ~ $14 by 14:15Z, estimated from pod hours). Deadline 2026-09-25T17:00Z.

## Commits
- a5's (on `lane/vllm-rf-a5`, all in my history): see `../vllm-rf-a5/STATE.md` plus `92d71b31` research Tools run
  `verity-vllm row stage`, `b44628d7` row_pod.sh / tp_stage.sh / run_row_v2.sh deleted, `8a9ea9d5` census keep-list,
  `5eff5c2e` cli argv, `1452248c` `verity_vllm.LLM` + README; `09511c5f` coordinator's WIP snapshot (2 test edits).

## Recovered from a5's pods (14:10Z)
- Gate 1 at `1452248c` (cpu, `r20260925-120411-8670`): lints/tools logs `/workspace/a5/logs/head-1452248c-*` on vyv-rf-a5-cpu.
- Gate (b) head `1452248c` vs base `10996616` (same cpu pod; base `r20260925-114039-ede8`): 6 new failures
  (/tmp/a5-cpu.txt): source_identity x2 and test_lint[cli.py] (fixed by `09511c5f`), plus
  weights_of_record CLI argv, release_json run as a file, run_config_dry_run index. No new skips.
- g1 `r20260925-120741-6922` (at `1452248c`): LLM example verity vs vllm-same greedy+sampled EQUAL (6 requests);
  vllm-plain died (`ninja` not on PATH: venv bin missing from PATH). OLMoE tp1 b1 i256 o32 greedy (head, `verity-vllm row stage`)
  build/match/commit rc 0 in `/workspace/sweep/olmoe-1b-7b__...__b1__i256__o32__...`; base side not yet run.
- tp2c (rjwxvl6f54ywo9): bootstrap `r20260925-121500-ed35` BOOTSTRAP_FAIL_CUDA (driver 550 = CUDA 12.4);
  cuda-compat-12-9 installed but `CUDA unknown error`. **Drained/terminated 14:20Z.**
- t1 (cyu8vao39x21th, 32 vCPU / 755 GB): bootstrap `r20260925-121213-3f2d` SUCCESS at `1452248c`; nothing else run.

## Running
- Poller `~/.research/notes/lanes/vllm-rf-a5b/tools/tp2-poll.sh` (laptop pid 53615, log /tmp/a5b-tp2-poll.log): 2x L40S
  with CUDA >= 12.9, registers `vyv-rf-a5-tp2d`. None available at 14:18Z.

## Next
1. Fix the 3 remaining gate (b) failures; commit, push.
2. cpu: gate 1 + gate (b) at new head vs base xml already on the pod. t1: prefetch + gate (a) T0+T1.
3. g1: LLM vllm-plain with PATH fixed + compare; OLMoE b1 base side (A/B). 4. #70 when a TP2 pod appears.

## Open questions
- (a5's) b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; keep the signature. b2v: `verity-vllm verdict from-record|mapping` lives in `pipeline/verdict_record.py`.

## Found, not fixed
- none yet
