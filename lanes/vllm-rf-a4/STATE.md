---
id: vllm-rf-a4/state
lane: vllm-rf-a4
kind: state
updated: 2026-09-25T07:12Z
---
# a4 (re-home into the §5.1 tree): state

> **Coordinator, 06:35Z: owner-approved naming. The evaluator implementations are "kernels": use `program/kernels/`, not `program/backends/`,** wherever SYNTHESIS 5.1/5.2 say `program/backends/`. That is where `numerics/` goes, with its `tables/` package data and `cpp/` sources, and where twins and derived rows go if a whole module moves. Put it in your move map now, and use "kernels" in `INTERIM_LAYER` / layer names. Details: `20260925T0635Z-handoff-from-vllm-coordinator.md`.
> **a4, 07:12Z: done** in `22f5bc58` (a follow-up commit renaming the PROGRAM commit's `program/backends/`). There is no backends layer in the P9 order (backends sat inside `program`), so `program/kernels/` stays in the `program` layer.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-a4`, branch
`lane/vllm-rf-a4`. **f1 merged; rebased onto origin/main `00ffe398` at 06:55Z** (force-with-lease).

## Done
- Tools in `tools/`: movemap.py (the map, per group), rewrite.py (git mv + AST import / dotted / path rewrite, line
  counts preserved), splitfix.py, allow.py (allowlist remap + P9 cycle/P11/P12 recompute), resolve.py, graph.py, simulate.py.
- Commits (each pushed): pipeline `2b8836c7`, engine `f2f1bf0a`, program `c397545b`, query `dd83b50b`, observe
  `ad847624`, kernels rename `22f5bc58`.
- Pod `vyv-rf-a4-cpu` (4q60rifwx2r1bp, registered, guard 90): bootstrap ok; base lints at 8efb918e green; base gate (b)
  at 8efb918e done (exit 1, expected failures).

## Running
- `vyv-rf-a4-cpu`: base lints + gate (b) at origin/main `00ffe398` (/workspace/basemain, started 07:03Z).

## Next
1. Groups commit, acquire, check, properties, collectives; then the final lint-map cleanup (INTERIM_LAYER -> package
   map), then the test-file moves.
2. Head lints + gate (b) on vyv-rf-a4-cpu vs basemain; gate (a) T0+T1 on a cpu3m pod; GPU smoke #101 on 1x L40S.

## Open questions
- none

## Found, not fixed
- `engine/engine_profile.py:130` `TP_WORKER_EXTENSION` names `verity_vllm.tp.poc_tp_worker`, which does not exist.
- `pipeline/commit.py` imports `workload_target` (absent; inside try/except).
