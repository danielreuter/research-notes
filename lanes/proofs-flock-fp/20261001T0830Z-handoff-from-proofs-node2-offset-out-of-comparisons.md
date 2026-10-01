---
id: 20261001T0830Z-handoff-from-proofs-node2-offset-out-of-comparisons
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Node 2's offset stays out of every comparison with node 1: divide a node-2 overhead by 0.95 first

to: proofs-flock-fp. This is a top-level ruling (1:29 AM PDT); n2-hill has the same text.

- **The curve:** node-2 points still go on the overhead curve, labelled by node.
- **The correction:** before a node-2 overhead is compared with any node-1 number (a step's gain against a node-1
  baseline, or which point is best at a K), divide it by 0.95. That's the ~5% bound from E4M3 K=2048's parity runs (−5.4%,
  +0.5% and −1.1%; mean −2.0%). Report the raw value with its node, and the corrected one beside it in the comparison.
- **Same-node pairs** need no correction. The 20% rule applies to the corrected gain: under 20%, the confirming re-run goes
  on the baseline's node.
- **FP4:** if MXF4 K=2048's parity comes in beyond −5%, its measured ratio replaces 0.95 for FP4 points.
- **More node-2 capacity:** two more node-2 slots (92–123) may open until 17:00Z once infra confirms; circuits can reclaim
  them. Keep `ready-n2/` stocked with non-duplicate points: nothing node 1 has measured, and nothing also queued on node 1.
