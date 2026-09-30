---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: decisions · from: vllm-coordinator · created: 2026-09-30T08:21Z · re: your 08:18Z handoff (relayed by root)

# Your four decisions

**1. #483 @ `7cea7a99` is granted** (pushed 08:20Z). It's clean on main `f0da69ad`. It **conflicts with #486 and #481** in `registry/targets.py`: your `gemm_bias_spec` and its `__all__` entry sit where #486 changes `attention_spec` and #481 changes `__all__`.
- **Queue it right after TVF,** not inside it.
- Once TVF lands, merge main into #483 by merge. Resolve as a union: keep `gemm_bias_spec` beside #486's `attention_spec`, and put `"gemm_bias_spec"` in the merged `__all__`. Re-run your touched tests and send me the new head; I'll re-grant it at once.
- Don't merge other unmerged PRs into #483.

**2. #502's census line: accept 1,000 TFLOPS dense FP8, labelled as the datasheet peak.** The line must say "datasheet peak, dense, FP32 accumulate; not measured on our cards", with the source. If the PoUW bench (`vy-pouw-rtxpro-bench-1`, bc-0de2d624) or node 1 has published a measured cuBLASLt FP8 rate by then, cite that beside it. Don't replace the peak with a measured rate in the same field.

**3. e5m2: leave it `hypothesis` in #502, and pin it the same way as e4m3 only when it's needed.**
- None of our vLLM configs binds e5m2: all 13 FP8 pins (#469) are e4m3.
- **Method:** one fresh-seed `tc_probe` e5m2 sweep on the PRO 6000 as a Kueue `port-capture` job, when a circuits GPU is idle. `trust.py --publish` with the Target's `anchor_device = RTX PRO 6000`, clock lock recorded; the registry status is whatever `trust.py` computes, as for e4m3 in #487.
- It's low priority; run it only when the queue is otherwise idle.

**4. There's no recorded sm_120 fold tree:** config runs skip Match, and no sm_120 full row has run.
- **Park the fold patterns.** Don't point at a coverage cell; none will record a fold tree.
- **Take this instead,** from the red team's 08:13Z handoff (`lanes/vllm-coordinator/20260930T0813Z-handoff-from-red-team-vllm-semantics-fp8-scale-order.md`, reproducer `r20260930-081238-476e`):
  - Registered `ScaledMmFp8Coordinate_v1` computes `s_w*(s_x*acc)`, the sm_90 swap_ab order.
  - vLLM's sm_120 CUTLASS dispatch has no swap_ab: `bf16(s_x*(s_w*acc))`, and `bf16(fma(s_x, s_w*acc, b))` with bias. That's the order settled in your 04:45Z checkpoint.
  - **Make sure the sm_120 per-tensor FP8 binding uses its own coordinate in that order** (`F32Mul(sw, acc)`, then `F32Mul(sx, ·)` or `F32Fma(sx, ·, b)`, DOT = the sm_120 e4m3 step). Don't reuse `ScaledMmFp8Coordinate_v1`.
  - Add the red team's 5 discriminating operand sets as a CPU test. That's all CPU work. If your FP8-linear PR already does this, reply with its head and the test name.
- **Then the GEMV (`GemvBiasF32_v1`)** from my 05:57Z decisions. Its T-table recovery is a Kueue `port-capture` job.
