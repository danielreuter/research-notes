---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T07:45Z

# Merge request: PR #128 @ a763a41a (`fp8.scale_products` through `F32Mul_v1`, the #106 follow-up): APPROVE, right after #106

The lane's handoff is `vllm-coordinator/20260927T0712Z-handoff-from-vllm-verify-optins-scale-products.md`. It implements root's 06:57Z
rule that host-computed values follow the IR exactly.

- **Stacking:** on #106 @ df13126f. One commit adds 17 lines to `registry/fp8.py` plus a test file. It merges cleanly into main 928790af
  (after train A).
- **What it does:** `scale_products(x_s, w_s)` returns `F32Mul_v1(x_s[kb], w_s[nb][kb])` through `verity.evaluation.evaluate_batch`,
  with no numpy multiply. Nothing calls it yet: it is the committer's function for the re-baseline's `<linear>/scale_products`. No
  Program, manifest or verdict moves.
- **Test:** every ordered pair of 32 edge words equals `evaluate(F32Mul_v1, a, b)`, including two NaNs with different payloads and signs
  in both orders, so an implementation that swaps the operands fails. `GivenScale` fed `scale_products` equals the old coordinate.
- **My run** on main + #128 (which brings #106): `test_fp8_scale_products.py` + `test_fp8_shared_scale.py` pass (12), and the lints,
  `test_no_by_name_rules` and `test_imports_resolve` pass.
- **Please also** update #106's "Serving" paragraph. It still says the host uses a numpy float32 multiply; it should say the host calls
  `F32Mul_v1` through `fp8.scale_products` (#128). The recompute lane has finished.
