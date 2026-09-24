---
id: vllm-rf-f3/state
lane: vllm-rf-f3
kind: state
status: active
created: 2026-09-24T17:36Z
---
# vllm-rf-f3: undeclared inputs (D3, D4, D14, D15) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D3, D4, D14, D15), §4 P7; coordinator note `20260924T1645Z-coordinator-checks-on-observe-survey.md`.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f3`, branch `lane/vllm-rf-f3` from `72884c8a`.
- **Scope:**
  - D3: one declared `layout` parameter (Commit config / CLI flag, recorded in artifact), read once at process start, inconsistent values refused; roots unchanged where the two env vars agreed.
  - D4: `GATHER_FLUSH_LEAVES` / `PRE_FLUSH_LEAVES` into a torch-free module, delete the ImportError fallback in `acquire/plan.py`, test plan + digest identical with torch stubbed.
  - D14: seeds defaulting to 0 become required or derived from commitment; list every challenge derivation touched.
  - D15: env-driven Definition semantics (MufuTanh tables etc.) -> package data with pinned digest; list every env-dependent Definition. STOP and report if a fix would change a digest because the env path was actually used.
- **Acceptance:** gates (a), (b); torch-stub plan test; D3 GPU Commit row re-run with roots == regression record; no Program/manifest digest changes.

## Inventory (17:40-17:57Z, laptop, rg only)
- D3 sites: `acquire/native_collect.py:721` (VERITY_LAYOUT -> layout_v2), `commit/padding_steps.py:405` (VERITY_LEAF_LAYOUT, gpu_tree else host-pos-leaf),
  `harness/commit_delta.py:583` (collector.layout = VERITY_LEAF_LAYOUT -> binding map layout), `:1258` (--layout -> VERITY_LAYOUT), `tp/worker.py:1043` (hard-coded v1).
  Nobody sets VERITY_LEAF_LAYOUT; no ops script passes --layout -> every regression row is v1 on both sides. row_pod uses native_collect_v2b --gpu-tree.
- D4: `plan._lifetime_tables` swallows native_collect ImportError. By-name lint pins the tables' file (`tests/by_name_allowlist.json:57,59`) -> update file path on move.
  `--late-read` mutates `native_collect.GATHER_FLUSH_LEAVES` (module global read at call time) -> keep the name imported into native_collect.
- D14 derivations: compiled_kernel_check (only caller seeds from run root), relations.draw_sample / ensure_adjacent_pair (no callers),
  replay.tier_a / tier_chain + CLI --seed 0, run_config --seed 0 (row_pod skips replay_a/chain; cov_pod passes --seed 0; verify_lane urandom),
  capture_identities.run + CLI --seed 0 (no python callers). Already derived: binding.challenge_identities, sampled_replay.challenge_seed (+ commit_delta/tp.worker), tp/xrank_collectives, vu_query.production_sample (required).
  Not challenges (left): twins.self_check / Replayer self-check seed, stoch_recompute reference-rows pick, holdout, difftest, adversarial, descriptor_equivalence.
- D15 env-dependent Definitions: MufuTanh (VERITY_MUFU_TANH_TABLES + dead `mufu_tanh_use_tables`), MufuEx2Ftz / MufuRcpFtz / Fa2InvSum (VERITY_MUFU_TABLES via fa2_relation.tables),
  MufuSqrtFtz / DivFullRcp / RsqrtApprox (VERITY_RMS_TABLES via rms_relation.tables), + every composite / twin / derived_rows using them; VERITY_ARCH fallback in
  fa2_model.arch_of + rms_relation.coverage (coverage gate of the PoC relations, not arithmetic). Env paths were used only pointing at the shipped fixture
  (git history: fa3_target_correspondence usage line; tests/program/test_composition.py setdefault) -> pinning the fixture digests changes nothing.
  Tables live in `integrations/vllm/fixtures/W11*` (not package data): the MOVE to package data is lane a23's (importlib.resources); f3 deletes the env overrides + pins digests.

## Done
- 17:36Z worktree created.
- 18:02Z Cursor restart interrupted the run; 18:47Z resumed. Worktree had uncommitted D4 start (new `acquire/flush_points.py`, tables cut from `native_collect.py`); no f3 pods or commands were running.
- 19:05Z D4 `a2164659` pushed: tables in `acquire/flush_points.py`, native_collect imports them, plan imports unconditionally; allowlist table entries -> flush_points.py;
  new `tests/acquire/test_plan.py::test_default_tables_do_not_depend_on_torch` (fresh processes, torch free vs blocked). NOT yet run (pod).
  Behaviour note for READY: under `--late-read` (canary/fa3 negatives only) the Commit-stage plan now lists the declared flush leaves (it read the
  mutated collector table before) -> that run's plan digest changes; roots unchanged (collector still reads its rebound copy).
- 19:10Z D3 `0f970b0e` pushed: `NativeCollectCommitter(layout=)` (unknown refused; v2 off-window refused as before), `NativeHostCommitter.layout = "chunk-leaf-v1"`,
  `padding_for_committer` takes `com.layout` (gpu tree) / host-pos-leaf (its `layout=` kwarg had no caller -> removed), `commit_delta --layout` default v1,
  no longer copied to env, `collector.layout = args.layout`, `make_committer` refuses a non-v1 layout for non-native_collect kinds. No VERITY_(LEAF_)LAYOUT read left.
  TP: `tp/commit.py` has no `--layout`; ranks build via `make_committer` with a Namespace without `layout` -> v1, matching its hard-coded
  `layout_version_per_rank: chunk-leaf-v1` (before, an exported VERITY_LAYOUT could make ranks v2 under that label). v1 runs: executed, padding and
  map label all v1 as before -> roots unchanged expected (GPU row to confirm).
  Tests (NOT yet run, pod): `tests/acquire/test_p0_footprint.py::test_the_declared_layout_reaches_only_a_committer_that_implements_it`,
  `tests/program/test_padding_pod_consumer.py::test_the_padding_leaf_rule_is_the_committers_not_the_environment`.
- 19:16Z D14 `bdcf4d5f` pushed. Challenge derivations touched (seed now required, derivation unchanged -> no sample moves for any caller that passed one):
  `CompiledKernelCheck(seed=)` (only caller: commit_delta, run root 4 bytes), `relations.draw_sample` / `ensure_adjacent_pair` (no callers),
  `replay.tier_a` / `tier_chain` + CLI (a/chain refuse no --seed; b/c keep self-check seed 0), `sampled_replay.sampled_replay(seed=)` (found in sweep;
  78 call sites all pass seed), `capture_identities.run` + CLI (no python callers; record gains `coordinate_sample: {seed, per_gemm}`),
  `run_config --seed` default None: refused only when replay_a/replay_chain run unskipped (row_pod skips both; cov_pod/verify_lane pass it);
  tier c gets --seed only if given. run.json `sampling.seed` = null (was 0) when not given (no reader except experiment.py's copy).
  Not touched (already derived): binding.challenge_identities, sampled_replay.challenge_seed, commit_delta/tp --replay-seed (root), tp/xrank_collectives,
  vu_query.production_sample. Not challenges: twins self-check, stoch_recompute ref rows, holdout, difftest, adversarial, descriptor_equivalence,
  engine/workload/fixture seeds, bootstrap CIs. "One function from the run root" (SYNTHESIS) NOT done: unifying the forms moves samples/verdict
  checks (commit_verdict `_REPLAY_SEED_ROOT_FORM`, compiled seed_source) -> Phase 3 / core C4.
  Tests (NOT yet run): new `tests/check/test_challenge_seeds.py`; `test_run_config_dry_run.py` (+refusal test, 4 calls get --seed 7);
  `test_replay_synthetic.py` tier_a call gets seed=0. Rebase note: if a23 deletes `check/relations.py`, drop its 2 SEEDED entries.
- 19:33Z D15 `d4a87683` pushed. Env reads deleted: `VERITY_MUFU_TANH_TABLES` (prims `_tanh_shards`; + dead `mufu_tanh_use_tables` /
  `_TANH_TABLES_OVERRIDE` / `_tanh_shards_from_dir`), `VERITY_MUFU_TABLES` (`fa2_relation.tables_dir`), `VERITY_RMS_TABLES`
  (`rms_relation.tables_dir`), `VERITY_ARCH` (`fa2_model.arch_of`, `rms_relation.coverage`: arch = declared consts or none).
  Pins: `prims.MUFU_TANH_TABLE_MANIFEST_SHA256` (manifest 674b3663…; manifest already pins the xzblocks 5e261b88…),
  `fa2_relation.TABLE_SHA256` {ex2 7b324911…, rcp 291d1c9c…}, `rms_relation.TABLE_SHA256` {triton: sqrt c5859583…, rcp 291d1c9c…;
  cuda: + rsq e9892020…}; checked on every `tables()` call against the loaded `source` digests (covers oracle.py's low-peak preload).
  Mismatch -> ValueError (fa2/rms), MufuTanhUnmeasured (tanh). Location stays one function per table set (`tables_dir()`,
  `tables_dir(kernel)`, `MUFU_TANH_TABLE_DIR`) for a23b's W11 move to replace. `doc` is not in `encode_program` (codec.py) and no
  profile snapshot records the MufuTanh doc -> no Program/profile digest change. Also: test_composition setdefault removed (it set the
  default path), docstrings/skip reasons naming the env vars. Test (NOT yet run): new `tests/program/test_mufu_tables_pinned.py`.

## Running
- CPU pod `vyv-rf-f3-veritor-campaign` (RunPod `drd3w6z9d22gvd`, cpu3g 16 vCPU / 64 GB, 80 GB disk), created 19:17Z, idle, nothing synced yet.

## Next
1. While a23b's `W11 move: <sha>` is pending (not in its STATE.md at 19:30Z): sync d4a87683 to the pod, bootstrap, run the new/changed
   test files (D3/D4/D14/D15) as an early check.
2. Once `W11 move` lands: rebase onto it (only the table location functions should conflict), re-sync, gates (a)/(b) on the pod.
3. GPU pod (L40S): one Commit row re-run for D3, compare roots with regression record.
4. READY.md in this dir when gates are in.

## Open questions
- D15 table location: a23 owns package-data moves; if a23 does not move `fixtures/W11*`, coordinator decides who does.
  - **Coordinator answer, 19:30Z:** a23b (the successor of a23) moves `fixtures/W11*` first. Write D15 now and rebase onto a23b's `W11 move: <sha>` before gates. Details: `20260924T1930Z-handoff-from-vllm-coordinator.md` in this dir.

## Found, not fixed
- `commit_delta` still copies other CLI flags into env for acquire/commit to read (VERITY_WINDOW_MB/SLOTS, RETAIN, STAGING_BOUNDED, ...), T7/B4.
- collector/binding-map `layout` label is `chunk-leaf-v1` for host (non-gpu-tree) committers whose leaves are host-pos-leaf (label only; changing it changes map digests).
