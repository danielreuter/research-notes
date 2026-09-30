---
id: 20260930T2359Z-handoff-from-circuits-gumbel-611
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Gumbel B>1 has a fix (#611, granted): merge it pre-merge, rerun g211's proof, then an approved Gumbel subset

vllm-staging-bug's #611 (the Gumbel sampler's `splits` at batch > 1) is granted and filed for merge.
1. **Merge #611 into your run branch** (pre-merge is fine; drop it when main has it).
2. **Rerun the proof:** g211 (TinyLlama Gumbel B8 256/32) and one more model's Gumbel B8. Question: *is the Gumbel `splits` tap now
   committed at batch > 1?*
3. **If both pass 460/460:** a Gumbel breadth subset like top-p's (each model at B1, B8, B32, 256/32), under the release pacer's limits
   (the steward's `release.py`: bundle estimate < 150 GB, ≤ 2 B8+). The research owner approved Gumbel B8 as a new path once the fix
   landed. **The rest of the 76 stay held.** If a proof fails, send me the first unbound identity.
