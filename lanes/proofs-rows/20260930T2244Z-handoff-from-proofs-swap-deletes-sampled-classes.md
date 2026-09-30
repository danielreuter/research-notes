---
id: 20260930T2244Z-handoff-from-proofs-swap-deletes-sampled-classes
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Add to the one swap (3:44 PM PDT): after a sampled deployment's prove commits, delete its stage row's out/classes too

Node 1 is at 77%, growing 4–5 GB/min, from `MODE=sampled-stage` rows (35–60 GB each in `runs/<run>/out/classes`). The steward
asks that the feeder clean up after each prove (thread `1790808184.589359`).

In the same shell-only swap of `73-sweep-shape.sh`, add this: once a `MODE=sampled` prove record is committed, delete that
deployment's staging row's `out/classes`, then prune its stage-cache entries (by now each has link count 1 and a committed
prove). Keep the run's record files. The steward deletes the rows that already exist, not you. Report the swap time in PT and
the diff path as before.
