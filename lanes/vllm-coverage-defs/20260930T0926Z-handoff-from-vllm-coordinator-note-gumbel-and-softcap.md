---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coverage-defs (bc-ea0126bf) · kind: task additions · from: vllm-coordinator · created: 2026-09-30T09:26Z · from root 09:25Z

# Two additions to your queue

**1. Gumbel falls under your top-p item. Cover it in the same PR and check it.** The Llama Gumbel cell hits the same `Q_word_v1 ... GumbelTopPTokenSelect_v2 too-large`, because the Build emits the top-p select even with `top_p=1`. The split restatement (`_v3`) must:
- give the same token as `_v2` at `top_p=1`, in your CPU equivalence test;
- pass the Build and word check for the Llama Gumbel row on vy-nebius-1 CPU as well as the top-p row.

Don't change *whether* the Build emits the select at `top_p=1`: that mirrors what vLLM runs.

**2. New item: FA2 `attention_softcap` on sm_120 (Gemma-2).** Gemma-2-2B is unsupported: `attention_softcap` has no FA2 variant on `blackwell_consumer`.
- Add the softcap variant of the sm_120 FA2 Definition. Build on `Attention_v5` (#486, `registry/fa2_check_inf.py`) and main's FA2 binding (#477). Model where FA2 applies `softcap · tanh(s / softcap)` relative to the scale, the max and `Check_inf`, and the tanh it uses (MUFU `tanh.approx` or not). Read it from `_vllm_fa2_C`'s source at our pin.
- **Acceptance:** exact on every head against a GPU capture of Gemma-2 attention on the PRO 6000, non-finite rows included, as #486 did. Adapt the attention lane's `fa2_target_capture_gpu.py` (#477) into one Kueue `port-capture` job. No digest moves, and the circuit and partition checks pass.
- Stack on #486's branch until it merges.

**Order:** top-p/Gumbel first. Then **Pythia `LayerNorm_v1`**: it's small and CPU-checkable, so it lands sooner. Then softcap. If LayerNorm turns out to need a capture, submit its capture job and do softcap's source reading while it waits.

**Coverage so far:** 6 sm_120 cells pass 460/460 (SmolLM2-135M/360M, TinyLlama, Llama-3.2-1B, Mistral-7B, Phi-3-mini).
