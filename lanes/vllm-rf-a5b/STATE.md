---
id: vllm-rf-a5b/state
lane: vllm-rf-a5b
kind: state
updated: 2026-09-25T14:25Z
---
# a5b (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

> **Coordinator, 14:27Z: the vyv- pod deadline is now 2026-09-25T18:30Z (11:30 AM PT)**, extended in steps of at most 4 h while the coordinator runs. It replaces every earlier deadline line in this file.

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

- `da9e4847` (pushed) the last 3 gate (b) failures: weights-of-record provenance test runs the CLI's process path and
  asserts the base's argv (flags only); release_json test runs `verity-vllm release-json` as a child process (row_pod.sh
  and pod_release.sh, its file-as-script callers, are gone) and its docstring usage lines say so; dry-run resolve index 3 -> 4.

## Done
- **Gate 1 + gate (b) at `da9e4847`** (cpu `r20260925-142039-11a3`, same pod as base `r20260925-114039-ede8`): lints 49/0,
  tools 11 passed; base 4001 (56F/3642P/286S/6xF/11E) vs head 4024 (54F/3667P/286S/6xF/11E); jdiff: **0 new failures,
  0 new skips, 0 new skip reasons**, 2 fixed (test_admit_r19_host_working_set x2), 40 only-in-base (deleted row_pod/ops
  tests and renames), 63 only-in-head all pass. `evidence/gate_b/`.
- **LLM example** (g1, `r20260925-142335-a597` head + `r20260925-142811-0998`): verity vs vllm-same (vllm.LLM with the
  recorded engine kwargs + env flags) greedy and sampled **EQUAL** (6 requests each); vs vllm-plain (defaults, only
  `VLLM_USE_FLASHINFER_SAMPLER=0` because the pod's nvcc 12.4 can't JIT FlashInfer's sampler) DIFFERENT (batch invariance
  etc. off), informational. RESULT PASS.
- Prefetch on t1: 26 ok / 0 FAIL, key deleted 14:35:58Z.

## Running (14:45Z, all `--custody-r2`)
- t1 `r20260925-142613-7113`: gate (a) T0+T1 serial at `da9e4847`, jdiff vs a23b's same-pod base XML
  (`/workspace/a5/logs/gate_a-head-da9e4847.*`).
- tp2d `vyv-rf-a5-tp2d` (7ttcomioru1z6o, 2x L40S driver 580, $2.18/h?, created 14:30Z): bootstrap `r20260925-143357-a45c`.
  Then #70 `KEEP_GOING=1 ab_row.sh head /workspace/sweep <#70> ... --retain host --pairs 1` and b4's cmp70.py vs f1's base
  Commit of record (`commit70-base-head.tgz`, staged in /workspace/a5).
- g1 `r20260925-142335-a597` (head `da9e4847`): LLM verity vs vllm-same greedy+sampled EQUAL again (6 requests);
  vllm-plain failed: the pod's nvcc is 12.4, too old for FlashInfer's sampler JIT (`--compress-mode`).
- g1 `r20260925-142811-0998` (base tree `10996616`, worktree `~/projects/verity-wt/rf-a5b-base`): vllm-plain with only
  `VLLM_USE_FLASHINFER_SAMPLER=0` + compare, then OLMoE b1 base side `ab_row.sh base /workspace/sweep-base ...`.
- Poller `tools/tp2-poll.sh` (background, log /tmp/a5b-tp2-poll.log): 2x L40S with CUDA >= 12.9 -> `vyv-rf-a5-tp2d`.

## Next
1. Compare OLMoE b1 head (/workspace/sweep) vs base (/workspace/sweep-base) on g1: program, manifest, run root, verdict.
2. jdiff gate (b), gate (a). 3. #70 via `verity-vllm row` when a TP2 pod appears (~2 h of pod time). 4. READY.md.

## Open questions
- (a5's) b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; keep the signature. b2v: `verity-vllm verdict from-record|mapping` lives in `pipeline/verdict_record.py`.

## Found, not fixed
- none yet
