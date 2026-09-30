---
id: 20260930T2142Z-handoff-from-proofs-replan-stop-rows-do-stage-split
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Re-plan, 2:42 PM PDT: don't queue next-coordinate whole rows on node 1; build the (b) stage/prove split instead

Why: the old research coordinator's value ranking (Slack thread `1790804308.098509`). Next-coordinate whole rows are
filler past 3 chunks per shape class, and node 1's GPUs are fully reserved. Node 2's guest worker (`proofs-n2-guest`) now
covers 3 chunks per distinct shape class, and the rest of the K=2048 row from statement 10,000.

1. **Stop your feeder's next-coordinate queueing** (tmux `proofs-rows-feed`). Delete any of your unstarted ready items;
   leave any running chunk to finish. Kill only pids you started.
2. **New task: the stage/prove split.** A K=2048 chunk holds a GPU through about 3 min of `class_statement` staging, then a
   prove that alternates host witness-building (about 120–290% CPU) with GPU bursts.
   - Add a stage-only `MODE=shape` to your own copy of `backends/flock/pod/73-sweep-shape.sh`, not backend-sweep-2's
     branch or files. It writes the chunk's statement in a CPU-only job, so the GPU job starts at the prove.
   - Put the scripts in `lanes/proofs-rows/tools/`. Hand the node-2 guest worker the recipe in `lanes/proofs-n2-guest/`.
   - Write a short note for the old research coordinator in `lanes/coordinator/`, saying how sweep2-feed could adopt it.
3. **Measure** one chunk staged separately against the current way: GPU-held minutes, and whether the bytes are identical.
