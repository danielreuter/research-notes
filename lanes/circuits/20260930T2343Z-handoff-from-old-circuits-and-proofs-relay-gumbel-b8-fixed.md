---
id: 20260930T2343Z-handoff-from-old-circuits-and-proofs-relay-gumbel-b8-fixed
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Relay: Gumbel B8 splits fixed (#611, granted and filed for merge)

- TinyLlama Gumbel B8 (g211) passes 460/460 with #611. Top-p B8 (g218) and Gumbel B1 (g250) keep their exact roots.
- Once #611 lands, Gumbel deployments with B>1 are Commit-ready again; stage them as a breadth subset (B8/B32 per model).
- Not covered: TP2 Gumbel with B>1 still fails coverage, fail-closed, because TP ranks attach taps via attach_rank. Hold those until the follow-up lands.
