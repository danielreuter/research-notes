---
id: vllm-rf-b5gm/state
lane: vllm-rf-b5gm
kind: state
created: 2026-09-25T09:10Z
---
# vllm-rf-b5gm: split check/match/global_match.py (state)

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

- a4 base: 10996616
- Worktree: `~/projects/verity-wt/rf-b5gm`, branch `lane/vllm-rf-b5gm`.
- Brief: `../vllm-refactor/WAVE2_BRIEF.md`; scope from the coordinator prompt (B5, global_match `_check`).
- Budget: $15 of pod spend, CPU pods only.

## Done
- 10:00Z `55b9d1ff` (pushed): the split. `global_match.py` 416 lines, `_check` 119; new `match_run.py`, `record.py`,
  `sampler_geometry.py`, `declaration.py`, `attribution.py`, `per_request.py`, `chronology.py`, `engine_steps.py`.
  P10 entries `_check`, `_check.leg`, `<module>` deleted; P03/P04/P07/P09/P11/by_name entries moved (counts equal).
  Tests: `test_global_match.py`, `test_compare_splits_binding.py`, `test_global_program_regress.py` import the moved names
  from their new modules. Laptop: pyflakes clean, every lint test function passes (stdlib runner), by_name 0/0.

## Pods
- `vyv-rf-b5gm-cpu` = RunPod `d8iv0xx7nruohu` (cpu3g 16 vCPU / 64 GB cgroup, EPYC 7713 host, 80 GB, $0.64/h), created ~10:08Z.
  Bootstrap run `r20260925-100929-878e` BOOTSTRAP-OK; + pytest-xdist 3.8.0, xgrammar 0.2.7, googleapis-common-protos 1.75.3,
  uvicorn 0.53.0 -> `uv pip freeze` identical to a1's `baseline-freeze.txt`. Trees: `/workspace/research/src/{55b9d1ff...,10996616...}`
  (base shipped from a detached worktree `~/projects/verity-wt/rf-b5gm-base`, run `r20260925-101120-a5ca`).
  GM-01 inputs: ro key minted on the laptop, piped in, fetched (matchrec 66 s, build 160 s), key deleted 10:18:45Z.
- `vyv-rf-b5gm-big` = RunPod `jnuvfc6j890g7v` (cpu3m 32 vCPU / 256 GB, EPYC 9655 as a23b's, 200 GB, $1.76/h), created 10:31Z.
  cpu3m and cpu5m x64 (512 GB) were "no instances available" on every try 10:08-10:30Z; a single T0+T1 run peaked ~63 GB at a23b.
  Bootstrap run `r20260925-103915-eb0b`.

## Runs
- Lints at head (cpu): `r20260925-102424-bb2e` rc 0, 45 tests passed.
- GM-01 base1 (base tree): `r20260925-102545-9b89` rc 0, wall 550.6 s, CPU 1878.3+211.5 s, 13.34 GiB (host load ~210).
- GM-01 head1: `r20260925-103943-2969` running.

## Next
- cpu: bootstrap, GM-01 inputs (own ro key, deleted after fetch), lints, GM-01 ABAB base/head, gate (b) head + base.
- big: bootstrap, prefetch (own ro key, deleted), gate (a) T0+T1 at head; jdiff vs a23b's same-pod base XML.

## GM-01 inputs (row #23), as f24 (`/workspace/gm23/{build,matchrec}`, `evidence/gm_run.sh`)
- Match record `art:33632a009b86fb07e24c8cf39ff7aabb31836ebbb4f58cda56943c3a5588d7d4` (fixture, 2.94 GB, source
  `/workspace/cp/sweep_v2acq/<row>`, excludes the build_request* symlinks) -> `/workspace/gm23/matchrec`.
- Staged Build: correspondence builds `art:7e51cdad13a4328b58697762a5b7d48598bcd4445db26d8bbaa2c01d34654542` (2.1 GB, `/workspace/v2corr`):
  `<row>/build_workload`, `<row>/build_request`, `<row>/shapes/build_request_LP*_T*` -> `/workspace/gm23/build`.
- Layout: `/workspace/cp/sweep_v2acq/<row>/{match,...}` -> matchrec, `build_workload`, `build_request`, `build_request_LP*` -> build.
- Same output path for base and head (`/workspace/out/gm/run`, moved aside after each run) so `x09.pipeline.decomp_out` is equal;
  `global_match_fast.py` untouched so `impl.source_sha256` is equal.

## Plan (split)
- `global_match.py` keeps the docstring, constants, `check`, a short `_check` driver, `match_ops`, impl dispatch, `main` (a5's).
- New modules under `check/match/` (one job each): Program declaration + engine facts + G1; record reading/canonicalisation;
  sampler geometry; per-request G3/G4/G5; G6 chronology; G7 + G8; a small shared-state base.
- Code moves verbatim and in order (dict key order, `mark()` order, `P.canon` side effects).

## Open questions
- P09 `module-cycle` entry: the SCC `batch_decomp <-> global_match <-> global_match_fast <-> program_compare <-> ...` exists
  because GMF imports GM (deferred) and BD reads GMF via `sys.modules.get`. Any new module GM imports that imports BD/C/GMF
  joins the SCC, so the entry's member list must name the new modules (no new external edge). Recorded in READY.md.

## Found, not fixed
- (none)
