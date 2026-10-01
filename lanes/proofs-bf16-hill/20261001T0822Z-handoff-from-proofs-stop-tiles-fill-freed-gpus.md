---
id: 20261001T0822Z-handoff-from-proofs-stop-tiles-fill-freed-gpus
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Stop the K=4096 tile ladder, and fill the freed GPUs with non-tile points on both nodes

to: proofs-bf16-hill (bc-89f3138c). Act on this before you queue your next item.

**1. No more tile stages.**
- Your K=4096 tile stages keep failing: `stage-tile4x3-lc2-k4096-66defbf` (rc 1, 08:02Z) and `tile4x2` (rc 1, 08:13Z).
  `tile3x2` (08:16Z) may finish, but queue no further tile stage.
- red-team-proofs-554's Q2 is an OBJECT (`note:proofs/20261001T0817Z-reply-from-red-team-proofs-554-tile-4x4-statement`).
  `stage_tiled` takes both tile sides from port-0 rows. At the hill point every unit proves x·x for one activation row, no
  weight row is bound, and the tile path never checks outputs against `want`.
- So a tiled point is a cost, not the untiled claim. It stays off the overhead curve until Daniel rules on cross-Call
  grouping (that's on his morning list). This holds at K=2048 too: report K=2048 from your best non-tile point, and keep
  `tile-statement-unreviewed` on tile points.

**2. Capacity (top-level, 08:20Z).** Circuits is cancelling five stuck Commits on node 2 (GPUs 0, 2, 4, 5, 6). Node 2's GPU
1 and node 1's GPUs 1 and 2 are empty. Everything stays preemptible: circuits' new Commits take priority on node 2, and
compute accounting's runs arrive on node 1 at about 08:30Z. A preempted point is re-run, never reported.
- **Node 2, now:** your next non-tile step at every K, in `/workspace/jobs/ready-n2/proofs-bf16-hill/`.
- **Node 1:** while `provers` has free GPUs, keep up to two GPU items there, on 16-core slices in 128–191.
- **Never the same point on both nodes.** Node-2 points count beside node 1's, and a gain under 20% has its confirming
  re-run on the baseline's node. n2-hill is holding your three 08:00Z node-2 copies (K=2048 s7 tile-lc, K=4096 s3, K=8192
  s3), because node 1 had already run them.
- **Nothing to restart.** Your K=4096 step 2 (overlap) wasn't displaced: it succeeded at 07:37Z, and step 3 at 07:42Z. If
  cg16's Commit on node 1 GPU 3 displaced any other point of yours, re-run it.

My 08:16Z flag rules stand (`20261001T0816Z-handoff-from-proofs-554-grant-narrow-the-flag`).

Reply with one line in `lanes/proofs/`: what you queued on each node, and the next non-tile lever at each K.
