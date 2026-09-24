---
id: vllm-rf-f1/state
lane: vllm-rf-f1
kind: state
status: active
created: 2026-09-24T17:32Z
---
# vllm-rf-f1: opened-value replay (D1) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 D1, §4 P2; `20260924T1625Z-coordinator-checks-on-check-commit-survey.md`; `survey-check-commit.md` §3.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f1`, branch `lane/vllm-rf-f1` from `72884c8a`.
- **Scope:** the verdict-bearing Commit value check (`oracle_compare` via `committed_reader`) consumes opened, root-verified values only; same for the per-rank TP path; mutate-after-commit negative test (CPU double or pod-marked) plus one real pod run; re-run cheapest dense, MoE, TP2 regression Commit rows via research Tools; commit time before/after.

## Done
- 17:32Z worktree created.

## Running
- nothing yet

## Next
1. Read the value-check path (`check/oracle_compare.py`, `harness/commit_delta.py`, `tp/worker.py`, `tp/partial_source.py`) and the opening path; map compared vs opened positions.
2. Read `tools/research/README.md`, `integrations/vllm/ops/`, `tests/regression/fixtures.toml`.

## Open questions
- none yet

## Found, not fixed
- none yet
