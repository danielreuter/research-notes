---
id: 20261001T0001Z-handoff-from-circuits-gumbel-proof-already-passed
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: g211 already passes 460/460 with #611 (staging-bug's proof): skip that rerun; one other model's Gumbel B8, then the subset

Amends `note:20260930T2359Z-handoff-from-circuits-gumbel-611`. staging-bug reports g211 (TinyLlama Gumbel B8) at 460/460 with #611, and g218
/ g250's run roots unchanged. With #611 merged into your run branch, run **one other model's Gumbel B8** (e.g. Llama-3.2-1B) as the
second proof, then the Gumbel breadth subset (each model at B1/B8/B32, 256/32) under the pacer's limits. The rest of the 76 stay held.
