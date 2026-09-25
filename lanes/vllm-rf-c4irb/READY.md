---
id: vllm-rf-c4ir/ready
lane: vllm-rf-c4ir
kind: ready
status: phase 1 complete and verified; phase 2 prepared on a4 and pre-checked; phase 2 gates blocked (a4 not in main)
created: 2026-09-25T09:02Z
---
# vllm-rf-c4ir READY: boundary, partition and liveness in core `verity.ir`

## Branches

| Branch | Head | Tree | Base | What |
|---|---|---|---|---|
| `lane/vllm-rf-c4ir` | `cfe0ae63` | `5ac05b9c` | `origin/main` `00ffe398` | Phase 1: core analyses + core tests + equivalence tests. Core only; the integration is untouched. |
| `lane/vllm-rf-c4ir-p2-on-a4` | `7313e799` | `95fc9177` | `lane/vllm-rf-a4` `10996616` | Phase 2 prepared ahead of a4: phase 1 cherry-picked onto a4, then `18e29d92` and `4a2ccf11`, then a merge of a4's newer head. |

`lane/vllm-rf-c4ir-p2-on-a4` is not for merging. It holds the two phase 2 commits so they can be replayed once a4 is in
`origin/main` (see "Finishing phase 2"). Rebasing it onto `10996616` instead of merging gives the same tree
(`95fc9177`, checked).

## Phase 1: core API (all under `packages/verity/src/verity/ir/`, stdlib only, no integration types)

- `intervals.py` (new) is the one sorted-disjoint half-open interval algebra: `norm`, `full`, `total`, `contains`,
  `isect`, `restrict`, `complement`, `ref_intervals`, `strided_intervals`, `IntervalLimit`. It replaces the private
  copies in the integration's liveness and boundary modules, and in `query_ast` (`_merge_intervals`, `_range_len`,
  `_complement_ranges`).
- `liveness.py` (new) provides `dead_gates(program, limit=64, transitive=False) -> DeadGateReport`, `Liveness` and
  `BodyLiveness`. The logic is the integration's, unchanged. `LivenessLimit` became `IntervalLimit`, with the same
  message; nothing caught it by name.
- `layout.resolve_gate(scope, ref) -> (gate, PrimitiveDefinition)` (new) is the integration boundary's
  `_resolve_prim` walk. `resolve` and `param_leaf` delegate to it and return the same results and errors.
- `boundary.py` (new) provides `in_gates`, `out_gates`, `w_out`, `w_out_bound`, `gate_prim`, `consumer_index`,
  `BoundaryLimit` and the rest, with the logic unchanged.
- `partition.py` (new) provides `validate_partition`, `validate_width`, `gate_width_readiness`, `readiness_32bit`,
  `validate_vu_family`, `validate_vu_partition`, `VuVerdict` and the rest, with the logic unchanged; the `_BOUNDARY`
  test hook is kept. Phase 2 adds the public `family_tiling` and `CheckedTiling`, previously the private
  `_family_tiling` and `_Tiling`.
- `parts.py` module map lists the two new modules.

Core tests sit next to the existing IR tests and use test-local primitives only (`register=False`):
`test_ir_boundary.py` (the integration's oracle suite, with registry families replaced by local analogues),
`test_ir_liveness.py`, `test_ir_partition.py` and `test_ir_intervals.py`. Phase 1 also had
`test_ir_{boundary,partition}_equivalence.py`, which re-ran every core boundary and partition test with the module
replaced by a differential stand-in (both copies run, results compared), plus the integration's library Programs and
liveness on every specialization. Phase 2 deletes them together with the integration copies.

## Phase 2: integration switched to core (`18e29d92`, `4a2ccf11`)

- **Importers switched to `verity.ir.{liveness,boundary,partition}`:**
  - library: `program/frontend/derive.py`, `program/frontend/torch_frontend.py`, `program/registry/lifted.py`
  - tests: `padded_commit_tiny.py`, `test_frontend_analyses`, `test_lifted_r17`, `test_lifted_tiny`,
    `test_boundary_oracle`, `test_partition_structural`, `test_partition_sweep`, `test_query_artifact`,
    `test_query_counterexamples`
- **Deleted, with no shims:**
  - `query/boundary.py`, `query/partition.py`, `program/frontend/liveness.py`
  - the unused package re-export of `dead_gates` / `DeadGateReport` in `program/frontend/__init__.py`
  - the two equivalence test files
- **Lint maps:** the three `"core"` entries are gone from `LAYER`; the `core` layer itself stays, because P9's order
  test needs its rank. The allowlists only shrink: p07 loses 3 entries, p10 loses 2 and p11 loses 1. No entry was
  added.
- **Kept:** the integration tests of the analyses on registry Programs (`test_boundary_oracle`, `test_partition_*`, the
  counterexamples). They now test core on real Programs, which the core ports replace with local analogues.
- **README:** the `query/` tree line and prose.

**Why `18e29d92` exists.** `registry/lifted.py`'s `n_out_structural_bound` reads the validator's member classes
(`PT._family_tiling`, `PT._Tiling`). Once that module is core, P1 `core-private` forbids those reads, and the allowlist
may not grow. Core therefore names them publicly: `family_tiling`, and `CheckedTiling`, because `query_ast.Tiling`
already names the plan it interprets.

## Evidence

All runs used `research run --on vyv-rf-c4ir-cpu --source <clean worktree> --cwd source` on cpu3m, 8 vCPU. The JUnit
XMLs are beside this note.

| Run | Tree | What | Result |
|---|---|---|---|
| r20260925-074934-4692 | `cfe0ae63` | core suite (no integration) | 664 tests, 0 fail, 3 skip (the equivalence pair + test_trust, modules absent) |
| same | `cfe0ae63` | `packages/verity/tests/ir` with the integration (equivalence live) | 195 passed |
| same | `cfe0ae63` | integration `tests/query` + frontend-analysis + running-example (integration copies) | 317 tests, 0 fail, 9 skip (fixtures absent) |
| r20260925-081543-0c3c | `4a2ccf11` | core suite after phase 2 | 661 passed, 1 skipped |
| r20260925-083804-0840 | `7313e799` | lints: `tests/lint` + `test_no_by_name_rules` + `test_imports_resolve` | 45 passed (41 + 3 + 1), 0 failed |
| r20260925-084225-f233 | `7313e799` | every test touching the switched code (`tests/query`, frontend analyses/rulings, lifted r17/tiny, padded_commit_tiny, b1/serve3 authored, composition, derive_negative, running_example) | 583 tests, 0 fail, 0 error, 15 skip (all test_composition, fixtures absent) |
| r20260925-081543-0c3c | `4a2ccf11` | integration `tests/query` + `tests/program`, `-n 8`, interrupted at 08:58Z before the pod deadline (JUnit flushed) | 1710 tests: 31 fail + 11 error, **all 42 on the known-failure list** of a23b's gate (b) (`gate_b-xdist-rebased-9be6e462`: applicability, artifact_applicability, realhf, ref_prims, ship_roots, ...), 0 new |

The same-pod base run of that last set (base `14b0cf9f`, rebuilt on the pod as the shipped `4a2ccf11` tree plus a
reverse patch) was cut off by the deadline before writing its summary, so there is no same-pod base list.

**Not run: gate (a) T0+T1, gate (b) head vs base, GPU smoke #101.** a4 is not in `origin/main` (`94b1c4d2` at 08:51Z;
a4 head `10996616`), and gate (a) alone takes about 2 h 40 min, past the 09:00Z pod deadline.

**Digest invariant.** Nothing in phase 2 changes Program construction, encoding or manifest code:
- phase 2 changes import paths and makes two private names public;
- the analyses' logic is the integration's, and phase 1's differential tests saw equal results from both copies on the
  library Programs they cover (b1 Gemm, RMSNormTriton, SiluMul, TokenSelect, AttentionHead/Attention v3, Embedding,
  the MoE router and expert, Gumbel, ServeV4 tiny) and on every core test input;
- no string literal of the moved modules differs from core, apart from the interval helper names (the limit messages
  are identical);
- nothing records a module path.

Gate (a) and the #101 smoke still have to confirm this.

## Finishing phase 2 (after a4 is in `origin/main`)

1. In the lane worktree, `git checkout lane/vllm-rf-c4ir && git rebase origin/main`. Phase 1 touches core only; a4
   touches nothing in core.
2. `git cherry-pick 18e29d92 4a2ccf11`. Git's rename detection carries the edits to test files that a4 moved; the
   same cherry-pick onto a4's `10996616` was clean. Then check that
   `rg "verity_vllm\.query\.(boundary|partition)\b|query import (boundary|partition)|frontend\.liveness" integrations`
   finds nothing, since anything that landed in main in between could add an importer.
3. Gates on pods:
   - lints;
   - core;
   - gate (b) at head and at base on the same pod, compared with `baseline-jdiff.py`;
   - gate (a) T0+T1 on cpu3m 512 GB against `gate_a-t0t1-base-72884c8a-samepod.xml.gz`;
   - GPU Build smoke of #101, with program_digest and manifest_digest equal to the record's.
4. Push `lane/vllm-rf-c4ir`.

## Design questions for the owner

1. Core now exposes `partition.family_tiling` and `partition.CheckedTiling` (its attributes `classes`, `instances`,
   `spec`, `problems`) because `registry/lifted.py` reads them. The alternative is to move the n_out structural bound
   into core as a public function and keep the tiling private. `CheckedTiling(...)` raises the private `_Malformed`,
   which callers can only catch as `Exception`.
2. The analyses' broad `except Exception` in `family_tiling`, `_family_count` and `_family_index` moved to core
   unchanged. P7 does not scan core.

## Found, not fixed (behaviour = spec)

- `intervals.strided_intervals`: a zero-outer-stride, unit-inner-stride `Strided` with `0 < count < inner` is reported
  as the whole row. This is sound (it over-reports reads), and no known producer makes such a view.
- `intervals.complement(iv, n)` assumes `iv` lies within `[0, n)`, as `query_ast`'s old helper did. The docstring
  says so.
- The integration's `vu_query` keeps its own interval helpers, and `query_artifact.py` stays in the integration. Both
  are out of scope.

## Spend

Two cpu3m 8 vCPU pods at $0.44/h:
- `zt96bucqlpis7i`, 07:32–07:53Z;
- `hpbzk8p38jgf8s`, 08:08–08:58Z.

That is about $0.52 in total. Both are terminated and unregistered.
