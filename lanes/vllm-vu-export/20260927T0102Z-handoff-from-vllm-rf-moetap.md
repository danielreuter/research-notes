---
lane: vllm-vu-export
kind: handoff
from: vllm-rf-moetap (agent bc-2c25902d)
created: 2026-09-27T01:02Z
---
# fine-query-plan §4b / §5: the committed router words are topkGating's (fmaxf max, 0x7FFFFFFF NaN); PR #96 changed MoeRouterProbs to match

At the vLLM coordinator's request (handoff 20260927T0015Z to vllm-rf-moetap): please update `docs/fine-query-plan.md` §4b (and §5 where it
describes the router's committed values) to say the ordered router's committed words are `topkGating`'s own.

- PR #86's `MoeRouterProbs` took the row max with `F32Max_v1` (FA2's fast-math `x > y ? x : y` with ftz) and let NaN results keep the
  registry's x86 encodings (`F32Add/F32Mul/F32Div`: 0x7FC00000, 0xFFC00000 for invalid). vLLM's `topkGating` is built without fast math:
  its max is `fmaxf` (a NaN operand yields the other, subnormals kept, max(+0,-0) = +0, two NaNs 0x7FFFFFFF), and FP32 arithmetic on the GPU
  returns 0x7FFFFFFF for every NaN.
- Outputs (ids, weights) never differed -- probabilities are clamped -- but the committed max, exponentials and reciprocal did, on rows with a
  NaN at the head of a thread's columns, all-NaN / +-inf rows, and subnormal rows.
- PR #96 (`cursor/vllm-rf-moetap-82dc`) states `MoeRouterProbs` with `F32Fmaxf_v1` and maps a NaN exponential or reciprocal to 0x7FFFFFFF.
  `MoeRouterTopK_v1` (the record) is untouched; the word counts stay 130 (E = 64) and 267 (E = 128, Norm) with 0 recomputes.
- Suggested wording for §4b's "Under the no-recompute rule" bullet: "the softmax is committed once, 2E + 2 values per token, word for word
  `topkGating`'s: the `fmaxf` row max, the E `expf` exponentials, the IEEE reciprocal of their sum and the E clamped probabilities, a NaN word
  being the GPU's 0x7FFFFFFF (router-tap exactness, PR #96)."
- The GPU record (router-tap exactness, run on vyv-rf-moetap-g2) will be named in my merge-ready handoff to vllm-coordinator.
