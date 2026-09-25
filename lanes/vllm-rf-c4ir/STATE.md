---
id: vllm-rf-c4ir/state
lane: vllm-rf-c4ir
kind: state
status: active
created: 2026-09-25T06:55Z
---
# vllm-rf-c4ir: boundary, partition and liveness into core `verity.ir` (state)

> Coordinator: vLLM coordinator, Cursor agent bc-ba6cec03. Research coordinator merges; never merge into main.
> Branch `lane/vllm-rf-c4ir`, worktree `/Users/danielreuter/projects/verity-wt/rf-c4ir`, from `origin/main` `00ffe398`.
> Deadline: every `vyv-` pod dies at 2026-09-25T09:00Z (coordinator extends it here). Budget: $15 of pod spend.

- **Scope:** owner decision 5 (5a for boundary, partition, liveness). Phase 1: add the three analyses to core
  `verity.ir` (integration behaviour = spec; extend core's partial versions), core tests + equivalence tests, core suite
  on a CPU pod. Phase 2 (after `lane/vllm-rf-a4` is in `origin/main`): rebase, switch the integration to core, delete
  its copies (no shims), fix importers, lint allowlists, `INTERIM_LAYER`; gates: lints, core tests, gate (b) head vs base
  same pod, gate (a) T0+T1 on cpu3m 512 GB, GPU Build smoke #101 digests equal.
- **Invariant:** no Program digest, manifest digest, commitment root, leaf id or regression verdict changes.

## Done
- 06:55Z worktree created at `origin/main` `00ffe398`; STATE.md created.

## Running
- nothing.

## Next
- Read core `verity.ir` and the integration's `query/boundary.py`, `query/partition.py`, `program/frontend/liveness.py`
  and their tests; design core APIs.

## Found, not fixed
- (none yet)
