---
id: vllm-rf-b1c/ready
lane: vllm-rf-b1c
kind: ready
status: DRAFT
created: 2026-09-25T18:10Z
updated: 2026-09-25T18:10Z
---
# vllm-rf-b1c READY: evaluator kernels and replay

b1c succeeds b1b (bc-033f1f34, ended at the 16:03Z restart), which succeeded b1 (bc-910bfdb6). The code is b1's; b1c
rebased it, merged main and a5c into it, and fixed the merge fallout. Agent bc-e079e6ee, coordinator bc-ecac3029.

- **Branch:** `lane/vllm-rf-b1c`, head **`1fd7e9dc`**, pushed. History: b1's 12 commits rebased with
  `git rebase --onto origin/main 10996616` onto main `239c0e28` (clean; head `0e954bf0`), then
  - `8f94cb48` merge `origin/main` `38a8d35d` (b2vb, b5gmb, c2b): import blocks of `properties/admission.py` and 4
    commit-verdict tests, p03/p10/p11 entries. b1 never edited `check/commit_verdict.py`, so nothing of b1's had to move
    into b2vb's `c2_rules.py` / `verdict.py`;
  - `ec6219f5` P10 `pipeline/commit.py::main` cap 1913 -> 1912 (b1 and main each removed one line);
  - `1fd7e9dc` merge `lane/vllm-rf-a5c` `40b9e571` (base of this request; merge order a5 -> b4 -> b1): `ops/row_pod.sh`
    deleted by a5, so b1's `form_b_families` import-path change moves to a5's `pipeline/row_stages.py::form_b`
    (`check.replay.coverage`); `twins.py` keeps both import sets; `tests/program/{beyond_gemm,crosscheck}.py` keep a5's
    `Options`/`main(options)` form, and **the `verity-vllm beyond-gemm` and `crosscheck` commands are removed from
    `pipeline/cli.py`** (their modules are test-side since b1's `19ca2453`; a `verity-vllm` command must name a
    `verity_vllm` module); p06 takes a5's list, P10 `commit.py::main` at the merged size 1776.
  A static scan of the merged tree (every `from verity_vllm…/tests… import` resolves, every `cli.COMMANDS` module
  exists) finds nothing but the pre-existing `workload_target` import below.
- **Gates at `1fd7e9dc`:** lints GATE_LINTS; gate (b) vs `40b9e571` GATE_B. Gate (a) T0+T1 and #101 were run by b1b on
  `8c0bec08` (the same lane code; nothing in the merges touches replay, kernels or the regression checks beyond import
  lines) and carry over.
- **GPU rows:** #101 head = base = record; #70 (TP2) head = f1's base record on 32/32 fields; **#67 not reached on
  either arm: the Commit is OOM-killed on this pod shape at base exactly as at head** (below).
- **Needs a decision:** whether #67 is re-run on a 1x L40S host with >= ~256 GB (~4.5 h from scratch: Build 2.7 h, Match
  42 min, Commit ~1-2 h; outside b1c's $10), or accepted on gate (a)'s T1 replay_partition for the MoE rows.

## What changed

Kernels (`program/kernels/`; the owner's rename had already moved `numerics/` and the `relations` checkers there):

- `bf3bdbec` `derived_rows.py` moves from `program/registry/` to `program/kernels/` (file move, import lines, allowlist
  paths).
- `a6613e94`, `fce215be` `program/kernels/rows.py`: the sampled-replay evaluator ladder becomes 22 per-family row kernels,
  each registered with core `register_kernel` (kernel `"rows"`) against the Definition it computes, with a sampler and,
  where the served statics are too wide for the gate reference, small check specialisations. The Gumbel row kernel calls
  core `evaluate` (the check -> properties import and its p05 entry go).
- `a6613e94` `program/kernels/kernel_registry.py`: core's registry plus what it does not carry yet (see "Upstream
  candidates"). A kernel is written per instance and raises `Declined(why)`; core sees the batch form with a decline
  mask, so `evaluate_batch` falls back to the reference for what a kernel declines.
- `c42923bc` The twins are core kernels (kernel `"twin"`). The Twin protocol, `twin_for`, `why_no_twin`, `TwinDeclined`,
  twins' own `self_check` and the gate-word comparator `gate_words` are deleted; `twins.admit` runs core `self_check`
  per instance; `replay.twin_of` uses `kernel_registry.covers` / `instance`.
- `e86c93b3`, `ee2a319f` `tests/program/test_kernel_self_check.py` runs core `self_check` on every registered
  (Definition, kernel) pair: 31 pairs (22 row kernels, 9 twins), plus a test that every row family and twin is
  registered with core.

Replay (`check/replay/`):

- `a6ba1e5b` `check/replay/challenge.py` holds every seed derivation of record and is the only module that constructs a
  random generator (P3 `RNG_OWNERS`): `root_seed`, `challenge_seed`, `kernel_check_seed`, `reference_rows_seed`,
  `case_seed`, `stream`, `generator`. The drivers draw from it: sampled replay, replay's tier A / chain tiers,
  `compiled_kernel_check`, `stoch_recompute`'s reference rows, `vu_query.production_sample`, difftest
  (`properties/admission.produce`) and the relation sampler (`draw_sample` / `ensure_adjacent_pair`). No derivation
  changed; `tests/check/test_challenge_seeds.py` pins each one by value.
- `31a0be62` `check/replay/sampled_replay.py` is deleted, split into `index` (ProgramIndex, struct parsing), `opening`
  (CommittedStore over the opened reader it is given; weights provider), `population`, `coverage`, `sample`,
  `evaluate`, `compare`, `linkage` and `driver` (the C2 driver). The import graph is acyclic. `driver.__all__`
  re-exports the caller interface, so `pipeline/commit.py` and `engine/rank_worker.py` change one import line each
  (`driver as SR`). Opened values come from f1's `commit.opened.OpenedReader`, which `pipeline/commit.py` hands in, as
  before.
- `7cde62a5` difftest's `evaluate_spec` is core `verity.evaluation.evaluate` over word arrays (it built a one-call
  Program by hand and imported `observe.fold`'s `_replayer`). This works for unregistered specs (`DT.spec(...)`).
- `19ca2453` `program/registry/crosscheck.py` and `program/kernels/beyond_gemm.py` move to `tests/program/`: their only
  production importer was the twins' gate-word self-check, so `test_no_dead_modules` failed without the move. Their p03,
  p06, p07 and p08 entries are deleted; `dead_code_keep.json`'s `fa3_model` reason drops "crosscheck".
- `b7a70aa8`, `8c0bec08` tests that read source text follow the new call sites (`CH.kernel_check_seed(rc.run_root)`,
  whose value the test also pins, and `SR.arrivals_of_record`). **History note:** `b7a70aa8` also carries the two `git mv`
  renames of `19ca2453` (staged by `git mv`); their import lines are in `19ca2453`, so `b7a70aa8` alone does not import.
  History was not rewritten.

Hunks in other lanes' files (import lines unless stated):

- c2, `program/registry/`: `ref_prims.py:850` and `sampling_rows.py:34` (derived_rows import). `crosscheck.py` left the
  directory (`19ca2453`).
- b4, `engine/rank_worker.py:1143`: `sampled_replay as SR` -> `driver as SR`.
- b2v, `properties/admission.py`: the difftest rng lines (`CH.stream`, `CH.generator(CH.case_seed(...))`) and the
  `evaluate_spec` body (core `evaluate`), beyond import lines, because difftest is one of the four drivers in scope.
- `pipeline/commit.py` (a5 area): five import lines (plus one local import removed), four one-line seed hunks
  (`CH.root_seed` twice, `CH.challenge_seed`, `CH.kernel_check_seed`), and a comment and a string naming derived_rows' new path.
- `ops/row_pod.sh`: the `form_b_families` import path and its comment. `check/weights_of_record.py`: one import line.
- `tests/regression/checks/replay_partition.py` and `test_check_lifts.py`: import lines and call-site prefixes
  (`SR.X` -> `IX.` / `POP.` / `SM.X` of the split modules; `sampled_replay as SR` -> `driver as SR`).

## Gate evidence

Pod trees: head is `research pods sync` of the worktree at `8c0bec08` (the GPU #101 tree at `19ca2453`, whose production
code is `8c0bec08`'s; `8c0bec08` changes one test), and base is `git archive 10996616`. On `vyv-rf-b1-cpu` the head
tree was checked against git blob by blob before the final gate (b).

- **Lints** (`tests/lint`, `test_no_by_name_rules.py`, `test_imports_resolve.py`): 45/45 pass at head, inside the gate (b)
  run below.
- **Gate (b)**, `OMP_NUM_THREADS=3 ... -n 12 --dist loadfile`, head and base on the same pod (`vyv-rf-b1-cpu`, cpu3g 32
  vCPU / 128 GB), head `r20260925-112532-d480`; compared with `baseline-jdiff.py` (exit 0):
  - Base: 4,001 tests, 3,645 passed, 52 failed, 11 errors, 287 skipped, 6 xfailed. Head: 4,036 tests, 3,683 passed, 50
    failed, 11 errors, 286 skipped, 6 xfailed.
  - New failures 0, new errors 0, new skips 0, new skip reasons 0. Failures + errors 63 -> 61.
  - Fixed on head: `test_row_pod_cancel_forwarding::test_sigint_is_forwarded_the_same_way` (a 15 s timeout at base) and
    `test_twins::test_check_writes_the_evidence_schema` (a4 showed it depends on whether the numerics build directory
    starts empty). `test_observer_encoding::test_weakref_death...` went from skipped to passed (order-dependent).
  - **Renamed test ids (4):** `test_twins::test_twin_for_covers_every_logged_specialization[m1-statics0|m6-statics1]` ->
    `test_twins_cover_every_logged_specialization[...]`; `test_twin_for_declines_statics_outside_the_body` ->
    `test_twins_decline_statics_outside_the_body`; `test_challenge_seeds::test_the_seed_has_no_default[verity_vllm.check.replay.sampled_replay-sampled_replay]`
    -> `[verity_vllm.check.replay.driver-sampled_replay]` (the parameter is the module path). All pass.
  - 39 ids only on head, all pass: the 31 self-check pairs, the registration test, 3 new challenge-seed tests and the 4
    renamed ids.
  - `test_roundtrip::test_transient_storage_is_released`, which failed in an earlier head run at `a6ba1e5b` (c1 saw it flip
    too), passes at head and at base.
  - Evidence (b1's notes, `lanes/vllm-rf-b1/`): `head-gate_b-8c0bec08-xdist.xml.gz`,
    `base-gate_b-10996616-xdist.xml.gz`, `head-gate_b-8c0bec08-xdist.jdiff-base.txt`, `cpu-pod-logs.tgz`.
- **Gate (a)** T0+T1 (`VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 ... -m regression`), `vyv-rf-b1-big` (cpu3m 64
  vCPU / 512 GB), run `r20260925-115853-be37` (`tools/big_gate_a.sh`): fixtures prefetched with a 3 h read-only key (ok=26
  fail=0, key deleted); head in four processes over disjoint tests (everything but `replay_partition`, and
  `replay_partition` in three row groups), then base `replay_partition` in the same three groups on the same pod.
  - Head merged vs a23b's `gate_a-t0t1-base-72884c8a-samepod.xml.gz` (`baseline-jdiff.py`): the same 158 test ids, 73
    passed / 85 skipped on both sides, 0 outcome changes, 0 failures or errors, 0 new skips.
  - jdiff exits 1 only on two skip-reason texts, T0 `manifest_digest` for #70 and #75: "merged by `row_pod_tp2.sh`" became
    "merged by `tp_stage.sh`". That text is a4's base (`10996616` `tests/regression/checks/manifest_digest.py:46`), not
    this lane's change.
  - Evidence: `evidence/gate_a/gate_a-8c0bec08.tgz` (merged head and base XML, per-process driver logs, prefetch log),
    `evidence/gate_a/jdiff-a23b-vs-head-and-rptimes.txt`. The whole run dir is in R2 as run-files/v1
    `art:c62253feccee236bd2da2346e3e8db370dafc0be6e7f5a1861b376f06fdfb1e1`.

## Acceptance

- **Self-check covers every (kernel, Definition) pair:** `test_kernel_self_check.py`, 31 pairs, all pass (gate (b)).
- **`check/sampled_replay.py` is gone** (`31a0be62`).
- **Seeds unchanged:** every derivation pinned by value (`test_challenge_seeds.py`,
  `test_compiled_replay_seed_source.py`); on #101 head and base draw the same seed (8853214064722388274) and the same
  picks.
- **Sampled replay unchanged on regression rows:** gate (a) T1 `replay_partition` passes at head and at base on the same
  pod for #101, #11, #39, #57, #60, #67, #68, #73 and #74 (the recorded partition, strata and picks reproduce; #4, #23,
  #70 and #75 skip on both, no sampled_replay record). Dense and MoE rows are both in that set (#67, #68, #73, #74 are MoE).
- **GPU Commit rows** (`row_pod.sh <row> ... build,match,commit` / `tp_stage.sh`, `PAIRS=1`):
  - **Dense #101** (`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, `vyv-rf-b1-g1`, 1x
    L40S, `r20260925-113151-99a2`): head and base both equal the record: program `ccc21347…`, manifest `90f81868…`, run
    root `7adcef49…`, commit PASS, and every typed check is the same at head and base (runtime_match, local_replay,
    boundary_linkage, checkpoint_binding, execution_extent, required_value_coverage, program_source_identity and their
    sub-checks). C2 oracle compare 6,304 = 6,304 equal, mismatch 0, attribution complete. Sampled replay: 1,374 picked =
    evaluated = equal of 46,558 VUs in 868 strata, 0 not evaluated, seed 8853214064722388274; picks, strata, by-family and
    not-evaluable digests identical; the forked evaluators opened the same 84,118 reads (432,949 leaves). Stage walls: Build
    112 / 99 s, Match 167 / 154 s, Commit 191 / 243 s (head / base; base ran second and paid the tree switch).
  - **MoE #67** (`olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager`, `vyv-rf-b1-g2`, 1x L40S,
    cgroup limit 175 GiB, pre-merge tree `8c0bec08`; base `10996616`): Build PASS (9,739 s), Match PASS (2,510 s;
    verdict PASS, global PASS, tokens_equal, fold) against the record's program `fdd998d4` / v2 manifest `47990631`
    lineage. **Commit OOM-killed at head and at base, identically:** head rc 137 after 2,598 s
    (`r20260925-120629-a48a`, run dir `art:ef852ef3dde91db67bcda746dae9b96057f6bc4b6f6ddf921e28da293d29d566`), base rc 137
    after 2,676 s (`r20260925-170559-fe8e`, custody-r2, PRESERVED). Both die right after sampled replay forks 32 workers
    (head 250,868,374 / base 250,867,638 objects frozen), with 85.8 GiB of shmem (host retention) held since the instrumented
    run and anon at 58 GiB before the fork on both (per-minute cgroup curves track within 1-3 GiB). The admission advisory
    predicted it on both ("commit=REFUSE 191,021 MiB, short 11,730 MiB of 179,290"). Before the kill, head's C2 oracle
    compare (pair 0) was 16,120 = 16,120 equal, 278,604 opened reads / 36.8 M leaves verified. So #67's verdict row is not
    produced by this lane; it is a host-memory limit, not a code change (f1's 188 GB g1b got through base #67's sampled
    replay on `72884c8a` for 1 h 50 min before a cancel; since then this host shape does not fit).
  - **TP2 #70** (the rank path changed: `engine/rank_worker.py` imports the driver, and the evaluators changed):
    `vyv-rf-b1-tp2` (2x L40S), `r20260925-141723-16b0` (custody-r2, PRESERVED; run_files
    `art:96703080859f66c77c3f5e834c60dfcbe30e47b9de1468850c13e94571fa8e75`), head `8c0bec08` PAIRS=1 against f1's base
    Commit of record (3 pairs): **32/32 fields equal** (tp_run_root, per-rank roots, leaves, tensors, bytes bound, classes,
    openings, tokens_equal, commit_pass, pass, value_check, match oracle per rank, sampled_replay / boundary_linkage /
    cross_rank_collectives / fold_match_binding / query_population / weights_pin results, required manifest digest, ...).
    Root `0b91229f06480ce4` as recorded. Both head and record carry `pass False`: the record's own failure (fold_match
    `AllGather2_v1{N=1024}.parts: own partial must be a row-major bf16 [1, 1024] view`, replay/xrank/fold_binding False)
    reproduces field for field. Build 1,330 s, Match 1,179 s, Commit 3,439 s. Evidence `evidence/r70_cmp.txt`.
- **Replay wall time, before -> after:**
  - #101 GPU Commit sampled replay: 79.3 s (base) -> 79.8 s (head), 32 workers, same pod.
  - Gate (a) T1 `replay_partition`, CPU over recorded words, same pod, head vs base: 3,409 s vs 3,422 s in total (9 rows);
    per row #101 3.4 / 3.4, #11 465.7 / 469.8, #39 833.2 / 838.9, #57 165.6 / 166.6, #60 168.1 / 170.0, #67 359.4 / 362.2,
    #68 361.0 / 355.5, #73 472.0 / 473.0, #74 580.9 / 582.7 s (within 1.6% everywhere).
  - #67: no Commit wall at either arm (both OOM-killed, above).

## Deliberately not changed

- Core `verity.evaluation` is untouched; what the integration needs beyond it is in `kernel_registry.py`.
- Every row evaluator is bit-for-bit what `sampled_replay.py` computed, including where it differs from its Definition on
  edge words (below), because no per-VU result may move.
- The `relations` checkers (`program/kernels/relations.py`, `compiled_relations.py`) check node instances of compiled
  kernels against the numerics models; they are not (Definition, kernel) pairs, so they are not registered with core.
  They now draw their samples from the challenge module.
- Seed sites in other lanes' files or in modules at their P10 cap are not routed through `challenge.py` (listed below).

## Upstream candidates (core `verity.evaluation`)

- An instance form of a kernel that says why it declines (`kernel_registry.instance`, `Declined`), where core's kernel is
  a batch function with a decline mask.
- A per-specialisation domain (`covers(statics)` -> reason or None), where core's `domain` is a description.
- The specialisations a kernel's self-check binds when the served statics are too wide for the gate reference
  (`check_targets(rng)`).
- The list of registered (Definition, kernel) pairs (`registered()`), which `self_check` coverage tests need.
- `check/replay/challenge.py`'s derivations, if other integrations should sample the same way.

## Found, not fixed

- `pipeline/commit.py` (`from verity_vllm.pipeline.workload import workload_target`, on main since before `10996616`):
  the function lives in `pipeline/global_program.py`, so the ImportError is always swallowed and the admission bound's
  `lag` is always 1 (its comment calls that the sound side). Not this lane's file.
- #67 on a 188 GB 1x L40S host: Commit exceeds the cgroup at head and base (above); the admission advisory already says
  so, but only as a WARN, so the stage runs ~45 min before the kill. After the kill the engine child keeps the GPU, so a
  following Commit on the same pod fails at vLLM start (`Free memory on device ... less than desired`): row_pod did not
  reap it (seen in `r20260925-120629-a48a`'s base arm).

- The row evaluators differ from their Definitions on edge words (the twins follow the Definition): `TokenSelect_v1`
  with a NaN `logits[0]` (Definition 0; row kernel the argmax of the rest), `BiasAdd_v1` NaN result word (Definition
  0x7FC0; row kernel 0x7FFF), and `Gemm_v1`, `MoeExpertGemm(W)_v1` and padded MoE blocks evaluate lanes with a
  non-finite operand or accumulator with the vectorised twin instead of declining. Committed finite words do not reach
  these; the core batch kernel declines them.
- Seed sites not routed through the challenge module: `engine/rank_worker.py:1220` root seed (b4),
  `check/commit_verdict.py`'s seed recompute (b2v), `commit/binding.challenge_identities` (c1),
  `correspondence/capture_identities.run`'s `default_rng(seed)` (module at its P10 cap).
- `relations.draw_sample` / `ensure_adjacent_pair` have no caller in the integration.
- `kernel_registry._batch` treats `ValueError` as a decline, as the ladder did; a kernel bug that raises `ValueError` is
  therefore a fallback to the reference, not an error.
- Prose outside this lane still names `sampled_replay.X`: `engine/rank_worker.py`'s docstring and other lanes'
  docstrings; `tests/commit/fa2_prototype/oracle.py` names crosscheck's old path. `tests/program/crosscheck.py` keeps its
  unused imports.
- Gate (b)'s base run on `vyv-rf-b1-cpu` was started with nohup, not `research run`; its logs, env and RSS files are in
  b1's `cpu-pod-logs.tgz`.
- Runs launched before the 12:26Z `--custody-r2` rule cannot get R2 custody from the pod: `research data custody RUN
  --publish` refuses them ("the attempt names no run record (published without custody): only `research fetch --all` gives
  this run custody"), and `fetch --all` is banned. b1b preserved their run dirs with `data put --kind run-files/v1 --tree
  --preserve` from the pod (`tools/put_runfiles.sh`) and terminated `vyv-rf-b1-big` with `drain --custody-r2 --force`
  (reason logged). The research tool could accept a run-files tree as custody for such runs.
- Laptop tooling: a background job started with `nohup ... &` from an agent shell dies when that shell call returns. b1's
  first pod-retry loop died that way after RunPod had created `vyv-rf-b1-g2` (11:18:44Z) but before `--register`, so the pod
  ran unregistered for ~30 idle minutes ($0.55). Its later loop was detached with `subprocess.Popen(start_new_session=True)`,
  outlived b1's hang, and created `vyv-rf-b1-tp2` at 13:09Z; b1b found it idle at 14:05Z (~1 h, ~$2.2) and used it for #70.
- RunPod had no 2x L40S on any cloud with CUDA 12.8-13.0 from 11:00Z to 13:09Z, retried every 60 s.

## Pods and cost

b1c (from 16:20Z): `vyv-rf-b1-tp2` terminated 16:28Z (~$0.3); `vyv-rf-b1-g2` terminated 18:03Z (~$1.9); `vyv-rf-b5pat-cpu`
(from b5patc, 16:40Z) GATE_CPU. b1c total ~COST_B1C of its $10. b1 + b1b before: ~$32 of $45 (b1b's estimate).
