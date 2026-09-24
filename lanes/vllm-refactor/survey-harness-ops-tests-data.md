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
  - About 12 more files build paths to in-repo locations that moved or were deleted: `data/logs/m1`, `vllm-poc/`, `record_v5/ship.sh`, `fixtures/results/…`, `docs/data/tc-total-…`, `observe/profiles/workload_cov_*`. Some of these skip on every checkout and some would error (see DEAD).
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

Counts: CORE-DUP 2, INTERNAL-DUP 11, VERSION-RESIDUE 8 (plus a LEGIT list), HARDCODING 7, SCRIPT/ENV/PATH 11, LAYERING 6, GOD-MODULE 4, DEAD 18, NAMING 7, DOCS 8, FALLBACKS 7, OTHER-WEIRD 9. **Total 98.**

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

  The row id is the de facto configuration key (Map 2), and nothing owns its grammar. The grammar has no slot for a construction variant, so `workloads/olmoe-1b-7b-padded__bf16__l40s__tp1__b1__…json` splices `-padded` into the model tag while its own `sweep.row_id` is the unpadded id. Two workloads now claim the same embedded row id. *high*
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
- `harness/commit_delta.py` reads 17 environment variables by name (about 24 sites), including behaviour switches `VERITY_FAULT` (`:984, :1217`), `VERITY_SWITCH` (`:986, :1407`), `VERITY_TRACEDUMP` (`:1033`), `VERITY_DUMP_STEP` (`:516`), `VERITY_LEAF_LAYOUT` (`:583`), four `VERITY_ADMIT_*` (`:1633-1760`) and `VERITY_HOT_SUBMIT` (`:3022`). *medium*
- `ops/row_pod.sh` reads 45 caller-settable environment variables and exports 18 in 13 `export` statements (Map 1). Its "Env:" header (`:17-21`) documents 14 of them. *high*
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

### DEAD (18)
Each item gives its confidence and what I searched.

- `harness/hot_commit.py:51-52`: 4 of 6 `CODE_ROOTS` (`verity_vllm_sampler`, `e2e`, `record_v5`, `scripts`) do not exist, and Verity core is never hashed. Edits to `packages/verity/src` therefore do not change the hot-engine key, which breaks the promise that the hot worker never runs stale code. *high*; confidence high (filesystem).
- `harness/derive_step.py:52-60, 67-78`: all 13 `_CONSTRUCTION_SOURCES` are joined to `dirname(dirname(verity.ir.__file__))`, which is `packages/verity/src`, but they live under `integrations/vllm`. Every file is silently hashed as "missing", so `construction_version` no longer changes when the builder's code changes (also FALLBACKS). *high*; confidence high (checked each root; three files spot-checked under both).
- **The tools that ship code to a pod are not in this repo, but the harness depends on their outputs.**
  - Absent: `record_v5/ship.sh`, `pod_release.sh`, `pod_up.sh`, and the "dead launcher" `run_row.sh` (`row_pod.sh:61`, still cited as a live producer at `:149`).
  - `pod_release.sh` alone is named 17 times in 7 files.
  - Consumers of their outputs:
    - `EXPORT.json` (written by `ship.sh`): 7 modules (`harness/{source_identity, derive_step, commit_delta, experiment, release_json, hot_commit}`, `check/noninterference`), plus `row_pod.sh:131`.
    - `RELEASE.json`: `row_pod.sh`, `canary.sh`, `release_json.py`, `hot_commit.py`, `acquire/native_jit.py`.
    - `pod_release.sh`'s RELEASING marker: `hot_commit.py:63-68`.
    - `hot_commit.py:52` also hashes a `record_v5` root.
  - `tests/program/test_ship_roots.py` has 4 tests. Read, not run:
    - `:30` and `:45` read `record_v5/ship.sh` and the gitignored `out/gen/r17/sparse-patterns.txt` with no skip guard, so those two tests would error on this checkout.
    - `:72` runs `bash record_v5/ship.sh --pack`.
    - Its fallback defaults to the owner's laptop copy of the old repo (`:66`, `/Users/danielreuter/projects/veritor`).

  *high*; high (`git ls-files` for each script name; `rg` over `verity_vllm`, `tests`, `tools/research`).
- `harness/workload.py:352`: the `vllm-poc` path is absent. *low*; high.
- `ops/row_pod.sh:553`: `ACQUIRE_ENGINE` is only interpolated into a log line and has no reader in `integrations/vllm` or `tools/`. Yet `tests/regression/fixtures.toml:730` records "ACQUIRE_ENGINE=v2" as if it selected something. *low*; high.
- `ops/run_row_v2.sh:80`: `--query` exports `VERITY_QUERY_ID`, which nothing reads. `query` is still part of the `research` key (`research_tools.py:57-67`), so attempts are keyed by a value that changes nothing. *medium*; high (searched `integrations/vllm`, `tools`).
- `harness/rebuild_digest_gate.py` (130 lines): no importer or invoker. I searched absolute and relative imports, `-m` in `ops/`, `tests/`, README and `tools/research`, and string references. Only `tests/census_roots.txt:36` names it. *low*; medium (it may be run by hand).
- `data/rec` (34 files), `data/census` (33), `data/contract` (20, including `argmax_rule/probe_pinned.py`), `data/workloads_r12` (1) and `data/logs/m6/log.jsonl.gz` are not referenced by directory name or file basename from `verity_vllm`, `tests`, `ops`, `tools` or README. `verify_lane.sh:59` even excludes `data/contract` from its sparse checkout. *medium*; medium (hand use possible).
- `manifests/semantic-profiles/llama-eager-batch-invariant-v1.json`, `-v2.json` and `qwen2-eager-batch-invariant-v1.json` are named only in `tools/move_map.txt`; `program/registry/b1.py:397` is a docstring glob. *low*; medium-high.
- Six legacy workloads are read by nothing: `workload_b0_{chunked_200p, conc2_small, conc4_mixed, conc8_mixed, long512_1req}` and `workload_qwen15_conc4_mixed`. `chunked_200p` appears only in test comments. `workload_b1_sampling_topk50_topp09` looks unnamed but is read through a parametrize list (`tests/observe/test_gen_ov_sampling.py:16, 32-34`). *low*; low (`cov_pod.sh:130` and `run_config` accept any name at runtime).
- **Referenced data that is missing:**
  - `check/noninterference.py:778` defaults to `data/logs/m1_ctl_tokens.json`.
  - `check/fold_compare.py:3` and `check/replay.py:8` use the snapshot directory `data/logs/m1`.
  - `program/registry/rmsnorm_fused_sweep.py:48` `NORM_WEIGHTS` is a live constant.
  - `program/registry/topp_split.py:71` cites `tests/data/topp_split_fixture`; the real path is `tests/program/data/topp_split_fixture`.
  - Provenance strings point at absent evidence: `docs/data/tc-*` (`conformance.py:63`, `prims.py:203`, `derived_rows.py:461`, `hopper.py:77`, `fp8.py:125`), `fixtures/results` (`vllm_adapter.py:73`, `poc_rows.py:6`, `kernel_zoo.py:3`, `vllm_d9105ea80_sm89_eager.py:55`), `fixtures/verity-ir` (`conformance.py:45, 50`), and `docs/data/l8-nan-scan-*` (`conformance.py:75`; the data now lives in `data/`).

  *medium*; high (filesystem).
- **13 first-party `importorskip` guards whose targets all exist:** `observe/test_execution_label.py:11, 49`; `program/test_derive_negative.py:765, 1050`; `program/test_lifted_dense_b1_padrev.py:17, 18`; `program/test_lifted_tiny_padrev.py:24`; `program/test_vllm_bindings_pins.py:83`; `query/test_partition_structural.py:408`; `tp/test_tp_partial_source_mid_module.py:12, 143`; `tp/test_tp_partial_source_moe.py:13, 175`. They are "not merged yet" guards, and they turn an ImportError in first-party code into a skip. *medium*; high.
- **Tests silently disabled by in-repo paths that moved or were deleted** (read, not run):
  - `tests/input_provenance/test_root_policy.py:18, 21`: the module-level `skipif` requires `data/logs/m1`, which is absent, so the whole module never runs.
  - `tests/harness/test_coverage_workloads.py:51-53`: it looks for `workload_cov_b0_*` under `verity_vllm/observe/profiles/` (the files live in `workloads/`). Its first combination, `b1_c1024`, was never generated anywhere, so the in-loop `pytest.skip` always fires.
  - `tests/program/test_nan_conversion.py:26, 53`: it parametrizes over a glob of the absent `docs/data/tc-total-2026-09-07`, giving an empty parameter set.
  - `tests/harness/test_run_config_dry_run.py:163` requires `data/logs/m1` and `m1_ctl_tokens.json`.
  - `tests/observe/test_m1_log.py:95` asserts only if `data/logs/m1/tokens.json` exists.
  - `tests/program/test_conformance_record.py:13` points at the absent `fixtures/results/TA1-typed-b1-20260907`.
  - `tests/program/test_composition.py:35, 77-79`: `_hp_config` always takes its fallback because `vllm-poc/profiles/b1-hopper/static_config.py` is gone.
  - `test_derived_rows.py:18`, `test_rmsnorm_fused.py:16` and `observe/test_gen_ov_easy.py:75` put the absent `vllm-poc` on `sys.path`.

  *medium*; high (checked each literal path chain in `tests/` against the filesystem).
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

---

## Map 1: The de facto API

**Counts.**
- **Shell entry points:** 16 scripts, grouped in the table below.
- **`python -m verity_vllm.*` targets:** 47 distinct, invoked from `ops/`, harness subprocess calls, README and `tools/research`. `row_pod.sh` alone invokes 19 distinct modules 34 times.
- **argparse CLIs in harness:** 19 (20 modules have `__main__`).
- **`research` Tools:** 3 (`vllm.build`, `vllm.match`, `vllm.commit`). Each resolves to `bash run_row_v2.sh stage <stage> …`, which runs `row_pod.sh` or `tp_stage.sh`.
- **Environment variables:**
  - `row_pod.sh`: 45 caller-settable, 17 exported.
  - `run_row_v2.sh`: turns 23 flags into those env vars.
  - `tp_stage.sh`: 28 caller-settable.
  - `commit_delta.py`: 36 reads, 12 writes.
  - `hot_commit.py`: 17 reads.
  - Regression harness: 10 (`VERITY_REGRESSION`, `_ROWS_ROOT`, `_CANDIDATE`, `_CANDIDATE_CACHE`, `_ORACLE`, `_RECORD_ACTUAL`, `_VERIFY_ALL`, `_SCRATCH`, `_STOCH_JOBS`, `_TIERS`).
  - `REF_PRIMS_RECORD_DIR` for `test_ref_prims.py`.
- `row_pod.sh` references 126 distinct uppercase variable names in total, of which it assigns 63 itself. The brief's "108 env vars" presumably used a different cut; the 45 below are the ones a caller can set.

**Layering of the entry points today.**
1. `research run --tool vllm.<stage>` (`tools/research`) loads `integrations.vllm.verity_vllm.harness.research_tools`.
2. That runs `bash ops/run_row_v2.sh stage <stage> <row> <ROLE> <hf-repo> <rev> [--flag v …]`, which turns 23 flags into env vars.
3. That runs `ops/row_pod.sh <row> <ROLE> <hf-repo> <rev> <stage>`, or `tp_stage.sh` for `__tpN__` rows with N>1.
4. The runner makes 34 `python -m` calls, 24 `python -c` calls and 12 heredocs.

People also run steps 3 and 4 by hand, along with the variant scripts.

**Shell scripts by job.**

| job | scripts |
|---|---|
| Provision a pod | `pod_bootstrap.sh`, `pod_fa2_tap.sh`, `pod_fa3_tap.sh`, `pod_hidden_gpu.sh` |
| Run a row (Build + Match + Commit) | `row_pod.sh`, `tp_stage.sh`, `row_pod_tp2.sh`, `run_row_v2.sh` |
| Variant runs | `canary.sh` (checked against `known_roots.json`), `compiled_commit.sh`, `cov_pod.sh` |
| Negatives (hand-run) | `fa3_row_negatives.sh`, `stoch_negative_n3.sh`, `stoch_negatives.sh` |
| Gates / sealed verify | `pod_gate.sh`, `verify_lane.sh` |

**The 47 `python -m` targets by job, with invokers.**

| job | targets (invoked by) |
|---|---|
| Define a run (3) | `harness.workload`, `harness.coverage_workloads`, `harness.topp_split_probe` (all hand-run; only their own docstrings show the command) |
| Build a Program (7) | `harness.derive_step` (`row_pod` 7×, `tp_stage`, `stoch_negative_n3`, `rebuild_digest_gate`), `harness.launch_context` (`row_pod`), `program.global_program` (`row_pod`, `tp_stage`, `canary`), `query.cli` (`row_pod` 2×, `tp_stage`, `pod_gate` 2×, `compiled_commit`), `query.manifest.compiled` (`compiled_commit` 2×), `query.manifest.verify` (`row_pod`), `harness.rebuild_digest_gate` (nobody) |
| Capture a run (3) | `observe.m1_capture` (`run_config` 2×, `stoch_negatives`), `observe.resolve_log` (`run_config`), `tp.capture` (`tp_stage`) |
| Match (14) | `harness.run_config` (`row_pod`, `cov_pod`, `verify_lane` 2×, `stoch_negatives`, itself), `check.global_match` (`row_pod` 2×, `canary`), `check.program_compare` (`row_pod`, `stoch_negatives`), `check.stoch_recompute` (`row_pod`, `stoch_negatives`), `correspondence.batch_decomp` (`row_pod`, `stoch_negative_n3`), `check.census` / `check.noninterference` (`run_config` 2× each), `check.fold_compare` / `check.golden` / `check.replay` / `check.operand_provenance` / `input_provenance.root_policy` (`run_config`), `tp.match` / `tp.fold_match` (`tp_stage`) |
| Commit (5) | `harness.commit_delta` (`row_pod` 4×, `compiled_commit` 2×, `canary`, `fa3_row_negatives`, `hot_commit` 2×), `harness.hot_commit` (`row_pod` 2×), `harness.compiled_merge` (`compiled_commit`), `input_provenance.weights_of_record` (`row_pod` 2×), `tp.commit` (`tp_stage`) |
| Check / gate / plan (11) | `check.verdict` (`row_pod`), `check.holdout` (`cov_pod`, `verify_lane`), `check.protected` / `check.quarantine_lint` (`verify_lane`), `acquire.gate` / `correspondence.runtime_tree` (`pod_gate`), `harness.source_identity` (`row_pod`, `tp_stage`), `harness.target_family` (`row_pod` 2×, `tp_stage`), `harness.telemetry.admission` (`row_pod`), `harness.admission_bound` / `harness.admission_planner` (hand) |
| Report / record (4) | `harness.timeline` (`row_pod` 2×, `tp_stage`), `harness.research_result` (`row_pod`, `tp_stage`), `harness.research_outputs` (`run_row_v2` 2×), `harness.release_json` (hand; the library is used by `row_pod`/`tp_stage`) |

The Match verdict itself has no module: it is the heredoc at `row_pod.sh:686-800`.

**`row_pod.sh` positional arguments.** `<row-id> <ROLE> <hf-repo> <revision> [stages=build,match,commit]`. The model and revision are passed here and also declared in `workloads/<row>.json`, and nothing cross-checks the two.

**The 45 environment variables `row_pod.sh` reads** (line, default, what it controls).

| group | variable | line | default | controls |
|---|---|---:|---|---|
| environment | `PY` | 69 | `/workspace/venv312/bin/python` | interpreter for the GPU half |
| | `PY312` | 69 | `$PY` | interpreter for the CPU half (a leftover from the two-venv era) |
| | `VERITOR_REPO` | 49 | unset | legacy tree override; refused if it names another tree, then re-exported as this tree (`:52`) |
| | `HF_HOME` | 57 | `/workspace/hf` | checkpoint cache (exported with `HF_HUB_OFFLINE=1`) |
| | `CUDA_HOME` | 58 | `/usr/local/cuda` | toolchain for JIT builds |
| | `SWEEP_DIR` | 26 | `/workspace/cp/sweep` | evidence root; `$D = $SWEEP_DIR/<row>` |
| | `RESEARCH_RUN_DIR` | 85 | unset | set by the `research` runner; enables `result.json` |
| | `VERITY_TIMELINE` | 100 | `$D/timeline.jsonl` | timeline path, exported to every Python process |
| | `NATIVE_COLLECT_BUILD` | 72-73, 129 | release per-tree dir, else `/workspace/cp/nc_build` | native collector build dir |
| | `HIDDEN_GPU_BUILD` | 76 | unset | passed through to the `hidden_gpu` JIT |
| | `HIDDEN_SO` | 77-78, 213 | FA3 → hardcoded `.so` | FA matReq tap library |
| Build | `BUILD_TIMEOUT` | 346 | 900 s × env scale, capped at 4 h | derive timeout |
| | `BUILD_JOBS` | 377 | 1 | parallel derive jobs |
| | `LP`, `T` | 195 | from the manifest (longest prompt, cap − 1) | request-wrapper shape passed to `derive_step` |
| | `PROGRAM_DIGEST` | 918 | computed | Program digest handed to Commit |
| Match | `MATCH_IMPL` | 68 | `fast` | exported; Match implementation |
| | `MATCH_PIPELINE` | 68 | `shared` | exported; Match pipeline |
| | `MATCH_PHASE` | 548 | `all` (only `all` or `cpu`) | exported; `cpu` resumes over a preserved capture |
| | `MATCH_SNAP_STEPS` | 238 | `0,1` greedy / `all` stochastic | snapshot steps |
| | `MATCH_SNAP_MAX_BYTES` | 238 | derived by `run_config` | per-tensor snapshot cap |
| | `MATCH_TIMEOUT`, `COMPARE_TIMEOUT` | 537-538 | scaled by B and T, capped at 4 h | Match and compare timeouts |
| | `VERITY_INSTANCES_FORM` | 543 | `progressions` | exported; instance encoding (`run_config` defaults to `runs`) |
| | `ACQUIRE_MANIFEST` | 553 | `$D/manifest.json` if present | exported; acquisition manifest for the capture |
| | `ACQUIRE_ENGINE` | 553 | `v2` | **log line only** |
| | `WITHIN_STEP` | 594 | `dag` | `global_match --within-step` |
| Commit | `GPU_UTIL` | 79 | 0.5 | vLLM `gpu_memory_utilization` |
| | `PAIRS` | 79 | 3 | Δ_commit control/treatment pairs |
| | `COMMIT_TIMEOUT` | 817 | 2400 s × scale, capped at 4 h | Commit timeout |
| | `RETAIN`, `WINDOW_MB`, `WINDOW_SLOTS` | 831 | `host`, 256, 8 | collector retention and window; `commit_delta` turns them back into env |
| | `OPEN_AFTER_RELEASE` | 834 | 1 | openings after engine release |
| | `TAP_CAP_MB` | 839 | 2048 | FA2 tap cap |
| | `EXTRA_ENGINE_ARGS` | 842 | none | `k=v` engine args for Commit |
| | `EXTRA_COMMIT_ARGS`, `COMMIT_ARGS` | 845, 934 | none | raw `commit_delta` flags (two knobs, one job) |
| | `REPLAY_CACHE` | 851 | 1 | sampled-replay cache |
| | `REPLAY_ARGS` | 974 | none | raw replay flags |
| | `REQUIRED_CLASSES` | 852 | none | REL-02 override of the required classes |
| | `REQUIRED_MANIFEST` | 856 | `$D/manifest.json` of record | required-value manifest override |
| | `HOT_ENGINE`, `HOT_ROOT`, `HOT_IDLE` | 1086, 299, 1091 | 0, `/workspace/cp/hot`, 900 s | hot-worker Commit |

Exported constants: `PYTHONPATH=.:$VERITY_CORE:$VERITY_RESEARCH`, `HF_HUB_OFFLINE=1`, `VLLM_BATCH_INVARIANT=1`, `TOKENIZERS_PARALLELISM=false` (`:57`).

**Sketch of a small explicit API.** A few functions plus one CLI would need to cover the following. (Names are illustrative, not a proposal for module placement.)

~~~
RowSpec.load(row_id, workloads_dir) -> RowSpec     # the ONE row-id + workload parser: model, revision, dtype, hw, tp, batch,
                                                   # input/output, arrivals, sampling, exec; cross-checks id vs JSON vs checkpoint pin
RunEnv.resolve() -> RunEnv                         # interpreter, tree, core/research paths, HF cache, evidence root, native build dirs;
                                                   # recorded once (replaces PY/PY312/VERITOR_REPO/HF_HOME/CUDA_HOME/SWEEP_DIR/...)
precheck(spec, env) -> PrecheckRecord              # source identity + target family + advisory admission plan
build(spec, env, BuildConfig) -> BuildRecord       # derive_step xN + launch context + global Program + manifest + manifest verify
match(spec, env, build, MatchConfig) -> MatchRecord          # capture + resolve/fold/compare/replay/gates + THE verdict (now a heredoc)
commit(spec, env, build, match, CommitConfig) -> CommitRecord  # engine (cold or hot), collector config, pairs, openings, C2, verdict
report(record_dir) -> RowReport                    # timeline, research outputs/result, card
CLI:  verity-vllm row <row-id> [--stages build,match,commit] [--config row.toml] [--out DIR]
      verity-vllm {build,match,commit,check,report} ...     # the same functions, one stage each
~~~

The 45 knobs collapse into four typed configs:
- **`RunEnv`:** the 11 environment variables.
- **`BuildConfig`:** timeout, jobs, LP/T, digest.
- **`MatchConfig`:** impl, pipeline, phase, snapshot steps/cap, within-step, instances form, timeouts.
- **`CommitConfig`:** GPU utilisation, pairs, retain/window/slots/open-after-release/tap cap, engine args, required classes/manifest, replay cache/args, hot-worker settings, timeout.

Consequences of the move:
- The `research` Tool passes a config object instead of argv. That removes `run_row_v2.sh`, `research_tools._parse_flags` and the dead `VERITY_QUERY_ID`.
- `tp_stage.sh`, `compiled_commit.sh`, `canary.sh` and `cov_pod.sh` become `RowSpec` variants (tp > 1, exec = compiled, known roots, coverage case).
- `ops/` shrinks to provisioning (`pod_bootstrap.sh` and the tap builders) plus a short wrapper that resolves the venv and runs the CLI.
- Tests call these functions instead of regex-extracting bash or walking `commit_delta.main()`'s AST.

## Map 2: Configuration

**Where run configuration lives (12 places).**
1. **The row id**, i.e. the filename `workloads/<row>.json`, which carries 10 fields: `model_tag, dtype, hw, tp, batch, input, output, arrivals, sampling, exec`. It is parsed in 10 places (INTERNAL-DUP).
2. **`workloads/<row>.json`** (132 files):
   - `model` (all), `tokenizer_revision` (117) *or* `checkpoint_revision` (15), `sampling` (118), `seed` (119) *and/or* `seeds` (113), `engine_args_required` (112), `sweep` (97; holds `tp`, `row_id`, `execution`), `serving_profile`/`context_class`/`length_rule` (105), `expected_engine_steps` (105), `target` (11), `env_required` (2).
   - No file carries a top-level `dtype` or `tp`.
3. **`row_pod.sh` positionals:** `<ROLE> <hf-repo> <revision>`, which duplicates `model` and the revision from item 2.
4. **Environment variables:** 45 for `row_pod.sh`, 28 for `tp_stage.sh`, 23 via `run_row_v2.sh` flags, 36 read by `commit_delta`, 17 by `hot_commit`, 10 for regression.
5. **`manifests/checkpoints.json`**, the checkpoint pins, used as the default in 16 argparse definitions.
6. **`manifests/semantic-profiles/*.json`**, which set per-family kernel constants (FA version, splits, head size).
7. **Observe capture profiles.** These pin engine args, including `"dtype": "bfloat16"` (`coverage_workloads.py:132-133`). They are outside this slice.
8. **Hardcoded tables:**
   - `derive_step`'s `vm.PIN` (the B0 model, revision and dtype)
   - `target_family.DEVICE_FAMILY`
   - `research_tools.STAGE_KEY_FLAGS` defaults
   - `telemetry/admission.INVENTORY`
   - `run_config`'s `DEFAULT_K`, `DEFAULT_CHAINS`, `SNAPSHOT_CAP_FLOOR` (`:66-70`)
   - the admission constants in `commit_delta`
9. **`tests/regression/fixtures.toml`**, which holds reference artifacts, decisions and pins for each of 13 rows.
10. **`ops/known_roots.json`**, the canary's expected roots.
11. **`/workspace/cp/RELEASE.json`**, which feeds the hot key and provenance (`hot_commit.py:74`, `release_json.py`).
12. **The `research` store params**, a derived copy (`research_tools.py:57-102`).

**How many places define the same thing.**

| setting | places | detail |
|---|---:|---|
| model id | 7 | workload `model`; `row_pod.sh` `<hf-repo>` (and the `run_row_v2.sh` positional); row-id `model_tag` (short name, implicit mapping); `manifests/checkpoints.json`; `derive_step --model` (default `vm.PIN` B0); `research` key param `model`; `hot_commit.WORKLOAD_ENGINE_KEYS` (`model`, `repo`). The SmolLM2-135M literal appears 101 times in 90 files, 10 of them in library code. |
| TP degree | 7 | row id `__tpN__` (read by `run_row_v2.sh:95`, `workload.py:344`, `research_tools`); workload `sweep.tp` (`tp_stage.sh:47`); `WORLD` env; `row_pod_tp2.sh` (`WORLD=2`); `tp_stage.sh`'s fallback of 2; `derive_step --tp` (default 1); engine args (`tensor_parallel_size`, via the hot key). None of the 132 workloads disagree today. |
| row id | 6 | filename; `sweep.row_id` inside the JSON; `$SWEEP_DIR/<row>/`; `fixtures.toml` `rows."<row>"`; `tests/regression/expected/<row>.json`; `research` key param `row` |
| dtype | 6 | row-id token (a label: nothing in the execution path reads it); observe-profile pin `bfloat16`; `engine_args_required.dtype` (unused by any workload); the checkpoint itself (FP8 rows); `derive_step` `model_pin.dtype` (hardcoded `bfloat16`); `card.py` (reads engine args). Only the checkpoint and the profile actually decide it. |
| Python interpreter | 17 | 16 script defaults across three venv names, plus `research_tools.DEFAULT_PY` |
| evidence root | 32 occurrences / 24 files | `/workspace/cp/sweep` |
| query id | 74 occurrences / 27 files | `Q_module_body_v1` |

## Map 3: Data

| directory | contents | read by | kind |
|---|---|---|---|
| `data/hf_configs/` (12 files, 48 KB) | HF `config.json` copies per role | **library**: `observe/profiles/generic.py:26`, `profiles/__init__.py:51`, `dense_generic.py:117`; tests | package data (not packaged) |
| `data/l8-nan-scan-2026-09-07/` (2) | B0/B1 store NaN scans | tests only (`tests/program/test_nan_conversion.py:98`); the library's provenance string still says `docs/data/…` (`conformance.py:75`) | test data |
| `data/logs/m1.jsonl.gz` (532 KB) | the B0 capture log | **library CLI defaults and usage** (`check/census.py:550`, `fold_compare.py:3`, `replay.py:8`, `operand_provenance.py:3`, `golden.py:13`, `noninterference.py:37`, `protected.py:44`, `observe/resolve_log.py:3`, `adversarial.py:18`); tests | test data used as library defaults |
| `data/logs/m6/log.jsonl.gz` | a second capture log | **nobody** | evidence, unread |
| `data/logs/m1/`, `data/logs/m1_ctl_tokens.json` | (absent) | `noninterference.py:778` default; `fold_compare.py:3`, `replay.py:8` | **missing** |
| `data/rec/` (34, 544 KB), `data/census/` (33, 2.3 MB), `data/workloads_r12/` (1, 64 KB) | old records, census outputs, the R12 workload snapshot | **nobody** | evidence, unread |
| `data/contract/` (20, 328 KB) | contract probes, including `argmax_rule/probe_pinned.py` | **nobody**; `verify_lane.sh:59` excludes it | evidence plus stray code |
| `fixtures/B0-divergence-20260907T1604Z/` (12, 4.3 MB) | B0 divergence bundle (`cos_sin_cache.npy` …) | **library** `check/fold_compare.py:59`; tests `input_provenance/test_root_policy`, `test_analytic`, `program/test_composition` | evidence used as library and test input |
| `fixtures/W11-…T1800Z/` (2), `W11R-…T1802Z/` (2), `W11C-…T1900Z/` (3) | MUFU tables (Triton, CUDA) | **library** `check/fa2_attn_oracle.py:11`, `program/numerics/fa2_relation.py:117`, `rms_relation.py:37-38, 59`; `tests/program/test_composition.py` | package data (kernel-model tables) |
| `fixtures/verity-ir/…`, `fixtures/results/…` | (absent) | `rmsnorm_fused_sweep.py:48` (live constant); provenance strings in `conformance.py:45, 50`, `vllm_adapter.py:73`, `poc_rows.py:6`, `kernel_zoo.py:3`, `vllm_d9105ea80_sm89_eager.py:55`, `verity_vllm/__init__.py:21` | **missing** |
| `manifests/checkpoints.json` (64 KB) | checkpoint pins | **library**: 16 argparse defaults (`commit_delta`, `hot_commit`, `run_config`, `census`, `noninterference`, `protected`, `weights_of_record`, `m1_capture`, `vllm_adapter`, `engine_profile`, `tp/*`); tests | run definition |
| `manifests/semantic-profiles/` (6, 132 KB) | semantic profiles for llama and qwen2 | tests (`program/test_composition.py`: llama-v3, qwen2-v2, qwen2-hopper-v1); **3 files named only in `tools/move_map.txt`** | run definition (3 superseded) |
| `docs/data/ref-prims/` (31, 164 KB) | reference-primitive conformance records | **library** `program/registry/ref_prims.py:192`, `conformance.py:25`, `frontend/rules/vocab.py:86`, `reference.py:4`; **written** by `tests/program/test_ref_prims.py:43` | package data rewritten by a test |
| `docs/data/tc-*` | (absent) | provenance strings (`conformance.py:63`, `prims.py:203`, `hopper.py:77`, `fp8.py:125`, `derived_rows.py:461`) | **missing** |
| `workloads/` (132) | 97 row-grammar run definitions + 35 legacy `workload_*` | `row_pod.sh`/`tp_stage.sh` (`$WL`), `tests/regression/resolver.py:240`, harness/observe/admission tests, library defaults (`commit_delta.py:1039`, `hot_commit.py:175`, `noninterference.py:768`, `tp/capture.py:65`, `observe/m1_capture.py:122`, `vllm_adapter.py:85`); **7 legacy files named by nothing** | run definitions |
| `tests/harness/fixtures/admission/` (9) | planner calibration | **library `commit_delta.py:1793`**; tests | test data read by library |
| `tests/program/data/` (3 + `topp_split_fixture/` 6) | `fp8_block_operands.npz`, TopP split schedules | tests; library provenance strings (`sampled_replay.py:169`, `derived_rows.py:565`; `topp_split.py:71` cites a stale path) | test data |
| `tests/regression/fixtures.toml` + `expected/` (13) | reference artifact index and expected verdicts | regression harness | evidence index |
| `tests/tp/fixtures/tp2/` (7), `tests/query/gate/` (6) | TP2 and gate fixtures | tests | test data |
| `ops/known_roots.json` | expected canary roots | `canary.sh` | run expectation |
| `tools/` (3) | relayout tool, map generator, 1,229-line move map | `tests/program/test_relayout_map.py` only | one-shot dev tooling |

Flags:
- **Library reads `tests/`:** `commit_delta.py:1793`, the only live read. Library provenance strings also point into `tests/program/data`.
- **Library reads data outside the package:** `data/hf_configs`, `data/logs`, `docs/data/ref-prims`, `fixtures/B0-divergence`, `fixtures/W11*`, `manifests/`, `workloads/` (see LAYERING).
- **Data nothing reads:** `data/rec`, `data/census`, `data/contract`, `data/workloads_r12`, `data/logs/m6`, 3 semantic profiles, 7 legacy workloads.
- **Referenced but missing:** `data/logs/m1/`, `m1_ctl_tokens.json`, `fixtures/verity-ir`, `fixtures/results`, `docs/data/tc-*`, `docs/data/l8-nan-scan-*` (moved to `data/`), `tests/data/topp_split_fixture` (moved to `tests/program/data/`).

## Map 4: Tests

**Organisation** (see §3): each subpackage has a mirror directory under `tests/` (281 test files, 74k lines), plus root lints and census tooling. There are 7 regression tests with 20 helper modules.

**Kinds.** There is no marker for unit or GPU tests, so the following counts come from gating code rather than a clean partition.
- **Unit (CPU):** the default. About 46 files need torch through `importorskip` and run on the laptop's CPU torch.
- **GPU:**
  - 14 files check `cuda.is_available()` and 3 use `importorskip("vllm")`.
  - 18 import torch or vLLM at module top with no guard, so they error at collection without those packages.
  - There is no `gpu` marker.
- **Pod/evidence:**
  - About 34 files skip when an evidence path is absent: `out/gen` (23 files, gitignored and absent), `/workspace` (19), `/vault` (3).
  - The registered `pod` marker is applied only inside the regression harness (`test_regression.py:119`).
  - `@pytest.mark.slow` is unregistered (`program/test_derive.py:416`).
- **Regression:** `tests/regression/` is skipped unless `VERITY_REGRESSION=1` and is driven by `fixtures.toml` (13 rows, 9 decisions) through `resolver.py` (10 env vars). Its markers are `regression`, `pod` and `weak`.
- **Source-text and lint tests:** 12 files extract shell blocks, 4 files parse or `exec` `commit_delta.py`, about 24 files make source-text assertions, and there are 3 root lints (imports resolve, no dead modules, no by-name rules).

**Tests of code that no longer exists.**
- `acquire/schemes.py:77-121` (`veritor.*`)
- the skip reasons in `program/test_derived_rows_fp8.py:14` and `test_fp8.py:24` (`veritor.core`)
- `test_imports_resolve.py:15` (3 absent packages)
- `dead_code_keep.json:5-7, 11-15` (`fa2_commit`, `cb_a` paths)
- `program/test_relayout_map.py` (enforces a finished migration via `tools/`)
- the two padrev files whose base suites are gone (`test_lifted_workload_padrev.py`, `test_workload_compose_padrev.py`)

The inverse case also exists: 13 `importorskip` guards wait for modules that have since merged.

**Skipped and xfail.**
- 87 `pytest.skip(` calls in 44 files, 51 `skipif` in 37 files, and 71 `importorskip` in 59 files.
- 11 xfail markers, all strict "documented gap" markers:
  - `check/test_gen_adversarial.py:82, 100, 135, 165, 189` (HOLE-1..4)
  - `program/test_harden_guards.py:92, 104, 161, 171, 197`. `:161` says dtype is not an applicability constraint, and `:197` says `construction_version.mechanism` is a duplicated literal (`derive_step.py:81` vs `:656`).
  - `program/test_heldout_codec_compose.py:109`, a runtime xfail.
- `check/test_rev_r16_*.py` document xfails that have since been flipped to passing.
- The whole regression suite is skipped by default.

**Duplicates.**
- Seven `*_padrev.py` files (1,778 lines) re-test the lifting subjects independently.
- `tests/regression/checks/attempt_provenance.py:27-37` copies `research_tools.row_config`.
- Three run_config test files (`test_run_config_dry_run`, `test_run_config_load_stages`, `test_snapshot_cap`) are separate concerns, not duplicates.
- **Misplaced tests:** `harness/test_admit_r19_host_working_set.py` and `harness/test_prescribed_input_linkage.py` test `check/` and `acquire/`.

## Map 5: Harness vs. its name, `ops/` and `tools/research`

**Name vs job.** See §1. It is the production pipeline (Build, Match driver, Commit, verdict inputs, engine reuse, admission, provenance, telemetry, the research adapter) and a library for 11 lower-layer modules. It is not a dev harness, and README.md:86-90's rule ("a check that lives here is misfiled") is broken by `commit_delta`'s C2 oracle-compare, executed-prefix placement and verdict assembly (`:2128-2349`).

**Duplication with `ops/`.**
1. **Stage orchestration in both.** `row_pod.sh` (Build, Match, Commit), `harness/run_config.py` (19 Match stages), `harness/hot_commit.py` (Commit jobs), and `compiled_commit.sh` plus `harness/compiled_merge.py` (the compiled variant).
2. **Verdicts in both.** The Match verdict is `row_pod.sh:686-800` (bash heredoc); the Commit verdict inputs are built in `commit_delta.main()`; `check.verdict` is invoked from `row_pod.sh`.
3. **Defaults in both.**
   - `research_tools.STAGE_KEY_FLAGS` mirrors `row_pod.sh:79, 594`.
   - `DEFAULT_PY` mirrors `row_pod.sh:69`.
   - `HOT_ROOT`/`HOT_IDLE` are defaulted in `row_pod.sh:299, 1091`, `hot_commit.py:654, 665` and `commit_delta.py:3028`.
   - `VERITY_INSTANCES_FORM` is defaulted in `row_pod.sh:543` (`progressions`) and `run_config.py:1025` (`runs`).
   - `MATCH_PHASE` is accepted as `all|cpu` by `row_pod.sh:548` but documented as `all|gpu|cpu` by `run_row_v2.sh:14`, and `run_config` supports `gpu`.
4. **Row-id parsing in both:** `run_row_v2.sh:95` and `compiled_commit.sh:35` versus five harness parsers.
5. **Admission in both:** the advisory plan at `row_pod.sh:237` (`telemetry/admission`) and the in-process planner in `commit_delta` (`admission_planner` plus `admission_bound`).

**Duplication with `tools/research`.**
1. **Source identity.** `harness/source_identity.py` wraps `research.telemetry.source_identity` and adds `hidden_gpu` candidates. `acquire/native_host.py:1392` calls the harness copy.
2. **Spans and timeline.**
   - `research` wraps each stage in `span_start`/`span_end` events (`tools/research/src/research/telemetry/run.py:169, 206`), written to `events*.jsonl`.
   - Inside the stage, the harness writes `timeline.jsonl` (`timeline.py`) and per-component `Spans` (`spans.py`).
   - A row run under `research` therefore records the same stages twice in two formats, and `telemetry/admission.py:898` reads whichever exists.
3. **Resource telemetry.** `research`'s `cgroup.py`/`procs.py`/`sample.py` produce what `telemetry/admission.observe_increment_a` reads, while `observe_r17` re-derives the same from `timeline.jsonl` and logs.
4. **Tool adapter.** `research_tools`, `research_outputs` and `research_result` live in the integration. They import `research` at load time, `tools/research` imports them back under the `integrations.vllm…` module name (`tools_registry.py:26-28`), and the result schema is owned by `tools/research/src/research/result.py` (`research_result.py:1`).
5. **Run wrapping.** `run_row_v2.sh:50` locates or installs `research` on `PYTHONPATH`, and `row_pod.sh:57` adds `tools/research/src`.

<!-- APPEND -->
