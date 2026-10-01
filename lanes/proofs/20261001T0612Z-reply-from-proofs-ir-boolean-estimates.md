---
id: 20261001T0612Z-reply-from-proofs-ir-boolean-estimates
campaign: verity
lane: proofs
kind: reply
status: open
repo: danielreuter/verity
origin: proofs-ir (bc-6cd83494), re note:20261001T0607Z-handoff-from-proofs-estimates-for-daniel
---

I'm not giving clock times. My setup doesn't let me estimate calendar time, and a guess would be worse than none. Here
is each item's remaining work and the gate it waits on.

1. **Boolean IR PR: code done.** `cursor/proofs-ir-95d4` at `ac15d5abf` has the IR, `bits`, `ml.boolean`, BF16 and
   circuit-check. It merges cleanly with main at `72aacf9b2`, and 20 of 21 suites pass locally.
   - The one failure is vLLM's TP2 MoE build, OOM-killed on this 15 GB VM; it needs a pod.
   - What's left: merge main, then a recorded `check --record --on POD` (gpu: 0). That includes `lean-agreement`,
     since it touches `backends/flock/`.
   - Confidence high. Risks: the `lean-agreement` leg, and the reviewer for any changed Lean record (none expected).
2. **Attention v6.**
   - The arithmetic is done: FTZ ops, max, -inf guard and `DotBf16_v3`.
   - With the `Rom` family: add the family to the IR, PROTOCOL §9, vectors, `bits` and the tracer. C-Flock's `_Read`
     lowering already exists. Then MUFU.EX2 / inverse sum, `AttnBlock` / `AttentionHead` / `Attention` v6 in
     `verity_vllm` with word-view tests against v3, and circuit-check. CPU only.
   - Without it: explicit ROM bodies of about 1.1 × 10^7 refs per table, hundreds of MB per descriptor. I don't
     recommend that path.
3. **FP8/FP4:** no new mechanism; the `fp` builders exist. It waits on `proofs-gemm-defs` and `proofs-flock-fp`
   merging, since both edit `unit_fp4.py`.
4. **The rest of the library:**
   - Non-table pieces follow item 2's pattern.
   - Tables need `Rom`; tanh, at 2^27, needs it most.
   - Switching served Programs changes their digests: a separate step after the hillclimb.

**Tonight, in order:**
- (a) Item 1 as one PR, which carries the attention arithmetic.
- (b) If Daniel rules for `Rom` soon, the `Rom` family as a follow-up PR, then attention v6.
