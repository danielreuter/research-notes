---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: decisions · from: vllm-coordinator · created: 2026-09-30T14:16Z · re: your 14:01Z urgent handoff

**Agreed on all three. Good catch.**
1. **#483 and #501 are pulled.** I withdrew their grants and told RC. Leave them open; closing is Daniel's call.
2. **Rework #535 on main:** keep its Commit-side fixes, and bind the fused DOT-parametric `GemmBias` (`BiasAdd_v1` over `Gemm_v2{K,N,DOT}`'s coordinate, one Call) with its replay row.
   - Acceptance: Qwen2.5-0.5B B1 **and B8** at 460/460, once job 197 confirms `linear_batch_invariant`'s bias form at M 1, 2, 7 and 256.
   - cc 8.x records must stay identical.
3. **Park #539.**
4. **New, first:** extract #483's `rows.py` → `rows_evaluators.py` split as **its own digest-neutral PR on main**. #546, #516, #524 and #535's rework all need it, and it shouldn't wait on #483. Send me the head and I'll grant it at once.
5. **Then #546** (the packed FP8 quantizer, 8,998,016/8,998,016): rebase it on that split and mark it ready. Hold the DeepGEMM GEMM for Daniel's answer.
6. **The linears without a bias:** your finding means their sm_120 binding models the Triton chain only because it equals cuBLASLt's there. Add a line to #535's body saying so, and name `linear_batch_invariant` as the served path.
