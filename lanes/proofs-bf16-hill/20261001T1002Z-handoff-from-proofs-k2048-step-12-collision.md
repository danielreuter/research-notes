---
id: 20261001T1002Z-handoff-from-proofs-k2048-step-12-collision
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# K=2048 roll-up: step 12 is used twice; you own the numbering

to: proofs-bf16-hill. From proofs.

- I told proofs-verify-overlap to renumber its 10 session points (`r20261001-092917-8b05`) from 8 to 12, and at the same time
  you put HS_DMA at K=2048 as step 12 (`r20261001-095346-2fe1`). My mistake.
- **Do:** keep your HS_DMA point at 12, and move the 10 session points to your next free step (13, or later if you've used
  it), with your next write to the file. Nothing else about them changes. Re-label them in the same write as the Q3c re-label
  (`note:proofs-bf16-hill/20261001T0948Z-handoff-from-proofs-q3c-granted-drop-c0-once-and-fix-accepted`); they're already
  unflagged.
- proofs-verify-overlap is idle and won't write the file again, so you're its only writer from now on. `proofs.json`'s row
  says "step 12"; change that word to the new step.
- Node 1's GPUs have all been idle since your HS_DMA points ended (09:55:55Z). Put your next points in when ready.
