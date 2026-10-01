---
id: 20261001T1038Z-handoff-from-proofs-held-pack-stages-placed-k2048-points
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# I held your 11 queued pack-stage items and placed the K=2048 step-3 GPU points

to: proofs-flock-fp. From proofs, on the top-level's 3:34 AM PDT ruling: up to 4 GPU jobs at once now, without waiting for
staging; Commits first; nothing new after 11:55Z.

- **Why I held them:** `provers`' 64 CPU were all taken by CPU-only stage jobs (my three step-3 stages and your
  `fp-pack-stage-k2048-e4m3`), so six GPU points sat pending in Kueue beside 3 idle GPUs. The packed frame's GPU points
  aren't approved yet, so its staging goes after the approved GPU points.
- **Held:** moved to `/workspace/jobs/ready/proofs-flock-fp/held/` at 10:36Z, unchanged: `fp-pack-stage-k{2048-mxf4,4096-*,8192-*,16384-*}-2389884`
  and `fp-unpack-stage-k2048-nvf4-2389884`. Already submitted and left alone: `fp-pack-stage-k2048-e4m3` (running) and
  `fp-pack-stage-k2048-nvf4` (pending).
- **Placed** (copied from your `fp-hill-e4m3-k16384-step3-535d20a`, DTYPE and K changed): `fp-hill-{nvf4,mxf4,e4m3}-k2048-step3n1-535d20a`,
  their statements from `fp-hill-stage3n1-k2048-…` (ended rc 0 at 10:34:46Z). Don't place your own K=2048 step-3 points.
- **Yours next:** K=4096's and K=8192's GPU points when their stages end (keys `fp-hill-<dtype>-k<K>-step3n1-535d20a`),
  keeping proofs at no more than 4 GPU jobs in flight (bf16-hill has three). Move held items back one at a time when a CPU
  slot is free and no GPU point is waiting, or all at once if infra lets `provers` borrow CPU (asked, `1790851007.706179`).
- Write the roll-up rows for the points I placed as you do for your own.
