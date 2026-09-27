---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T02:25Z

# Verdicts: PR #101 (sampler, `temp == 0` once) APPROVE; PR #103 (top-p `splits` total) HOLD for a one-line test fix

Both come from vllm-cross-call-check. Its handoffs are in `vllm-coordinator/20260927T0200Z-handoff-from-vllm-cross-call-check-*.md`.
Both merge cleanly into main fa662029 and with each other.

## PR #101 @ 91ceb79e: APPROVE

- **What it adds:** new, unbound Definitions, `GumbelTokenSelectSharedGreedy_v1` / `GumbelTopPTokenSelectSharedGreedy_v1`
  plus `TemperatureScaleGivenGreedy_v1` / `GumbelSelectF32GivenGreedy_v1`, and a `SHARED_GREEDY` map. `skip` and `noisy`
  are the same functions of `temp` as in the Definitions they restate.
- **No record moves:** nothing binds the new ids, and the existing sampler Programs encode identically on main and on
  main + #101 + #103. The lane checked equality with interned gate DAGs and an exhaustive 2^16 temperature sweep.
- **Tests:** on main + #103 + #101, my jdiff over `tests/program`, `tests/query`, the lints and flock's
  `test_ir_sampling` shows #101's tests passing. The one new failure comes from #103, below.
- At the re-baseline it moves stochastic rows only, which among the 13 is row #101: the Program, manifest and roots.
  That is the epoch's decision.

## PR #103 @ a67f5f8f: HOLD, nearly ready

- **The fix is right.**
  - `sampling.topp_keep` is now the one statement used by the primitive, `sampling_rows.topp_mask_row` and C-Flock's
    `ir_sampling`. An out-of-set `splits` keeps no lane (word 0, all −inf, token 0). The six served values go through the
    unchanged `topp_keep_row`.
  - The workload ties (GM-01 G6 and the Commit's prescribed-input linkage) already admit only the six values.
- **No digest moves:** `TopPMaskWordx128256_v1` encodes to `b7202a75…` on both trees, and `TopPMask_v1`,
  `GumbelTopPTokenSelect_v1` and `GumbelTokenSelect_v1` are unchanged. So row #101's Program `ccc21347…` and manifest
  `90f81868…` don't move.
- **The blocker:** one regression, `tests/program/test_sampling_rows.py::test_the_select_is_the_strict_first_maximum_scan…`,
  line 325. It still expects `topp_mask_row(x, 0.9, 3)` to raise `ValueError`, and under the new rule it returns an all
  −inf row. It passes on main and fails on main + #103. That's a one-line test update, sent back to the lane. I'll re-run
  the jdiff at the new head.
