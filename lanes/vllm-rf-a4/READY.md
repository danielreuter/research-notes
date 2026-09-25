---
id: vllm-rf-a4/ready
lane: vllm-rf-a4
kind: ready
status: DRAFT
created: 2026-09-25T08:50Z
---
# vllm-rf-a4 READY: re-home into the §5.1 package tree (file moves only)

- **Branch:** `lane/vllm-rf-a4`
- **Head:** `10996616`, on `origin/main` `00ffe398` (f1 merged; rebased at 06:55Z). All gates ran at this head.
- **Base for gates and diffs:** `00ffe398`. Since then, main has moved to `5631e667` (merges #19 and #20). Those
  merges touch only `backends/numerical/`.
- **Scope:** 500 files changed. There are 287 renames and 193 files edited in place (importers, strings, prose). 14
  package `__init__.py` files were added and 6 were removed; the removed ones belonged to the emptied `harness/`, `tp/`
  and `input_provenance/` packages and their test packages. No other file was deleted. No allowlist grew.

## Gate evidence

Every pod tree was built the same way (`tools/mkhead.sh`): copy the base tree `00ffe398`, remove `__pycache__` and the
numerics `cpp/build`, `git apply` the binary diff `git diff --binary -M 00ffe398 10996616`, and drop the emptied
directories. On the pods, head is `/workspace/head2` and base is `/workspace/basemain`. The trees also carry 29
`docs/data/ref-prims` JSONs that the base gate (b) run regenerated (`tests/program/test_ref_prims.py` writes them). No
regression check or stage reads them.

- **Lints:** 45/45 pass at head and at base (`vyv-rf-a4-cpu`; `evidence/gate_b/cpu-pod-logs.tgz`: `head2-lints.log`,
  `basemain-lints.log`).
- **Gate (b)**, xdist `-n 12 --dist loadfile`, head and base on the same pod (`vyv-rf-a4-cpu`), compared with
  `tools/jdiff_moved.py` (which wraps `baseline-jdiff.py` and maps base ids through the move list):
  - Base: 4,001 tests, 3,641 passed, 56 failed, 11 errors, 287 skipped, 6 xfailed. Head: 3,641 passed, 57 failed, 11
    errors, 286 skipped, 6 xfailed.
  - No new error, no new skip and no new skip reason.
  - **One new failure**, `tests/program/test_twins.py::test_check_writes_the_evidence_schema`. It fails whenever the
    numerics build directory starts empty, at base as well: the first process to JIT-build `tc_model` records
    `libraries["openmp"]`, which the test does not expect. The base tree on the gate (b) pod already held the built
    libraries and the head tree did not. Same pod (`vyv-rf-a4-reg`), empty `VERITY_NUMERICS_BUILD_DIR`: base and head
    both 19 passed, 1 failed (this test), 1 skipped. Rerun on the now-built directory: both 20 passed, 1 skipped
    (`evidence/twins/twins-fresh-vs-built.tgz`, `evidence/gate_b/twins-rerun.txt`).
  - `tests/observe/test_observer_encoding.py::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation` went
    from skipped to passed. It is known to depend on test order ("allocator did not reuse the pointer").
  - **Renamed test ids:** 942 in 85 files, listed old -> new in `evidence/gate_b/jdiff-head2.txt`. That file also lists 13
    parametrized ids whose parameter is a module path or file name, which differ only in the embedded path; all 13 pass
    on both sides. One test function was renamed, `tests/lint/test_p09_layering.py::test_interim_layer_map_names_existing_modules`
    -> `test_layer_map_names_existing_modules`, together with the map it checks.
  - XML: `evidence/gate_b/gate_b-xdist-{base-00ffe398-samepod,head-10996616}.xml.gz`, plus the early head run at
    `14b0cf9f`, whose failures `756d04d2` and `10996616` fixed.
- **Gate (a) T0+T1:**
GATE_A_RESULT
- **GPU smoke, row #101** (`vyv-rf-a4-g1`, 1x L40S; `row_pod.sh … build,match,commit`, PAIRS=1, through the moved
  entry points `verity_vllm.pipeline.{cli,match,hot,commit}`), head, then base on the same pod:
  - Both exit 0. run_root `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` on both, equal to the
    record. Program `ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b` and manifest
    `90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac` on both. `commit_pass` true, with every Commit
    check PASS. Build digest `03ace66f1c80b04a` and workload digest `a2b43bde001d335a` are equal.
  - A normalized diff of every output JSON (`evidence/gpu_r101/r101_normdiff.txt`) finds 42 files the same. The
    differences are code provenance, measurements and per-run values. Code provenance covers
    `construction_version` (and the `artifact_identity` and `identity` fields built on it), the registry digest,
    `derived.tool`, module names in the match spec's `driver` (so the spec digest `8de1a58e…` -> `d14c9938…`), the
    declaration evidence module (`properties.fa_tap_exactness`), and `hidden_gpu`'s path and file hash. Measurements
    are timings, calibrated byte bounds and gc counts. Per-run values are internal request ids and paths. The
    workload's component `descriptor.json.gz` differs only in `annotations.derive.registry`.
- **`python -m` in `ops/*.sh`:** all 33 targets resolve at head, and each has a `__main__` guard (`tools/pym.txt`).

## What changed (one commit per destination package; each importable and pushed)

| commit | scope |
|---|---|
| `2b8836c7` | `harness/` -> `pipeline/`: `derive_step` -> `build`, `run_config` -> `match`, `hot_commit` -> `hot`, `commit_delta` -> `commit`, and `harness/target_family.py` -> `verity_vllm/target_family.py`. Also `build_paths.py` -> `pipeline/layout.py`, `query/cli.py` -> `pipeline/cli.py`, `program/global_program.py` and `observe/m1_capture.py` -> `pipeline/`, and `tp/{capture,commit,match,fold_match}` -> `pipeline/tp/`. Each file moved whole. |
| `f2f1bf0a` | engine: `observe/{vllm_adapter,engine_profile,arrivals,engine_driver}` and `observe/profiles/` (including `hf_configs`) -> `engine/`, plus `tp/worker.py` -> `engine/rank_worker.py`. This covers the `EXTENSION` string module path. |
| `c397545b` | program: `numerics/` (with `tables/` and `cpp/`) -> `program/backends/` (renamed in `22f5bc58`); `check/{twins,relations}` -> the same place; `input_provenance/analytic` -> `program/model.py`; `correspondence/emit` and `tp/export_ops` -> `program/frontend/`. |
| `dd83b50b` | `query/v1_bridge.py` -> `query/required.py`. |
| `ad847624` | observe: `fold`, `tree`, `views`, `memory`, `resolver`, `patterns` and `tp/collective_pattern` -> `observe/fold/`; `correspondence/{runtime_tree,chunk_attribution}` -> `observe/{runtime_tree,chunks}.py`. |
| `22f5bc58` | `program/backends/` -> `program/kernels/`. This rename follows an **owner decision of 2026-09-25**, relayed by the vLLM coordinator at 06:35Z. SYNTHESIS records it at line 641. |
| `9b755a43` | `acquire/{native_host,native_collect,leafhash,native_jit,flush_points,hidden_gpu_src,*.cu,*.cpp}` -> `commit/committer/`. |
| `32f783c5` | the sources (hidden FA tap, MoE, compiled, `tp/partial_source`) -> `acquire/sources/`; `query/manifest/compiled.py` -> `acquire/compiled.py`. |
| `c95d3199` | test fixture: `test_commit_tree_of_record`'s fake tree creates `pipeline/tp/`. |
| `2bdfd9ce` | `global_match`, `global_match_fast`, `program_compare`, `correspondence/batch_decomp`, `tp/{rank_match,xrank_collectives}` -> `check/match/`; the replay drivers and `query/vu_query` -> `check/replay/`; `input_provenance/{weights_of_record,root_policy}` -> `check/`. |
| `e6f19e42` | `check/{noninterference,census,kernel_allowlist,golden(+corpus),holdout,difftest->admission,quarantine_lint,protected,fa_tap_exactness}` -> `properties/`. |
| `6a0097f6` | `tp/{collective_record,collective_sites,embedding_shard}` -> `collectives/`; `tp/{analyze,collective_link}` -> `tests/collectives/`. |
| `34400229` | lint: P9 checks the target layer order. `_imports.LAYER` is now the package map, which replaces `INTERIM_LAYER`. See "P9" below. |
| `14b0cf9f` | README layout, and short-path prose that names the new files. |
| `756d04d2` | drops the P11 allowlist entry of the deleted `verity_vllm/tp/__init__.py`. |
| `10996616` | test files follow their subject into the mirrored package paths, with file names kept. There are 89 moves: `tests/harness` -> `tests/pipeline`, `tests/input_provenance` -> `tests/check` and `tests/program`, `tests/tp` -> the package of each subject, committer tests -> `tests/commit`, property tests -> `tests/properties`, profile and adapter tests -> `tests/engine`, and so on. It also fixes three fixture paths that encode module depth. |

**P9.** `_imports.LAYER` maps each package to its layer, following the order: tests > pipeline > check|properties >
acquire > observe|commit > engine > query|correspondence > program > collectives > config > core. There are three
exceptions, and each goes where §5.2 sends its module: `query.boundary`, `query.partition` and
`program.frontend.liveness` go to core, and `target_family` goes to config. The `program/kernels/` directory stays in the
`program` layer, because the P9 order has no separate backends or kernels layer. Package cycles are computed over the
top-level package. The p09 allowlist went from 179 to 177 entries: package cycles dropped from 22 to 20, while module
cycles (10), layer entries (100) and the other kinds are unchanged.

**Allowlists** (base -> head): p06 221 -> 217, p08 305 -> 300, p09 179 -> 177, p11 718 -> 715, `by_name_allowlist` 221 ->
219, `dead_code_keep` 23 -> 21 modules. The other allowlists are unchanged: p01 33, p02 1, p03 35, p04 64, p05 2, p07 355,
p10 76 and p12 15. The P10 line counts are unchanged, because every rewrite kept its line count.

## Code identities (before -> after; allowed to change)

These were computed on the same pod from the base tree and the head tree (`evidence/ident/ident-{basemain,head2}.json`,
script `tools/ident.py`).

| identity | base `00ffe398` | head `10996616` |
|---|---|---|
| `code_identity`, which is also the hot-commit key and the research Tools' closure (VLLM_BUILD/MATCH/COMMIT) | `248d66214aa006ef…` (1,170 files) | `a2cf5fc7267c3c4b…` (1,178 files: +14 package inits, -6) |
| `construction_version.sources_sha256` | `9738a467dadc4230…` | `53cfbe1cff286914…` (the listed source paths moved) |
| `registry_version.digest` | `a2204fa7c7180d2e…` | `beb5d5f73aff6abd…` (six import lines in `registry/prims.py`; `b1.py` unchanged) |

## Deferred (per the brief; each file was moved whole)

- **Module merges and splits:**
  - `global_match_fast` into `global_match`.
  - `determinism.py` (`value_check` + `compiled_value_check` + `oracle_compare`).
  - `verdict` absorbing `commit_verdict` and `gates`.
  - `check/provenance.py` (`weights_of_record` + `root_policy`, now separate files in `check/`).
  - One correspondence reader (`reader_for_query` + `reader_for_acquire`).
  - `observe/fold/patterns/`, one module per kernel family; `collective_pattern` sits in `observe/fold/` for now.
  - `global_program` into `pipeline/build.py` (now `pipeline/global_program.py`).
  - `m1_capture` and `pipeline/tp/capture` into the capture stage of `pipeline/match.py`.
  - World-parametric `pipeline/` drivers from `pipeline/tp/{capture,commit,match,fold_match}`.
  - The three-way `commit_delta` split. The file is `pipeline/commit.py` and holds verdict, C2, prefix, binding record and openings.
  - `research_*` -> `research`, admission x3 -> `admission`, `source_identity` + `release_json` + `experiment.code_version` -> `identity`, `workload` + `coverage_workloads` -> `workloads`, `card` -> `report`, and spans/timeline -> one telemetry module.
  - `target_family` -> `config.py` (now `verity_vllm/target_family.py`, in the config layer).
  - The one collectives hook.
  - `twins` and derived rows as kernels modules.
- **`commit/scheme.py`** and the move onto `verity.commitments`. The leaf and root rules still live in `semantic_layout`, `hidden_stream`, `hidden_engine`, `padding_steps` and `fasttree`.
- **Modules §5.2 sends to core:** `query/boundary.py` and `query/partition.py` (to `verity.ir`), `program/frontend/liveness.py`, and `binding`'s challenge. P9 already places them in core.
- **`program/kernels/cuda/*.cu`** go to pod probes outside the package. There is no destination yet, so they stayed with the kernels.
- **Data:** `docs/data/ref-prims` -> `program/registry/`. No library code reads it; `tests/program/test_ref_prims.py` writes it.
- **Ops scripts becoming CLI subcommands** (`row_pod.sh`, `tp_stage.sh`, ...).
- **Deletions:** `poc_rows`, `poc_verify_bindings`, most of `compiled_fx_kernels`, `resolve_decomp`, `batch_candidate`, `capture_identities_program`, `reference_engine*`, `engine_rs/`, `rebuild_digest_gate`, `topp_split_probe`, `row_pod_tp2.sh` and the negative-campaign scripts.

## Notes for the merge

- **Provenance strings.** Some strings name module paths and are written into records at run time, for example
  weights_of_record's `derived.tool` and match's `impl_info` module. These now name the new modules. They feed no
  Definition id, Program digest, manifest digest, commitment root or leaf id; the GPU row and gate (a) check this.
- **Strings kept as written:** the historical record strings. These are the v1_bridge method string in
  `pipeline/commit.py`, `acquire/sources/partial_source.py:584`, the GEMMA2_2B quarantine `stamped_by` and
  `gemm_targets` `evidence`, which lands in `describe()`.
- **Prose** that names old module stems as bare words (for example "derive_step", "run_config", "hot_commit",
  "difftest", "tp2_worker") was not rewritten. Only paths and dotted names were.
- **Test ids renamed:** 942 test ids in 85 files. The full old -> new list is in `evidence/gate_b/jdiff-head2.txt`. The
  parametrized ids that embed module paths are listed there too (13 each side, same outcomes).

## Found, not fixed (pre-existing)

- `engine/engine_profile.py:130` `TP_WORKER_EXTENSION = "verity_vllm.tp.poc_tp_worker…"` names a module that has never existed.
- `pipeline/commit.py` imports `workload_target`, which is absent. The import is inside try/except.
- `engine/engine_profile.py:102`'s comment names `verity_vllm/input_provenance/add_checkpoint.py`, which never existed.
- `check/match/global_match_fast.py:24` names mfast's `verity_vllm/harness/match_diff.py`.
- The `commit/__init__.py` docstring describes native_collect, an artefact of the old relayout.
- `tests/program/test_twins.py::test_check_writes_the_evidence_schema` depends on process state. The first process to
  JIT-build `tc_model` records `libraries["openmp"]`, and the test then fails. It fails at base too on a tree without
  the JIT build (`/workspace/basefresh`), and it passes at base and at head once the library exists
  (`evidence/gate_b/twins-rerun.txt`).
- `tests/commit/test_roundtrip.py::test_transient_storage_is_released` sits 152 B over its tracemalloc bound in one
  xdist ordering (early head run). It passes alone at base and at head, and it passed in the head run.
