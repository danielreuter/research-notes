---
id: vllm-rf-c4ir/state
lane: vllm-rf-c4ir
kind: state
status: active
created: 2026-09-25T06:55Z
updated: 2026-09-25T08:06Z
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
  module map); `197789aa` query_ast onto `verity.ir.intervals`. All pushed.
- Core tests (`packages/verity/tests/ir/`, test-local primitives only): `ebea7849` test_ir_boundary (the integration's
  oracle suite: hand-built programs verbatim, registry families replaced by local analogues), `9ff3ef64`
  test_ir_liveness (dead gates vs flat scan, reads vs operands), `6b02abe7` test_ir_partition (stubs + structural +
  sweep, plus real-boundary and query_ast checks), `23904dd6` test_ir_intervals.
- `297d2d84` equivalence: test_ir_{boundary,partition}_equivalence re-run every core boundary/partition test with the
  module under test replaced by a differential stand-in (both copies run, results asserted equal), plus the
  integration's library Programs (Gemm ... ServeV4 tiny) and liveness on every specialization. importorskip
  `verity_vllm`; deleted in phase 2.
- 07:32Z pod `vyv-rf-c4ir-cpu` = RunPod zt96bucqlpis7i, cpu3m 8 vCPU / 64 GB, 80 GB, $0.44/h (cpu3g x16 unavailable);
  registered by `research pods create --register --guard 90` (registry file `notes/machines.d/vyv-rf-c4ir-cpu.toml`,
  the registry's one-file-per-machine form of the machines.toml entry).
- Pod run r20260925-073513-4b10: bootstrap ok. Run 1 at 297d2d84: 3 core test mistakes (two interval tests, one
  partition assert with the stub still installed) + equivalence collection error (dataclass module not in
  `sys.modules`); fixed in `b890473b`. Run r20260925-074537-7e2b at b890473b: core 661 passed / 3 skipped; `tests/ir`
  with `integrations/vllm` on PYTHONPATH (equivalence live) 193 passed.
- `cfe0ae63` equivalence tidy (stub counter restore, re-exports). Lane head = `cfe0ae63`, pushed.

- Run r20260925-074934-4692 at `cfe0ae63` (JUnit): core 664 tests / 0 fail / 3 skip (the two equivalence files and
  test_trust skip without `verity_vllm`/`research`); `tests/ir` with the integration 195 passed; integration
  `tests/query` + `test_frontend_analyses` + `test_running_example` 317 tests / 0 fail / 9 skip (compiled_manifest:
  row-of-record output code not present). Phase 1 complete. Pod terminated 07:53Z and unregistered.
- Phase 2 prepared ahead of a4 (a4 not in origin/main yet): local branch = phase 1 cherry-picked onto a4 head
  `14b0cf9f`, plus `18e29d92` (core partition names `family_tiling` / `CheckedTiling` publicly: `registry/lifted.py`'s
  structural n_out bound reads them, and P1 `core-private` forbids `_family_tiling` / `_Tiling` off core with no
  allowlist growth) and `4a2ccf11` (importers -> `verity.ir.{liveness,boundary,partition}`; the three integration
  modules, the package re-export of `dead_gates`, the three `LAYER` "core" entries, 6 stale allowlist entries
  (p07 x3, p10 x2, p11 x1) and the two equivalence test files deleted; README query prose). Pushed as
  `lane/vllm-rf-c4ir-p2-on-a4` (NOT the lane branch; the lane branch stays on origin/main until a4 lands).
  Integration tests of the analyses on registry Programs (test_boundary_oracle, test_partition_*, counterexamples) kept,
  switched to core. Static checks: no new pyflakes findings; no string literal of the moved modules differs from core
  except the interval helper names (limit messages identical); nothing records a module path.

## Running
- (08:06Z) pre-check pod for `4a2ccf11`: lints (41 + by-name + imports), core suite, integration `tests/query` +
  `tests/program`.

## Next
- Phase 2 proper when a4 is in origin/main: rebase lane onto origin/main (cherry-pick `18e29d92`, `4a2ccf11`), then
  lints, core, gate (b) head vs base same pod, gate (a) T0+T1 on cpu3m 512 GB, GPU smoke #101.
- 08:05Z: origin/main = `b9cd5368`; a4 head `14b0cf9f` not merged. Gate (a) alone is ~2 h 40 min, so phase 2 gates
  need the pod deadline (09:00Z) extended.

## Found, not fixed
- `intervals.strided_intervals` (the integration's liveness `_strided_targets`, moved unchanged): a zero-outer-stride,
  unit-inner-stride `Strided` with `0 < count < inner` (one partial run of a broadcast row) is reported as the whole row
  (`inner` leaves). Sound (over-reports reads) and no known producer makes such a view; kept for behaviour = spec, the
  core test asserts superset there and exactness everywhere else.
- `intervals.complement(iv, n)` assumes `iv` within `[0, n)` (so did query_ast's old `_complement_ranges`); docstring now says so.
- `partition._family_tiling`/`_family_count`/`_family_index` swallow every `Exception` (kept: behaviour = spec).
- `vu_query` keeps its own interval helpers in the integration (not in scope).
- `query_artifact.py` is another generic analysis still in the integration (not in scope).
