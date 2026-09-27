---
cursor:
  subagentId: "bc-a80fa085-ee8b-5c0d-99d2-c81a08a6a795"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-verify-optins (bc-a80fa085) · created: 2026-09-27T07:12Z

# PR #128 merge-ready: `fp8.scale_products` through `F32Mul_v1` (the #106 follow-up, stacked on #106)

[PR #128](https://github.com/danielreuter/verity/pull/128) (draft), branch `cursor/fp8-scale-products-a795` @ `a763a41a`, base `cursor/vllm-rf-recompute-fp8-cbba` @ `df13126f` (#106). One commit, two files.

## What it does
- **`registry/fp8.py::scale_products(x_s, w_s)`** gives the products as u32 words: [N/G, K/G], or [R, N/G, K/G] for R rows. Each is `F32Mul_v1(x_s[kb], w_s[nb][kb])`, computed with `verity.evaluation.evaluate_batch` on `F32Mul_v1`. `F32Mul_v1` has no registered kernel, so this is the plain-integer reference and no `self_check` is needed. No bare numpy multiply is used.
- **The new test** is `tests/program/test_fp8_scale_products.py`, with 4 tests:
  - Every ordered pair of 32 edge words equals `evaluate(F32Mul_v1, a, b)`. The words include two NaNs with different payloads and signs (quiet, signalling, negative), in both orders.
  - The pairs reach every case you listed: NaN × finite / 0 / ±inf, ±0, subnormals, ±max, ±inf, overflow, and underflow to a subnormal and to zero. `F32Mul_v1`'s NaN choice depends on the operand order, so a swapped implementation fails.
  - Rows and shape refusals.
  - `GivenScale` fed `scale_products` equals the old coordinate's word on 24 vectors.
- **The PR body** says:
  - host-computed committed values call `F32Mul_v1`, NaN payloads included;
  - the GPU register (canonical `0x7FFFFFFF` on NaN) is never observable;
  - a kernel store would need the `0x7FFFFFFF` mapping (#96);
  - and it asks the research coordinator to update #106's "Serving" paragraph, which still says numpy float32 multiply.

## Runs
Pod run `r20260927-070757-78c4`, on `a763a41a`, `vyv-rf-verify-optins-l40s`, GPU hidden:

| check | command | result |
|---|---|---|
| tests | `pytest tests/program/test_fp8_scale_products.py tests/program/test_fp8_shared_scale.py` | rc 0, 12 passed |
| lints | `tests/lint`, `test_no_by_name_rules`, `test_imports_resolve`, `test_no_dead_modules` | rc 0 |

- **The check script uses it.** `lanes/vllm-verify-optins/evidence/vo_fp8_values.py` takes its host products from `fp8.scale_products` now. The #74 value run restarted on the VM with it, on the verification merge `d6ea2dc3` (= `b7a4092a` + #128). A bare numpy multiply is counted beside it for information only.
- **No behaviour change.** Nothing calls `scale_products` yet: it is the committer's function for the re-baseline's `<linear>/scale_products` source. No Program, manifest, root, leaf id or verdict moves, and no allowlist grows.
- **No partition checker output needed.** This adds no Definition, query or partition; #106's partition result stands.
