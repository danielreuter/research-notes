---
id: 20261001T0813Z-handoff-from-proofs-n2-hill-node2-counts-on-overhead-proofs-bf16-hill
campaign: overnight
lane: proofs-bf16-hill
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
- **The end is now 17:00Z (10:00 AM PDT)**, as infra extended it. No new job starts during 09:40–10:30Z, 11:10–12:00Z,
  12:40–13:30Z, 13:40–14:30Z or 14:40–16:30Z; the last is compute accounting's 15:00, 15:30 and 16:00Z windows. After
  16:30Z, a job starts only if its expected run ends by 17:00Z. GPU 7 is kept free for memory accounting until 17:00Z.
- **Your three items (08:00Z) wait for a slot.** These are K=2048 s7, K=4096 s3 and K=8192 s3. All four slots hold GPU points
  that are already staged and wait for GPUs, which circuits' Commits hold. Your lane has nothing running, so it gets the next
  free slot. The slot count (4 × 16 cores, 1 GPU each) and the return path are as in my 08:00Z handoff.
