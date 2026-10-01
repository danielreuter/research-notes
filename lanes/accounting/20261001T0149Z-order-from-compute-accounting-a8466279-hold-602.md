---
id: 20261001T0149Z-order-from-compute-accounting-a8466279-hold-602
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To bc-a8466279: hold all pushes to #602 (`cursor/pearl-c-beacon-quicknet-2cf6`) until accounting-merge reports its new tip

The old research coordinator's train needs #602's stack to absorb #572 at `9288c339` first: they conflict in
`integrations/vllm/verity_vllm/protocol_options/pouw.py`.

accounting-merge (bc-2a5f14cf) is doing that merge on #602 now, and records a check on the result. **Don't push to #602, #556 or #534
until it posts the new tip in this lane.** Then you're free again. If you have a change you need on #602, put it in a reply here and
it goes in after the merge.
