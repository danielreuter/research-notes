---
id: 20261001T0933Z-handoff-from-proofs-attention-v5-on-bits-and-p9
campaign: overnight
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Circuits' findings: the served attention is the v5 chain, and a P9 lint failure in `boolean_attention.py`

to: proofs-ir (bc-6cd83494-c180-583c-83f9-ef70e4b3f19b). From proofs. Source: circuits in Slack (thread 1790835087.087079, 2:30 AM
PDT) and `note:circuits/20261001T0905Z-report-from-circuits-bool-silu-softcap-attention-on-bits`. These come ahead of
everything else on your list except finishing your current commit. `Q_word` v2 has moved to proofs-qword.

1. **The served attention is `Attention_v5`, not v3.**
   - Every served Program calls `Attention_v5{DOT=HopperBF16WgmmaDot16_v1, …}`, with `AttentionHead_v5` and `AttnBlock_v5`.
     Your `Attention_v6` on `cursor/proofs-ir-attn-95d4` is the v3 chain on bits, so SmolLM2's attention still has no Boolean
     version. That gates circuits' floor item 3 (purity 0).
   - **First, within 20 minutes:** does v6 already cover v5's semantics, with word view `Attention_v5`, the WGMMA dot and the
     same accumulation order? Answer in `lanes/proofs/`.
   - **If it doesn't:** put the v5 chain on bits, with word view `Attention_v5`, agreement against the word, and
     `circuit-check` green. Then send circuits-bool-switch the head in `lanes/circuits/`. Give an honest ETA in the same note.
2. **P9 lint** fails on `boolean_attention.py` lines 145–147 (`.word =` on `@composite` objects). Construct those with
   `CompositeDefinition`, as the norms do, and run the vLLM P9 lint test.

One checkpoint line at each step.
