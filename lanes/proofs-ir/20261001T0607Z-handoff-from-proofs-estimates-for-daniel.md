---
id: 20261001T0607Z-handoff-from-proofs-estimates-for-daniel
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on Daniel's question relayed by the top-level at 11:04 PM PDT
---

# Daniel asks: when are the circuits fully Boolean? Your fastest honest time for each item, today

to: proofs-ir (bc-6cd83494). Please answer before anything else, as a short `reply` note in `lanes/proofs/`, then carry on.

Circuits told Daniel 0% of the served Definitions on main are Boolean, and it can't give a time without yours. For each
item, give your fastest honest wall-clock time from now (PT clock time, e.g. "by 3 AM PDT"), what it depends on (Daniel's
ROM ruling, a review, a train, GPU time), and your confidence:

1. Landing the Boolean IR itself on main (`verity.ir.boolean`, `verity.evaluation.bits`, `verity.ml.boolean`,
   circuit-check), as one PR with a passing recorded `check`.
2. Attention (`AttnBlock` / `AttentionHead` / `Attention` v6), with and without the `Rom<n>x<w>[<sha256>]_v1` decision.
3. FP8/FP4 (the E4M3, NVF4 and MXF4 steps and coordinates).
4. The rest of the word library: element-wise FP32/BF16, casts, RoPE, SiLU, norms, sampling, and the MUFU tables.

Also: **what could land tonight** (in a train before 7:50 AM PDT), and in what order. Keep it to about ten lines.
