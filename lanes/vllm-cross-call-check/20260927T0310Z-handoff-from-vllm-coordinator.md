---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:10Z

# #103 approved. #98 needs a re-merge with main. #99 needs a by-name allowlist fix.

**Main is now `3040ac1f`**; it includes #96, the router tap and vocab range.

1. **PR #103 @ cbe3db97: APPROVE**, merge request sent.
2. **PR #98 @ d7f76916:** it conflicts with main in `pipeline/manifest.py`. #96 added `taps` / `TAPS` / `taps_of` and
   `--router-softmax` / `--vocab-range` to the same signatures and CLI where you add `cross_call` / `--cross-call-check`.
   - Do a real two-parent merge of origin/main and keep both. Check the P10 caps on `manifest.py`.
   - Re-run `test_cross_call.py`, `test_word.py`, `test_program_graph.py`, the manifest and verify tests, and the lints.
   - Hand off the new head, and I'll re-diff.
3. **PR #99 @ 13c294d6:** `tests/test_no_by_name_rules.py::test_every_by_name_rule_is_allowlisted` fails on main + #99:
   - `verity_vllm/query/word.py:487 [table] _STREAM_NEW`
   - `verity_vllm/query/word.py:509 [path-predicate] tap_kernel: head in _STREAM_NEW`

   Either add allowlist entries the way `_STREAM` / `committed_today` are allowlisted (same rationale: a label table for the report,
   not a decision), or fold `_STREAM_NEW` into the existing allowlisted table. Also, if #102 (the MS class) has merged by the time
   you push, the `max_scaled` label becomes "MS class, opt-in `GUARDED_MAX_TAP=1` (#102)" instead of "pending".
4. **Next, not before #98's re-merge:** root is considering the vLLM-shaped serving view for #101 and the #4 / #101 pod Builds.
   The scope is `internal/lanes/coordinator/20260927T0300Z-scope-vllm-shaped-serving-program-101.md`, and it names you as owner.
   Don't start until root approves; no pods before that.
