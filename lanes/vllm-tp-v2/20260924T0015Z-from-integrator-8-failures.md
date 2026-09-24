---
id: vllm-tp-v2/20260924T0015Z-from-integrator-8-failures
lane: vllm-tp-v2
kind: handoff
status: open
repo: verity
origin: lane/vllm-cleanup-2
---
# From the integrator: `e6f8aa0` fails 8 offline tests on its own

Staging `lane/vllm-cleanup-2` is now **`270db8f`** (sampler-literals + p2p4).

I trial-merged dead-code-2 `e0fd6f7` and then you (`e6f8aa0`) into it and ran the vllm default suite on cpu2 (`--dist loadfile`, gate env). There are 8 failures beyond staging's known set. All 8 reproduce on **`e6f8aa0` alone**, run single-process with no xdist, so this is not the test-order leak and not the stacking. Log: `vyv-v2cpu2:/workspace/p6_logs/tpv2_3files.log`; 8 F / 70 pass over the three files.

## A. p2p4 × tp-n: `manifest_format` has no `collective_kind` (3 tests)
- `verity_capture/commit/sampled_replay.py:59` is `from verity_capture.commit import manifest_format as RM` (p2p4 step 1 re-pointed it). Lines `:418-419` call `RM.collective_kind(f0)` (tp-n `aa03f5ab`). `collective_kind` lives only in `required_manifest.py:351`.
- Error: `AttributeError: module 'verity_capture.commit.manifest_format' has no attribute 'collective_kind'`.
- Failing tests:
  - `commit/tests/test_sampled_replay_moe_tp_sum_copy.py::test_tp_rank_moe_sum_row_is_addressed_at_its_partial_and_its_plane_copy`
  - `commit/tests/test_sampled_replay_moe_tp_sum_copy.py::test_tp_rank_population_reconciles_the_sum_plane_identities_the_manifest_requires`
  - `tp/tests/test_tp2_sampled_replay_fold.py::test_rank_program_rows_describe_the_tp_members_of_that_rank`
- This is the live sampled-replay path for TP rank Programs, not only the tests.

## B. `collective_kind` now imports the registry, so the CLI subprocess tests lose `verity` (4 tests)
- tp-n `aa03f5ab` made `members_for` (`required_manifest.py:209`) call `collective_kind`. That function lazily imports `verity_vllm.registry.b1_tp2` (`:354`), which imports `verity.ir.codec` (`registry/__init__.py:41`). The old prefix predicates needed no registry.
- These tests spawn `python -m verity_capture.commit.required_{values,manifest}` with `PYTHONPATH=".:vllm-poc"`, which replaces the path (`test_required_values.py:699`, `:849`, `:962`). Without `verity` installed in the venv (the pods' `venv312`), the child dies with `ModuleNotFoundError: No module named 'verity'`.
- Failing tests:
  - `test_audit_cli_exit_codes_and_streaming_reader`
  - `test_streamed_global_fold_equals_loaded_and_the_build_global_cli_under_the_flag`
  - `test_cli_verify_with_traversal_engine_cross_checks_both_engines`
  - `test_cli_verify_a_tp_rank_fold_manifest_of_record_with_repeated_program_and_rank`
- These pass at staging `270db8f` in the same env (gate `t1`). A laptop venv with `verity` installed editable would mask this.

## C. The world-4 test pins the pre-tp-n rule (1 test)
- `test_required_values.py:519` `test_a_world_other_than_two_leaves_the_peer_inputs_unnamed_and_the_population_incomplete_by_name` asserts `not t.complete` with `peers_<k>` unnamed for world 4 (`:528`).
- tp-n generalises world N, and the traversal is now complete.
- tp-n never changed this test (it is identical on main, tp-n and staging). Either pin the world-N behaviour, or explain why the old refusal should stay.

## Also: keep-list follow-through with dead-code-2 (no action needed from you)
Your `bench/tp2_analyze.py` → `tp/analyze.py` move leaves dead-code-2's `tests/dead_code_keep.json` naming `verity_capture.bench.tp2_analyze`. I rename it to `verity_capture.tp.analyze` in whichever merge lands second. If you merge staging after dead-code-2 lands, make the same rename.

## Other results on the trial
- Allowlist stacked: 316 → 293 (−4 from dead-code-2, −19 from you), merged one entry at a time.
- Research, core, root and extra show the same sets as staging.
