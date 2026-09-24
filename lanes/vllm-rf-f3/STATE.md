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

## Running
- nothing yet (launcher: `~/.research/bin/research`)

## Next
1. Implement D14, D15 as separate commits; push (D4, D3 done).
2. CPU pod: gates (a)/(b) (+ base measurement if a1 baseline.md absent).
3. GPU pod (L40S): one Commit row re-run for D3, compare roots with regression record.

## Open questions
- D15 table location: a23 owns package-data moves; if a23 does not move `fixtures/W11*`, coordinator decides who does.

## Found, not fixed
- `commit_delta` still copies other CLI flags into env for acquire/commit to read (VERITY_WINDOW_MB/SLOTS, RETAIN, STAGING_BOUNDED, ...), T7/B4.
- collector/binding-map `layout` label is `chunk-leaf-v1` for host (non-gpu-tree) committers whose leaves are host-pos-leaf (label only; changing it changes map digests).
