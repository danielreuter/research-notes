---
id: vllm-rf-c4ir/state
lane: vllm-rf-c4ir
kind: state
status: active
created: 2026-09-25T06:55Z
updated: 2026-09-25T07:15Z
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

## Core API (phase 1)
- `verity.ir.intervals` (new): the one sorted-disjoint half-open interval algebra (`norm`, `full`, `total`, `contains`,
  `isect`, `restrict`, `complement`, `ref_intervals`, `strided_intervals`, `IntervalLimit`). Replaces liveness's and
  boundary's private copies; query_ast's `_merge_intervals`/`_range_len`/`_complement_ranges` switch to it next.
- `verity.ir.liveness` (new): `dead_gates(program) -> DeadGateReport`, `Liveness`, `BodyLiveness`. Logic unchanged;
  `LivenessLimit` is gone (`IntervalLimit` instead; the integration never caught it by name).
- `verity.ir.layout.resolve_gate(scope, ref) -> (gate, PrimitiveDefinition)` (new): the integration's `_resolve_prim`
  walk; `resolve` and `param_leaf` now delegate to it (same results, including the scan-carry and root errors).
- `verity.ir.boundary` (new): `in_gates`/`out_gates`/`w_out`/`w_out_bound`/`BoundaryLimit` etc., logic unchanged.
- `verity.ir.partition` (new): `validate_partition`/`validate_width`/`readiness_32bit`/`validate_vu_family`/
  `validate_vu_partition`/`VuVerdict` etc., logic unchanged; `_BOUNDARY` test hook kept.

## Done
- 06:55Z worktree created at `origin/main` `00ffe398`; STATE.md created.
- `e5f36b1f` intervals + liveness; `6b7493c1` boundary + `layout.resolve_gate`; `63a9ffef` partition (+ parts.py
  module map). All pushed. Laptop checks only: ruff F/E9 clean, AST parse; nothing executed yet.

## Running
- nothing.

## Next
- query_ast onto `verity.ir.intervals` (commit).
- Core tests in `packages/verity/tests/ir/` (test-local primitives only), then equivalence tests (importorskip
  `verity_vllm`; integration copy vs core copy on the same programs; deleted in phase 2).
- CPU pod `vyv-rf-c4ir-cpu`: core suite + equivalence tests. Terminate after fetch.
- Phase 2 waits on a4 in origin/main (a4 at 07:12Z: groups commit/acquire/check/properties/collectives still to do).

## Found, not fixed
- `partition._family_tiling`/`_family_count`/`_family_index` swallow every `Exception` (kept: behaviour = spec).
- `vu_query` keeps its own interval helpers in the integration (not in scope).
- `query_artifact.py` is another generic analysis still in the integration (not in scope).
