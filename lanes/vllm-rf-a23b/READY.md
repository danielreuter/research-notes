---
id: vllm-rf-a23b/ready
lane: vllm-rf-a23b
kind: ready
status: draft (gates running)
created: 2026-09-24T20:50Z
---
# vllm-rf-a23b READY: dead code, data and paths

a23b took over from a23 at `c1cf11ef`. a23 did part 1 (dead code out, moves to tests); a23b did part 2 (data and paths).

- **Branch:** `lane/vllm-rf-a23b`
- **Head:** `4e26d864` (tree `a8917dce`)
- **Base for gates and diffs:** `72884c8a`

## Gate evidence

_Pending: filled in when the runs finish._

## What changed

### Part 1 (a23, `b9b23ebf`..`c1cf11ef`)

- `b9b23ebf`: deleted `integrations/vllm/tools/` (the finished relayout tooling, 3 files, 3,068 lines) and `tests/program/test_relayout_map.py`.
- `84c691c9`: deleted the CMT-1 committer (`commit/reference_engine/`, `reference_engine_adapter.py`, the `cmt_ref_*`
  committers in `harness/commit_delta.py`), `commit/engine_rs/`, their tests, and the CmtRef/veritor adapters in `schemes.py`.
- `446fe8b6`: deleted `poc_rows`, `poc_verify_bindings` (`dist_identity` moved to `observe/engine_profile.py`),
  `compiled_fx_kernels` (`normalise_kernel` moved to `check/kernel_identity.py`), `batch_candidate`,
  `capture_identities_program`, `rebuild_digest_gate` and `ops/row_pod_tp2.sh`, plus their test parts, census roots, keep
  list and allowlist entries.
- `c1cf11ef`: moved test-only modules next to their tests: `fa2_prototype/` and its fixtures, `stream_merkle`, `synthetic`
  to `tests/commit/`; `adversarial` to `tests/check/`; `fa2_attn_oracle` to `tests/acquire/`; `b1_authored`,
  `serve3_authored`, `inductor_models` to `tests/program/`. `commit/hidden_engine.py` was trimmed to what the committers import.

### Part 2 (a23b, `96c12c0b`..`4e26d864`)

- `96c12c0b`: the W11, W11R and W11C MUFU and RMS tables (7 `.xz` files) moved with `git mv` to
  `verity_vllm/program/numerics/tables/<fixture id>/`. `fa2_relation.tables_dir()`, `rms_relation.tables_dir()` and the
  `prims.MUFU_TANH_TABLE_DIR` default now use `importlib.resources.files(__package__)`. The env overrides
  (`VERITY_MUFU_TABLES`, `VERITY_RMS_TABLES`, `VERITY_MUFU_TANH_TABLES`) and digest pins are untouched. The bytes are
  unchanged (same sha256).
- `928813d3`: removed the dead `sys.path` inserts in `program/registry/prims.py`, `check/twins.py` and
  `commit/padding_steps.py`. `hidden_gpu.py` keeps its insert of its own tree and drops the `vllm-poc` entry (no tree of
  this repo has `vllm-poc/`). This commit also carries the two `git mv` renames of `dfb8cd8b`, which were staged by
  accident; it was not rewritten.
- `ed31d31c`: new `verity_vllm/config.py` (25 lines), the one helper that locates the source tree:
  `ROOT = Path(str(resources.files("verity_vllm"))).resolve().parent`, `MANIFESTS`, `WORKLOADS`, `CHECKPOINTS` and
  `checkpoints_hf_home()`. It replaces `Path(__file__).parents[N]` in `check/golden.py`, `check/protected.py`,
  `check/quarantine_lint.py`, `harness/workload.py` (and its `case_for` `sys.path` insert), `harness/coverage_workloads.py`,
  `observe/profiles/dense_generic.py`, `program/registry/rmsnorm_fused_sweep.py`, `input_provenance/weights_of_record.py`,
  `tp/worker.py` and `harness/source_identity.py`. `dense_generic` also drops its `data/hf_configs` fallback: every role
  there also has a copy in the shipped `observe/profiles/hf_configs/`, which is searched first.
- `dfb8cd8b`: the B0 cos_sin table moved to `check/tables/B0-divergence-20260907T1604Z/cos_sin_cache.npy`
  (`fold_compare.DEFAULT_COS_SIN`), and the planner calibration moved to `harness/planner_calibration.jsonl`
  (`admission_planner.CALIBRATION`). `harness/commit_delta.py` no longer reads `tests/`. `fold_compare` lost its laptop
  `DEFAULT_RECORD`; `--record` now defaults to none. Both files keep their sha256 (`7f789108...`, `fac80635...`).
- `24466fdd`: `engine_profile.apply_env()` and `beyond_gemm.load_norm_weights()` take the HF_HOME default from
  `manifests/checkpoints.json` (`"hf_home": "/workspace/hf"`, the same value) instead of a literal.
- `6da1b430`: `tests/program/test_composition.py` loads the FA2 MUFU tables through `fa2_relation.tables_dir()`.
- `ed81ba7f`: the profile lookup error messages and docstrings stop naming `data/hf_configs` (message text only).
- `4e26d864`: `weights_of_record._default_manifest()` walked `dirname(__file__)/../..`; it now tries
  `config.CHECKPOINTS`, then the cwd, in the same order.

`pyproject.toml` is unchanged: hatchling's wheel with `packages = ["verity_vllm"]` ships every non-ignored file under the
package. `uv build --wheel integrations/vllm` on the pod gave `verity_vllm-0.1.0-py3-none-any.whl`, which contains all
7 `.xz` tables, the `.npy`, the `.jsonl`, `corpus_coverage.json` and the tanh tables.

### Counts (rename-aware, `72884c8a`..`4e26d864`)

| | files | lines |
|---|---|---|
| library files deleted (`verity_vllm/`) | 17 | 4,358 |
| lines removed / added in modified library files | 27 files | -163 / +132 |
| `integrations/vllm/tools/` deleted | 3 | 3,068 |
| moved from `verity_vllm/` to `tests/` | 18 text + 7 binary (`.npz`) | 8,361 |
| data moved into the package | 9 (7 `.xz`, 1 `.npy`, 1 `.jsonl`) | binary / data |
| whole lane | 113 files changed | +231 / -8,479 |

Part 2 alone (`c1cf11ef`..`4e26d864`): `verity_vllm/` 33 files +102/-81; `tests/` 7 files +8/-19.

### Path smoke at the head (CPU pod, HF_HOME unset, cwd `/tmp`)

`smoke_paths.py` beside this note, run in a fresh tree at `4e26d864`: `config.ROOT` is the tree's `integrations/vllm`;
`MANIFESTS`, `WORKLOADS` and `CHECKPOINTS` exist; `checkpoints_hf_home()` and `apply_env()` give `/workspace/hf`;
`_default_manifest()` gives the tree's `manifests/checkpoints.json`; `workload.CORPUS` exists; `case_for(SmolLM2)` is
`B0`; the cos_sin table and calibration resolve with sha256 `7f7891085473...` and `fac806350bec...`;
`fa2_relation.tables_dir()` lists the two W11 tables; `rms_relation.tables()` loads.

No GPU smoke Build was needed. The GPU-only paths are the JIT build in `hidden_gpu.py` and native_host's
`_gpu_ext_load`, and neither changed. The one `hidden_gpu.py` change is the dropped `vllm-poc` entry, and the module-level
import (the identity checks and the insert) runs on CPU in `test_source_identity.py`.

## Remaining grep hits in `verity_vllm/` and why they stay

`rg -n 'sys\.path\.(insert|append)|parents\[' verity_vllm` and `rg -n "['\"](/workspace|/vault|/Users|/home|/root|/tmp)" --type py verity_vllm`:

- `acquire/hidden_gpu_src/hidden_gpu.py:41` `sys.path.insert(0, REPO)`: hidden_gpu is imported as a top-level module from
  either the shipped copy or the copy materialised at `out/gen/r9/cmt-hidden/src`. REPO is found by walking up to the
  directory that holds `verity_vllm/`, so both copies give the same tree. This is the source-identity design, and the tests
  pin it.
- `acquire/native_host.py:1387` `_sys.path.insert(0, src_dir)`, and the dirname climb on line 1380: this puts the chosen
  hidden_gpu copy on the path. GPU-only, source-identity design, unchanged.
- `harness/source_identity.py:73-74` `root.parents[1]`: normalises a caller-supplied `--tree` given as
  `<repo>/integrations/vllm`. It is not anchored at `__file__`. `TREE = INTEGRATION.parent.parent` (line 46) derives the
  repo root from `config.ROOT`.
- `harness/derive_step.py:67` climbs from `verity.ir.__file__` to hash the builder sources. f24 owns derive_step's
  identity parts.
- `harness/research_tools.py:39` `DEFAULT_PY = "/workspace/venv312/bin/python"`: mirrors `ops/row_pod.sh:69` and is
  recorded in the pins probe.
- `harness/release_json.py:35-37, 212`: defaults of the pod-release CLI (`/workspace/cp/...`), which only runs on a pod.
- `harness/hot_commit.py:63, 74, 654, 665` and `harness/commit_delta.py:3020` (`HOT_ROOT`): f24 owns `hot_commit.py`.
  Each can be overridden through the environment.
- `build_paths.py:11` and `hidden_gpu.py:18`: docstring examples, not defaults.
- `ops/*.sh` (`canary.sh`, `tp_stage.sh`, `row_pod.sh`, `pod_bootstrap.sh`, `cov_pod.sh`, `pod_hidden_gpu.sh`): pod runner
  scripts, not library defaults.

All 17 `__file__`-anchored `parents[N]` uses at base are gone. So is the one `os.path` equivalent (`weights_of_record`).
Of the 8 `sys.path.insert` calls at base, 4 were removed (prims, twins, padding_steps, workload) and 2 went with part 1
(`hidden_engine`, `reference_engine`). `hidden_gpu` was reduced to its own tree, and `native_host` stays.

## What deliberately didn't change

- Run definitions stay where they are and are located through `config.ROOT`: `manifests/`, `workloads/` and `data/logs/`.
  `golden`'s frozen `corpus.json` names `data/logs/...`, `protected.py` protects `data/logs/*`, and the CLI defaults are
  relative to the cwd.
- **Data the library does not read (listed, not moved or deleted):**
  - `data/hf_configs/` (12 files): read only by tests (`test_gen_llama`, `test_gen_ln`, `test_gen_dense2`,
    `test_ship_roots`). The library fallback was dropped because the shipped `observe/profiles/hf_configs/` holds every role.
  - `docs/data/ref-prims/` (31 files): named in docstrings, and written and read by `tests/program/test_ref_prims.py`.
  - `data/census/` (33), `data/rec/` (34), `data/workloads_r12/` (1): nothing reads them.
  - `data/contract/` (20): named only in `ops/verify_lane.sh`'s sparse-checkout patterns.
  - `data/l8-nan-scan-2026-09-07/` (2): read by `tests/program/test_nan_conversion.py`.
  - `fixtures/B0-divergence-20260907T1604Z/` remainder (11 files): the eager/compiled operands and `fixture.json`.
    `test_composition` looks for an `index.json` there that isn't in the tree (it skips at base, too).
- The env overrides and digest pinning of the tables (f3's), `acquire/native_collect.py` and the layout env vars in
  `commit/padding_steps.py` (f3's), and the value check in `commit_delta.py` (f1's).
- Record content, not code: the `CORE` label in `tests/program/padded_commit_tiny.py` still names `stream_merkle`, and
  the frozen `why` strings in `tests/regression/expected/*.json` still name `row_pod_tp2.sh`. The live string in
  `checks/manifest_digest.py` names `tp_stage.sh`.
- `registry_version()` hashes the source of `registry/prims.py`, so the `sys.path` edit there changes that digest. It is
  export-report provenance only: no Program or manifest digest, and no regression check, reads it.

## Rebase note

When `main` moves (a1 merges first): rebase, add `"verity_vllm.config": "config"` to a1's `INTERIM_LAYER`, and delete the
lint-allowlist entries for the modules this lane deleted or moved.

## Found, not fixed

- `backends/sp1/common/src/ftz.rs:41`: a comment names the old `vllm-poc` W11 table path.
- `program/registry/conformance.py:75`: the record string names `docs/data/l8-nan-scan-2026-09-07/`, but the files are at
  `data/l8-nan-scan-2026-09-07/`.
- `fixtures/B0-divergence-20260907T1604Z/.../fixture.json` still lists `cos_sin_cache.npy` as an operand beside it. That
  file now lives in the package.
- `rmsnorm_fused_sweep.BUNDLE` and `NORM_WEIGHTS` point at files that aren't in the tree (the test skips: "B0 bundle
  not present").
- `tests/program/test_composition.py`: its `W11`, `W11R` and `B0_DIV` fixture paths (`natural/`, `stress/`,
  `index.json`) aren't in the tree, so those tests skip at base and at head. The module docstring still names
  `fixtures/W11-*`.
- `input_provenance/test_analytic.py::test_check_cos_sin_against_the_captured_b0_table` fails at base (29,154 words
  differ) and at head. The table bytes are the same.
