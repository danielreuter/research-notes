---
lane: vllm-vu-export
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T19:45Z
---
# New task (Daniel-approved 19:33Z): restate the MoE router as one top-k subcircuit. Opt-in, off the record path

Your plan's §4b option (b), as the architecture study recommends (`docs/boolean-core-architecture.md` §4.2/§4.4). Daniel: "whatever
is optimal, as long as it matches the hardware bit for bit and keeps the invariants" (strict partition, committed boundaries, output
ports ≤ X bits, total circuits, verifier evaluates nothing). If you find a tap is strictly better, say why before building it.

- **Restate `MoeRouterTopK_v1` / `MoeRouterTopKNorm_v1` (vLLM `topk_softmax`)** as one top-k subcircuit: round k = the argmax over the
  logits masked by the ids chosen before it, so a round unit reads earlier selections, not score vectors. It's a new Definition under
  a new id, citing core where it's silicon semantics. Tie-breaking, NaN and -inf handling, and the renormalization in the `Norm`
  variant must match the kernel bit for bit.
- **Equality evidence, CPU first:**
  - exhaustive or wide randomized comparison against the current Definition's evaluator, including ties, ±0, NaN and -inf, and E = 64
    / top-8 (OLMoE) and E = 128 (Qwen3-30B);
  - replay against recorded router words from #67 / #70 fixtures on a CPU pod with fixtures (mint the key on your VM, per the rules).
- **Invariants:** `Q_word_v1{16,32}` over the restated body gives units with ports ≤ 32 bits and committed boundaries only, with no
  per-round interior score vectors. Report the new committed-word count for #67 and #70 against the plan's 170.7 M / 71.8 M.
- **Opt-in:** the registry keeps the current router Definition for every recorded Program. The restatement is used only behind a
  flag (for example a Build option), so no digest of record moves.
- **Don't build on** the recompute threshold ("2 gates" against "64 ANDs"): it's undecided. The re-baseline epoch stays on hold.
- **Pods:** your work should need none, or at most a short live `topk_softmax` comparison on an L40S, which you could share with lane
  `vllm-rf-normtap`'s pod if it's up. **Create no pod until the coordinator confirms Daniel approved the GPU estimate.** Your cap for
  this task: $5 (CPU pods included).
- Merge-ready handoff to me as usual.
