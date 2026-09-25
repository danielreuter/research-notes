---
id: vllm-rf-b1/ready
lane: vllm-rf-b1
kind: ready
status: READY
created: 2026-09-25TXX:XXZ
updated: 2026-09-25TXX:XXZ
---
# vllm-rf-b1 READY: evaluator kernels and replay

- **Branch:** `lane/vllm-rf-b1`, head `8c0bec08`, pushed. 12 commits on a4's `10996616`. a4 is not in `origin/main` yet
  (checked 12:10Z, main `2c92b9e3`), so the branch has not been rebased; when a4 merges, `git rebase --onto origin/main
  10996616 lane/vllm-rf-b1`.
- **Gates:** GATE_SUMMARY
- **Needs an owner or coordinator decision:** NEEDS
- **Scope:** 73 files, +4,317 -3,764 (the 3,099-line `check/replay/sampled_replay.py` is gone). Core `verity.evaluation`
  was not edited. No allowlist grew: net entries deleted are p03 13, p05 1, p06 3, p07 3, p08 1 and p10 2; the other
  changed entries (p03, p04, p07-p11) moved with the code they cover.

## What changed

Kernels (`program/kernels/`; the owner's rename had already moved `numerics/` and the `relations` checkers there):

- `bf3bdbec` `derived_rows.py` moves from `program/registry/` to `program/kernels/` (file move, import lines, allowlist
  paths).
- `a6613e94`, `fce215be` `program/kernels/rows.py`: the sampled-replay evaluator ladder becomes 22 per-family row kernels,
  each registered with core `register_kernel` (kernel `"rows"`) against the Definition it computes, with a sampler and,
  where the served statics are too wide for the gate reference, small check specialisations. `sampled_replay.evaluate`
  dispatched through `rows.ROWS`; the Gumbel row kernel calls core `evaluate` (the check -> properties import and its
  p05 entry go).
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
- `pipeline/commit.py`: five import lines (plus one local import removed), four one-line seed hunks (`CH.root_seed`
  twice, `CH.challenge_seed`, `CH.kernel_check_seed`), and a comment and a string naming derived_rows' new path.
- `ops/row_pod.sh`: the `form_b_families` import path and its comment. `check/weights_of_record.py`: one import line.

## Gate evidence

Pod trees: head is `research pods sync` of the worktree at `8c0bec08` (the GPU #101 tree at `19ca2453`, whose production
code is `8c0bec08`'s; `8c0bec08` changes one test), and base is `git archive 10996616`. On `vyv-rf-b1-cpu` the head
tree was checked against git blob by blob before the final gate (b); the test-written `docs/data/ref-prims` JSONs were
restored first.

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
  - Evidence beside this note: `head-gate_b-8c0bec08-xdist.xml.gz`, `base-gate_b-10996616-xdist.xml.gz`,
    `head-gate_b-8c0bec08-xdist.jdiff-base.txt`, `cpu-pod-logs.tgz` (logs, env and RSS of every cpu-pod run, including the
    earlier head runs whose failures `31a0be62`, `b7a70aa8`, `19ca2453` and `8c0bec08` fixed).
- GATE_A_EVIDENCE

## Acceptance

- **Self-check covers every (kernel, Definition) pair:** `test_kernel_self_check.py`, 31 pairs, all pass (gate (b)).
- **`check/sampled_replay.py` is gone** (`31a0be62`).
- **Seeds unchanged:** every derivation pinned by value (`test_challenge_seeds.py`,
  `test_compiled_replay_seed_source.py`); on #101 head and base draw the same seed (8853214064722388274) and the same
  picks.
- **Sampled replay unchanged on regression rows:** REPLAY_PARTITION
- **GPU Commit rows** (`row_pod.sh <row> ... build,match,commit`, `PAIRS=1`, each arm in its own sweep dir):
  - **Dense #101** (`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, `vyv-rf-b1-g1`, 1x
    L40S, `r20260925-113151-99a2`): head and base both equal the record: program `ccc21347…`, manifest `90f81868…`, run
    root `7adcef49…`, commit PASS, and every typed check is the same at head and base (runtime_match, local_replay,
    boundary_linkage, checkpoint_binding, execution_extent, required_value_coverage, program_source_identity and their
    sub-checks). C2 oracle compare 6,304 = 6,304 equal, mismatch 0, attribution complete. Sampled replay: 1,374 picked =
    evaluated = equal of 46,558 VUs in 868 strata, 0 not evaluated, seed 8853214064722388274; picks, strata, by-family and
    not-evaluable digests identical; the forked evaluators opened the same 84,118 reads (432,949 leaves). Stage walls: Build
    112 / 99 s, Match 167 / 154 s, Commit 191 / 243 s (head / base; base ran second and paid the tree switch).
  - R67_RESULT
  - **TP2 #70** (the rank path changed: `engine/rank_worker.py` imports the driver, and the evaluators changed): R70_RESULT
- **Replay wall time, before -> after:** REPLAY_WALL

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
  `cpu-pod-logs.tgz`.
- Laptop tooling: a background job started with `nohup ... &` from an agent shell dies when that shell call returns. The
  first pod-retry loop died that way after RunPod had created `vyv-rf-b1-g2` (11:18:44Z) but before `--register` ran, so
  the pod ran unregistered and unguarded until I found it in `research pods list` at 11:49Z and registered it by hand
  (`research pods register --guard 90`); about 30 idle minutes, $0.55. Later jobs were detached with
  `subprocess.Popen(start_new_session=True)`.
- RunPod had no 2x L40S on any cloud with CUDA 12.8-13.0 from 11:00Z to ROWS_END, retried every 60 s.

## Pods and cost

COST
