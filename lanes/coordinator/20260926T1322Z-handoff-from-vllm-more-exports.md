---
lane: coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T13:22Z
---

# MERGE REQUEST: PR #63, the VU exporter's FP8 block GEMM and MoE expert GEMM coordinates (exporter only, record-neutral)

- **Merge:** PR [#63](https://github.com/danielreuter/verity/pull/63), branch `cursor/vllm-more-exports-0df4`, head `898c32ef`. It's one commit on main `e3a2d81d` and merges cleanly with main `e77d40c9`. It touches `vu_export.py` and `vu_store.py` (+145/−12, with +69 of tests).
- **Why:** main's exporter stores nothing for `ScaledMmFp8Block_v1` (the FP8 rows) or `MoeExpertGemm_v1` / `W_v1` (the MoE rows). Their whole weight operand exceeds `max_row_words`, so every such unit is dropped as "not_stored_operand_too_large".
- **Change:**
  - Three `DECOMPOSE` cuts: `ScaledMmFp8BlockCoordinate<K,G>` (x, sx, w, sw, y), plus `GemmCoordinate` and `RoutedGemmCoordinate` over the routed expert's rows. Each is re-evaluated before it's written.
  - `WEIGHT_ROWS_OF` beside `DECOMPOSE`; the store's row sample goes through it. Gemm output is byte-identical to before.
  - The `extract(weights=)` checkpoint fallback reads the weight's own word type (it had hard-coded u16).
- **Tests on pod** (vyv-more-exports-h100, tree `898c32ef`), 0 failures:
  - `r20260926-082552-2706`: vllm-vu-export's test set (`test_vu_export`, `test_program_graph`, `tests/lint`, sampled replay, `test_cli`, `test_row*`), 148 passed, 1 skipped.
  - `r20260926-083238-6f6f`: `test_no_by_name_rules`, `test_no_dead_modules`, `test_vu_export`, 22 passed.
- **Not changed:** any record, Program, manifest, root, verdict or allowlist.
- **Caveat:** no served row has exported with it yet. #74's Commit doesn't fit a 251 GB H100. #67's export hit a time-budget flaw in `vu_store`, which is main's behaviour and not this PR's (handoff to vllm-vu-export, 1322Z). vllm-vu-export OK'd the additions (its handoff to me, 0830Z).
