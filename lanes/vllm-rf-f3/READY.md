---
id: vllm-rf-f3/ready
lane: vllm-rf-f3
kind: ready
status: ready
created: 2026-09-25T02:15Z
updated: 2026-09-25T03:45Z
---
# vllm-rf-f3: undeclared inputs (D3, D4, D14, D15) -- READY

**Branch** `lane/vllm-rf-f3`, **head `4c4159c5`**, rebased onto main `bbbe936c` (6 commits, all pushed; origin == `4c4159c5`).
**Pre-rebase head `4fb0eb2c`**, on `72884c8a`.

| commit | pre-rebase | what |
|---|---|---|
| `8d8952e2` | `a2164659` | D4: the gather flush tables in a torch-free module (`acquire/flush_points.py`); `acquire/plan.py` imports them unconditionally |
| `688807b9` | `0f970b0e` | D3: the leaf layout is one declared argument (`commit_delta --layout` -> collector, padding leaves, binding map); no layout env reads |
| `d0f169f3` | `bdcf4d5f` | D14: challenge seeds are required, never 0 by default; `run_config` refuses the sampled replay stages without `--seed` |
| `bb675253` | `d4a87683` | D15: the MUFU tables are the in-tree files pinned by digest; no table or arch env reads |
| (dropped) | `9bddf741` | cherry-pick of a23b's W11 move `96c12c0b`; main has it as `a9abe0a0`, so the rebase dropped it |
| `bca6ab61` | `4fb0eb2c` | D14 follow-up: the two `run_config --phase all` dry-run tests pass `--seed` |
| `4c4159c5` | | lint: main's ratchet allowlists after D3, D4, D14 and D15 (below) |

**Rebase** (coordinator notes 22:13Z and 00:32Z): `git rebase origin/main` from `4fb0eb2c` onto `bbbe936c` (main after a23b's merge
`4bd6c54c` and one research-tools commit), then `git push --force-with-lease`. The only conflicts were the three the 00:32Z note names,
all in the D15 commit: `fa2_relation.tables_dir()`, `rms_relation.tables_dir()` and the docstring of `tests/acquire/fa2_attn_oracle.py`.
They are resolved as the note says: main's `resources.files(__package__) / "tables" / <fixture id>` location, D15's deletion of the env
overrides, and its "pinned by TABLE_SHA256" docstring. That is the code the pre-rebase head already had through the cherry-pick: the
three files are byte-identical at `4fb0eb2c` and `bca6ab61` (the oracle was in `check/` there). So `bca6ab61` is exactly
`git merge-tree 4fb0eb2c bbbe936c` with f3's side taken in those three files. `git range-diff` shows every other patch unchanged, apart
from context lines main edited. `9bddf741` came up empty and git dropped it.

**Merge note:** main has since moved to `ca396d13`: 7 commits touching only `tools/research/` and `backends/direct/`, none of f3's
files, and `git merge-tree` with `4c4159c5` is clean. I have not rebased again because the brief says to rebase when the coordinator
says main moved. `git merge-tree` against the open lanes: clean with f56 `a4b823a3`. It conflicts only in
`tests/lint/allowlists/p10_size.json` with f1 `d1f18fc8` and f24 `e818a5d4`, where lanes changed neighbouring caps:
- `commit_delta.py` `main` (main 1918): f3 cut it to 1916, f1 to 1917, and f24 to 1917. After merging, run `tests/lint` and set the
  count it prints (the ratchet fails when a cap is above the count).
- With f24 only: take f24's `check/verdict.py` counts (`c2_rules` 159, module 1407) and f3's `commit/padding_steps.py` 930.

## At the rebased head `4c4159c5`

On CPU pod `vyv-rf-f3-lint` (`xroshfy57ofi18`, cpu3g 16 vCPU / 64 GB, terminated), in `/workspace/venv312` from `pod_bootstrap.sh
--cpu` plus pytest-xdist 3.8.0 and xgrammar 0.2.7. Its `uv pip freeze` equals a1's `baseline-freeze.txt` exactly, after pinning
`googleapis-common-protos` back to a1's 1.75.3 (the bootstrap pulled 1.75.4). Every run used a fresh copy of its tree and gate (b)'s
environment. Evidence: `evidence/lint_pod/` (xml, logs, env, freeze, scripts, `judge_b_exact.txt`).

- **`python -m pytest integrations/vllm/tests/lint -q`: 41 passed** at `4c4159c5` (junit: 41 tests, no failures, errors or skips).
  Main `bbbe936c` on the same pod: 41 passed. `bca6ab61` (rebased, before the lint commit): 37 passed, 4 failed. `4c4159c5` fixes them:
  - P7: deleted 17 entries made stale by this lane. These were the `VERITY_LAYOUT` / `VERITY_LEAF_LAYOUT` reads (D3), the plan's
    `except Exception` torch fallback (D4), the seed defaults (D14), and the MUFU table and `VERITY_ARCH` env reads (D15).
  - P9: one new `layer` violation, `acquire.native_collect -> acquire.flush_points`. D4's new module had no `INTERIM_LAYER` entry,
    so it took its package's layer `acquire`, one above `native_collect` (`observe|commit`), which held those tables at main. Fixed
    by mapping `verity_vllm.acquire.flush_points` to `observe|commit`, like the other committer modules. `acquire.plan` imports it
    downward.
  - P10: 3 caps lowered (`native_collect.py` module 1931, `padding_steps.py` module 930, `commit_delta.main` 1916). Seven sizes the
    lane had grown by 1-3 lines are back at their caps, and no cap was raised. The code changes:
    - `replay.main` passes `seed=a.seed or 0` to the tier b / c self-checks instead of through a temporary.
    - `run_config.main`'s seed check binds its stage list in the condition.
    - `commit_delta.make_committer` binds `layout` in its check.
    - `capture_identities.run` puts `coordinate_sample` on an existing line of its record, so the key now follows
      `input_gate_records`. This key order is the lint commit's only observable effect.
    - Formatting only, with the AST unchanged: two `run_config` help strings rewrapped (same text), one triple blank line in
      `replay.py`, and one lone `}` in `native_host.py`.
    - No other open lane touches `run_config.py`, `replay.py` or `capture_identities.py`.
- **Post-rebase checks (00:32Z note)**, at `bca6ab61` and at `4c4159c5`: every `tables_dir()` resolves under
  `verity_vllm/program/numerics/tables/` (`W11-…1800Z`, and `W11R-…1802Z` / `W11C-…1900Z` for `rms_relation` triton / cuda). Each
  loads through its `TABLE_SHA256` check with `VERITY_MUFU_TABLES`, `VERITY_RMS_TABLES`, `VERITY_MUFU_TANH_TABLES` and `VERITY_ARCH`
  unset, and again with them set to `/nonexistent` / `sm_90`, which is ignored. `MUFU_TANH_TABLE_DIR` is
  `program/registry/quarantine/dense/tables`. The digest-pin test `tests/program/test_mufu_tables_pinned.py`: 3 passed.
- **Targeted tests** (f3's test files and those of the code it touches, 31 files): 596 passed, 48 skipped, 3 failed. All three are in
  a1's list with its messages: the two `observe/test_gen_ov_easy.py` serve_untied tests and `program/test_sampling_rows.py`'s
  `nv_logf` NaN sign.
- **Gate (b) at `4c4159c5` and at main `bbbe936c`**, one after the other on this pod, with the settings of the `4fb0eb2c` run below
  (`-n 12 --dist loadfile`, `OMP_NUM_THREADS=3`):

  | tree | passed | skipped | xfailed | failed | errors | wall |
  |---|---|---|---|---|---|---|
  | head `4c4159c5` | 3534 | 286 | 6 | 54 | 11 | 13 min 22 s |
  | main `bbbe936c` | 3515 | 286 | 6 | 56 | 11 | 14 min 00 s |

  Per test (`judge_b_exact.txt`):
  - Every failure or error at head also fails at main. Main's two extra are the order-dependent
    `harness/test_admit_r19_host_working_set.py` gc-freeze tests from a1's serial section, which passed at head.
  - The 17 tests only at head are f3's, and all pass.
  - Skip reasons are the same at head and main, reason by reason.
  - Against a1's base runs, head's 65 failures and errors are exactly a1's xdist list. At head and at main alike, one skip reason is
    in neither a1 run: `program/test_ship_roots.py::test_ship_pack_carries_out_gen_hf_configs`, "this checkout has no
    record_v5/ship.sh or data/hf_configs". That comes from main's own change to the file, which f3 doesn't touch.
- **Not re-run at the rebased head:** gate (a) and the GPU rows (below, at `4fb0eb2c`). The rebase changed none of f3's code (above),
  and the lint commit's only observable effect is the key order in the `capture_identities` record, which neither covers.

## Gate evidence at the pre-rebase head `4fb0eb2c`

Environment (every pod, `/workspace/venv312` from `pod_bootstrap.sh`): Python 3.12.14, torch 2.13.0+cu129, vLLM
0.28.1rc1.dev472+gd9105ea80.cu129, triton 3.7.1, numpy 2.3.5, transformers 5.17.0, safetensors 0.8.0, pytest 9.1.1 (= a1's table).
One difference from a1's freeze: the CPU pod got `xgrammar` 0.2.8 (a1: 0.2.7; bootstrapped later). My head and base runs on that pod
share it, and gate (b)'s counts equal a1's base exactly. The gate (a) pod was pinned to 0.2.7: its freeze equals a1's
`baseline-freeze.txt` except pytest-xdist / execnet (not installed there).
Pods, all terminated: CPU `vyv-rf-f3` (`drd3w6z9d22gvd`, cpu3g 16 vCPU / 64 GB, + pytest-xdist 3.8.0) for gate (b); CPU
`vyv-rf-f3-big2` (`t5fh4zrbo4dg1s`, cpu3m 64 vCPU / 512 GB) for gate (a); CPU `vyv-rf-f3-big` (`sda06pqcfi51jt`, same flavor) for an
earlier head-only run of the two B=1 `replay_partition` checks; GPU `vyv-rf-f3-g2` (`by47y4tvsavbln`, 1x L40S, driver 595.91.07) for
the SmolLM2 A/B and the late-read A/B; GPU `vyv-rf-f3-g3` (`91c19vn318ptnj`, 1x L40S, driver 580.178.04) for row #101.
Every gate ran in a fresh copy of the tree (the suites write under the tree). Base trees (`72884c8a`): on `vyv-rf-f3` and g2, the head
tree plus `git diff --binary 4fb0eb2c 72884c8a`, checked blob by blob against `git ls-tree 72884c8a` (36 files) with the 3 head-only
files absent; on g3 and big2, `research pods sync` of a clean `72884c8a` worktree.

### (b) `python -m pytest integrations/vllm/tests` -- green against a1's baseline (xdist vs xdist)

~~~
cd /workspace/base      # 4fb0eb2c, fresh
PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src \
HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=3 \
python -m pytest integrations/vllm/tests -ra -o junit_family=xunit1 --junitxml=... -n 12 --dist loadfile
~~~

**54 failed, 3553 passed, 297 skipped, 6 xfailed, 11 errors** in 19 min 42 s (base: 54 F, 3536 passed, 297 skipped, 6 xfailed,
11 E; +17 passed = the new f3 tests). All 65 F/E are named in `vllm-rf-a1/baseline.md`: 63 from its xdist list, plus the two
`harness/test_admit_r19_host_working_set.py` gc-freeze tests from its serial section ("fail serially", one "also fails when the file runs
alone"). A/B: that file alone fails the same two tests at `4fb0eb2c` and at `72884c8a` on the same pod. Two xdist-list entries passed
this run (`check/test_twins.py::test_check_writes_the_evidence_schema`, `ops/test_row_pod_cancel_forwarding.py::test_sigint_is_forwarded_the_same_way`,
both host/timing entries in a1's list). Every skip reason is in a1's list.

An earlier run at `9bddf741` had 3 more failures, all mine: the `test_gen_llama` / `test_gen_ov_easy` `run_config --phase all` dry runs
plan `replay_a` / `replay_chain` without `--seed`, which D14 now refuses. `4fb0eb2c` passes `--seed 7` there.

### (a) `VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression` -- green

~~~
cd /workspace/head-reg  # 4fb0eb2c, fresh copy (base: /workspace/basetree-reg, 72884c8a)
PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src \
HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 RESEARCH_STORE=/workspace/research/store \
RESEARCH_STORE_CONFIG=$PWD/tools/research/store.pod.toml VERITY_REGRESSION_SCRATCH=/workspace/rff3/scratch/full_head \
VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 \
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=...
~~~

On `vyv-rf-f3-big2`, head and base side by side, each in a fresh copy of its tree with its own `VERITY_REGRESSION_SCRATCH`, nothing
deselected, no rows root or candidate. Every row's fixtures were fetched into the pod store first (26 of 26) with my own 1 h read-only
key, which was deleted before either run started (no `AWS_*` in either run's env).

| tree | tests | passed | skipped | failed | errors | wall |
|---|---|---|---|---|---|---|
| head `4fb0eb2c` | 158 | 72 | 86 | 0 | 0 | 2 h 57 min |
| base `72884c8a` | 158 | 73 | 85 | 0 | 0 | 3 h 07 min |

One test differs: `T0-manifest_digest-r11` passed at base and skipped at head ("merged Programs view has no instances.json.gz").
That is a race in the harness, not a change at head. `store_io.fetch` materialises each artifact into the store's shared cache and
only checks that the path exists. The store was fresh, so base was still writing #11's `programs` tree when head resolved it. Rerun
alone at head (fresh copy, same env, trees complete): **1 passed** (468 s). Every skip reason is the same at head and base.

Against a1's baseline (T0 only, 64 passed), every check that passed there passes at head (`manifest_digest-r11` in the rerun). T1 adds
9 passes at both trees: `T1-replay_partition` on #11, #39, #57, #60, #67, #68, #73, #74 and #101. `T1-decomp_hashes` passes nowhere.
It does not apply on 6 rows; on the other 7 (#23, #57, #60, #67, #68, #73, #74), `match/program.json` is not in the stored trees,
the store-only gap a1 names for `step_segmentation`. Pod memory peaked at 220 GB with both runs. Evidence `evidence/gate_a_full/`
(xml, logs, env, `judge_a.txt` = the per-test comparison, scripts). An earlier head-only run of the two B=1 checks on `vyv-rf-f3-big`
also passed (`evidence/gate_a_big/`).

### (c) scope acceptance

- **D3, GPU Commit row re-run, roots == the regression record:** frozen regression row **#101**
  (`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, the T0/T1 L40S B=1 row with a Commit record),
  `row_pod.sh build,match,commit` PAIRS=1 (the record's `--pairs 1`) on one L40S, both layout variables unset, from the head tree and
  from the base tree. **Head: run root `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` = the record's**
  (`commit/verdict.json` of records `art:a4ea1a18…`), `commit_pass` true, every Commit check PASS. **Base: the same root**, same
  verdict. 55 row files are identical once volatile keys are masked (both Programs' `instances.json.gz`, `manifest.json`,
  `global_match.json`, `commit/{verdict, acquisition_plan, binding_map_p0, layouts_pair0_instrumented, structure_p0}.json`,
  `match/{program.json, instances.jsonl, card.json}`); the 30 that differ are the classes listed for SmolLM2 below (here 96 of 163,409
  captured values differ: `block_table_ptrs` device pointers, 3 per step).
  The rebuilt Program (`ccc21347…`, step `03ace66f…`) and manifest (`90f81868…`, 7043 identities) are the same at head and base but
  not the record's (`079ee0a8…` / `368283ad…`, 7043): the records were built before the relayout (f24 found the same: 25 vs 27
  binding rules). The run root covers the committed values only, and those reproduce the record byte for byte.
- **D3, second row (A/B + `known_roots.json`):** SmolLM2-135M B1 256/32 (`row_pod.sh build,match,commit`,
  PAIRS=1, `native_collect_v2b --gpu-tree`, FA2 matReq tap) on one L40S, from the head tree and from the base tree, both variables
  unset (every regression row is v1 on both sides; nobody sets `VERITY_LEAF_LAYOUT`). Both exit 0, `commit_pass` true, **run root
  `cb129578b7846e1f…` at head = at base = `known_roots.json` (smollm2, cc 8.9)**. Program digest `64033eec…`, manifest digest
  `e3c2a34d…`, acquisition plan, binding map (`chunk-leaf-v1`) identical. 53 row files are identical once volatile keys are masked,
  including `commit/{verdict, binding_map_p0, layouts_pair0_instrumented, structure_p0, runtime_tree, manifest_verify}.json`,
  `manifest.json`, `match/{program.json, instances.jsonl, card.json}`. The rest differ for known reasons: the source hashes of the
  files D15 edited (`descriptor_sha256`; the Program digest doesn't hash them), measured RSS / file-open counts, `sampling.seed` null
  instead of 0 in `match/run.json` (D14), `hidden_gpu.py` resolved at another path (same bytes), and six captured
  `block_table_ptrs` values (uint64 device pointers: CUDA allocation addresses).
- **D4, plan identical with torch stubbed:** `tests/acquire/test_plan.py::test_default_tables_do_not_depend_on_torch` (fresh processes,
  torch importable vs blocked: same tables, same plan digest) passes in gate (b).
- **D14, every challenge derivation touched** (seed now required; derivation unchanged, so no sample moves for any caller that passed one):
  `CompiledKernelCheck(seed=)` (only caller: `commit_delta`, run root); `relations.draw_sample` / `ensure_adjacent_pair` (no callers);
  `replay.tier_a` / `tier_chain` and the CLI (`--seed` required for tiers a/chain; b/c keep their self-check seed); `sampled_replay.sampled_replay(seed=)`
  (78 call sites, all pass one); `capture_identities.run` and the CLI (the record gains `coordinate_sample: {seed, per_gemm}`);
  `run_config --seed` default None, refused only when `replay_a` / `replay_chain` run (row_pod skips both; cov_pod / verify_lane pass it).
  Already derived, not touched: `binding.challenge_identities`, `sampled_replay.challenge_seed`, `commit_delta` / TP `--replay-seed`,
  `tp/xrank_collectives`, `vu_query.production_sample`. Not challenges: twins self-check, stoch_recompute reference rows, holdout, difftest,
  adversarial, descriptor_equivalence, engine / workload / fixture seeds. Test: `tests/check/test_challenge_seeds.py`.
- **D15, every env-dependent Definition:** MufuTanh (`VERITY_MUFU_TANH_TABLES`, plus the dead `mufu_tanh_use_tables` override);
  MufuEx2Ftz / MufuRcpFtz / Fa2InvSum (`VERITY_MUFU_TABLES` via `fa2_relation.tables`); MufuSqrtFtz / DivFullRcp / RsqrtApprox
  (`VERITY_RMS_TABLES` via `rms_relation.tables`); and every composite / twin using them. `VERITY_ARCH` was a fallback in
  `fa2_model.arch_of` and `rms_relation.coverage` (a coverage gate, not arithmetic). Pins: `prims.MUFU_TANH_TABLE_MANIFEST_SHA256`,
  `fa2_relation.TABLE_SHA256`, `rms_relation.TABLE_SHA256`, checked on every `tables()` call. No digest moved: the env paths only
  ever pointed at the shipped fixture, and `doc` is not in `encode_program`. Test: `tests/program/test_mufu_tables_pinned.py`.
- **No Program / manifest digest change:** both GPU rows build the same Program and manifest digests at head and base (#101:
  `ccc21347…` / `90f81868…`; SmolLM2: `64033eec…` / `e3c2a34d…`). Gate (a)'s `manifest_digest` passes at head on all 10 rows where
  it applies (#11 in the rerun; #4 has no manifest of record, #70 / #75 are TP rows). `program_digest` is tier T2, outside the gate.

## What changed, and what deliberately didn't

- D3: `NativeCollectCommitter(layout=)` refuses an unknown layout (v2 outside the window refused as before); `NativeHostCommitter.layout`
  is `chunk-leaf-v1`; `padding_for_committer` takes the committer's layout; `commit_delta --layout` (default v1) is no longer copied to
  env, sets `collector.layout`, and `make_committer` refuses a non-v1 layout for committers that don't implement it. TP ranks: v1, as their
  hard-coded `layout_version_per_rank` label always claimed (an exported `VERITY_LAYOUT` could make them v2 under that label before).
- D4: under `--late-read` (canary / FA3 negatives only) the Commit-stage plan now lists the declared flush leaves (it read the mutated
  collector table before), so that negative run's plan digest changes; its roots and verdict don't. Before/after on the L40S (the SmolLM2
  row's own Commit argv + `--late-read qkv_proj`): head and base both COMMIT FAIL, exit 3, "C2 oracle mismatch: 60 identities differ
  from the Match oracle (first: step 0 model.layers.0.self_attn.qkv_proj/0 ...)", run root `8393b652…` at both (positive `cb129578…`).
  Plan: head = the positive run's plan byte for byte (`plan_digest` `6b702155…`); base `a5995461…`, whose flush residual omits every
  `qkv_proj/0` leaf.
- D14: "one derivation from the run root" (SYNTHESIS) is not done: unifying the forms moves samples and verdict checks
  (`commit_verdict._REPLAY_SEED_ROOT_FORM`, the compiled check's `seed_source`), so it waits for Phase 3 / core C4.
- D15: the table location stays one function per table set (`tables_dir()`, `tables_dir(kernel)`, `MUFU_TANH_TABLE_DIR`), now a23b's
  `importlib.resources` path.

## Found, not fixed

- `commit_delta` still copies other CLI flags into env for acquire / commit to read (`VERITY_WINDOW_MB` / `_SLOTS`, `RETAIN`,
  `STAGING_BOUNDED`, ...): T7 / B4.
- The collector / binding-map `layout` label is `chunk-leaf-v1` for host (non-gpu-tree) committers whose padding leaves are
  host-pos-leaf. Label only; changing it changes map digests (Phase 3).
- Gate (b) writes tracked files: `tests/program/test_ref_prims.py` records to `<repo>/docs/data/ref-prims/` unless
  `REF_PRIMS_RECORD_DIR` is set (32 files rewritten per run; the committed records are stale at base: `ref_vocab_digest` 82fd6a28 vs
  63c73b5e from the tree, platform fields). A re-run in a used tree tests against the rewritten records.
- `canary.sh`'s `lateread` negative is stale at base: with the canary's own arguments (no `--required-manifest`) `commit_delta` refuses
  it, exit 3, "FUSE: the acquisition plan needs --required-manifest and a hooking committer (got native_collect_v2b)", at `72884c8a` as
  at head. A canary run would record that as a FAIL ("no run root"). The same negative on the row's own Commit arguments works (above).
- `known_roots.json` has not been updated since 09-21, but its smollm2 cc 8.9 root still reproduces at base and head (above).
- Gate (a) T0+T1 does not fit a 64 GB pod. `T1-replay_partition` loads the whole Program: about 100 GB on the B=1 rows #11 / #39 (the
  check's docstring says 120-250 GB). With those two deselected, head and base side by side were still OOM-killed at
  `T1-replay_partition-r67`, after 80 identical results (`evidence/gate_a_oom/`). On 512 GB both fit side by side (220 GB peak), in
  about 3 h. `--deselect` ids are relative to the rootdir `integrations/vllm` (`tests/regression/...`); ids starting
  `integrations/vllm/...` deselect nothing.
- Regression harness: two gate (a) runs sharing a fresh store can skip checks spuriously. `store_io.fetch` returns a tree another
  process is still materialising (`research data fetch` prints the path once it exists), and `programs_root()` / `path()` then find
  files missing and raise NotResolvable. It showed up once here (above). Run one gate at a time on a fresh store, or let the first
  run finish materialising. A fix would make the fetch atomic (temp dir + rename) or have it wait on a lock.
- `research pods ssh` does not forward stdin and can run a command twice (two copies of each detached gate run once), so launch
  detached runs under `flock -n`. When launching over ssh, `cd X && setsid nohup job &` backgrounds the whole `&&` list; its subshell
  keeps the session open until the job ends, and its command line stays in `pgrep -f`. Write `cd X; setsid nohup job … &`.
