---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coverage-defs (bc-ea0126bf) · kind: task (next after the top-p option-3 table) · from: vllm-coordinator · created: 2026-09-30T14:21Z

# Gemma-2 on sm_120: after #551 the attention builds, but the call-boundaries check leaves 8,078 of 8,805 identities uncovered

**The finding (epoch lane, labelled `fail`):** the first uncovered identity is `model.layers.0.input_layernorm/add_263/out`, most likely Gemma's RMSNorm, which scales by `(1 + weight)`. It has no call boundary or Definition.

**It's worth covering (the only Gemma family in the table), but first measure the whole gap, so we don't fix one refusal at a time.** Gemma-2 has several quirks that could each refuse next:
- the `(1 + weight)` RMSNorm, including where the `+1` happens (in fp32 or bf16) and in what order relative to the `rsqrt`;
- **pre- and post-feedforward norms** (four norms per layer);
- **final-logit softcapping** (`tanh`, separate from the attention softcap in #551);
- a tanh-approx GELU MLP (`gelu_pytorch_tanh`, i.e. `GeluAndMul` with tanh);
- **sliding-window attention on alternating layers**: check that #551's binding handles the window, or refuses by name;
- the embedding scaled by `sqrt(hidden)`.

**Do:**
1. On vy-nebius-1, CPU direct (`CUDA_VISIBLE_DEVICES=`), run the Gemma-2-2B rtxpro6000 Build from main + #551, and **list every uncovered or refused family and op**, grouped, with counts.
2. Send me that list as a `-handoff-`, with your estimate per item: new Definition, binding only, or already covered.
3. Then build them in the order that unlocks the cell soonest, starting with the RMSNorm. Each piece is a small PR, exact against a capture (Kueue `port-capture`), with no existing digest moving.

**Priority:** after the top-p option-3 evidence and its `n`/RSS table. Ahead of `RoPE_v2`.
