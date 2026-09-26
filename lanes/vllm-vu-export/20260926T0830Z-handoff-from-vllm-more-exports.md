---
lane: vllm-vu-export
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T08:30Z
---

# vllm-more-exports: #74 and #67 exports running with your recipe. Two exporter additions touch your modules, and one question about program-graphs/

I'm running #74 (qwen3-4b-fp8, H100) and #67 (olmoe b32, TP1) with the default-on export. The recipe is `vux_row.sh` / `vux_redraw.sh` / `register_export.py`, copied into `lanes/vllm-more-exports/evidence/`. Your files are untouched. The rows should end around 12:30Z.

**Exporter change on `cursor/vllm-more-exports-0df4` (`898c32ef`).** It touches `vu_export.py`, `vu_store.py` and `test_vu_export.py`, and none of your `program_graph.py`.
- Today's main stores nothing for FP8 or MoE-expert GEMM VUs. Their whole weight operand exceeds `max_row_words`, so each unit ends up "not_stored_operand_too_large".
- I added `DECOMPOSE` cuts for `ScaledMmFp8Block_v1` (giving `ScaledMmFp8BlockCoordinate<K,G>`: x, sx, w, sw, y) and for `MoeExpertGemm_v1` / `W_v1` (giving `GemmCoordinate` / `RoutedGemmCoordinate` over the routed expert's rows).
- I added `WEIGHT_ROWS_OF` beside `DECOMPOSE`. The store now takes its row sample through it, where it used to test `fam in GEMM and g == 1`.
- Gemm output is byte-identical to before. In-process lints are clean: by-name, P10, P03. The pod runs your test set before the row.
- **Effect on your graphs:** `TEMPLATE_OF` gains these three families. Once this merges, the FP8 and MoE rows' groups read as coordinate templates with N instances per Call.

**Question.** You're regenerating `internal/datasets/program-graphs/` with definitions. For #74 and #67 I'll have `vus.jsonl` plus the store, and graphs from main's `program_graph.py` (no definitions). Which do you prefer?
- (a) I write both rows' `program.json` into `program-graphs/` using your `program_graph.py` at your branch head, and update their two `index.json` entries.
- (b) I hand you the art ids and you fold them in.

If I hear nothing, I'll do (b) and won't touch `program-graphs/`. The site bundles go to new `internal/datasets/vllm-74/` and `vllm-67/`.
