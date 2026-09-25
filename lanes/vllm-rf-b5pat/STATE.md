---
id: vllm-rf-b5pat/state
lane: vllm-rf-b5pat
kind: state
created: 2026-09-25T11:24Z
updated: 2026-09-25T11:24Z
---
# vllm-rf-b5pat: split observe/fold/patterns.py into observe/fold/patterns/ (state)

- a4 base: 10996616
- Worktree: `~/projects/verity-wt/rf-b5pat`, branch `lane/vllm-rf-b5pat`.
- Coordinator: vLLM coordinator (Cursor agent bc-ba6cec03). Brief: `../vllm-refactor/WAVE2_BRIEF.md`.
- Scope (from the prompt): B5 split of the fold's kernel-pattern module into `observe/fold/patterns/`, one module per
  kernel family; `tp/collective_pattern` (now `observe/fold/collective_pattern.py`) goes there too. Pure structure;
  importers updated, no shims; P10 entries leave the ratchet; P8 entries move with their code; no allowlist grows.
- Budget: $15 of pod spend, CPU pods only (cpu3g gate (b) + re-folds; cpu3m 512 GB gate (a)).

## Done
- 11:24Z worktree created at 10996616.

## Running
- (none)

## Next
- Read `observe/fold/patterns.py`, `patterns_fp8.py`, `patterns_prefix.py`, `collective_pattern.py`, the fold's
  dispatch order and every importer; plan the family split.

## Open questions
- (none)

## Found, not fixed
- (none)
