---
id: vllm-rf-b5vab/ready
lane: vllm-rf-b5vab
kind: ready
status: ready
created: 2026-09-25T21:10Z
---
# vllm-rf-b5vab READY: split `engine/vllm_adapter.py` into `engine/` modules (B5)

Successor of `vllm-rf-b5va` (bc-649f6a27, no commits). Lane agent bc-a4fbe8b2 (Cursor cloud).

- **Branch:** `lane/vllm-rf-b5vab`, **head `3201c3f4`** (pushed).
- **Base:** b4c's head `9689a1ef` (= b4 `5c05ff6d` + main `38a8d35d` + a5c `40b9e571`). The lane's own work is one commit,
  `d0e04cf8` (the split, on `5c05ff6d`); `42cf1781` and `3201c3f4` are merges of b4c's heads `5494e29f` and `9689a1ef`.
- **Against current main `fee32f05`** (b4, c4ir, gc, PR #29, b5vc in): `3201c3f4` merges **cleanly** (checked in a scratch
  worktree, not pushed). At that merge the lint scan shows 0 problems, the split proof still holds, and every `va.X` in
  the tree resolves. The gates below ran at `3201c3f4`, which predates PR #29.

## What changed
- `engine/vllm_adapter.py` (1,913 lines) is split; every top-level statement moved verbatim:
  - `build.py` (318 lines): the engine under κ: `CASE`, `case_of`, `Engine`, `EXECUTION_ENFORCE_EAGER`, the execution
    and target helpers, `parse_engine_args`, `engine_kwargs_for`, `build_engine`, and the read-backs (`effective_execution_doc`,
    `target_mismatches`, `compilation_facts`, `resolved_async_scheduling`, `observed_flash_attn_version`, `vllm_has_flashinfer`).
  - `code_identity.py` (407 lines): cubin ELF sections, `loaded_code_objects(_delta)`, `generated_kernels_of_this_process`,
    `_VERITY_INDUCTOR_DIR_MARK`.
  - `run_facts.py` (220 lines): `ACCEPTED*`, `profile_manifest`, `model_config_subset`, `host_doc`, `versions_doc`.
  - `capture.py` (795 lines): the step-observation docstring, `SCHEMA`, `ObserverConfig`, `_Step`, `Capture`, `make_header`.
  - `pinned.py` (42 lines): `PinnedArena`, `spanned_bytes`, `storage_bytes_view` (`capture.py` would otherwise exceed 800 lines).
  - `vllm_adapter.py` (205 lines) keeps `load_workload`, `ACCEPTED_TOKENS`, `execution_of_workload` and `sampling_params`
    (the tests exec them from this file's source), plus `run_requests` and `throwaway_requests`. It re-exports every
    public moved name, `_VERITY_INDUCTOR_DIR_MARK` and `RunHeader`, so none of the 39 importers changed. The signatures
    of `build_engine` and `engine_kwargs_for` are unchanged.
- **Proof** (`evidence/verify_split.py`, `evidence/split.py`): 56/56 top-level statements have identical source lines,
  attached comments and AST, and there are no extra statements. Every global each module reads is bound (symtable, all
  scopes). A negative check reports an edited statement and a dropped import. Only module docstrings and imports are new.
- **Import graph:** `vllm_adapter` imports the others, `capture` imports `build`, `pinned` and `run_facts`, `run_facts`
  imports `build` and `code_identity`, and `build` and `code_identity` import `env`. There are no cycles. P9's layer edges
  total 7 before and after: `capture` carries the five `observe.*` edges, `code_identity` the `check.kernel_identity` edge,
  and `vllm_adapter` keeps `observe.chunks`.
- **Allowlists** (`evidence/move_entries.py`): entries follow their code, one for one, with totals unchanged: P7 13,
  P8 1, P9 6, P11 19. The P10 `vllm_adapter.py` `<module>` entry (1,913 lines) is deleted, and there is no new P10 entry.
  No allowlist grew.
- **Tests:** in `tests/engine/test_compiled_execution_header.py`, `target_mismatches` now reads `observed_flash_attn_version`
  and `torch` from `engine.build`, so the test patches `build` instead of `vllm_adapter`. That is its only change.
- **README:** the `engine/` lines are updated.

## What deliberately didn't change
- No behaviour, Program, manifest, commitment root, leaf id or verdict changed; the #101 values below are equal. Code
  identities change only where they hash these files.
- No importer or caller changed. Prose elsewhere that says `vllm_adapter.X` still resolves through the re-exports.
- The `_adapter_fn` tests (lane gc) are untouched.

## Gate evidence
### Lints
`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`
(`evidence/gate_b.sh`), on `vyv-rf-b4b-cpu`: rc 0 at head `3201c3f4` (run `r20260925-181128-fbe5`) and at base `9689a1ef`
(run `r20260925-181148-2918`). Rc 0 earlier at `42cf1781` (run `r20260925-172259-170d`).

### Gate (b): `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`
Head and base ran concurrently on the same pod, `vyv-rf-b4b-cpu` (32-CPU EPYC 9965, 128 GB), with the same runs as above:
- base `9689a1ef`: 4,063 tests, with 3,703 passed, 56 failed, 11 errors, 287 skipped and 6 xfailed.
- head `3201c3f4`: 4,063 tests, with 3,705 passed, 54 failed, 11 errors, 287 skipped and 6 xfailed.
- jdiff (`baseline-jdiff.py`, sha256 `363304c0…`): 0 tests on only one side, 0 new failures, 0 new skips, 0 new skip
  reasons, rc 0. Two outcomes changed, failed -> passed: `test_admit_r19_host_working_set::test_fork_gc_freeze_opt_out…`
  and `…::test_forked_children_inherit_a_frozen_heap…`. These are flaky gc-freeze tests, and they flipped the same way
  at `42cf1781`. No test was renamed. Evidence: `evidence/jdiff-gate_b-head-3201c3f4-vs-9689a1ef.txt`, and for
  `42cf1781` vs `5494e29f`, `evidence/jdiff-gate_b-head-42cf1781-vs-5494e29f.txt`.

### Gate (a): `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`
- Ran at `3201c3f4` on `vyv-rf-c4ir-reg` (cpu3m, 32 vCPU / 256 GB), using the fixtures already in its store, so no key
  or fetch was needed (`evidence/gate_a_half.sh`, timeout 8 h). It ran as two concurrent halves:
  - `-k replay_partition`, run `r20260925-181956-7c6e`: 9 passed and 4 skipped, 2:29 h.
  - `-k "not replay_partition"`, run `r20260925-182011-fabf`: 64 passed and 81 skipped, 1:49 h.
- The two JUnit files were merged into `evidence/gate_a_head_merged-3201c3f4.xml.gz`: 158 tests, 73 passed, 85 skipped,
  0 failed.
- jdiff against `gate_a-t0t1-base-72884c8a-samepod.xml.gz` (`evidence/jdiff-gate_a-head-3201c3f4-vs-a23b-base.txt`):
  158/158, 0 outcome changes, 0 new failures, 0 new skips. jdiff exits 1 on two reworded skip reasons (#70 and #75:
  "merged by `tp_stage.sh`"). That rewording is a4's, and b4b's READY records it identically.
- Both runs are PRESERVED on R2.

### Lane acceptance: #101 GPU Build smoke
`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager` ran on `vyv-rf-b4b-g1` (1x L40S) with
b4c's `g1_cli.sh` and `nonint_cli.sh` (a5's CLI), through the FA2 matReq tap with `MAX_JOBS=12`. It is run
`r20260925-185918-5fec`, rc 0, PRESERVED (`evidence/r101-head-3201c3f4.txt`, `evidence/r101.sh`).
- build, match and commit all PASS.
- program `ccc213475e7c…`, manifest `90f8186879d5…` (7043 B) and run root `7adcef491845…` equal the record. Commit PASS
  on every check.
- non-interference PASS: hashes 992/992, tokens equal. This is the record.
- The multiset of program, manifest, run-root and verdict values in the row directory is identical (md5) to b4c's
  `r101-9689a1ef` run on the same pod.

## Pods and spend
- `vyv-rf-b4b-cpu` (from b4c): terminated 19:03Z.
- `vyv-rf-b4b-g1` (from b4c): terminated 20:17Z.
- `vyv-rf-c4ir-reg` (from the coordinator): terminated 21:05Z.
- `vyv-rf-b5vab-reg` (own): up about 12 min, terminated 18:20Z. Its run was killed when c4ir-reg arrived.
- New spend is about $9 of the $16 budget.
- Key mints, both read-only, 3 h, scoped to `manifests/` and `objects/sha256/`:
  - 18:17:52Z: lost in a failed ssh pipe, never stored.
  - 18:18:43Z: piped into `vyv-rf-b5vab-reg` and deleted there about 18:19Z.

## Found, not fixed
- `_adapter_fn` in `test_gen_ov_sampling.py`, `test_gen_sampling.py` and `test_cov_difr_b0.py` (lane gc) execs only
  `ACCEPTED_TOKENS` and the named function, but `load_workload` calls `execution_of_workload`. `execution_of_workload`
  stays a top-level def in `vllm_adapter.py`, so the tests can extract it.
- `capture.py` is at 795 of P10's 800 lines. Its docstring cites "pattern `capture.py:679-720`", a veritor-era file, not
  itself.
- `tests/pipeline/test_llm.py` patches `va.build_engine`. This works because `pipeline/llm.py` reads it through the module
  at call time. A caller that imported `build_engine` from `engine.build` directly would bypass such patches.
