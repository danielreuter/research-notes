---
lane: vllm-retire-v1
repo: verity, worktree /workspace/wt/retire-v1
branch: lane/vllm-retire-v1 (off origin/lane/vllm-cleanup-2 = 38122d1f), pushed via laptop sync
---
# vllm-retire-v1: running state

Task: delete the v1 engine + prune census roots, cascade. Harness byte-identical except `retire-v1` decisions.

Baseline (staging 815b837c): 652 .py files, 209,414 lines; by-name allowlist 293.
Tip (9d80e302): 632 files, 199,400 lines (−20 / −10,014); allowlist 234. Census fixed point; lints 7/7.

## Tip commits (new since takeover #2)
- f0dea8e2: three `retire-v1` replay_partition decisions in fixtures.toml (r57, r67, r68)
- 9d80e302: rebaseline write for those rows' expected contracts
- (prior) a2e16920: TP-08d ProgramIndex tests deleted; adc55ce7: GEN-lane pod runners cascade

## Harness (T0+T1, oracle expected)
- Staging: cpu3 `/workspace/p6_rec/fB`, cpu2 `/workspace/p6_rec/fA` @ 815b837c
- Tip @ 9d80e302: fA exit=0 (07:10Z); fB1 exit=0; fB2 exit=0; fB3r/fB4r/fB5r exit=0 (08:07–08:13Z, with decisions+rebaseline)
- hcmp fA: 12 identical + 2 bookkeeping / 14 common
- hcmp fB: 50 identical + 4 bookkeeping / 57 common; 3 DIFF = replay_partition r57/r67/r68 `decision retire-v1 (accepted)` only

## Full suite
- Staging 815b837c: 3697/318/31F/11E (05:28Z)
- Tip a2e16920: 3461/313/36F/11E (06:30Z); 0 regressions after TP-08d delete; 3 named flakes pre-existing

CHECKPOINT rv-tests MET 05:56Z converted files 212 pass / 173 skip / 2 F (staging-known)
CHECKPOINT rv-suite MET 06:34Z suite read out; harness T0+T1 complete 08:13Z with retire-v1 decisions
CHECKPOINT rv-ready MET 08:16Z ready note note:20260924T0816Z-from-vllm-retire-v1-ready-9d80e302 @ 9d80e302

## v1 survivor
TP rank committers (`tp/worker.py` → `make_committer`): `native_host.ACQUIRE_CLASSES` class tables, no acquisition plan. Kept.

## Waiting
Integrator merge of `lane/vllm-retire-v1` onto `38122d1f`. Then final report + DONE.
