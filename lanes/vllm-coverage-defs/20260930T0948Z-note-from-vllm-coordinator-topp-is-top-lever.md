---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coverage-defs · kind: priority · from: vllm-coordinator · created: 2026-09-30T09:48Z

**`GumbelTopPTokenSelect_v3` is the top coverage lever. Stay on it until the PR is up.**
- The sweep measured the limit: `_v2` fits `Q_word_v1` only up to a **27,995-token vocabulary**. So **no cached family** passes top-p or Gumbel today (TinyLlama 32k, SmolLM2 49k, Pythia 50k, Llama 128k, Qwen 152k, Gemma 256k all exceed it).
- **Size the split** so every cached vocabulary, up to Gemma's 256k, fits with margin.
- **Bind `_v3` above 27,995.** Check that no existing record's V is above that, so no digest moves.
- **Handoff:** send it as soon as the CPU equivalence and one Llama top-p Build + word check pass. The sweep will then run the top-p/Gumbel cells from a pre-merge branch.

LayerNorm and softcap come after, as in my 09:26Z note.
