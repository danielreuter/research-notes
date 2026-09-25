---
id: vllm-rf-gc/ready
lane: vllm-rf-gc
kind: ready
created: 2026-09-25T18:45Z
updated: 2026-09-25T22:45Z
---
# gc2 READY: gate (b) in a git checkout; veritor-era file tests retired; G4c fixed

branch `lane/vllm-rf-gc2` @ `a0ec1083` (from 270b0de2; merged origin/main 7da00370 at 0c49886a), base `7da00370`.

## Gates (pod vyv-rf-gc2-cpu, cpu3g 32 vCPU, sequential; script `evidence/gate_b2.sh`)
Tree under test = `git clone` of `$RESEARCH_SOURCE_SHA` from the pod's bare repo `/workspace/research/git/verity.git` (fed by
`research run`'s git transport), checked file-for-file against the shipped tree (less research's READY.json). PYTHONPATH adds
`protocols/sampled_proofs` (PR #29 gap; bootstrap fixed on main at fee32f05, this pod predates it).
| side | run | lints | gate (b) |
|---|---|---|---|
| base 7da00370 | r20260925-205634-fe83 | rc 0 | 41 F / 3727 P / 287 S / 6 xf / 11 E (4072) |
| head a0ec1083 | r20260925-205636-fd0a | rc 0 | 35 F / 3729 P / 286 S / 6 xf / 11 E (4067) |
jdiff rc 0: 0 new failures, 0 new skips, 0 outcome changes; 7 only-in-base (the retired tests below), 2 only-in-head (renames, pass).
Evidence: `evidence/gc2-jdiff-head-a0ec1083-vs-base-7da00370.txt`. All runs preserved on R2.

**Bootstrap gap it would have hidden** (unfixed base r20260925-202807-da6a, same tree, no sampled_proofs on PYTHONPATH):
72 F / 3291 P / 286 S / 46 E. Against the fixed base, 472 outcome changes: 35 files error at collection (about 437 tests never run:
all of `check/test_sampled_replay*`, `commit/test_challenge`, `commit/test_production_vectors`, `commit/test_binding_*`,
`check/test_prescribed_input_linkage`, `pipeline/test_admit_r19_host_working_set`, ...) and 31 tests fail (`check/test_weights_of_record*`
23, `pipeline/test_tp2_*` 5, `test_oracle_compare`, `test_challenge_seeds`, `test_running_example`). Per-file list:
`evidence/gc2-bootstrap-gap-unfixed-vs-fixed-base.txt`. A comparison with the gap on both sides would have looked clean.
Round 1 (base 270b0de2 / head 6f95928a, runs r20260925-185947-d8fe / r20260925-190114-7dc1) predates gc on main: its only jdiff
flags were the gc-freeze pair (order-dependent, fixed by gc's 301ce7dc); superseded.

## Decisions, with evidence
- **test_source_identity x4: not skipped.** They pass on both sides in the git clone (base 52 F+E includes none of them). `6f95928a`
  documents in the test's docstring that REPO must be a git checkout and how to get one on a pod. The pytest command is unchanged;
  WAVE2's gate (b) text should add the tree preparation: "run from `git clone <root>/git/verity.git T && git -C T checkout
  $RESEARCH_SOURCE_SHA`, not the shipped tree" (coordinator-owned file, not edited by me).
- **pod_release.sh (`0a043f11`): retired.** Not in the tree; replaced by research run/pods. Product code mentions it only in comments
  (`rg -n pod_release --glob '!tests/**'`: hot.py, release_json.py, row_stages.py, ops/*.sh comments). Deleted
  `test_release_json::test_pod_release_sh_writes_through_the_module_and_checks` and `::test_pod_release_busy_pattern_...`;
  `test_native_jit_keying::test_pod_release_fails_closed_on_a_stale_so_and_records_the_digest` keeps its `release_json.parse_artifacts`
  assertions as `test_release_json_records_the_collector_source_digest`.
- **ship.sh + out/gen/r17/sparse-patterns.txt (`1c6efa53`): retired.** Neither in the tree; `ship.sh` only in comments
  (experiment.py, native_jit.py, native_collect.py, dense_generic.py, weights_of_record.py, pod_hidden_gpu.sh); `sparse-patterns` no
  hit outside tests. Deleted `test_ship_roots::test_ship_roots_name_out_gen_hf_configs`, `::test_r17_sparse_patterns_re_include_hf_configs`,
  `::test_ship_pack_carries_out_gen_hf_configs` (skipped without ship.sh). `test_tracked_hf_configs_are_the_roles_the_profiles_read` stays.
- **out/gen/cards/SCHEMA.md (`1ec0c565`): retired, not migrated.** Only docstrings name it (`pipeline/report.py:6`, `check/gates.py:73`);
  nothing opens it. The card JSON roundtrip stays as `test_card_json_roundtrip`.
- **G4c (`a0ec1083`, from b5vc):** `ROOT` derives from `verity.ir.__file__` = `packages/verity/src`, where the four `verity_vllm` files
  don't exist, and the loop skipped missing files: it checked nothing. It now reads them from `integrations/vllm` (all four exist,
  0 literal hits, passes) and fails if one is missing. Outcome unchanged (pass -> pass), now meaningful.

## Found, not fixed (G4b follow-ups, same stale ROOT in `tests/program/test_harden_guards.py`)
- `EVIDENCE = ROOT/out/gen/r10/cb-fix/evidence/fix` never exists (veritor path): G1-G4b skip "recorded evidence ... not present"
  (10 skips). Either migrate that evidence or retire those checks.
- `DERIVE_STEP = ROOT/verity_vllm/pipeline/build.py` is wrong (should be the integration's `verity_vllm/pipeline/build.py`); G4b
  (`xfail(strict=True)`) never reaches it because `_load("base")` skips first. Fixing EVIDENCE without DERIVE_STEP turns G4b into an
  error, and its xfail reason still names `derive_step.py`.
- G5 (`HARDEN_LIVE=1` only) builds `PYTHONPATH={ROOT}:{ROOT}/vllm-poc:{ROOT}/src`, `cwd=ROOT`: veritor layout, broken when enabled.
- `test_artifact_applicability_independent.SOURCE_ROOTS` still names `verity.ir` (from gc).
- Pods bootstrapped before fee32f05 need `protocols/sampled_proofs` on PYTHONPATH (research coordinator's fix is on main).

## Pods, spend
vyv-rf-gc2-cpu (2a6r9033cmk5vg) terminated 22:39Z after all runs were preserved. Spend about $4.84 (18:52-22:39Z at $1.28/h), cap $6.

---
# gc (first round, merged): record below
# gc READY: gate (b) test-side fixes (successor of gb)

branch `lane/vllm-rf-gc` @ `f2599a27` (3 test commits + merge of origin/main `2603dfcc`), base `38a8d35d`.
`2603dfcc` over `38a8d35d` touches only `backends/numerical` (not on the gate (b) path).

## Gates (same pod vyv-rf-gb-cpu, cpu3g 32 vCPU, one after the other; script `evidence/gate_b.sh`)
| side | run | lints | gate (b) |
|---|---|---|---|
| base 38a8d35d | r20260925-165445-d918 | rc 0 | 51 F / 3668 P / 287 S / 6 xf / 11 E |
| head f2599a27 | r20260925-165502-2bc9 | rc 0 | 45 F / 3674 P / 287 S / 6 xf / 11 E |

jdiff (`baseline-jdiff.py`, sha 363304c0): 4023 tests on both sides, 0 only-in-one-side, 6 outcome changes, all failed -> passed;
**0 new failures, 0 new skips, rc 0** (`evidence/jdiff-head-f2599a27-vs-base-38a8d35d.txt`). XMLs: in the runs (R2, preserved) as
`gate_b-base38.xml` / `gate_b-head.xml`.

## What changed (test files only)
- `0b54b584` (gb's WIP 176d3bff): `_adapter_fn` in `tests/observe/test_gen_sampling.py` + `tests/engine/test_gen_ov_sampling.py` also execs
  `execution_of_workload`, which `load_workload` calls. Fixes 4 (incl. `test_cov_difr_b0`, which reuses `_adapter_fn`).
- `301ce7dc`: autouse fixture in `tests/pipeline/test_admit_r19_host_working_set.py` unfreezes a gc heap left frozen by an in-process vLLM
  engine earlier in the worker (`EngineCore.__init__` -> `freeze_gc_heap()`), refreezes after. Fixes 2.
- `79206954`: `test_applicability` / `test_artifact_applicability_independent` put `packages/verity/src` on the build subprocesses'
  PYTHONPATH (was the integration tree only -> `No module named 'verity'`). No outcome flips on a CPU pod: the builds now get past the
  import and stop in vLLM's platform detection (`RuntimeError: Device string must not be empty`, CUDA wheel + `CUDA_VISIBLE_DEVICES=""`
  on a GPU-less host). On a GPU pod (the docstring's host) the import error is gone. Keep or drop; it is outcome-neutral here.

## Deliberately not changed
No product code, no deleted/skipped/weakened test, `load_workload` untouched, no allowlist change. `test_source_identity` and the
missing-file tests were left failing rather than skipped (a skip is a "new skip" in jdiff).

## Remaining 56 failures/errors at head, triage
- **Need a GPU host (env), 30:** `test_applicability` (11 E, base build has no result.json) and `test_artifact_applicability_independent`
  (19 F): vLLM `DeviceConfig` finds no platform on a CPU pod.
- **Files never migrated from veritor (tree), 6:** `tests/sweep/pod_release.sh` (`test_native_jit_keying`), `verity_vllm/ops/pod_release.sh`
  (2 in `test_release_json`), `out/gen/cards/SCHEMA.md` (`test_gates_fixtures`), `record_v5/ship.sh` + `out/gen/r17/sparse-patterns.txt`
  (2 in `test_ship_roots`). Owner decision: migrate the files or retire the tests.
- **Pod tree has no `.git` (tree/gate procedure), 4:** `test_source_identity` (`repo_root_of` -> None, precheck cannot compare a sha).
  Fix options: run gate (b) in a git checkout, or skipif-not-a-checkout (precedent: `test_ship_roots`, `test_relayout_map`) -- coordinator's call.
- **Product, 1:** `test_research_tools::test_closure_covers_every_core_file`: `research_tools.CLOSURE` misses `verity/evaluation/**`.
  Changing it changes store derivation keys (invariant), so not touched.
- **Product/host, 1:** `test_compiled_source::test_renumber_assigns_invocations_per_call_site`: `compiled_source._record` calls
  `torch.cuda.is_current_stream_capturing()`, which raises on a CUDA-runtime host without a driver.
- **CPU-host numerics / host facts, 11:** 4 `test_derive_realhf` + 4 `test_derive_hf5b_realhf` (torch-CPU mismatch / digest prefix),
  `test_twins` (extra `openmp` library), `test_norm_chain::test_mean_pins_match_installed_vllm` (pinned vLLM source not found, empty sha),
  `test_sampling_rows` nv_logf NaN sign.
- **Model expectations (product), 3:** untied `lm_head`: 2 `test_gen_ov_easy`, `test_derive::test_s3_untied...`.
- **vLLM sampler pattern (product), 1:** `test_patterns_synthetic::test_gumbel_two_stage_sampler_is_one_token_select`.
All 56 fail or error identically at base (a1's baseline.md lists the same causes at 72884c8a).

## Found, not fixed
- `research_tools.CLOSURE` lacks `packages/verity/src/verity/evaluation/**` (hot-Commit / TP keys never see those files).
- `SOURCE_ROOTS` in `test_artifact_applicability_independent` still names `verity.ir` (veritor layout; absent, skipped by copy_tree).

## Pods, spend
vyv-rf-gb-cpu terminated at READY. New spend about $3.1 (16:21-18:47Z at $1.28/h), cap $5.
