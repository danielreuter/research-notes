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
- adc55ce7 (pushed) -- GEN-lane roots dropped (own revertable commit); census fixed point; allowlist 234, lints 7/7 on pod
- 6813fe06 (pushed) -- replay tests on v2 addressing (suite + harness runs are at this sha; adc55ce7 touches no harness code)

## Takeover 05:46Z (previous owner died 04:43Z)
- staging suite (815b837c) finished 05:28Z, exit=1, 42 F/E lines: /workspace/rv1/logs/suite_staging.{log,xml}
- 05:49Z launched on cpu3 (tree /workspace/rv1/tip = full git archive of 6813fe06):
  crun.sh (converted test files) -> logs/conv_tip.log; srun.sh (full suite) -> logs/suite_tip.{log,xml}
- 05:52Z harness T0,T1 (oracle expected) @ 6813fe06, split like the integrator's staging run (p6 hrun.sh):
  cpu3 fB: serial run killed at 06:00Z (staging fB was 2h12m serial: manifest_digest + replay_partition on r74/r73/r68/r67);
  relaunched 06:01Z as 5 row groups fB1 "r74", fB2 "r73 or r101 or r4 or r70 or r75", fB3 "r68 or r60", fB4 "r67 or r23",
  fB5 "r57 or negative_57 or decisions_are_listed" -> /workspace/rv1/hrec/fB<k>, logs/h_fB<k>.out, locks retire-v1-harness-fB<k>.json
  compare: /workspace/rv1/hcmp.py STAGING_REC TIP_REC --skip program_digest (bookkeeping keys source/seconds/manifest reported apart)
  cpu2 fA "r11 or r39" -> /workspace/rv1/hrec/fA, log /workspace/rv1/logs/h_fA.out (lock retire-v1-harness-fA.json); ssh /tmp/rv1ssh2
- staging harness to compare against (815b837c, T0,T1,T2): cpu3 /workspace/p6_rec/fB, cpu2 /workspace/p6_rec/fA (integrator's)
- converted test files @6813fe06 (cpu3, logs/conv2_tip.{log,xml}): 212 pass / 173 skip / 2 F, both F on staging's list
  (test_norm_chain::test_mean_pins_match_installed_vllm, test_compiled_source::test_renumber_assigns_invocations_per_call_site);
  skips environmental (157 VERITY_REGRESSION-gated, CUDA, real Programs). vs staging junit per test (jcmp.py): 0 pass->fail,
  0 pass->skip; 25 v1-comparison tests gone, 14 new/renamed pass. No fixes needed.

- counts (git cat-file, = wc -l; reproduces the 209,413 baseline): 815b837c 652 files / 209,413 lines -> adc55ce7 632 / 199,445 (-20 / -9,968)
- test_repository.py 6/6 on laptop @adc55ce7; allowlist 293 -> 234

- harness partial 06:14Z: fA 6/6, fB3 6/6, fB5 6/7 byte-identical to staging. MOVED: replay_partition r57 (gemma2-2b b8):
  4150 Bf16MulScalarTensor_v1 rows evaluable under the v2 rule (vus 651982->656132, strata_n 5846->5883, draw/lifetime follow).
  proof probe: staging code's check with the record's addresses.rule forced to "v2-query" vs tip actual
  (/workspace/rv1/rpv2.sh ROW TIPREC -> logs/rpv2_r57.out). If equal -> retire-v1 decision + rebaseline write for that row/check.

- 06:21Z probe: staging code under v2 rule == tip actual for r57 replay_partition: True (solely the rule).
  retire-v1 decision added to fixtures.toml (r57 replay_partition; uncommitted until the rerun passes by decision);
  06:26Z rerun `replay_partition and r57` on tree /workspace/rv1/tip2 (tip + decision) -> hrec/rp57, logs/h_rp57.out
  then: rebaseline write --record hrec/rp57 (pod, tip2) -> copy expected/<gemma row>.json back -> commit + push

CHECKPOINT rv-tests MET 05:56Z converted test files @6813fe06 on cpu3: 212 pass / 173 skip / 2 F (both staging-known), 0 regressions per test vs staging junit

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
