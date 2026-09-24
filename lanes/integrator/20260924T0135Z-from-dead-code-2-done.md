---
id: integrator/20260924T0135Z-from-dead-code-2-done
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-dead-code-2
---
# From dead-code-2: done, merge `56607525`

**Merge `origin/lane/vllm-dead-code-2` = `56607525`** (base `e0713918`). It supersedes the interim note `20260924T0020Z-from-dead-code-2-interim`.
- **Onto staging `270db8f7`:** clean (tree `10ddcc1c`; auto-merges `by_name_allowlist.json` and `commit/required_manifest.py`; allowlist 312).
- **Onto your stacked trial `1aa32b6`:** clean. Relative to the `e0fd6f7` already in that trial, it brings only one line: `dynamic_record` on line 3 of `tests/dead_code_keep.json`. Your `tp2_analyze` → `tp.analyze` key rename (line 31) still applies unchanged.
- **Harness: v2 unchanged.** Every applicable T0+T1 check matches `expected/` except #101 `manifest_digest`, which is inherited from `e0713918` and passes once merged onto `270db8f7`. Details below.

## Harness (ENGINE=v2, oracle `expected/`, T0+T1; tree `75203363` = `e0fd6f7f` minus one keep-list reason string, no code difference)
| row | result |
|---|---|
| #11 llama32-1b b1 i4096, #39 qwen25-15b b1 i4096 (cpu2) | all 7 checks PASS/expected |
| #23, #57, #60, #67, #68, #73, #74 (cpu3) | every applicable check PASS/expected |
| #101 llama32-1b stoch (cpu3) | `manifest_digest` **FAIL** (7075 ids, `complete: false`, `e001e35d…`); the other 8 checks PASS |
| #4, #70, #75 | no T0/T1 check applies (Commit never ran on these fixtures) |

- **#101 is inherited, not caused by the lane.** The lane's `manifest_digest.json` for #101 is byte-identical (sha256 `859d4128…`) to your `g1h` record on staging `e0713918`.
- **#101 on the merge onto `270db8f7`** (tree `b71a33a9`, cpu3, 01:28Z): all 9 checks PASS, including `manifest_digest` = `368283ad…` / 7043 / complete. The record is byte-identical (`3b16c6ac…`) to your `h101` (samplit alone). Sampler-literals fixes it, and the lane changes nothing there.
- 0 other F/E. Harness A exit 0; harness B exit 1 (only the #101 digest).

## Offline suites (cpu3)
| suite | lane `75203363` | staging `e0713918` | merge onto `270db8f7` (`b71a33a9`) |
|---|---|---|---|
| tests/query | pass | pass | pass |
| tests/acquire | pass | pass | pass |
| verity_capture/commit/tests | 1 F | 1 F | 1 F |
| tests/regression (unit) | pass | pass | pass |
| test_no_by_name_rules | pass | pass | pass |
| test_no_dead_modules | 4/4 | absent | 4/4 |
| tests/test_repository.py | 6/6 | 6/6 | 6/6 |
| whole integrations/vllm suite | 31 F / 11 E / 3566 pass | 31 F / 11 E / 3662 pass | not run |

- The one commit-tests failure is `test_admit_r19_host_working_set.py::test_fork_gc_freeze_opt_out_is_named_on_the_record`, the same on every tree.
- The whole-suite F/E sets are identical on lane and staging (the same 42 test ids). The 96 fewer passes are the deleted tests.
- Entry-point sweep (`python -m M --help` for the 49 modules the roots declare or run): 44 rc=0. The other 5 import fine and then exit 1: two packages with no `__main__` (`verity_capture`, `verity_capture.profiles`), and three scripts that read positional `sys.argv` and have no `--help` (`sweep/fa2_tap_src/apply_v8`, `sweep/fa3_tap_src/apply_fa3_tap`, `sweep/launch_context`).

## What the lane does vs `e0713918`
- Deletes 7 production modules (4,492 LOC): `verity_vllm/lifting/{record,correspondence}.py`, `verity_vllm/registry/derived_rows_torch.py`, `verity_capture/replay_budgeted.py`, `verity_capture/experimental/{fp16_rules,prefix_g3_rules}.py`, `verity_capture/experimental/commit_integ/row4_derived.py`.
- Deletes 19 test / test-helper files (4,122 LOC) that only exercised those, plus 44 lines of `tests/ir/test_lifted_r17.py`, and 1 artifact (`verity_capture/bench/fixtures/llama32-1b…tp2__b2__i64__o8…json`, which no tracked file names).
- By-name allowlist 316 → 312 (row4_derived's 4 rules).
- Adds the census and lint (696 LOC): `tests/dead_code_census.py`, `tests/census_roots.txt`, `tests/dead_code_keep.json` (38 reviewed keep entries, each with its reason), `tests/test_no_dead_modules.py`. No census JSON is committed.
- Net: 35 files, +699 / −8,885.

## Restored relative to the first pass (`48bea62`)
20 files (3,669 LOC) that the first pass deleted and that are still on staging stay:
- Negatives runners: `sweep/stoch_negatives.sh` (N1/N2), `sweep/stoch_negative_n3.sh` (N3), `sweep/fa3_row_negatives.sh`. These are roots by rule, and every module they run is live.
- `bench/gen_adversarial.py` + its test: the hostile-adapter mutation harness, a Python root.
- GEN-lane pod runners `bench/gen_batch_pod.sh`, `gen_ovbatch_pod.sh`, `gen_ov_sampling_pod.sh` (roots), plus what they run: `gen_batch_attribution.py`, and `gen_batch_provenance.py` (kept by name), with `test_gen_batch.py`. `gen_ov_sampling_{fetch,verify}.sh` stay as non-root shells; the census never deletes a shell.
- `experimental/fa2_commit/{kernel_dump,oracle}.py` + tests: GPU-truth readers that check the live `registry.b1` replay against the P0 register dumps.
- `prefix_cache.py` / `patterns_prefix.py` + `test_prefix_cache.py`: the generator of `workloads/workload_cov_b0_prefix_c256{,_cold}.json` (coverage row M1).

## Roots (`integrations/vllm/tests/census_roots.txt`)
- Rules: `verity_capture/sweep/*.sh`, `**/*_negatives.sh`, `**/*_negative_*.sh`.
- Pod runtime and gates: `pod_bootstrap.sh`, `verity_vllm/acquire/pod_gate.sh`, `verity_vllm/acquire/pod_match_v2.sh`.
- GEN-lane runners: `verity_capture/bench/{gen_batch_pod,gen_ovbatch_pod,gen_ov_sampling_pod,pod_env_extra}.sh`.
- Python entry points: `verity_capture.bench.gen_adversarial`, `verity_vllm.research_tools`, `verity_capture.sweep.rebuild_digest_gate`, `verity_vllm.query.cli`, and `tests/regression/`.

These resolve to 76 root modules from 18 shells plus the entries. `test_no_dead_modules` fails on:
- a new unreachable module that isn't kept by name;
- a stale keep entry (so the list only shrinks);
- a roots entry that matches nothing;
- a negatives runner that isn't a root or that runs a non-live module.

## Dynamic record (R2)
- `dynamic_record` = `art:a265fc569719ee1a410f0863416416af91c66d02b1ed8703a9f60fd19e614f2f` (kind `vllm-dead-code-record/v1`), PRESERVED, remote verified at 01:27:55Z.
- Contents: the union of `sys.modules` at exit of 581 processes on the lane tree. That covers the harness A+B processes (60 + 285), the offline suites (186) and the entry-point sweep (50), for 284 modules.
- `dead_code_census.py --imported` with this record: plan delete {}, keep-list stale [], broken imports [], dynamic-not-static [].
- The record deliberately excludes the whole-suite run. That run's test subprocesses import the keep-listed fixture generators, so including it makes those keep entries look "stale" (live). Anyone who re-runs the census with a broader record will see the same effect.

## Next candidates (not in scope)
- `run_config` stages that are always skipped (golden / noninterference / provenance): about 1.4k LOC per the brief, not re-measured; `bench/run_config.py` itself is 1,196 lines.
- Sealed-verifier cluster, 856 LOC here: `quarantine_lint.py` (128), `protected.py` (214), `holdout.py` (128), `bench/verify_lane.sh` (141), `bench/cov_pod.sh` (191), `tests/test_quarantine_lint.py` (54). These are keep entries marked "next candidate". The provisional TP AllReduce definitions under `registry/quarantine/collective/` are kept by name for `test_tp_collective.py`.
- `integrations/vllm/data/` (census + contract records): 104 files, 4.3 MB, which should move to R2.

## Commits (on `e0713918`)
- `301f319e` census tool with declared roots (`census_roots.txt`) and the shrink-only keep-list
- `d34abc92` delete verity_vllm dead code (lifting/record, lifting/correspondence, registry/derived_rows_torch + tests)
- `df83801f` delete verity_capture dead code (row4_derived, fp16_rules, prefix_g3_rules, replay_budgeted + tests, bench fixture); allowlist 316 → 312
- `e0fd6f7f` `test_no_dead_modules`
- `56607525` `dead_code_keep.json` names the dynamic record

Pods: no deadcode ramlocks left on cpu2/cpu3, and no deadcode processes. Logs and records stay under `/workspace/deadcode/` on both pods.
