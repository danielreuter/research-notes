---
id: vllm-rf-a23/state
lane: vllm-rf-a23
kind: state
status: active
created: 2026-09-24T17:27Z
---
# vllm-rf-a23: dead code, data and paths (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2, §5, §6 (lanes A2, A3); survey `survey-harness-ops-tests-data.md` DEAD, Map 3, Map 4.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-a23`, branch `lane/vllm-rf-a23` from `72884c8a`.
- **Scope:** (1) delete §5.4 "dead now" + CMT-1 (`commit/reference_engine/`, `reference_engine_adapter.py`, `cmt_ref_*` in `harness/commit_delta.py`) + `commit/engine_rs/` + `tools/` and its test; move §5.4 "moved to tests" next to their tests; re-verify every deletion has no caller at 72884c8a. (2) library-read data to package data via `importlib.resources`; one helper for `manifests/` and `workloads/`; remove 8 `sys.path.insert`, 16 `parents[N]`, machine-path defaults, library read of `tests/`; pyproject ships package data.

## Done
- 17:27Z worktree created.

## Running
- nothing yet

## Next
1. Re-verify every deletion candidate at 72884c8a (imports, importlib/string paths, `-m` in ops/tests, research_tools).
2. Deletions + moves (commit per group).
3. Data/paths.
4. Pod: baseline (a1 baseline not yet written) + gates.

## Open questions
- none yet

## Found, not fixed
- none yet
