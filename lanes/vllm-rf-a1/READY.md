---
id: vllm-rf-a1/ready
lane: vllm-rf-a1
kind: ready
status: ready
repo: verity
updated: 2026-09-24T21:45Z
---
# a1 (guardrails and baseline): READY

## Branch

`origin/lane/vllm-rf-a1` at `39c5ee7a`, on `main` `72884c8a`. Two commits: `f1a513a9` adds the lints and allowlists,
and `39c5ee7a` rewrites their docstrings so they state each rule instead of citing notes sections. The diff is 28 new
files under `integrations/vllm/tests/lint/`. No library code changed.

The baseline for every lane is `baseline.md` beside this note: the commit, the environment recipe, counts per file,
every failure with its cause, and the skip reasons.

## Gate evidence

All runs are on `vyv-rf-a1` (RunPod cpu3g, 16 vCPU / 64 GB) in the `baseline.md` environment (py 3.12.14, torch
2.13.0+cu129 on CPU, vLLM 0.28.1rc1.dev472+gd9105ea80, triton 3.7.1, pytest 9.1.1, pytest-xdist 3.8.0). Each tree is a
clean `research pods sync` of its commit. The JUnit XML of every run is kept after the pod: the head runs are beside
this note as `head-gate_*.xml.gz`, and the base runs are beside `baseline.md` as `baseline-gate_*.xml.gz`.
`python3 baseline-jdiff.py baseline-gate_X.xml.gz head-gate_X.xml.gz --ignore-prefix tests.lint.` reproduces each
comparison below, and all three exit 0.

| gate | commit | total | passed | failed | error | skipped | xfailed | exit | time |
|---|---|---|---|---|---|---|---|---|---|
| (a) | base `72884c8a` | 158 | 64 | 0 | 0 | 94 | 0 | 0 | 2 h 42 min |
| (a) | head `39c5ee7a` | 158 | 64 | 0 | 0 | 94 | 0 | 0 | 2 h 36 min |
| (b) serial, the brief's command | base | 3904 | 3534 | 57 | 11 | 296 | 6 | 1 | 1 h 50 min |
| (b) serial, the brief's command | head | 3945 | 3574 | 57 | 11 | 297 | 6 | 1 | 1 h 46 min |
| (b) xdist, `-n 12 --dist loadfile` | base | 3904 | 3536 | 54 | 11 | 297 | 6 | 1 | 40 min |
| (b) xdist, `-n 12 --dist loadfile` | head | 3945 | 3576 | 56 | 11 | 296 | 6 | 1 | 39 min |

- **Gate (a) is green**, and the head run is identical to the base run test by test. The brief's command runs tier T0
  only; `baseline.md` explains the tiers and why 9 of the skips are fixture gaps.
- **Gate (b) cannot have 0 failures at this base.** The serial base run has 68 failures and errors, all explained in
  `baseline.md`. Against the base run of the same mode, the head adds the 41 lint tests, which all pass. It adds no
  failure, no skip and no skip reason apart from four tests whose outcome at base already depends on test order or heap
  state:
  - Serial: the same 68 tests fail or error at both commits. The only change is that
    `observe/test_observer_encoding::test_weakref_death...` passed at base and skipped at head ("allocator did not
    reuse the pointer"). The lints are not the cause: run alone, with no lint test collected, it skipped in 2 of 4
    runs, and after the lint package in 2 of 5.
  - xdist: the two `harness/test_admit_r19_host_working_set` tests went from pass to fail, and the observer test went
    from skip to pass. The pair fails in the serial base run too. On the pod the file fails the same way at both
    commits when it runs after `observe/test_execution_label.py`: vLLM's `EngineCore` leaves the heap frozen.
- **Lints:** `python -m pytest integrations/vllm/tests/lint` gives 41 passed in 25 s on the idle pod. About 10 s of that
  is the first test parsing the tree, which the later rules then reuse. No torch, vllm, triton, numpy or `verity_vllm`
  module is imported, with or without the tests' conftest.

## Allowlist sizes (the ratchet's starting point)

An entry is one `(file, kind, symbol, detail)` key. "Occurrences" adds up the entries' `count` where it is above 1. For
P10, `count` is the recorded size in lines, so only entries are given.

| rule | allowlist | entries | occurrences | by kind (entries, occurrences) |
|---|---|---|---|---|
| P1 core abstractions | `p01_core_abstractions.json` | 37 | 38 | core-private 27 (28), core-patch 6, definition-id 4 |
| P2 value checks | `p02_value_checks.json` | 1 | 1 | import 1 |
| P3 one evaluator | `p03_one_evaluator.json` | 39 | 40 | rng 32 (33), if-ladder 7 |
| P4 one result | `p04_one_result.json` | 65 | 101 | g-literal 43 (72), reason-prefix 12 (19), g-identifier 8, verdict-import 2 |
| P5 properties | `p05_properties.json` | 2 | 2 | import 2 |
| P6 one CLI | `p06_one_cli.json` | 231 | 344 | main-block 73, argparse 71, python-m 53 (72), heredoc 20 (39), python-c 14 (89) |
| P7 declared inputs | `p07_declared_inputs.json` | 388 | 457 | environ 184 (218), broad-except 136 (164), seed-default 33, optional-import 15 (16), machine-path 12 (16), cwd 8 (10) |
| P8 facts | `p08_facts.json` | 328 | 436 | layer-class 165 (191), model 66 (115), gpu 52 (59), sm-arch 45 (71) |
| P9 layering | `p09_layering.json` | 214 | 220 | layer 104, runtime-patch 44 (50), package-cycle 23, repo-path 21, module-cycle 11, sys-path 7, forbidden-import 4 |
| P10 size | `p10_size.json` | 77 | - | module 41, function 36 |
| P11 names | `p11_names.json` | 751 | 1002 | doc-round 355 (511), doc-board-id 211 (301), def-name 90, doc-date 56 (61), doc-lane 13, module-name 12, class-name 7, flag-name 7 |
| P12 shared keys | `p12_shared_keys.json` | 17 | 17 | root-list 7, row-id-split 7, row-id-regex 3 |

## What changed

- `tests/lint/_ratchet.py` holds the shared machinery: the scan (every `verity_vllm/**/*.py` and `*.sh`, parsed once
  and cached), the key, loading and checking the allowlist, and the two failure messages.
  - When a key is found more often than its entry allows, the test fails and says to fix the new code, or to move the
    entry if the violation only moved.
  - When an entry allows more than is found, the test fails and prints the exact JSON line to delete or lower.
  - Line numbers are not part of the key, so edits elsewhere in a file do not churn the allowlists.
- `tests/lint/_imports.py` builds the import graph: module-level and lazy imports, plus `importlib.import_module` with
  a literal name. `INTERIM_LAYER` maps every module of today's layout to the layer of the package it moves to. The
  order is `pipeline` > `check|properties` > `acquire` > `observe|commit` > `engine` > `query|correspondence` >
  `program` > `collectives` > `config` > core, with modules bound for tests above `pipeline`.
- There is one `test_pNN_*.py` per rule, and each file's docstring says what is checked today and what applies once
  its package exists.
  - Each file has `test_no_new_violations`, `test_allowlist_has_no_stale_entries` and a detector test. The detector
    test runs a synthetic snippet and expects the exact violations, which pins each detector's behaviour.
  - P10 replaces the first two with `test_no_new_or_grown_offenders` and `test_recorded_sizes_are_current`. P2 and P5
    add `test_contract_modules_exist`, and P9 adds `test_interim_layer_map_names_existing_modules`.
- `tests/lint/test_ratchet.py` tests the machinery itself: new and stale entries on a synthetic tree, and malformed
  allowlists being refused.
- 41 tests in all, with no new dependency and no torch, vllm or `verity_vllm` import.

## Deliberately not changed

- No import-linter: the contracts are AST checks over the graph in `_imports.py`.
- No `[project.scripts]` entry (the CLI lane adds it).
- No allowlist generator is committed. Entries are edited by hand, and each failure message prints the lines, so an
  allowlist cannot be regenerated wholesale and the ratchet stays shrink-only.
- The runtime halves of the rules are not lints; each is named in its rule's docstring:
  - P1: one process that imports `verity.ml` and every integration registry.
  - P2: the pod negative test that mutates the retained buffer after commit.
  - P3: the per-(backend, Definition) self-check.
  - P5: the `properties.REGISTRY` test.
  - P7: the digest being the same with torch stubbed out.
  - P12: editing a core file in a temp tree changes the identity.
- No library code changed. Every finding below is in an allowlist or in `baseline.md`.

## For the lanes merging after this

- A lane that removes a violation (for example, a23's `sys.path` and `parents[N]` fixes, which are P9 `sys-path` and
  `repo-path` entries) turns its entry stale. The lint then fails and prints the line to delete, so delete it in the
  same change.
- A lane that moves or renames a file moves its entries, because the key contains the file path.
- A lane that adds a new top-level package under `verity_vllm/` adds it to `INTERIM_LAYER`. Otherwise it falls to the
  `verity_vllm` default, which is the `pipeline` layer.
- Where the rule's owner module or package now exists, add it to the rule's owner tuple. These are `CLI_OWNERS`,
  `ENV_OWNERS`, `RNG_OWNERS` and `VERDICT_ALLOWED`, and the P9 runtime-patch exemption for `engine/hooks.py`.

## Found, not fixed

- Test builds cannot import core `verity`. `program/test_applicability.py` (11 errors) and
  `program/test_artifact_applicability_independent.py` (19 failures) start their builds with `PYTHONPATH` set to the
  integration tree only. On a bootstrap pod, which puts core on `PYTHONPATH` rather than in the venv, every build dies
  on `ModuleNotFoundError: No module named 'verity'`.
- `test_artifact_applicability_independent` skips or fails depending on collection order.
  `harness/commit_delta.py` calls `apply_env()` at import, and that sets `HF_HOME`. The file's builder probe reads
  `HF_HOME`, so whether it runs depends on what was imported before it (already on the integrator's open list).
- Test inputs are not tracked at `72884c8a`: `tests/sweep/pod_release.sh`, `verity_vllm/ops/pod_release.sh`,
  `out/gen/cards/SCHEMA.md`, `out/gen/r17/sparse-patterns.txt` and `record_v5/ship.sh` (6 failures).
- The extracted `vllm_adapter.load_workload` calls `execution_of_workload`, which the extraction leaves out
  (`NameError`, 4 failures).
- On a pod with only the store, gate (a) skips T0 `step_segmentation` on 9 rows (#11, #23, #39, #57, #60, #67, #68, #73,
  #74). The check reads `build_request*/descriptor.json.gz`. `fixtures.toml` lists those files as role `record`, but
  `stage_store.py` puts only small records and `instances.json.gz`, so no stored tree has them. The integrator passed
  those 9 from live row directories (73 passed against 64 here).
- `acquire/test_compiled_source.py::test_renumber_assigns_invocations_per_call_site` needs CUDA but does not skip
  without it.
- A `research pods sync` tree has no `.git`. So `harness/test_source_identity.py` fails 4 tests, and the 8
  `test_relayout_map.py` tests skip. Those 8 pass at `39c5ee7a` on a pod tree that was `git init`-ed from the sync,
  new `tests/lint/` files included, and so do `test_imports_resolve.py` and `test_no_by_name_rules.py`.
- Core's Definition registry refuses duplicates, and four integration modules register ids that core also registers:
  `registry/hopper.py` (`HopperBF16WgmmaDot16_v1`) and `registry/prims.py` (`Bf16ToF32_v1`, `F2fpBf16_v1`,
  `F32ToBf16Rn_v1`). So importing `verity.ml` and every integration registry in one process fails (P1
  `definition-id`).
- Core objects patched at run time (P1 `core-patch`):
  - `check/global_match_fast.py` swaps `verity.ir.codec._spec_id` and `verity.ir.refs.runs`.
  - `registry/ref_prims.py` extends `codec._LAZY_PRIMITIVE_FAMILIES`.
  - `registry/lifted.py` calls `REGISTRY.add`.
- Library code imports the test or tool trees (P9 `forbidden-import`):
  - `check/adversarial.py` imports `tests.check.test_compare_synthetic` and `tests.observe`.
  - `harness/research_tools.py` and `harness/source_identity.py` import `research`.
- Eleven import cycles (P9 `module-cycle`). The largest spans `check.global_match`, `check.program_compare`,
  `correspondence.batch_decomp`, `program.global_program` and `program.registry`. Another spans `correspondence.emit`
  and `program.frontend`.
- P2: `check/value_check.py` imports `acquire.native_host` (the committer).
- P4: `check/commit_verdict.py` imports `check.sampled_replay` and `query.manifest.format`.
- P5: `check/sampled_replay.py` and `check/stoch_recompute.py` import the property harness `check.difftest`.
