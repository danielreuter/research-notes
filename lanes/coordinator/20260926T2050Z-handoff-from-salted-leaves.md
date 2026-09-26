lane: coordinator · kind: handoff · from: salted-leaves · created: 2026-09-26T20:50Z

# salted-leaves ready for review: hm96-sha256/v1 in core, opt-in on the vLLM host committer (PR #88, draft)

- **Tip:** `cursor/hm96-sha256-leaves-18a8` @ f1df809f (base main@2431e3c1), [PR #88](https://github.com/danielreuter/verity/pull/88).
  It is a draft at the Project coordinator's request, so merge when Daniel approves.
- **Tests:**
  - core: 1,078 passed;
  - vLLM integration: every failure is pre-existing on 2431e3c1 (10), order-dependent and passes alone (2), or needs torch (20
    errors);
  - lints P1–P10 and the dead-code census pass;
  - `tools/research` registry tests pass.
- **Behaviour changes:** none by default. `NativeHostCommitter(leaf_scheme="hm96-sha256/v1")` is opt-in. `Opening` and
  `RangeOpening` gain a defaulted `salt`/`salts` field, and a vllm-v1 opening that carries a salt is rejected. `open_levels` moved
  from `native_host` to `native_ranges`, and the P10 cap for `native_host` dropped to 2563. New tool `hiding_leaf_cost` in the
  registry.
- **Negatives:** altered value, salt, commit string or key; a missing or short salt; a salt on a vllm-v1 opening; cross-run
  openings; range openings with a swapped salt.
- **Evidence:** run `r20260926-204634-0958`, `art:b3a08e21`. The report is `lanes/salted-leaves/20260926T2047Z-report-salted-leaves.md`.
