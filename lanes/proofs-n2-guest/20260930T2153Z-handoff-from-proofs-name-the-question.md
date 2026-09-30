---
id: 20260930T2153Z-handoff-from-proofs-name-the-question
campaign: verity
lane: proofs-n2-guest
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Daniel's rule, 2:53 PM PDT: every job names its research question; nothing added without the owner's yes

- Every fill-job script and run you queue carries its research question, in a header comment and in its run meta or
  labels. For your chunks: `question: "what is the whole-row proving cost against K, per shape class, on sm_120? (3
  chunks per new class)"`.
- The research owner's yes covers only what tonight's review keeps: 3 chunks per new shape class. Don't queue anything
  else, not even to fill idle GPUs. Idle beats padded. If you think something else is worth running, write it in your
  notes lane and I'll take it to the owner.
