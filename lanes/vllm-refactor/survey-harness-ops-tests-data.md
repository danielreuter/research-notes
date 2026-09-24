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

It is also **not a leaf**. Eleven lower-layer modules import it at 16 sites:
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

---

## Findings by category

Counts: CORE-DUP 2, INTERNAL-DUP 11, VERSION-RESIDUE 8 (plus a LEGIT list), HARDCODING 7, SCRIPT/ENV/PATH 11, LAYERING 6, GOD-MODULE 4, DEAD 16, NAMING 7, DOCS 8, FALLBACKS 7, OTHER-WEIRD 9. **Total 96.**

### CORE-DUP (2)
- `tests/acquire/schemes.py:77-121, 196-207`: `ProtocolMerkleScheme` imports `veritor.core` and `veritor.protocol.merkle`, a package that no longer exists anywhere in the repo. On ImportError it prints "scheme skipped" (`:203`). The cross-scheme agreement suite therefore never compares the integration's openings with a protocol-side Merkle. The core equivalent is `packages/.../commitments/merkle.py`, and no file in the integration imports `verity.commitments`. *high*
- `harness/synthetic.py:30, 417-449`: the toy end-to-end model builds on `verity_vllm.commit.merkle` and `commit.hashing.leaf_hash`, the integration's copy of `packages/.../commitments/leaves.py`. It should move when that duplicate is replaced. *low*

### INTERNAL-DUP (11)
- **The row-id grammar is parsed in 10 places:**
  - `harness/research_tools.py:111-131` (`row_config`)
  - `harness/target_family.py:43-53` (a split and a second regex `_ROW_RE`)
  - `harness/telemetry/admission.py:678`
  - `harness/workload.py:344` (regex `__tp(\d+)__`)
  - `harness/research_outputs.py:87` (regex `__b(\d+)__`)
  - `ops/run_row_v2.sh:95` (`row_world`, sed)
  - `ops/compiled_commit.sh:35, 104`
  - `tests/regression/checks/attempt_provenance.py:21-37`, a declared verbatim copy of `row_config` and `DEFAULT_QUERY`
  - `tests/regression/lift_expected.py:111-112`

  The row id is the de facto configuration key (Map 2), and nothing owns its grammar. *high*
- **Four definitions of "the code this run depends on", and they disagree:**
  - `harness/hot_commit.py:51-52` `CODE_ROOTS`: only under `integrations/vllm`, and 4 of its 6 roots are absent.
  - `harness/derive_step.py:52-60` `_CONSTRUCTION_SOURCES`: 13 files, resolved against the wrong root (see DEAD).
  - `harness/research_tools.py:44-49` `CLOSURE`: `integrations/vllm/**` plus `packages/verity/src/verity/{ir,ml,verification}/**`.
  - `harness/source_identity.py:44-53` plus `research.telemetry.source_identity`: module resolution.

  A core edit changes the `research` attempt key but not the hot-worker key. *high*
- `harness/research_tools.py:71-102`: `STAGE_KEY_FLAGS` and `NON_KEY_FLAGS` re-declare `row_pod.sh` knobs and their defaults (`pairs "3"` = `row_pod.sh:79`, `within_step "dag"` = `row_pod.sh:594`, `snapshot_steps "row-default"`). They are recovered by reverse-parsing argv (`:142-163`). If a default changes in bash, the `research` key silently stops matching what ran. *medium*
- **Three span and timing systems:**
  - `harness/timeline.py:53-66` (`Timeline`, writes `timeline.jsonl`)
  - `harness/spans.py:26-51` (`Spans`)
  - `tools/research/src/research/telemetry/events.py:195-205` (`span_start`/`span_end`, writes `events*.jsonl`)

  `harness/telemetry/admission.py:898` therefore needs two readers, `observe_increment_a` (`:814`) and `observe_r17` (`:597`), picked by which files exist. *medium*
- **Two admission planners and a bound:** `harness/admission_planner.py:1` ("ONE conservative resource planner", in-process at `commit_delta.py:1778`), `harness/telemetry/admission.py:1` ("Empirical admission planner", advisory at `row_pod.sh:237`) and `harness/admission_bound.py` (`commit_delta.py:1722`). The Merkle-levels factor 1.25 is defined twice (`admission_bound.py:44`, `telemetry/admission.py:102`). *medium*
- **Two row runners:** `ops/tp_stage.sh` repeats `row_pod.sh`'s preamble with different values: tree check (`tp_stage.sh:34` / `row_pod.sh:49`), `PY` (`:50` / `:69`), `GPU_UTIL` (`:58` computed / `:79` 0.5), release and timeline lines (`tp_stage.sh:79, 117`). *medium*
- **Stage orchestration implemented 7 times:**
  - Six shell runners each carry their own tree, `PY`, `PYTHONPATH`, HF env and timeout preamble: `row_pod.sh`, `tp_stage.sh`, `canary.sh`, `compiled_commit.sh`, `cov_pod.sh`, `verify_lane.sh`.
  - `harness/run_config.py:76-86` is a seventh (19 stages, own skip groups).

  *medium*
- `ops/row_pod.sh:845` `EXTRA_COMMIT_ARGS` and `:934` `COMMIT_ARGS` both append verbatim flags to the same `commit_delta` command; they come from different rounds ("P0", "R13 hopper runner"). Both comments cite the flag set that `WINDOW_MB`/`WINDOW_SLOTS`/`RETAIN`/`OPEN_AFTER_RELEASE` now set by default (`:831-834`). *low*
- **Workload generators:** `harness/workload.py` (row-grammar ids) and `harness/coverage_workloads.py` (`workload_cov_*`) write one directory in two naming schemes, and `observe/prefix_cache.py` is a third generator (`tests/dead_code_keep.json:41`). *low*
- **Duplicate padrev suites:** seven `tests/program/*_padrev.py` files (1,778 lines) are a reviewer lane's independent re-tests of the lifting suites (`test_lifted_tiny_padrev.py:1-6`: "Independent of pad's own suite").
  - Three of the five paired files import nothing from their base.
  - `test_lifted_workload_padrev.py` and `test_workload_compose_padrev.py` have no base file left.
  - They are adversarial by intent, but they are now a second suite on the same subjects, named after a lane. *medium*
- **Interpreter path copied 17 times:** 16 script defaults (SCRIPT/ENV) plus `harness/research_tools.py:39` `DEFAULT_PY`. *low*

### VERSION-RESIDUE (8)
- `ops/run_row_v2.sh`: `_v2` in the name of the only wrapper, which is also hardcoded as `research_tools.py:41` `WRAPPER`. *medium*
- `ops/row_pod_tp2.sh` (5 lines): a shim named after TP degree 2 for a runner that is now any-N (`tp_stage.sh:2`: "formerly row_pod_tp2.sh"). *low*
- `harness/derive_step.py:675` `--profile default="b1-eager-v3"` and `:681` "default: the B0 pin": case and profile version names serve as the CLI defaults of the Build. *medium*
- `harness/run_config.py:1025` `VERITY_INSTANCES_FORM` says "runs (default, v1) | progressions (v2)" while `row_pod.sh:543` sets `progressions`. Every reader accepts both forms. *medium*
- **Case names B0/B1/B7 as configuration:**
  - 35 `workloads/workload_b0_*`, `workload_b1_*`, `workload_b7_*`, `workload_cov_b0_*` files.
  - `row_pod.sh:564` passes the `<ROLE>` positional as `run_config --case`.
  - `commit_delta.py:1039` and `hot_commit.py:175` default to `workload_cov_b0_b1_c256.json`.

  *medium*
- `harness/run_config.py:5, 27-30, 66`: replay "tier a/b/c/chain" flags (`--tier-c`, `DEFAULT_K` "tier a"). *low*
- `harness/telemetry/admission.py:597, 814`: round names as function names (`observe_r17`, `observe_increment_a`). *low*
- **Round-named test files (11):** `check/test_rev_r16_duplicate_binding.py`, `check/test_rev_r16_named_population_gap.py`, `harness/test_admit_r19_host_working_set.py`, `program/test_lifted_r17.py` and the seven `*_padrev.py`. They are named after a review round or lane rather than the behaviour they test. *low*

**LEGIT versioned ids.** These are hashed or schema data; leave them unless a migration re-hashes:
- `cb-a/aot-artifact/v1` (`derive_step.py:81`; the old package name inside a schema id)
- `verity-sweep/hot-commit/v1` (`hot_commit.py:50`)
- `verity-gen/card/v1` (`card.py:1`)
- `verity-sweep/release/v1` (`release_json.py:1`)
- `research/outputs/v0.1`, `research/result/v0.1`
- `verity-sweep/oracle-compare/v1`
- query id `Q_module_body_v1`
- Definition names `TopPMask_v1` and `SplitsFor_v1`

### HARDCODING (7)
- `harness/derive_step.py:369-371`:
  - `model_pin.dtype` is always `vm.PIN["dtype"]` (bfloat16), even for the two `qwen3-4b-fp8__fp8__h100__*` rows.
  - `model` and `revision` fall back to the B0 pin (SmolLM2-135M) when `--model` is omitted.
  - `--model` is never cross-checked against the workload's `model`.

  *high*
- `ops/row_pod.sh:213`: FA3 rows get `HIDDEN_SO=/workspace/cp/fa2/build/fa3_matReq/verity_fa3_matReq.so` unless the caller overrides it. *medium*
- `ops/tp_stage.sh:47`: `WORLD` defaults to 2 both when the workload has no `sweep.tp` and when the Python read fails, and `row_pod_tp2.sh` hardcodes `WORLD=2`. *medium*
- `harness/commit_delta.py:1039-1040` and `harness/hot_commit.py:175-179`: the Commit CLI's default workload is one B0/B1 coverage workload. *medium*
- The default query id `Q_module_body_v1` appears 74 times in 27 files: 11 test files, 7 in `query/`, 3 in `ops/`, `research_tools.py:38`, `attempt_provenance.py:21`, README. *low*
- **Magic admission constants:** `commit_delta.py:1633-1634` (1.05, 2.0), `:1665` (6 GiB slack), `admission_bound.py:44` and `telemetry/admission.py:102` (1.25, twice). `GPU_UTIL` defaults differ per script: 0.5 (`row_pod.sh:79`, `canary.sh:62`, `fa3_row_negatives.sh:23`), 0.3 (`compiled_commit.sh:36`, `stoch_negatives.sh:20`), computed (`tp_stage.sh:58`). *low*
- `harness/target_family.py:35` `DEVICE_FAMILY`: a GPU-name → compute-capability table in library code. Acceptable as the one table, but it is the only map from row-id `hw` tokens. *low*

### SCRIPT/ENV/PATH (11)
- `harness/commit_delta.py:1197-1267, 1282, 1455` copies 12 CLI flags into `os.environ` so that `acquire/` and `commit/` code can read them back: `VERITY_RETAIN`, `WINDOW_MB`, `WINDOW_SLOTS`, `LAYOUT`, `STAGING_BOUNDED`, `LEARN_HOST_BUDGET_MB`, `RETAIN_EXCLUDE`, `FOOTPRINT`, `WEIGHTS_HASH`, `SOURCE_IDENTITY_DIR`, `FA2_TAP_CAP_MB`, `COLLECT_WATCHDOG_MARKER`. Configuration flows through process-global env. *high*
- `harness/commit_delta.py` has 36 env reads, including behaviour switches `VERITY_FAULT` (`:984, :1217`), `VERITY_SWITCH` (`:986, :1407`), `VERITY_TRACEDUMP` (`:1033`), `VERITY_DUMP_STEP` (`:516`), `VERITY_LEAF_LAYOUT` (`:583`), `VERITY_ADMIT_*` (`:1633-1760`) and `VERITY_HOT_SUBMIT` (`:3022`). *medium*
- `ops/row_pod.sh` reads 45 caller-settable environment variables and exports 17 in 12 `export` statements (Map 1). Its "Env:" header (`:17-21`) documents 14 of them. *high*
- **Three venv names across 16 scripts,** while `pod_bootstrap.sh:34` creates only `venv312`:
  - `venv312`: `row_pod.sh:69`, `tp_stage.sh:50`, `pod_gate.sh:11`, `pod_fa2_tap.sh:25`, `pod_fa3_tap.sh:16`, `pod_hidden_gpu.sh:19`, `pod_bootstrap.sh:34`
  - `venv-cu129`: `canary.sh:39`, `compiled_commit.sh:19`, `fa3_row_negatives.sh:20`, `stoch_negative_n3.sh:20`, `stoch_negatives.sh:19`, `cov_pod.sh:23`
  - `venv-py312`: `cov_pod.sh:23` (not overridable), `stoch_negative_n3.sh:20`, `stoch_negatives.sh:19`

  *high*
- The old repo path `/workspace/cp/veritor` appears 26 times in 13 files: `harness/release_json.py:36` `DEFAULT_TREE`; `compiled_commit.sh:22`, `stoch_negative_n3.sh:18` and `stoch_negatives.sh:17` default into it. *medium*
- **Other machine paths:**
  - `row_pod.sh`: `:26` `/workspace/cp/sweep` (32 occurrences in 24 files, 16 of them tests), `:57` `/workspace/hf`, `:73` `/workspace/cp/nc_build`, `:299` `/workspace/cp/hot`
  - `hot_commit.py:63, 74, 654, 665` (`/workspace/cp/RELEASING`, `RELEASE.json`, `hot`); `commit_delta.py:3028`
  - `source_identity.py:53` (`integrations/vllm/out/gen/r9/…`, a gitignored path)
  - `tests/regression/fixtures.toml:19, 27, 242, 738` (`/vault/tmp/oracle`; 19 machine paths in the file)

  *medium*
- **Working-directory-relative defaults:** `commit_delta.py:1039-1040`, `hot_commit.py:175-179`, `run_config.py:69`, and 16 argparse defaults of `manifests/checkpoints.json` across `verity_vllm`. `pyproject.toml:28` codifies it ("run from this directory"). *medium*
- `Path(__file__).parents[N]`: `commit_delta.py:1793` (into `tests/`), `source_identity.py:44` (`parents[4]` = repo root), `workload.py:40`, `coverage_workloads.py:37`. *low*
- `harness/workload.py:352` does `sys.path.insert(0, REPO/"vllm-poc")`, and that directory is absent. *medium*
- `ops/fa3_row_negatives.sh:21` sets `PYTHONPATH=$REPO:$REPO/vllm-poc`, which omits `packages/verity/src` and adds an absent directory. *medium*
- 20 of 25 harness modules are `__main__` CLIs and 19 use argparse (flag counts: `commit_delta` 62, `run_config` 43, `telemetry/admission` 36, `derive_step` 18). The harness API is argv, not functions. *medium*

### LAYERING (6)
- `harness/commit_delta.py:1793`: library code reads `tests/harness/fixtures/admission/planner_calibration.jsonl`. This is the only live library read of `tests/`. *high*
- **The integration imports `tools/research` at load time:** `harness/research_tools.py:36` (`research.store.tool`) and `harness/source_identity.py:36` (`research.telemetry.source_identity`). It is not a declared dependency (`pyproject.toml:6-9`), and `row_pod.sh:57` puts `tools/research/src` on `PYTHONPATH`. *high*
- `tools/research/src/research/store/tools_registry.py:26-28` (and `tools/research/tests/test_store_vllm_tools.py:100`) imports the harness as `integrations.vllm.verity_vllm.harness.research_tools`. That gives a second module identity for the same file, the failure the root `conftest.py` guards against for `verity`. *medium*
- **16 imports of `harness` from 11 lower-layer modules:**
  - `tp/worker.py:639, 887, 1435` and `tp/commit.py:330` (from `commit_delta`)
  - `tp/match.py:32`, `tp/fold_match.py:58`, `tp/rank_match.py:57` (from `derive_step`)
  - `observe/m1_capture.py:49` (`timeline`)
  - `observe/prefix_cache.py:92, 117, 539` (`coverage_workloads`)
  - `acquire/native_host.py:54` (`spans`), `:1392` (`source_identity`)
  - `check/global_match.py:2132`, `correspondence/batch_decomp.py:894` (`gc_tuning`)
  - `input_provenance/weights_of_record.py:912` (`experiment`)

  *high*
- **Library code reads top-level data directories that are not package data** (`pyproject.toml:19-22`):
  - `observe/profiles/generic.py:26`, `profiles/__init__.py:51`, `dense_generic.py:49-51, 117` (`data/hf_configs`, `manifests/`)
  - `program/registry/ref_prims.py:192`, `conformance.py:25`, `frontend/rules/vocab.py:86`, `frontend/rules/reference.py:4` (`docs/data/ref-prims`)
  - `check/fold_compare.py:59` (`fixtures/B0-divergence-…`)
  - `check/fa2_attn_oracle.py:11`, `program/numerics/fa2_relation.py:117`, `rms_relation.py:37-38, 59` (`fixtures/W11*`)
  - `program/registry/rmsnorm_fused_sweep.py:48` (`fixtures/verity-ir`, absent)
  - `harness/workload.py:42, 427`, `coverage_workloads.py:375` (`manifests/`, `workloads/`)

  *high*
- `harness/derive_step.py:27, 41` imports the private core helper `verity.ir.codec._spec_id`. *low*

### GOD-MODULE (4)
- **`harness/commit_delta.py` (3,030 lines; `main()` alone runs 1,921 lines from `:1030`).** Jobs:
  1. a 62-flag CLI;
  2. flag-to-env configuration of `acquire`/`commit`;
  3. hot-worker routing (`:3021-3029`) and engine-reuse bookkeeping (`:1312-1337`);
  4. engine build and workload run;
  5. FA2/hidden tap setup (`:1453-1455`);
  6. admission: bound (`:1722`), planner (`:1778-1802`), calibration read from `tests/` (`:1793`) and post-run calibration (`:2934-2938`);
  7. windowed native collector configuration;
  8. `binding_record` (`:549`, 212 lines);
  9. `openings_after_release` (`:769`, 196 lines);
  10. Δ_commit control/treatment pairs;
  11. live C2 oracle-compare (`:2318-2349`) and sampled replay with cache (`:2368`);
  12. executed-prefix placement in three sites (`:629-676`, `:2128-2176`);
  13. verdict-component assembly (`:2198-2267`);
  14. fault injection, GIL-switch experiment and trace dump (`:984-986`, `:1033`, `:1407`);
  15. committer factory and helpers imported by `tp/`.

  Four tests have to parse or `exec` its source to reach these pieces (OTHER-WEIRD). *high*
- **`ops/row_pod.sh` (1,147 lines of bash).** Jobs:
  1. tree and venv resolution;
  2. source-identity and target-family prechecks;
  3. admission hook;
  4. Build (7 `derive_step` calls, launch context, global Program, query manifest);
  5. Match (`run_config`, `global_match`, `program_compare`, `stoch_recompute`, `batch_decomp`, and the verdict heredoc at `:686-800`);
  6. Commit (`commit_delta` or the hot worker, `manifest.verify`, `weights_of_record` with staleness logic at `:1023-1067`);
  7. timeline, stages.txt, verdict.json and `research` result;
  8. timeouts scaled by B and T.

  *high*
- **`harness/run_config.py` (1,196 lines).** Jobs: a 43-flag CLI; 19-stage GPU/CPU orchestration with skip groups; subprocess launch of 9 modules (`:190-255`); snapshot-cap derivation; instances-form selection (`:1025-1113`); execution-label resolution (`:892`); card and gates; laptop RSS/wall watchdog; HF cache resolution (`:264`). *medium*
- **`harness/telemetry/admission.py` (1,198 lines).** Jobs: the `INVENTORY` allocation table (`:151`); workload-derived `RowConfig`; `predict` (`:389`); peak-overlap planning; two telemetry readers (`:597`, `:814`); row parsing from an attempt directory (`:661-696`); plan-vs-observed `compare` (`:893`); a 36-flag CLI. *medium*

### DEAD (16)
Each item gives its confidence and what I searched.

- `harness/hot_commit.py:51-52`: 4 of 6 `CODE_ROOTS` (`verity_vllm_sampler`, `e2e`, `record_v5`, `scripts`) do not exist, and Verity core is never hashed. Edits to `packages/verity/src` therefore do not change the hot-engine key, which breaks the promise that the hot worker never runs stale code. *high*; confidence high (filesystem).
- `harness/derive_step.py:52-60, 67-78`: all 13 `_CONSTRUCTION_SOURCES` are joined to `dirname(dirname(verity.ir.__file__))`, which is `packages/verity/src`, but they live under `integrations/vllm`. Every file is silently hashed as "missing", so `construction_version` no longer changes when the builder's code changes (also FALLBACKS). *high*; confidence high (checked each root; three files spot-checked under both).
- `harness/workload.py:352`: the `vllm-poc` path is absent. *low*; high.
- `ops/row_pod.sh:553`: `ACQUIRE_ENGINE` is only interpolated into a log line and has no reader in `integrations/vllm` or `tools/`. Yet `tests/regression/fixtures.toml:730` records "ACQUIRE_ENGINE=v2" as if it selected something. *low*; high.
- `ops/run_row_v2.sh:80`: `--query` exports `VERITY_QUERY_ID`, which nothing reads. `query` is still part of the `research` key (`research_tools.py:57-67`), so attempts are keyed by a value that changes nothing. *medium*; high (searched `integrations/vllm`, `tools`).
- `harness/rebuild_digest_gate.py` (130 lines): no importer or invoker. I searched absolute and relative imports, `-m` in `ops/`, `tests/`, README and `tools/research`, and string references. Only `tests/census_roots.txt:36` names it. *low*; medium (it may be run by hand).
- `data/rec` (34 files), `data/census` (33), `data/contract` (20, including `argmax_rule/probe_pinned.py`), `data/workloads_r12` (1) and `data/logs/m6/log.jsonl.gz` are not referenced by directory name or file basename from `verity_vllm`, `tests`, `ops`, `tools` or README. `verify_lane.sh:59` even excludes `data/contract` from its sparse checkout. *medium*; medium (hand use possible).
- `manifests/semantic-profiles/llama-eager-batch-invariant-v1.json`, `-v2.json` and `qwen2-eager-batch-invariant-v1.json` are named only in `tools/move_map.txt`; `program/registry/b1.py:397` is a docstring glob. *low*; medium-high.
- Seven legacy workloads are named by nothing: `workload_b0_{chunked_200p, conc2_small, conc4_mixed, conc8_mixed, long512_1req}`, `workload_b1_sampling_topk50_topp09`, `workload_qwen15_conc4_mixed`. *low*; low (`cov_pod.sh:130` and `run_config` accept any name at runtime).
- **Referenced data that is missing:**
  - `check/noninterference.py:778` defaults to `data/logs/m1_ctl_tokens.json`.
  - `check/fold_compare.py:3` and `check/replay.py:8` use the snapshot directory `data/logs/m1`.
  - `program/registry/rmsnorm_fused_sweep.py:48` `NORM_WEIGHTS` is a live constant.
  - `program/registry/topp_split.py:71` cites `tests/data/topp_split_fixture`; the real path is `tests/program/data/topp_split_fixture`.
  - Provenance strings point at absent evidence: `docs/data/tc-*` (`conformance.py:63`, `prims.py:203`, `derived_rows.py:461`, `hopper.py:77`, `fp8.py:125`), `fixtures/results` (`vllm_adapter.py:73`, `poc_rows.py:6`, `kernel_zoo.py:3`, `vllm_d9105ea80_sm89_eager.py:55`), `fixtures/verity-ir` (`conformance.py:45, 50`), and `docs/data/l8-nan-scan-*` (`conformance.py:75`; the data now lives in `data/`).

  *medium*; high (filesystem).
- **13 first-party `importorskip` guards whose targets all exist:** `observe/test_execution_label.py:11, 49`; `program/test_derive_negative.py:765, 1050`; `program/test_lifted_dense_b1_padrev.py:17, 18`; `program/test_lifted_tiny_padrev.py:24`; `program/test_vllm_bindings_pins.py:83`; `query/test_partition_structural.py:408`; `tp/test_tp_partial_source_mid_module.py:12, 143`; `tp/test_tp_partial_source_moe.py:13, 175`. They are "not merged yet" guards, and they turn an ImportError in first-party code into a skip. *medium*; high.
- `tests/program/test_derived_rows_fp8.py:13-14` and `test_fp8.py:23-24` skip on Python < 3.12, which can't happen under `pyproject.toml:5`. The reason given ("veritor.core needs Python 3.12") names a package that no longer exists. *low*; high.
- `tests/test_imports_resolve.py:15` `FIRST_PARTY` lists `verity_capture`, `verity_vllm_adapter` and `verity_vllm_numerics`, none of which exist. The lint also doesn't cover `veritor.*`, so `tests/acquire/schemes.py` passes it. *medium*; high.
- **Stale entries in `tests/dead_code_keep.json`:** `:5-7, 11-15` cite `fa2_commit` and `cb_a/tests` paths that no longer exist. `:37-38` say `verify_lane.sh` and `cov_pod.sh` are "bench/, not a root", but `test_no_dead_modules.py:4` makes every `ops/*.sh` a root, so the `check.protected` and `check.holdout` entries are unnecessary. *low*; high.
- `tools/gen_move_map.py` (599), `tools/relayout.py` (1,240) and `tools/move_map.txt` (1,229) are one-shot relayout tooling, kept alive only by `tests/program/test_relayout_map.py`. *low*; medium.
- `ops/fa3_row_negatives.sh`, `stoch_negative_n3.sh` and `stoch_negatives.sh` are named only in `tests/census_roots.txt`. They default into `/workspace/cp/veritor` and `venv-cu129`/`venv-py312`, so as written they cannot run on a bootstrapped pod. *medium*; medium.

### NAMING (7)
- `harness`: it is the production row pipeline and a library for `tp/`, `observe/`, `acquire/`, `check/`, `correspondence/` and `input_provenance/`, not a harness. *medium*
- **"fixture" has four meanings:** `fixtures/` (evidence the library reads), `tests/harness/fixtures/` (test data the library reads), `tests/regression/fixtures.toml` (an index of external reference artifacts), and "GPU-truth fixture" (`topp_split_probe.py:1`). *medium*
- **"manifest" has six meanings:** `manifests/checkpoints.json` (checkpoint pins), "workload manifest" (`derive_step.py:686`), the required-value manifest `$D/manifest.json` (`row_pod.sh:897`), `ACQUIRE_MANIFEST` (`row_pod.sh:553`), `construction_manifest.json` (`derive_step.py:667`), and `manifests/semantic-profiles/`. *medium*
- **"profile" has five meanings:** derive profile `b1-eager-v3` (`derive_step.py:675`), observe capture profiles, workload `serving_profile`, semantic profiles, and `TargetProfile` (`derive_step.py:684`). *medium*
- Role and case are the same thing: `row_pod.sh`'s `<ROLE>` becomes `run_config --case "$ROLE"` (`row_pod.sh:564`). *low*
- **"gate" has four meanings:** `rebuild_digest_gate.py`, `pod_gate.sh` (`acquire.gate`), `run_config`'s "gates" stage (G1..G8), and `target_family`'s "preflight". *low*
- `research_tools` / `research_outputs` / `research_result`: three modules for one adapter, and the names don't say which does what. *low*

### DOCS (8)
- **Lab-notebook docstrings:** there are 524 board or round tokens (`M-NNNN`, `F-r…`, `R1x`, `COORD`) in `harness/`: `commit_delta` 210, `telemetry/admission` 50, `derive_step` 36, `run_config` 32, `admission_planner` 21. Many module first lines open with one, for example `admission_planner.py:1` "(COORD R17-29 = Daniel; fp8 owner, stoch with, exec wires, revb reviews)" and `target_family.py:1` "(R18 infra, r18-int-2; x09 M-0009 / coord M-0026 / report M-0016)". *medium*
- **Stale paths in docstrings:**
  - `run_config.py:1, 9, 12, 18` (`bench/run_config.py`, `bench.m1_capture`, `bench.resolve_log`)
  - `card.py:3, 10`; `coverage_workloads.py:1`; `workload.py:1, 8` (`sweep/workload.py`, `bench/commit_delta.py`, `zk/bench/e2e_commit_run.py`); `commit_delta.py:1147`
  - `row_pod.sh:2-3` (`sweep/row_pod.sh`, `cb_a.compare`, `native_collect_v2b`); `tp_stage.sh:2`
  - `telemetry/admission.py:8, 18` (`out/gen/sweep/evidence/admit/INVENTORY.md`, `zk/campaign/telemetry`, both outside the tree)

  *medium*
- `ops/tp_stage.sh:11` describes a `row_pod.sh` hook that doesn't exist; dispatch actually happens at `run_row_v2.sh:149`. `row_pod.sh:17-21` documents 14 of 45 knobs. *medium*
- Three tap scripts document a `venv-cu129` default that their code overrides with `venv312`: `pod_fa2_tap.sh:19` vs `:25`, `pod_hidden_gpu.sh:16` vs `:19`, `pod_fa3_tap.sh:12` vs `:16`. *low*
- `tests/regression/test_regression.py:10` says "Twelve rows" and `:65` says "Today one decision", but `fixtures.toml` has 13 rows and 9 decisions. *low*
- `tests/test_no_dead_modules.py:3-4` reads "verity_vllm / verity_vllm / verity_vllm.program.numerics / verity_vllm", a mechanical-rename artifact. *low*
- **README drift:** `README.md:31` says the data directories are "never rewritten by the tool", but `tests/program/test_ref_prims.py:43, 157-165, 725-726` rewrites `docs/data/ref-prims`. `README.md:151, 154` cite `bench/m1_capture.py` and `experimental/cb_a/*`, and `:5-6` is migration history. *medium*
- `harness/research_tools.py:51` says "Row id grammar (see verity_vllm/ops/README)", but there is no `ops/README`. *low*

### FALLBACKS (7)
- `ops/tp_stage.sh:47`: world size comes from the workload's `sweep.tp`, otherwise 2, and also 2 if the Python read fails (`2>/dev/null || echo 2`). *medium*
- `harness/research_tools.py:111-121`: `row_config` is "tolerant", so a malformed row id still yields a distinct derivation instead of an error. *medium*
- `harness/run_config.py:1025`: the instances form is chosen by `VERITY_INSTANCES_FORM`, with an internal default of `runs` while `row_pod.sh:543` exports `progressions`. The output format depends on the caller's environment. *medium*
- `ops/row_pod.sh` has 15 `|| true` and 39 `2>/dev/null`, for example `:85` (`research_result`) and `:1134` (verdict summary). Failures in bookkeeping steps vanish. *low*
- **Precedence chains:** `NATIVE_COLLECT_BUILD` goes caller → release per-tree dir → `/workspace/cp/nc_build` (`row_pod.sh:72-73, 129`). `HIDDEN_SO` goes caller → FA3 hardcoded → default (`:77-78, 213`). `PY312` falls back to `PY` (`:69`). *low*
- `harness/hot_commit.py:62` (`RC_HOT_INFRA=70`: the client silently runs cold instead) and `:82` (`release_json_sig` catches every exception and returns None). `commit_delta.py:2343-2345` is a documented fail-closed catch, "not checked, never PASS", but it looks for `"OC" in dir()`. *low*
- Tests: about 34 files skip when evidence paths are missing. With `out/` gitignored, they skip on every checkout except a pod's (`.gitignore:7`). *medium*

### OTHER-WEIRD (9)
- `ops/row_pod.sh:686-800`: the Match verdict is computed by a 113-line Python heredoc. The script holds 12 heredocs (255 lines) and 24 `python -c` lines in total. *high*
- **Source-text tests:**
  - `tests/harness/test_engine_schedule.py:13-21` execs a function sliced out of `commit_delta.py`.
  - `tests/harness/test_hot_commit.py:240-243` execs `main()`'s argparse block.
  - `test_commit_delta_cli.py:20-24` and `test_commit_delta_placement_b1.py:16-20` walk `main()`'s AST.
  - 12 files regex-extract `row_pod.sh`/`tp_stage.sh` blocks: all 6 in `tests/ops/`, `harness/test_admission_hook.py:29-55`, `test_release_json.py`, `test_target_family.py`, `check/test_global_match.py`, `check/test_flip_weight_negative.py`, `commit/test_weights_pin_acceptance.py`.

  *high*
- `harness/hot_commit.py:532-535`: `os.environ.clear()` and `os.chdir()` for every job in a long-lived worker process. *medium*
- `harness/commit_delta.py:3021-3029`: `__main__` reroutes the process to the hot worker when `VERITY_HOT_SUBMIT=1`. *medium*
- `harness/research_tools.py:142-163`: `_parse_flags` reverse-parses shell command lines, using a whitespace heuristic, to recover the params that key `research` attempts. *medium*
- `tests/program/test_ref_prims.py:43, 157-165, 725-726`: by default the test writes records into the tracked `docs/data/ref-prims/`, which library code reads (`ref_prims.py:192`). *medium*
- **Misplaced tests:** `tests/harness/test_admit_r19_host_working_set.py` exercises `acquire.native_collect` and `check.sampled_replay`, and imports `tests.check.test_sampled_replay` at `:25`. `tests/harness/test_prescribed_input_linkage.py` exercises `check.sampled_replay`, `check.commit_verdict` and `program.global_program`. *low*
- `tests/program/test_relayout_map.py:53` repeats `"verity_vllm/observe/"` in a `startswith` tuple, a rename artifact that lost the intended third prefix. *low*
- **Subprocess orchestration in library modules:** `run_config` (9 modules), `hot_commit.py:336, 405`, `release_json`, `experiment`, `target_family`, `rebuild_digest_gate`, `research_tools`. `tests/regression/fixtures.toml` is 14,412 generated lines. *low*

<!-- APPEND -->
