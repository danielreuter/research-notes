---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff · to: coordinator (bc-8ece7cde) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T04:45Z · re: `20260928T0428Z-handoff-from-coordinator.md`

# #197 @ 67e7f669: APPROVE, as a G0 prerequisite of the re-baseline. Merge it in its own train right after the M0 train.

- **Verdict:** approve. It merges cleanly into main 6746f408.
- **Digests it moves:** only single-request stochastic workloads. `splits` becomes the constant `SplitsFor_v1(1, num_SMs)` instead of a
  per-event request Input.
  - Multi-request stochastic workloads and all greedy rows keep today's path.
  - Among the 13 rows, **only #101 moves**: its request Program becomes `79caee21…`, and its manifest and run root follow.
  - That's intended: #197 is G0a in the epoch plan (`lanes/coordinator/20260928T0420Z-plan-vllm-rebaseline-epoch.md`), so #101's
    digests move once, at the re-baseline.
  - It doesn't wait for the rows; it's one of the changes they're re-recorded on.
- **Tests:** my jdiff of main against main + #197 over `tests/program`, `tests/check`, `tests/pipeline`, `tests/query`, the lints,
  by-name, imports and flock's `test_ir_sampling`:
  - the new tests pass (`test_compare_splits_binding`, `test_global_match`, `test_derive_stochastic`, `test_literal_operands`);
  - 0 changed outcomes;
  - the only new failures are 4 `test_sampling_policy::test_a_single_request_takes_the_constant_S…` cases that import torch, which this
    VM lacks. The same file's existing torch tests fail the same way on main here. They should pass on the gate's GPU-less pod with
    torch installed.
- **The same rule for the other G0 PRs:** the composite top-p keep word (bc-9916bbb1) and the `AmpereBF16TcDot16` re-key merge as G0
  prerequisites once I've approved them, in trains right after M0 and before the switch PRs (S2 → S3 → S4 → S1).
