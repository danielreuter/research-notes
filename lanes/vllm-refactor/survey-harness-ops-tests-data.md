---
id: vllm-refactor/survey-harness-ops-tests-data
lane: vllm-refactor
kind: survey
status: in-progress
created: 2026-09-24
checkout: f0810a11 (lane/vllm-cleanup-2)
slice: integrations/vllm/{verity_vllm/harness, verity_vllm/ops, tests, data, fixtures, manifests, docs, workloads, tools, pyproject.toml, conftest.py, README.md}
---
# Survey: harness/, ops/, tests/, top-level data, packaging

This is a read-only survey of `/Users/danielreuter/projects/verity` at `f0810a11`. No Python or tests were run. The evidence comes from `rg`, `git ls-files`, `git check-ignore`, `wc`, `find`/`ls`, and reading files.

Paths are relative to `integrations/vllm/` unless they start with `packages/` (Verity core, `packages/verity/src/verity/`) or `tools/research/` (the repo-level runner at `<repo>/tools/research/`). `harness/` means `verity_vllm/harness/` and `ops/` means `verity_vllm/ops/`.

(Sections are appended as each module group is finished.)

## Slice size

| Part | Files | Lines / size | Notes |
|---|---:|---:|---|
| `verity_vllm/harness/` | 25 modules (+2 empty `__init__`) | 12,986 lines | 20 modules end in `__main__`, 19 build an argparse CLI |
| `verity_vllm/ops/` | 16 `.sh` + `known_roots.json` | 3,338 + 51 lines | `row_pod.sh` alone is 1,147 lines |
| `tests/` | 281 `test_*.py` (+ 38 other `.py`) | 74,187 `.py` lines | 48 non-Python files; `regression/fixtures.toml` is 14,412 lines |
| `data/` | 7 dirs, 104 files | 4.3 MB | |
| `fixtures/` | 4 dirs, 19 files | 4.9 MB | |
| `manifests/` | 7 files | 196 KB | |
| `docs/` | `docs/data/ref-prims/` only, 31 files | 164 KB | nothing else under `docs/` |
| `workloads/` | 132 JSON | | 97 row-grammar ids + 35 legacy `workload_*.json` |
| `tools/` | 3 files | 599 + 1,240 lines + 1,229-line map | one-shot relayout tooling |
| `pyproject.toml`, `conftest.py`, `README.md` | 3 | 36 / 46 / 173 lines | |

---

## 1. `harness/` (25 modules, 12,986 lines)

**What it does vs. its name.** The name, and README.md:86-90 ("the development harness … Never: Verity semantics -- a check that lives here is misfiled"), suggest a leaf layer of dev drivers. In practice `harness/` holds the **production row pipeline of record**:
- **Build:** `derive_step`.
- **Match driver:** `run_config`, which runs 19 stages and spawns 9 check/observe modules.
- **Commit and the verdict inputs:** `commit_delta`, which pulls 15 imports from `check/` (`commit_verdict`, `executed_prefix`, `sampled_replay`, `oracle_compare`) and 17 from `acquire/`.
- **Engine reuse:** `hot_commit`.
- **Admission planning:** three modules.
- **Provenance and precheck:** `source_identity`, `target_family`, `release_json`.
- **Telemetry:** `timeline`, `spans`.
- **Research-runner adapter:** `research_tools`, `research_outputs`, `research_result`.
- **Workload generators:** `workload`, `coverage_workloads`.

It is also **not a leaf**. Eleven lower-layer modules import it at 17 sites:
- `tp/` imports `make_committer`, `baseline_state`, `run_workload`, `class_coverage`, `assert_pristine` and `git_head` from `commit_delta`, plus `read_tp_links` and `same_module_path` from `derive_step`.
- `acquire/native_host.py` imports `spans` and `source_identity`.
- `observe/m1_capture.py` imports `timeline`; `observe/prefix_cache.py` imports `coverage_workloads`.
- `check/global_match.py` and `correspondence/batch_decomp.py` import `gc_tuning`.
- `input_provenance/weights_of_record.py` imports `experiment`.

### Modules

| module | lines | job | run by / imported by |
|---|---:|---|---|
| `commit_delta.py` | 3,030 | Commit stage of record. It measures Δ_commit over control/treatment pairs, commits every required value through the native collector, builds the binding record, openings, live C2 oracle-compare and sampled replay, and assembles the verdict components. It is also a committer factory for `tp/`. | `row_pod.sh` (4×), `canary.sh`, `compiled_commit.sh` (2×), `fa3_row_negatives.sh`, `hot_commit`; imported by `tp/worker.py`, `tp/commit.py` |
| `telemetry/admission.py` | 1,198 | Advisory host-memory plan written before Build (`$D/admission.json`), plus post-hoc comparison of the plan with observed telemetry in two file formats | `row_pod.sh:237` |
| `run_config.py` | 1,196 | Match driver: 4 GPU stages (`capture`, `control`, `census`, `nonint`) and 15 CPU stages (`resolve` … `gates`), card, laptop RSS watchdog, snapshot-cap derivation | `row_pod.sh:564`, `cov_pod.sh`, `verify_lane.sh` (2×), `stoch_negatives.sh`; re-invokes itself |
| `derive_step.py` | 719 | Build: `torch.export` of the pinned vLLM model class on meta, then derive the step/request Program; writes descriptor, instance sequence, input trace, derive report, construction manifest | `row_pod.sh` (7×), `tp_stage.sh`, `stoch_negative_n3.sh`; imported by `tp/match.py`, `tp/fold_match.py`, `tp/rank_match.py` |
| `hot_commit.py` | 684 | Long-lived worker that serves consecutive Commit jobs on one vLLM engine keyed by (code, native extensions, env, engine args), plus the submit client | `row_pod.sh` (`HOT_ENGINE=1`); `commit_delta.__main__` reroutes to it when `VERITY_HOT_SUBMIT=1` |
| `card.py` | 641 | "Configuration card" JSON (`verity-gen/card/v1`) summarising one run directory | `run_config` |
| `admission_planner.py` | 621 | "ONE conservative resource planner" for a Commit launch, plus post-run calibration | `commit_delta.py:1778`, `:2936` |
| `synthetic.py` | 457 | numpy toy model and capture that exercise the harness without vLLM | 2 tests only (`dead_code_keep.json`) |
| `compiled_merge.py` | 448 | Merges the control-only and treatment-only `commit_delta` outputs of an `Execution=compiled` row into one paired summary | `compiled_commit.sh`; test runs it by path |
| `workload.py` | 435 | Deterministic workload generator for the R12 sweep (`workloads/<row>.json`) | hand-run CLI only |
| `topp_split_probe.py` | 430 | GPU probe that generates the TopP split-geometry fixture | hand-run (`dead_code_keep.json`) |
| `coverage_workloads.py` | 424 | Generator for `workloads/workload_cov_*.json` (coverage campaign) | hand-run; imported by `observe/prefix_cache.py` (3×) |
| `timeline.py` | 393 | Append-only `timeline.jsonl` of stage start/end events per attempt (path in `VERITY_TIMELINE`), plus report/collect CLI | `row_pod.sh`, `tp_stage.sh`; imported by `observe/m1_capture.py`, `commit_delta`, `hot_commit` |
| `experiment.py` | 355 | Index that keeps a run directory's four records apart; `code_version()` | `run_config`; `input_provenance/weights_of_record.py:912` |
| `admission_bound.py` | 314 | Host-retention bound of a `--retain host` Commit from the declared workload | `commit_delta.py:1722`, `admission_planner.py:52` |
| `research_outputs.py` | 288 | Typed `outputs.json` of one stage for the `research` store | `run_row_v2.sh` (2×) |
| `research_tools.py` | 283 | `research` Tool declarations (`vllm.build/match/commit`), row-id parser, argv→params parser | `tools/research/src/research/store/tools_registry.py:26-28` (under a different module name, see LAYERING) |
| `release_json.py` | 232 | `RELEASE.json` writer/reader for a shipped worker package | `row_pod.sh`, `tp_stage.sh` |
| `target_family.py` | 207 | Preflight that checks the row id's device token against the visible GPU's compute capability | `row_pod.sh` (2×), `tp_stage.sh` |
| `source_identity.py` | 199 | Precheck that `verity`, `verity_vllm`, `research` and `hidden_gpu` resolve from this tree; a thin wrapper over `research.telemetry.source_identity` | `row_pod.sh:142`, `tp_stage.sh`; `acquire/native_host.py:1392` |
| `rebuild_digest_gate.py` | 130 | Re-derives a recorded row's Programs with the current frontend and compares digests | **nothing**; only listed in `tests/census_roots.txt:36` |
| `research_result.py` | 114 | `result.json` for the `research` runner | `row_pod.sh:85`, `tp_stage.sh` |
| `launch_context.py` | 87 | Launch context of each request shape (feeds `derive_step --launch-max-seqlen-q`) | `row_pod.sh`; imported by `derive_step` |
| `spans.py` | 60 | Per-component wall-clock accounting for commitment | `acquire/native_host.py:54` only |
| `gc_tuning.py` | 39 | Cyclic-GC thresholds for the analysis processes | `run_config`, `check/global_match.py:2132`, `correspondence/batch_decomp.py:894` |

Tests exist for 22 of the 25 modules. `compiled_merge` is tested only as a subprocess. `research_result`, `spans` and `rebuild_digest_gate` have no test.

## 2. `ops/` (16 shell scripts, 3,338 lines + `known_roots.json`)

**What it does vs. its name.** "Pod operations" undersells it: `ops/` is the **de facto public API** of the integration.
- `row_pod.sh` orchestrates the whole row. It invokes 19 distinct `python -m` modules 34 times and reads 45 caller-settable environment variables.
- It also contains 255 lines of Python in 12 heredocs plus 24 `python -c` lines. The Match verdict itself (`row_pod.sh:686-800`, 113 lines) lives in a heredoc, which is why 12 test files regex-extract blocks from shell scripts.
- `tp_stage.sh` is a second row runner, and `canary.sh`, `compiled_commit.sh`, `cov_pod.sh` and `verify_lane.sh` are further stage runners, each with its own preamble.
- The scripts disagree on the Python interpreter. They default to three different venvs (`venv312` ×7, `venv-cu129` ×6, `venv-py312` ×3), while `pod_bootstrap.sh:34` creates only `venv312`.

### Scripts

| script | lines | job | invoked by |
|---|---:|---|---|
| `row_pod.sh` | 1,147 | One sweep row: precheck, source identity, target family, admission hook, Build (derive ×7), Match (`run_config`, `global_match`, verdict heredoc), Commit (`commit_delta` or the hot worker, manifest verify, weights of record), `research` result | `run_row_v2.sh`, hand |
| `canary.sh` | 310 | Canary row (global Program, global match, one Commit) that checks against `known_roots.json` | hand; README |
| `tp_stage.sh` | 275 | Tensor-parallel row runner at any `WORLD=N`; duplicates `row_pod.sh`'s preamble | `run_row_v2.sh:149` (row id `__tpN__`, N>1), `row_pod_tp2.sh` |
| `pod_bootstrap.sh` | 244 | Creates `/workspace/venv312`, installs pinned vLLM/torch, fetches checkpoints, builds native taps | hand (first step on a pod) |
| `run_row_v2.sh` | 232 | Wrapper that turns `research run --tool vllm.<stage>` into one `row_pod.sh`/`tp_stage.sh` stage; flags become env vars | `tools/research` (tool command, `research_tools.py:254`) |
| `cov_pod.sh` | 191 | Coverage campaign: `run_config` on `workloads/workload_<name>.json` per case | hand (`dead_code_keep.json` says "bench/, not a root") |
| `compiled_commit.sh` | 187 | `Execution=compiled` Commit: two `commit_delta` arms, then `compiled_merge` and `query.manifest.compiled` | hand |
| `verify_lane.sh` | 141 | Sealed verifier: sparse checkout, then `run_config`, `check.protected`, `check.holdout`, `check.quarantine_lint` | hand |
| `pod_fa2_tap.sh` / `pod_fa3_tap.sh` / `pod_hidden_gpu.sh` | 113 / 82 / 80 | Build the FA2/FA3 matReq taps and `hidden_gpu` native extensions | `pod_bootstrap.sh`, `row_pod.sh` |
| `stoch_negative_n3.sh` / `stoch_negatives.sh` / `fa3_row_negatives.sh` | 102 / 88 / 64 | Hand-run negative campaigns | nothing but `tests/census_roots.txt` |
| `pod_gate.sh` | 77 | CPU gate: `acquire.gate`, `correspondence.runtime_tree`, `query.cli` | hand |
| `row_pod_tp2.sh` | 5 | Compatibility shim: `WORLD=2 exec tp_stage.sh` | README, regression expected JSON |
| `known_roots.json` | 51 | Expected Program roots for `canary.sh` | `canary.sh` |

## 3. `tests/` (281 test files, 74,187 lines)

**Organisation.** `tests/<subpackage>/` mirrors the package: acquire 22, check 42, commit 19, correspondence 7, harness 21, input_provenance 5, observe 37, ops 6, program 80, query 14, regression 7, tp 18, plus 3 suite-wide lints at the root. Around them sit the dead-code census (`dead_code_census.py`, 560 lines; `census_roots.txt`; `dead_code_keep.json`), a by-name lint (`test_no_by_name_rules.py` + `by_name_allowlist.json`, 249 lines), and the root `conftest.py`. That conftest is a guard against a second copy of `verity.ir.defs` being loaded, a symptom of tests that `exec` or re-import sources.

**Test kinds.**
- **Unit tests** are the default. There is no `unit` marker.
- **GPU/pod-only tests** have no single marker and are gated ad hoc:
  - 14 files check `torch.cuda.is_available()`, 46 use `importorskip("torch")`, 3 use `importorskip("vllm")`, and 18 import torch or vLLM at module top with no guard.
  - The registered `pod` marker is applied in one place (`regression/test_regression.py:119`).
  - 34 files skip when an evidence path is missing. 23 reference `out/gen/…`, which is gitignored (`.gitignore:7`) and absent from this checkout, and 19 reference `/workspace/…`.
- **Regression tests** live in `tests/regression/` (7 tests, 20 helper modules, `fixtures.toml`, 13 `expected/*.json`). They are skipped unless `VERITY_REGRESSION=1`, and inputs resolve through `resolver.py` from `/vault/tmp/oracle`, `/workspace/…` or `research` artifacts.
- **Source-text tests** are a distinct class:
  - 12 files regex-extract logic from `row_pod.sh`/`tp_stage.sh`.
  - 4 files parse or `exec` slices of `commit_delta.py`: `harness/test_engine_schedule.py:13-21` execs a function sliced from the file, `harness/test_hot_commit.py:240-243` execs `main()`'s argparse block, and `harness/test_commit_delta_cli.py:20-24` and `test_commit_delta_placement_b1.py:16-20` walk the AST of `main()`.
  - About 24 files read package source text for lint-style assertions.

Skip and xfail counts: 87 `pytest.skip(` calls in 44 files, 51 `skipif` in 37 files, 71 `importorskip` in 59 files, and 11 xfail markers (all `strict=True` documented gaps). Details are in Map 4.

## 4. Top-level data directories and `tools/`

**What they are vs. their names.** README.md:31 calls `workloads/ manifests/ fixtures/ data/ docs/` "records of the qualification table; never rewritten by the tool". In practice they mix four kinds of content:
- **Run definitions:** `workloads/` and `manifests/checkpoints.json`.
- **Library inputs:** `data/hf_configs`, `docs/data/ref-prims`, `fixtures/W11*`, `data/l8-nan-scan-*`.
- **Evidence records nothing reads:** `data/rec`, `data/census`, `data/contract`, `data/workloads_r12`, `data/logs/m6`.
- **Test-only inputs.**

None of it is package data: `pyproject.toml:19-22` ships only `verity_vllm`, yet library code reads these directories through `Path(__file__).parents[N]` or working-directory-relative defaults. `docs/` holds no documentation, only `docs/data/ref-prims/`. `tools/` holds the finished relayout's migration tooling, which a test still enforces. The full per-directory table is Map 3.

## 5. `pyproject.toml`, `conftest.py`, `README.md`

- **`pyproject.toml` (36 lines).**
  - `requires-python = ">=3.12"` (line 5), which makes two test-module Python-version skips dead.
  - Dependencies are only `verity` and `numpy` (lines 6-9), although `harness/research_tools.py:36` and `harness/source_identity.py:36` import `research` at load time.
  - The wheel packages only `verity_vllm` (lines 19-22).
  - Line 28 says fixtures are "read relative to" the working directory.
  - Three markers are registered (lines 32-36). `@pytest.mark.slow` (`tests/program/test_derive.py:416`) is unregistered, and without `--strict-markers` it only warns.
- **`conftest.py` (46 lines)** guards against a `verity` module being swapped mid-session (see §3).
- **`README.md` (173 lines).**
  - The vocabulary table (lines 101-160) still cites pre-relayout paths: `bench/m1_capture.py` (line 151) and `experimental/cb_a/batch_decomp.py` and `…/global_match.py` (lines 151, 154).
  - The rules at lines 86-95 ("a check that lives here is misfiled"; ops has "no Python that a layer above would import") hold in letter but not in spirit: verdict logic lives in `commit_delta.main()` and in a `row_pod.sh` heredoc.

<!-- APPEND -->
