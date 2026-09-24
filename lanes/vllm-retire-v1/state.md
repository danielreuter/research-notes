---
lane: vllm-retire-v1
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/retire-v1
branch: lane/vllm-retire-v1 (off origin/lane/vllm-cleanup-2 = 815b837c), pushed to origin
---
# vllm-retire-v1: running state

Task: delete the v1 engine (required_manifest traversal/tables, required_values, ACQUIRE_CLASSES tables, ACQUIRE_ENGINE switch,
compiled_source v1 branch, sampled_replay v1 addressing, replay_partition v1 recompute, ENGINE=v1 paths) + prune census roots, cascade.

Baseline (staging 815b837c): 652 .py files, 209,413 lines under integrations/vllm; by-name allowlist 293.
Census: run with python3.13 (`/opt/homebrew/bin/python3.13 tests/dead_code_census.py`); python3.9 mis-parses commit_delta.py.
By-name lint: `/opt/homebrew/bin/python3.13 tests/test_no_by_name_rules.py` (pure AST, laptop-safe).

## Tip
- 6813fe06 (pushed) -- replay tests on v2 addressing

## Takeover 05:46Z (previous owner died 04:43Z)
- staging suite (815b837c) finished 05:28Z, exit=1, 42 F/E lines: /workspace/rv1/logs/suite_staging.{log,xml}
- 05:49Z launched on cpu3 (tree /workspace/rv1/tip = full git archive of 6813fe06):
  crun.sh (converted test files) -> logs/conv_tip.log; srun.sh (full suite) -> logs/suite_tip.{log,xml}

## Done
- bda6f73a: ACQUIRE_ENGINE switch, v1_decision, gate v1 compare, plan class residuals, compiled_source v1 branch,
  commit_delta class-table extension, pod_match_v2.sh + match_compare.py (root dropped).
- c517b71b: harness v2-only (resolver ENGINE/BASELINE_ENGINE, rebaseline --engine, manifest_digest v1 builder).
- 53d20e6c: required_manifest.py + required_values.py deleted; sampled_replay v2-only addressing; replay_partition recompute v2;
  tests converted (test_sampled_replay.v2_manifest helper; test_manifest_format replaces test_required_manifest). allowlist -56.
- a71869e5: cascade vu_canonical.py + 3 tests. allowlist -1.
- NOT YET RUN ON A POD since 53d20e6c: converted tests may need fixes.

## Decisions / findings
- TP rank committers (tp/worker.py make_committer) have NO acquisition plan: they select by native_host's class tables.
  => class tables + _select_modules KEPT (TP only); report as the one v1 survivor.
- verdict.py structural-leak notes name "native_host.ACQUIRE_CLASSES" / "required_manifest.members_for": left (verdict.json content).
- deleted without v2 replacement: test_sampled_replay_moe_tp_sum_copy.py (args-less v1-vocabulary fixture; v2 copy path not
  exercised by it); sampled_replay/commit_verdict still read a manifest's `cross_check` (v1-only field) -- left (follow-up).

## Next
- pod: run converted test files; fix; staging vs tip full suite; harness T0+T1 (replay_partition -> retire-v1 decision if it moves)
- roots: drop GEN-lane runners (own commit, revertable); uncertain: canary.sh
- pod vyv-v2cpu3: ramlock /workspace/ramlock/retire-v1.json
