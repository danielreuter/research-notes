---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T09:10Z

**34 cells labelled. On sm_120 (pre-merge `2847317c`) 4 pass 460/460:** SmolLM2-135M (`r20260930-083205-087a`), TinyLlama (`r20260930-083504-55b7`), Llama-3.2-1B (`r20260930-083757-ea80`) and SmolLM2-360M (`r20260930-084530-7528`); slowdown is 1.1–1.8x (from the control arm).
- **1 fail:** Llama top-p (`r20260930-085223-cdf6`). The strict word check refuses `GumbelTopPTokenSelect_v2{V=128256,S=32}: too-large` under Q_word_v1: the top-p select over the 128k vocabulary exceeds the cut.
- **5 unsupported:** Pythia (no Definition for `aten.layer_norm`), the two Qwen2.5 twins (#483) and the two NVFP4 checkpoints.
- **In flight:** 7 cells (Gemma, Phi-3, Qwen3-4B, Mistral, Gumbel, FP8, and the 2 MoE).
