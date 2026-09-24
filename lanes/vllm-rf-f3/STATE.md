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

- 19:50Z a23b's W11 move `96c12c0b` CHERRY-PICKED (not rebased: it sits on 4 other a23b commits -- deletions, test moves, CMT-1
  removal in commit_delta.py -- which would confound gate (b) vs the base list; the coordinator allowed either) -> `9bddf741`, pushed.
  Conflicts only in the location functions (+ the oracle docstring hunk, whose file a23b had moved to tests/acquire/): resolved to
  a23b's `importlib.resources` path with D15's no-env/pinned form. At merge after a23b the cherry-pick should drop out (same bytes).
- 19:52Z targeted run (31 files touched by D3/D4/D14/D15, tree copy `/workspace/tgt` @ `9bddf741`): 1 failed, 557 passed, 48 skipped; the one
  failure (`test_sampling_rows::test_nv_logf_and_nv_log1pf...`, NaN sign) is on the a1 baseline list. All new f3 tests pass.
- 20:08Z gate (a) prefetch done: 12 rows x {records, programs} ok (row 101 records stalled on one R2 read -> killed, re-fetched by
  `retry101.sh` with the same key before the delete); log ends `key present: no`, `/workspace/prefetch` empty.
- 20:13Z gate (b) @ `9bddf741` (tree copy `/workspace/gb`, xdist, OMP_NUM_THREADS=3): 58 failed, 3550 passed, 296 skipped, 6 xfailed, 11 errors
  (base: 54 F + 11 E). Outside the a1 list: (1) 3 x D14 callers the sweep missed -- `test_gen_llama::test_run_config_dry_run_resolves_the_profile_from_the_case`
  [LLAMA32_1B, QWEN05] and `test_gen_ov_easy::test_run_config_dry_run_resolves_b7_and_forwards_the_engine_arg`: `--phase all` dry runs plan
  replay_a/replay_chain without `--seed` -> refused (exit 2); (2) `test_fork_gc_freeze_opt_out_is_named_on_the_record`, which a1 lists as
  order-dependent (fails serially / alone, passed under xdist at base; my new test files move the loadfile split). Skips: no reason outside the
  a1 list (the 6 "HOLE-*"/hopper entries in the junit are the 6 xfails); a1's xdist-only skip "allocator did not reuse the pointer" passed -> 296 vs 297.
- 20:17Z `4fb0eb2c` pushed: those two dry runs pass `--seed 7` (like test_run_config_dry_run). No other run_config caller hits the refusal:
  `--worker` returns before it; `test_snapshot_cap` stubs Plan before it; ops scripts skip or pass --seed.
- Found at 20:18Z (not f3's, base behaviour): gate (b) WRITES tracked files -- `tests/program/test_ref_prims.py` records conformance to
  `<repo>/docs/data/ref-prims/` unless `REF_PRIMS_RECORD_DIR` is set (32 files rewritten in `/workspace/gb`: platform fields, and
  `ref_vocab_digest` 82fd6a28 -> 63c73b5e, which is base drift since 0018fea0 -- f3 does not touch ref_prims.py or any function its
  manifest hashes). A gate (b) re-run in a used tree tests against those rewritten records -> always run gates in a fresh tree.

- 20:41Z **GATE (b) GREEN at `4fb0eb2c`** (tree `/workspace/base`, fresh; `-n 12 --dist loadfile`, OMP_NUM_THREADS=3; 19 min 42 s):
  54 failed, 3553 passed, 297 skipped, 6 xfailed, 11 errors = the base's counts (+17 passed: the new f3 tests). All 65 F/E are named in
  a1's baseline: 63 of its xdist list + the two `harness/test_admit_r19_host_working_set.py` gc-freeze tests of its serial section
  (fail serially / alone at base). Two xdist-list entries passed this time: `check/test_twins::test_check_writes_the_evidence_schema`
  ("openmp key on this host") and `ops/test_row_pod_cancel_forwarding::test_sigint_is_forwarded_the_same_way` (15 s timeout under load).
  Skip reasons: all in a1's list (297, same as base). A/B 20:44Z: the gc-freeze file alone fails the same 2 tests at head and at base
  (`/workspace/b0` = 72884c8a rebuilt from the head tree + `git diff --binary 4fb0eb2c 72884c8a`, 36 blobs checked == git ls-tree, 3
  head-only files absent). Logs: `logs/gate_b_final.{log,xml,env,rss}`, `logs/gate_b_final.fails.txt`.
- 20:26Z GPU pod `vyv-rf-f3-g1` (`qslw50vgt2kt9m`, 1x L40S, SECURE, $1.09/h) created; no ip/port in 28 min -> terminated 20:56Z.
  20:57Z `vyv-rf-f3-g2` (`by47y4tvsavbln`, 1x L40S 46 GB, driver 595.91, 16 vCPU, 120 GB, $1.09/h) up in ~1 min.
  21:00Z head tree `/workspace/head` = `4fb0eb2c` (tar sync 158 s); `/workspace/basetree` = 72884c8a rebuilt from it (reverse diff,
  36 blobs == git ls-tree, 3 head-only files absent). 21:00Z `pod_bootstrap.sh --gpu --cases B0 --out /workspace/bootstrap` from the
  head tree -> `/workspace/rff3/bootstrap.log` (21:01:58Z checkpoint OK B0; native taps next).
  D3 plan (known_roots.json smollm2 cc 8.9 `cb129578…` is R12-era, not updated since 09-21, i.e. before the v2 flip and the vLLM
  pin move -> may not reproduce even at base): A/B on the one L40S -- `row_pod.sh` SmolLM2 B1 256/32 `build,match,commit` PAIRS=1
  from a head tree and from a base tree (same reverse-diff rebuild, verified by blob hash); compare Build program/manifest digests,
  plan digest, binding-map digest, run roots; known_roots as a secondary reference. No native source differs base..head, so one
  bootstrap (venv312, FA2 tap /workspace/cp/fa2, nc_build, torch-ext cache) serves both trees.

- 21:05Z gate (a) T0-only run @ `9bddf741` STOPPED (at ~110/158, 0 F so far): the brief now says gate (a) = T0+T1 (coordinator 20:33Z,
  `VERITY_REGRESSION_TIERS=T0,T1`); a1 measures the T0+T1 base. T0+T1 is a superset, so the T0 run was redundant.
- 21:09Z GPU bootstrap BOOTSTRAP-OK (readiness all true: hidden_gpu sm_89, FA2 tap hdims 64,96,128,256, vllm d9105ea80, torch 2.13.0+cu129).
- Environment (both pods, venv312): Python 3.12.14, torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80.cu129, triton 3.7.1,
  numpy 2.3.5, transformers 5.17.0, safetensors 0.8.0, pytest 9.1.1 (+ xdist 3.8.0 on the CPU pod) = a1's table; GPU driver 595.91.07.

- **21:35Z D3 GPU A/B DONE: roots unchanged.** SmolLM2 B1 256/32 `row_pod.sh build,match,commit` PAIRS=1 on the L40S, head
  `4fb0eb2c` and base `72884c8a` trees, VERITY_(LEAF_)LAYOUT unset: both exit 0, `commit_pass` true, run root
  `cb129578b7846e1f…` at head == at base == known_roots.json smollm2 cc 8.9 (so the R12-era pin still reproduces). Program digest
  `64033eec…`, manifest digest `e3c2a34d…`, `acquisition_plan.json` (sha `1c2bf930…`), binding map (`chunk-leaf-v1`) identical.
  `ab_compare.py` (volatile keys normalized): 53 files identical, incl. commit/{verdict, binding_map_p0, layouts_pair0_instrumented,
  structure_p0, runtime_tree, manifest_verify, acquisition_plan}.json, manifest.json, match/{program, instances, card, gates}.
  The differing files are all explained: (1) `descriptor_sha256` / source hashes of `program/registry/prims` etc. (D15 edited those
  sources; the Program digest does not hash them); (2) inputs-trace counts and admission-planner RSS bounds (runtime measurements);
  (3) `match/{experiment,run}.json` `sampling.seed` null (was 0) -- D14's documented change, no reader but experiment.py's copy;
  (4) `hidden_gpu.py` resolved at different paths (same bytes `bbcd179c…` everywhere); (5) 6 `match/capture/snapshots.json`
  entries = `block_table_ptrs` / `{src,dst}_block_table_ptrs` uint64 device pointers (2 middle bytes differ: CUDA allocation
  addresses), identical metadata. Evidence copied to `evidence/d3_ab/` beside this file (row logs, verdicts, stages, compare output).
- 21:18Z / 21:38Z **gate (a) T0+T1 OOM, both runs** (exit 137; cgroup 64 GB, `oom_kill 2`): the base died with 2 runs on the pod, the
  head then alone on the same check. Both after the same 22 results: the 23rd check is `T1-replay_partition-r11`. Cause (as a23b found
  at 21:10Z): `tests/regression/checks/replay_partition.py` loads a B=1 row's whole Program ("0.9-1.7 GB compressed, 120-250 GB of RAM as
  Python objects: a big pod"). Not f3's: base and head die at the same check; the check calls `SR.sample(pool, per_stratum, seed)` with the
  record's seed, which D14 did not touch (D14 removed only `sampled_replay()`'s `seed=0` default).
  Plan, as f24: T0+T1 on this pod with the two B=1 checks deselected (head + base), and those two on a big cpu3m pod (head; base only
  if the head does not pass). **a1's T0+T1 base on its 64 GB cpu3g pod will hit the same OOM.**

## Running (pod `vyv-rf-f3-veritor-campaign`, RunPod `drd3w6z9d22gvd`, cpu3g 16 vCPU / 64 GB, created 19:17Z)
- 21:43Z gate (a) T0+T1 minus `--deselect ...test_reproduces[T1-replay_partition-r11]` and `...[T1-replay_partition-r39]`, both `nice`,
  concurrently, same trees (checked: no file written in them by the killed runs), fresh scratch per tag, no key on disk/env:
  head `/workspace/head-reg` (4fb0eb2c) -> `logs/a_head_t01d.*`; base `/workspace/b0-reg` (72884c8a) -> `logs/a_base_t01d.*`.
  Killed runs' logs: `logs/a_{head,base}_t01.*`.
## Running (GPU pod `vyv-rf-f3-g2`, RunPod `by47y4tvsavbln`)
- 21:36Z `/workspace/rff3/lateread_ab.sh`: the canary's lateread negative (`commit_delta ... --late-read qkv_proj`, canary BASE args)
  from the head tree, then the base tree -> `logs/lateread_{head,base}.log`, out `/workspace/cp/lateread-{head,base}/`, summary
  `logs/lateread_ab.out`. Expect roots head == base != known-good, and `acquisition_plan.json` to differ (the D4 behaviour note above).
  Terminate the GPU pod when it is done (D3 A/B finished; `row_ab.sh` logs in `logs/row_{head,base}.log`).

## (older) CPU pod notes
- Trees: `/workspace/base` = `4fb0eb2c` (rsync 20:17Z; only bootstrap ran in it); copies `/workspace/{tgt,ga,gb}` = `9bddf741`.
  Bootstrap `/workspace/bootstrap`, venv `/workspace/venv312`. Scripts `/workspace/rff3/gate_{a,b}.sh` (a1's), logs `/workspace/rff3/logs/`.
- T0-only gate (a) @ `9bddf741` in `/workspace/ga`: stopped 21:05Z (see above); partial log `logs/gate_a.log`.
- Gate (b) final: done (above). `/workspace/base` is now dirty (test_ref_prims rewrote docs/data/ref-prims); `/workspace/b0` = base rebuild (dirty copy).

## Next
1. Big pod `vyv-rf-f3-big` (cpu3m x64, 512 GB): sync head, bootstrap --cpu, own key -> prefetch #11/#39 -> delete key; run
   `T1-replay_partition-r11` and `-r39` at head side by side (as f24). Terminate as soon as they finish.
2. Gate (a): judge head vs my base (same pod, same env; green = nothing fails and every check that passed at base passes).
3. Late-read A/B result into READY; terminate the GPU pod.
4. READY.md (draft `/tmp/rf-f3/READY.draft.md` on the laptop) when gate (a) is in; terminate all pods.

## Open questions
- D15 table location: a23 owns package-data moves; if a23 does not move `fixtures/W11*`, coordinator decides who does.
  - **Coordinator answer, 19:30Z:** a23b (the successor of a23) moves `fixtures/W11*` first. Write D15 now and rebase onto a23b's `W11 move: <sha>` before gates. Details: `20260924T1930Z-handoff-from-vllm-coordinator.md` in this dir.

## Found, not fixed
- `commit_delta` still copies other CLI flags into env for acquire/commit to read (VERITY_WINDOW_MB/SLOTS, RETAIN, STAGING_BOUNDED, ...), T7/B4.
- collector/binding-map `layout` label is `chunk-leaf-v1` for host (non-gpu-tree) committers whose leaves are host-pos-leaf (label only; changing it changes map digests).
