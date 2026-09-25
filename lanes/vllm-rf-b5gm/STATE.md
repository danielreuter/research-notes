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
- (none yet)

## Running
- (nothing)

## Next
- Implement the split (plan below), AST size check on the laptop, commit + push; then pods.

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
