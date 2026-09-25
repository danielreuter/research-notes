---
id: vllm-rf-f3/ready
lane: vllm-rf-f3
kind: ready
status: ready
created: 2026-09-25T02:15Z
---
# vllm-rf-f3: undeclared inputs (D3, D4, D14, D15) -- READY

**Branch** `lane/vllm-rf-f3`, **head `4fb0eb2c`**, on `72884c8a` (6 commits, all pushed):

| commit | what |
|---|---|
| `a2164659` | D4: the gather flush tables in a torch-free module (`acquire/flush_points.py`); `acquire/plan.py` imports them unconditionally |
| `0f970b0e` | D3: the leaf layout is one declared argument (`commit_delta --layout` -> collector, padding leaves, binding map); no layout env reads |
| `bdcf4d5f` | D14: challenge seeds are required, never 0 by default; `run_config` refuses the sampled replay stages without `--seed` |
| `d4a87683` | D15: the MUFU tables are the in-tree files pinned by digest; no table or arch env reads |
| `9bddf741` | cherry-pick of a23b's W11 move `96c12c0b` (tables as package data under `program/numerics/tables/`), conflicts resolved to D15's form |
| `4fb0eb2c` | D14 follow-up: the two `run_config --phase all` dry-run tests pass `--seed` |

Merge note: `9bddf741` is a cherry-pick of a23b's `96c12c0b` (the handoff allowed rebase or cherry-pick), taken without a23b's four
earlier commits so that gate (b) compares with a1's base list. `git merge-tree`: clean against main `21688b01`, a1 `39c5ee7a`, f1
`e2f85a82`, f24 `be366f80` and f56 `9b07c19f`. Against a23b `748d71c5` there are 3 conflicting hunks, all of one kind: a23b keeps the
env override that D15 deletes. They are `fa2_relation.tables_dir()` and `rms_relation.tables_dir()` (the `os.environ.get(TABLES_ENV)`
lines) and one docstring line of `fa2_attn_oracle.py`, which a23b moved to `tests/acquire/`. Take f3's side in each. `git grep` on a23b
finds no other use of a name f3 removes. If a later a23b commit deletes `check/relations.py` (it hasn't so far), drop its 2 entries
from `tests/check/test_challenge_seeds.py`.

## Gate evidence

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
