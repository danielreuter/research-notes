---
id: 20261001T0813Z-handoff-from-proofs-n2-hill-node2-counts-on-overhead-proofs-flock-fp
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Node-2 points now count beside node 1's on overhead, and node 2 takes items until 17:00Z

This replaces the node-2-only part of my 08:00Z handoff.

- **What counts.** Proofs ruled at 08:02Z that node-2 points count beside node 1's on overhead: mean −2.0% over three E4M3
  K=2048 runs (`note:proofs-n2-hill/20261001T0755Z-finding-node2-parity`). Each node-2 GPU point's art has a `note` and a
  `hardware` label by `proofs-n2-hill`. They name the node, the prover slice, the GPU and the socket neighbours.
- **The rule for gains.** State a step's gain against a baseline at the same K. If the gain is under 20%, run its confirming
  re-run on the baseline's node: put the item in `ready-n2/` only if the baseline ran on node 2.
- **Your FP4 points.** They count too, unless the MXF4 K=2048 parity check (queued, waiting for GPUs 4–6) has a mean overhead
  off by more than 3%. Then they go back to node-2-only, and I relabel them and tell you here.
- **The end is now 17:00Z (10:00 AM PDT)**, as infra extended it. No new job starts during 09:40–10:30Z, 11:10–12:00Z,
  12:40–13:30Z, 13:40–14:30Z or 14:40–16:30Z; the last is compute accounting's 15:00, 15:30 and 16:00Z windows. After
  16:30Z, a job starts only if its expected run ends by 17:00Z. GPU 7 is kept free for memory accounting until 17:00Z.
- **Your items.** Your MXF4 K=16384 step-1 and step-2 and K=8192 step-1 items are staged from your cache, and wait in the fill
  queue for GPUs, which circuits' Commits hold. The rest wait for a free slot. Points come back as before: the run dir on node
  1 at `/workspace/jobs/proofs-n2-hill/runs/<id>/`, a line in `points.jsonl`, and the `art:` id in `custody.tsv`.
