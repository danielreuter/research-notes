---
id: 20260930T2237Z-handoff-from-circuits-g217-compare-rule
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); for n2-commits (bc-698052e1)
---

# circuits → n2-commits: for cov-g217, compare the run root and committed leaves; the node-1 record replayed in-process

`cov-g217`'s node-1 reference (`r20260930-175445-077e`, 10:54 AM PDT) replayed **in-process**. Your node-2 run uses `REPLAY_DEFERRED=1`,
which PR A keys into the Commit's record, so the record won't be byte-identical even if the computation is. The gate is:
**run root equal, committed leaves / manifest digests equal, replay 460/460**; the record may differ only in the `replay_deferred`
key and verdict fields. (The TP2 lane's SmolLM2 acceptance kept the same run root in-process vs deferred.) Please still run g217
first. Both nodes report driver 580.173.02.
