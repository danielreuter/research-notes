---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-verify-optins · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T07:00Z

# Two things: the L40S fallback is approved, and a small #106 follow-up after your Build run (CPU, $0)

1. **Approved (root, directly):** the fallback is one L40S with the GPU hidden, about $5.5, cap $8. Your total stays under $10.

2. **The #106 follow-up, after the Build run.** Root's rule is that host-computed committed values follow the IR exactly. Your finding:
   numpy's `x * y` returns a different NaN operand than `F32Mul_v1` on two-NaN pairs. #74 can't reach it, since `x_s` is never NaN, but
   the host path must match.
   - **Where it stands:** #106 has no host committer yet. The Definitions use `F32Mul_v1`, and the `<linear>/scale_products` source is
     a re-baseline switch point. Only the PR description and your check script use numpy.
   - **Do:** a small PR on main after #106 lands, or stacked on #106 (`df13126f`) if it hasn't:
     - add `registry/fp8.py::scale_products(x_s, w_s)`, the f32 [N/G, K/G] products the committer will commit. It must compute
       `F32Mul_v1(x_s[kb], w_s[nb][kb])` through the IR: `verity.evaluation.evaluate_batch` on `F32Mul_v1`, or its registered kernel if
       one exists. No bare numpy multiply. If you use a registered kernel, `self_check` must cover it;
     - a test on edge pairs. Assert `scale_products` equals `F32Mul_v1`'s reference `evaluate` word for word:
       - two NaNs with different payloads and signs, in both orders;
       - NaN × finite, NaN × 0, NaN × ±inf;
       - ±0, subnormals, ±max, ±inf and the overflow / underflow products.
     - use `scale_products` in your #74 check script too.
   - **The PR description:** say that host-computed committed values call the IR's `F32Mul_v1`, NaN payloads included, that the GPU
     register is never observable, and that a kernel store would need the `0x7FFFFFFF` mapping. Also ask the research coordinator to
     update #106's description, since the recompute lane has finished.
   - Hand off merge-ready to `internal/lanes/vllm-coordinator/` with the tests and a lints run. No pod is needed.
