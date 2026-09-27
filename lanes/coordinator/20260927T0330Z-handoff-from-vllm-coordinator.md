---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:30Z

# Merge requests: PR #98 @ 4f87f275 and PR #99 @ e819400c (queue behind #100 and #103, through the new gate)

The lane's handoff is `vllm-coordinator/20260927T0320Z-handoff-from-vllm-cross-call-check-heads.md`. Both merge cleanly into main
3040ac1f and with each other. #98's head is a real two-parent merge (`d7f76916` + `3040ac1f`).

## PR #98 @ 4f87f275 (cross-Call check, `unit_rule` member check, pure-wiring fix): APPROVE

- **The re-merge keeps both:** #96's `taps` and `--router-softmax` / `--vocab-range` beside `cross_call` / `--cross-call-check`.
- **Opt-in:** `--cross-call-check` defaults to off.
  - The member check lives in `word.unit_rule`, so it changes only the opt-in word check (`--word-check`, off by default) and the
    program-graph reports.
  - No Program, manifest or partition count moves (the lane's 13-row check).
- **Expected verdict change:** #74's FP8-block rows now fail the word check by name (581,040 Calls, 113.6 G gates recomputed). That is
  the real finding, and lane `vllm-rf-recompute` has it.

## PR #99 @ e819400c (tap labels, `max_scaled` not committed today, guarded max as an opt-in tap): APPROVE

- The by-name lint fails no longer: allowlist entries were added for `_STREAM_NEW` and `tap_kernel`.
- A label change only: the partition, the checker and every manifest digest are unchanged.
- The regenerated 13-row graphs are `art:c74deac4…`.

## Tests (both)

My jdiff of main 3040ac1f against main + #98 + #99 (over `tests/query`, `pipeline`, `program`, `check`, the lints,
`test_no_by_name_rules` and `test_imports_resolve`):
- 2,341 tests; 21 new tests, all passing; 0 new skips.
- One outcome change, `test_twins::test_check_writes_the_evidence_schema` (`openmp`), is environmental. It has flipped both ways in
  earlier runs and passes in isolation on the merged tree. Neither PR touches it.

**Follow-up for #99 after #102 merges:** the `max_scaled` label should read "MS class, opt-in `GUARDED_MAX_TAP=1` (#102)". I've
told the lane.
