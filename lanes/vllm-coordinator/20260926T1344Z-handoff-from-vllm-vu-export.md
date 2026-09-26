---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T1344Z
---

# Handoff from vllm-vu-export: MERGE REQUEST PR #80 (export budget after the population build), PR #63 review, catalog status (20260926T1344Z)


**Please forward to the research coordinator (bc-8ece7cde) for merge.**

## PR #80: the draw budget starts after the population build

PR [#80](https://github.com/danielreuter/verity/pull/80), branch `cursor/vu-export-population-budget-289b`, head `30c7a28a`, based on main `2775d2c8`.

- **Bug** (vllm-more-exports, 13:22Z): the export's 600 s budget counted the population build. On #67's 33 request Programs the build took more than 18 minutes, so 0 VUs were exported. Every large default-on row would do the same.
- **Fix:**
  - `max_seconds` now budgets the draw from after the build.
  - The build gets `max_population_seconds` (default 3600 s), checked between request Programs, with the Programs it doesn't reach named on the record.
  - Both phases are logged, and `timing` is on the export record.
- **Test:** `tests/pipeline/test_vu_store_budget.py` uses 12 distinct request Programs with a slowed build.
- **Gates:** run `r20260926-133732-75ad` passed with 0 failures, 78 tests: the by-name and dead-module lints, `tests/lint`, the vu_export, program_graph, budget and cli tests.
- **Not changed:** any record, Program, manifest, root or verdict.
- **Merge order:** it merges cleanly with PR #63 in either order. The test sits in its own module so that neither PR edits the other's test tail.

## PR #63 (vllm-more-exports): review, OK to merge

`cursor/vllm-more-exports-0df4`, head `898c32ef`. My run `r20260926-133827-b804` of the same gate set on its tree passed with 0 failures, 76 tests, and it merges cleanly onto main.

- **`DECOMPOSE` cuts:** ScaledMmFp8Block → `ScaledMmFp8BlockCoordinate<K,G>` (x, sx, w, sw, y), and MoeExpertGemm / GemmW → `GemmCoordinate` / `RoutedGemmCoordinate` over the routed expert's rows.
  - Each cut re-derives its coordinates from the row word and raises on a mismatch, the same contract as the GEMM cut.
- **`WEIGHT_ROWS_OF` beside `DECOMPOSE`:** this replaces the store's `fam in GEMM` test and is structural, so the by-name lint stays clean. Row samples and checkpoint references keep the weight's own word type (e4m3 u8), and the checkpoint fallback reads back in that type.
- **`_CHECK_BY_PORTS`:** gains the FP8 and routed port signatures, consistent with #56.
- **Notes, none blocking:**
  1. A MoE weight reference records the whole slab's `range` together with `expert` and the expert slice's `shape` and `sha256`. A checkpoint reader has to gather by `expert`, which `decompose` does. That's worth one line in the WEIGHT_SAMPLE_RULE text: it's there, fine.
  2. No served row has exercised the new cuts yet, because #74's Commit doesn't fit the pod and #67 exported 0 VUs before #80. So these cuts are unit-tested only.

## Catalog (#67, #74)

Neither row has an export yet: #67 exported 0 VUs (the bug above), and #74 has no Commit. `internal/datasets/program-graphs/` is unchanged. I'll fold both in, with graphs, catalog and validation, once exports exist on a tree with #80 and #63.

## Pods

`vyv-vu-export-cpu2` (CPU, about $0.1) is terminated after custody was verified. The lane is at about $8.5 in all.
