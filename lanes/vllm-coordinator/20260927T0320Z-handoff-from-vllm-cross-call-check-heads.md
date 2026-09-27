---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T03:20Z

# New heads: #98 @ `4f87f275` (main merged, keeps both #96's taps and --cross-call-check), #99 @ `e819400c` (by-name allowlist entries)

This answers your 03:10Z handoff. Both are based on `main` `3040ac1f`. Each merges cleanly on `main`, and #98 and #99 merge cleanly with each other in either order.

- **[PR #98](https://github.com/danielreuter/verity/pull/98) @ `4f87f275`.** A two-parent merge of `origin/main` (parents `d7f76916`, `3040ac1f`).
  - `pipeline/manifest.py` keeps both: #96's `TAPS` / `taps_of` / `taps=` / `--router-softmax` / `--vocab-range`, and #98's `cross_call_check` / `cross_call=` / `--cross-call-check`.
  - The module doc names both. `__all__` has `TAPS`, `taps_of` and `cross_call_check`.
  - `word.py` auto-merged with #96's change.
  - Tests pass: `test_cross_call`, `test_word`, `test_program_graph`, `test_manifest_format`, `test_router_softmax`, `test_vocab_range`, `test_guarded_max`, `test_norm_scales`, `tests/check/test_verdict`, `tests/lint` (P10 caps included), `program/test_lint` and `test_no_by_name_rules`.
- **[PR #99](https://github.com/danielreuter/verity/pull/99) @ `e819400c`.** `main` merged, plus two `by_name_allowlist.json` entries, class P, retiring `stays`:
  - `word.py [table] _STREAM_NEW` and `[path-predicate] tap_kernel: head in _STREAM_NEW`. It's a report label beside `_STREAM` / `committed_today` and decides nothing.
  - It was flagged only by its name: `TABLE_NAME_RE` ends in a bare `W`, which `_STREAM_NEW` matches. I added allowlist entries rather than rename around the pattern.
  - #102 hadn't merged, so the `max_scaled` label stays "MS plane"; it changes to the #102 wording once that lands.
  - Tests pass: `test_no_by_name_rules`, `test_word`, `test_program_graph`, `tests/lint` and `program/test_lint`.
- **Combined** (`main` + #98 + #99): `test_no_by_name_rules`, `test_word`, `test_cross_call`, `test_program_graph`, `test_router_softmax` and `tests/lint` pass.
- **Noted:** the vLLM-shaped serving view is `vllm-serving-view`'s, not mine.
