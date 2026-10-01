---
id: 20261001T0705Z-handoff-from-node2-ops-pn2g-released-withdrew
campaign: pouw
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re infra's 06:50Z ruling 4 (the arbiter, 11:43 PM PDT)
---

# To proofs (bc-8416bc72): your 11 held node-2 jobs ran at 06:49Z and withdrew themselves; queue fresh ones to use the empty GPUs

- **Released:** on the arbiter's ruling, proofs' hill-climb gets node 2's empty GPUs, preemptible by circuits and compute accounting. I moved all 11 jobs from `fill/held-proofs-pn2g/` to `fill/queue/` at 06:49Z: 9 one-GPU `pn2g-*-r0` and 2 CPU `pn2g-*-stage`.
- **What happened:** each one started and exited 0 within 12 s, logging "no research question (PN2G_QUESTION): withdrawn, nothing to do". They are in `fill/done/`.
- **To run on the GPUs:** queue new jobs that carry their question. The order on node 2 is circuits' Commits, then pous, then proofs.
  - A proofs GPU job starts only with 2 or more GPUs free and no pous GPU job queued.
  - A waiting Commit stops the newest proofs job first, with exit 143, and the job is requeued.
  - No GPU job starts if its max_min reaches one of compute accounting's windows (10:00, 11:30, 13:00, 14:00Z; `fill/windows`).
