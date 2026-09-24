---
id: vllm-rf-a23b/ready
lane: vllm-rf-a23b
kind: ready
status: complete (gates (a) T0+T1 and (b) green; rebased onto main, lints 41/41)
created: 2026-09-24T20:50Z
---
# vllm-rf-a23b READY: dead code, data and paths

a23b took over from a23 at `c1cf11ef`. a23 did part 1 (dead code out, moves to tests); a23b did part 2 (data and paths).

- **Branch:** `lane/vllm-rf-a23b`
- **Head:** `9be6e462` (tree `9cdc02c5`), rebased onto `main` `58e4c1aa`. See "Rebase onto main" below.
- **Pre-rebase head, where gates (a) and (b) ran:** `748d71c5` (tree `1158eb69`). `verity_vllm/` is identical at both
  heads except for one blank line in `tp/worker.py`.
- **Base for gates and diffs:** `72884c8a` (tree `7db3f3ba`)

## Gate evidence

Both gates ran at `748d71c5` on `vyv-rf-a23b-big` (RunPod `n2ei0ahhoeu80j`). A base run of each gate ran on the same pod
with the same flags. After the rebase, gate (b) and the lints ran again at `9be6e462`. Scripts beside this note:
`gate_a.sh`, `gate_b.sh` (a1's with the log directory moved), `prefetch.sh` and `lint_fix.py`.

**Summary:** gate (a) T0+T1 is green, with the same outcome as the same-pod base on all 158 tests. Gate (b) has no new
failure, error, skip or skip reason outside baseline.md's list, at both heads. The lints are 41/41 at `9be6e462`.

**Pod and environment.** cpu3m, 64 vCPU, 512 GB, AMD EPYC 9655 with AVX512, Linux 6.8.0-87, glibc 2.35. The venv comes
from `pod_bootstrap.sh --cpu` (BOOTSTRAP-OK) plus `pytest-xdist==3.8.0`, with `xgrammar` pinned to 0.2.7. Its
`uv pip freeze` is identical to a1's `baseline-freeze.txt`:

- python 3.12.14;
- torch 2.13.0+cu129 (CPU only);
- vllm 0.28.1rc1.dev472+gd9105ea80;
- triton 3.7.1;
- numpy 2.3.5, transformers 5.17.0, tokenizers 0.23.2, safetensors 0.8.0, huggingface-hub 1.33.0;
- pytest 9.1.1, pytest-xdist 3.8.0.

Trees:

- Head was shipped with `research pods sync` (tree `1158eb69` plus the sync stamp files).
- Base was built on the pod by reverse-applying `git diff -M --binary 748d71c5 72884c8a` (verified tree `7db3f3ba`,
  2,814 files; its stamp names `72884c8a`).
- Neither tree has a `.git`, as in a1's baseline. Each run used its own copy.

### Gate (b): `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`

| run | total | passed | failed | error | skipped | xfailed |
|---|---|---|---|---|---|---|
| head `748d71c5` | 3,833 | 3,476 | 54 | 11 | 286 | 6 |
| rebased head `9be6e462` (with main's 41 lint tests) | 3,874 | 3,515 | 56 | 11 | 286 | 6 |
| base `72884c8a`, same pod | 3,904 | 3,534 | 56 | 11 | 297 | 6 |
| a1's base (baseline.md, xdist) | 3,904 | 3,536 | 54 | 11 | 297 | 6 |

Comparison with a1's `baseline-jdiff.py` (exit 0 in every direction):

- **Head vs a1's base:**
  - 0 new failures or errors, 0 new skips and 0 new skip reasons.
  - The 65 failures and errors are exactly baseline.md's 65.
  - 71 tests exist only in the base. They are all tests of code deleted in part 1: `test_relayout_map` 8,
    `test_torch_sha256` 23, `test_commit_host` 9, `test_triton_sha256` 1, the `cmt_ref_engine` scheme cases of
    `acquire/test_security.py` 15, `test_gen_ovbatch`'s batch_candidate tests 3, and `test_derive_negative`'s
    corr-binding tests 12.
  - One outcome change: `observe/test_observer_encoding::test_weakref_death...` went from skip to pass. It depends on
    test order at base.
- **Head vs the same-pod base:** 0 new failures and 0 new skips. The gc-freeze pair in
  `harness/test_admit_r19_host_working_set.py` passes at head and fails at base; that pair depends on test order at base.
- **Same-pod base vs a1's base:** only the gc-freeze pair differs.
- **Rebased head `9be6e462` vs a1's base** (23:28-23:41Z; a fresh copy of the lint-verified tree):
  - 0 new failures and 0 new skips.
  - The 67 failures and errors are baseline.md's 65 plus the gc-freeze pair (order-dependent; it failed at the
    same-pod base too).
  - The 41 lint tests are new and all pass.
  - One skip reason is new, and it comes from main. `test_ship_roots.py::test_ship_pack_carries_out_gen_hf_configs`
    skipped at base with "not a git checkout (pod tree)". Main's `e0c7bfe9` rewrote its guard, so it now skips earlier
    with "this checkout has no record_v5/ship.sh or data/hf_configs". No tree here has `record_v5/`, base included.
    This lane doesn't touch that test. The file's other two tests fail as on baseline.md's list.
  - The `fold_compare` tests (`check/test_compare_*`, `test_replay_*`, `observe/test_fold_m1.py`, and others) and
    `test_ship_roots.py` ran in this run, which is the coordinator's rerun condition. None of them fail outside the
    list.

The JUnit XMLs are beside this note: `gate_b-xdist-head-748d71c5.xml.gz`, `gate_b-xdist-rebased-9be6e462.xml.gz` and
`gate_b-xdist-base-72884c8a-samepod.xml.gz`.

An earlier gate (b) run at `6da1b430`, on the first pod, found the one regression this lane introduced:
`harness/test_source_identity.py::test_shipped_tree_{takes_its_sha_from_research_source_sha,still_refuses_a_foreign_package}`.
The test's stub "shipped tree" copied only `source_identity.py`, which now imports `verity_vllm.config`. `748d71c5`
makes the stub copy `config.py` too. The production path is not affected, because a shipped tree is the whole package.

### Gate (a): `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`

**Green.** Head and base give the same outcome on all 158 tests.

| run | total | passed | failed | error | skipped | time |
|---|---|---|---|---|---|---|
| head `748d71c5` (21:37:17-23:19:35Z) | 158 | 73 | 0 | 0 | 85 | 6,135 s |
| base `72884c8a`, same pod (22:10:30-23:57:04Z) | 158 | 73 | 0 | 0 | 85 | 6,391 s |
| a1's base (baseline.md, T0 only) | 158 | 64 | 0 | 0 | 94 | |

Both runs exited 0 (33 tests deselected by `-m regression`). Environment: the one above, plus `VERITY_REGRESSION=1
VERITY_REGRESSION_TIERS=T0,T1`, `RESEARCH_STORE=/workspace/research/store`, the tree's
`tools/research/store.pod.toml`, and a scratch directory per run. There was no rows root and no candidate. The JUnit
XMLs are beside this note: `gate_a-t0t1-head-748d71c5.xml.gz` and `gate_a-t0t1-base-72884c8a-samepod.xml.gz`.

`baseline-jdiff.py`:

- **Head vs the same-pod T0+T1 base:** 0 new failures, 0 new skips, 0 outcome changes. One skip reason differs in
  text only. `manifest_digest` on the TP rows #70 and #75 skips at both, and the reason now names `tp_stage.sh`
  instead of `row_pod_tp2.sh`, because part 1 deleted that shim and updated the live string in
  `checks/manifest_digest.py`.
- **Head vs a1's T0 base:** 0 new failures and 0 new skips. Every check that passed there passes here. Nine
  `T1-replay_partition` tests go from skip (tier) to pass. The skip reasons that are new relative to T0 are the T1
  checks' own "does not apply" reasons, and all of them occur at the same-pod T0+T1 base too.

Per check at head, identical at base (13 rows each):

| check | tier | passed | skipped |
|---|---|---|---|
| manifest_digest, global_match_checks, executed_prefix, coverage, commit_summary, verdict | T0 | 10 each | 3 each |
| step_segmentation | T0 | 1 | 12 |
| stoch_value | T0 | 1 | 12 |
| attempt_provenance | T0 | 0 | 13 |
| replay_partition | T1 | 9 | 4 |
| decomp_hashes | T1 | 0 | 13 |
| program_digest | T2 | 0 | 13 (tier) |

The skips at T1:

- `replay_partition` skips on #4, #23, #70 and #75: "no sampled_replay record on this row". The run did replay
  #11, #39, #57, #60, #67, #68, #73, #74 and #101.
- `decomp_hashes` skips on all 13 rows. On the 6 B=1 and FAIL rows the reason is "no match_decomp.json". On the 7
  batched rows it is "`match/...` not resolvable here". See "Found, not fixed".

The other skips (T0) are baseline.md's: attempt_provenance has no candidate, stoch_value skips the greedy rows, rows
#4, #70 and #75 have no Commit, and step_segmentation's `build_request*/descriptor.json.gz` isn't in the store.

**Memory:** one process peaked at about 115 GB (VmHWM during #39's `replay_partition`). The container's
`memory.peak` was 163 GB, page cache included, with the two gate (a) runs overlapping each other and gate (b).

Fixtures: a read-only key (3 h) was minted on the laptop and piped to `/root/r2ro.env`. `prefetch.sh` fetched all 26
fixture artifacts into `/workspace/research/store` (26 ok, 0 FAIL) and deleted the key at 21:36:51Z, before gate (a)
started. The run has no `AWS_*` variables.

**T1 needs a big pod.** `tests/regression/checks/replay_partition.py` loads each B=1 row's whole Program JSON. Its
docstring says "0.9-1.7 GB compressed and need 120-250 GB of RAM as Python objects: a big pod". On the first pod
(`vyv-rf-a23`, cpu3g 64 GB), gate (a) T0+T1 was OOM-killed twice. The second kill also took sshd, so that pod was
terminated. On the 512 GB pod, row #11's `replay_partition` passed at about 63 GB.

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

### Part 2 (a23b, `96c12c0b`..`748d71c5`)

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
- `748d71c5`: the shipped-tree stub in `tests/harness/test_source_identity.py` also copies `verity_vllm/config.py`.

`pyproject.toml` is unchanged: hatchling's wheel with `packages = ["verity_vllm"]` ships every non-ignored file under the
package. `uv build --wheel integrations/vllm` at `748d71c5` on the pod gave `verity_vllm-0.1.0-py3-none-any.whl`
(375 files). It contains:

- the 7 `.xz` tables under `program/numerics/tables/`;
- `check/tables/B0-divergence-20260907T1604Z/cos_sin_cache.npy`;
- `harness/planner_calibration.jsonl`;
- `observe/profiles/corpus_coverage.json`;
- the tanh tables (`mufu_tanh_sm89.json` and `.xzblocks`);
- `verity_vllm/config.py`.

### Counts (rename-aware, `72884c8a`..`748d71c5`)

| | files | lines |
|---|---|---|
| library files deleted (`verity_vllm/`) | 17 | 4,358 |
| lines removed / added in modified library files | 27 files | -163 / +132 |
| `integrations/vllm/tools/` deleted | 3 | 3,068 |
| moved from `verity_vllm/` to `tests/` | 18 text + 7 binary (`.npz`) | 8,361 |
| data moved into the package | 9 (7 `.xz`, 1 `.npy`, 1 `.jsonl`) | binary / data |
| whole lane | 114 files changed | +235 / -8,480 |

Part 2 alone (`c1cf11ef`..`748d71c5`): `verity_vllm/` 33 files +102/-81; `tests/` 8 files +12/-20.

The rebase adds `3f794427` (`tp/worker.py` -1 line) and `9be6e462` (`tests/lint/`: 8 files, +7/-130). The library
counts above therefore hold at `9be6e462`, less that one line.

### Path smoke (CPU, HF_HOME unset, cwd `/tmp`)

`smoke_paths.py` is beside this note. It ran in a fresh tree at `4e26d864`, which has the same library code as the head,
and every path resolved:

- `config.ROOT` is the tree's `integrations/vllm`, and `MANIFESTS`, `WORKLOADS` and `CHECKPOINTS` exist.
- `checkpoints_hf_home()` and `apply_env()` give `/workspace/hf`.
- `_default_manifest()` gives the tree's `manifests/checkpoints.json`.
- `workload.CORPUS` exists, and `case_for(SmolLM2)` is `B0`.
- The cos_sin table and the calibration resolve, with sha256 `7f7891085473...` and `fac806350bec...`.
- `fa2_relation.tables_dir()` lists the two W11 tables, and `rms_relation.tables()` loads.

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

## Rebase onto main

The coordinator's 22:13Z broadcast said main was at `1d9c3198`. By 23:15Z main was at `58e4c1aa`, but nothing under
`integrations/vllm` changed between the two. The rebase used `git rebase origin/main` (`58e4c1aa`).

- **One conflict,** in `check/fold_compare.py` (commit `dfb8cd8b`), as the coordinator predicted. Both sides drop the
  laptop `DEFAULT_RECORD`. I kept this lane's side (`--theirs`): `DEFAULT_COS_SIN` from package data and no `REPO`. The
  file is byte-identical to its `748d71c5` version.
- `git diff 748d71c5 ea6625d3 -- integrations/vllm/verity_vllm` is empty. In `git range-diff`, 12 of the 13 commits are
  `=`, and the 13th is the `fold_compare.py` resolution.
- **Lints** (`python -m pytest integrations/vllm/tests/lint -q`, from the tree root, in gate (b)'s environment, on the
  pod):
  - At `ea6625d3` (rebased, no fixes): 11 failed.
  - After the two commits below: **41 passed**, on a pod tree whose `git write-tree` is `9cdc02c5` = `9be6e462^{tree}`.
- `3f794427`: `tp/worker.py` had grown to 1,580 lines, one over its recorded 1,579 (P10). The cause was the blank line
  `ed31d31c` put between the two function-local imports; this commit drops it. The repo has no isort config that wants
  the blank line.
- `9be6e462`: allowlists and `INTERIM_LAYER`:
  - Deleted the stale entries left by the deleted and moved modules and by the `sys.path`, `parents[N]` and
    machine-path fixes: P3 4, P6 10, P7 12, P8 22, P9 35, P10 1, P11 32.
  - Lowered five P10 caps to the current sizes: `twins` 1,050, `padding_steps` 933, `commit_delta` 3,022 and its
    `main` 1,918, `weights_of_record` 1,000.
  - Moved one P7 entry. `weights_of_record._default_manifest` still reads the cwd, now spelled `Path.cwd()`, so the
    entry changed from `os.getcwd` to `pathlib.Path.cwd`.
  - Dropped the 7 `INTERIM_LAYER` names that moved to `tests/`.
  - Added `"verity_vllm.config": "config"`. `config.py` imports nothing from `verity_vllm`; the 9 new P9 layering hits
    were `-> config` imports.
- Pushed with `--force-with-lease` (`748d71c5` -> `9be6e462`).

## Found, not fixed

- **Gate (a) at T0+T1 needs a pod with well over 64 GB.** `replay_partition` (T1) on the B=1 rows loads whole Programs;
  its docstring says 120-250 GB. A cpu3g 64 GB pod OOMs, and the OOM can take sshd with it. Any lane's T0+T1 gate (a)
  needs a big pod (here: cpu3m, 512 GB).
- **On a store-only pod, gate (a) T0+T1 never runs `decomp_hashes`.** It skips on all 13 rows at head and at base. On
  the 7 batched rows the check's `match/...` input isn't in the stored `records` artifact ("not resolvable here (roots
  tried: [])"). This is like baseline.md's `step_segmentation` finding. Exercising the check needs live row
  directories as the rows root, or the match files staged into the store.
- **Gate (b) writes into the tree.** `tests/program/test_ref_prims.py` writes its records to `$REF_PRIMS_RECORD_DIR`,
  which defaults to the tree's `docs/data/ref-prims/`. After a gate (b) run, 29 of those files differ from git, with the
  same bytes at head and base. A tree that ran gate (b) is not the commit's tree any more; here, gate (a) and the lint
  run used copies that had not run it.
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
- Host dependence: on the first pod (AMD EPYC 7702P, no AVX512), 6 of baseline.md's failures passed at `6da1b430`.
  Five are CPU numerics checks: `test_analytic` cos_sin, `test_gen_dense2` inv_freq, `test_ref_prims` gelu (2) and
  `test_derive_realhf` gpt2 bf16. The sixth is the `test_row_pod_cancel_forwarding` 15 s timeout. On that host the
  gc-freeze pair also failed at base with the file run alone. The AVX512 pod reproduces baseline.md's failure list exactly.
