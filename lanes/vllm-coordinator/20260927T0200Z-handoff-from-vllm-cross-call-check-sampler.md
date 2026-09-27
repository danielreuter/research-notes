---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T02:00Z

# PR #101 merge-ready: the Gumbel selects restated with `temp == 0` once (opt-in, new ids); no record moves

[PR #101](https://github.com/danielreuter/verity/pull/101), branch `cursor/sampler-greedy-once-666c` @ `91ceb79e` (base `main` @ `b1aa9bdb`; no conflict with later `main`).

- **New Definitions:** `GumbelTokenSelectSharedGreedy_v1{V}` and `GumbelTopPTokenSelectSharedGreedy_v1{V}`.
  - Their signatures equal the Definitions they restate. They compute `F32Eq(temp, 0)` once and pass it to `TemperatureScaleGivenGreedy_v1` and `GumbelSelectF32GivenGreedy_v1`.
  - `SHARED_GREEDY` maps each old id to its restatement. The names carry no version.
- **Evidence:**
  - Same circuit on every input: the interned gate DAGs coincide at V = 2 and 16, with 2 gates fewer (the second `F32Eq` and its `Const32[0]`).
  - Bit-equal on every 2^16 temperature pattern (every 16th for the top-p select), and on 160 random cases per select at V = 16. Temp 0, −0, ±inf, NaNs and subnormals are covered.
  - Checker: the old selects have 1 redundant gate each, the new ones 0.
- **Opt-in:** nothing binds the new ids, so no record moves now.
  - The re-baseline switches the frontend rule (`vllm_sampling.py`) and the fold pattern (`TokenSelectGumbelTopP`) together.
  - It also adds the new ids to the family tables listed in the PR.
- **Digests at the re-baseline:** stochastic rows only, which among the 13 is #101.
  - Moves: the request Program `ccc21347…` (the descriptor holds each Definition's body) and with it the global digest; the manifest `368283ad…`; the commit roots; the Flock sampler unit (2 gates fewer per Call); the census and bench manifests.
  - The greedy rows use `TokenSelect_v1` and don't move.
- **Tests:** the new test file passes, along with `tests/lint`, `program/test_lint` and `test_sampling_operands`. Two failures exist on `main` without this change: `test_sampling_policy` (needs torch) and `test_sampling_rows::test_nv_logf…` (a NaN sign mismatch).
