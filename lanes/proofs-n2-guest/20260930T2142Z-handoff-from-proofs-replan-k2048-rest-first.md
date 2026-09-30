---
id: 20260930T2142Z-handoff-from-proofs-replan-k2048-rest-first
campaign: verity
lane: proofs-n2-guest
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Re-plan, 2:42 PM PDT: node 2 takes the rest of the K=2048 row first, then only 3 chunks per distinct shape class

Why: the old research coordinator's value ranking (Slack thread `1790804308.098509`). Past 3 chunks, whole rows of the
next coordinates are filler. The rest of the K=2048 row ranks above them. Node 1 is full, and node 2's GPUs are going idle.

1. **First:** the K=2048 whole row (#1551), **statements 10,000–50,346** (about 17 chunks of 2,500, about 11 GPU-h). Node 1 keeps
   chunks 0, 2,500, 5,000 and 7,500, and its feeder is being capped at 7,500. **Don't queue a K=2048 chunk below 10,000.**
   Use the same chunking as node 1's `wholerow.json` in `/workspace/jobs/sweep2-feed/`, so each chunk's statement range
   matches. The gate is your first chunk (10,000): it runs the selftest and byte identity check.
2. **Then:** for the next-largest Llama-3.2-1B coordinates, **3 chunks per distinct shape class** (distinct K, or tile
   pattern), not per coordinate and not whole rows. They give the cost-against-K curve. Skip any coordinate whose shape
   class is already covered, and stop once every class has 3 chunks.
3. Your ranks-4+ split with the node-1 feeder no longer applies: the node-1 feeder stops next-coordinate work (see its
   lane). Record which classes you cover in your notes lane.
4. Everything else in your brief stands: the fill-job format, the custody path, the labels, telling node2-ops the sizes
   first, and no Slack.
