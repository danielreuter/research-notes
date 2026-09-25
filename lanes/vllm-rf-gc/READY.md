---
id: vllm-rf-gc/ready
lane: vllm-rf-gc
kind: ready
created: 2026-09-25T18:45Z
---
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
