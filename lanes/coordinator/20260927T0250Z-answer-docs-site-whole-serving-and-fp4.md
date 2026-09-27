---
id: 20260927T0250Z-answer-docs-site-whole-serving-and-fp4
lane: coordinator
kind: handoff
status: open
---

# Answers for the docs site: whole-serving Programs, and FP4

**To:** docs-site worker (bc-41cff24f). **From:** coordinator. Answers [20260927T0235Z](20260927T0235Z-docs-site-question-whole-serving-programs-and-fp4.md).

## Whole-serving Programs

- **Yes, and I've routed it.** The per-request Programs behind each row already exist for some rows; the cross-Call check read 8 of them for #57. What's missing is a dataset that keeps the vLLM hierarchy instead of folding it away: engine steps, the requests in each step, the model runner with its KV cache and sampler, and the tensor-parallel ranks.
- I've asked the vLLM coordinator to scope that for one row, preferably #101, since it's the headline row, and to name an owner. Building it from stored Builds is CPU work. Rows #4 and #101 need a pod Build first, because their redraw Builds aren't in the store.
- This is the "instrumented program" view from the commitments decisions: derived mechanically from the program and its partition, never authored by hand.
- I'll forward the scope and ETA when they come back. Until then, keep drawing the folded Program.

## FP4

- **Not scheduled.** No vLLM row serves NVFP4. The only FP4 data is the frozen backends' synthetic NVFP4 benchmark instances on an RTX 5090.
- **What a served FP4 row would need:**
  1. Blackwell hardware, an RTX 5090 or B200-class GPU;
  2. captures of its FP4 tensor-core step, plus an exact IR for it in `verity.ml.tc`, in the same way as the A100, RTX 4090 and H100 captures;
  3. a model served with NVFP4 weights;
  4. the vLLM row, with its Program and taps.
- **This is Daniel's call.** It's a new hardware family, so it needs his go-ahead and a budget. Tell him that if he wants it, I'll scope it with an estimate. Meanwhile the site can say FP4 isn't served yet.
