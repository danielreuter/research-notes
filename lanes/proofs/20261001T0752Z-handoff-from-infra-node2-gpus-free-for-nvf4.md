---
id: 20261001T0752Z-handoff-from-infra-node2-gpus-free-for-nvf4
campaign: overnight-sep30
lane: proofs
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

Node 2's GPUs 1 and 3 are idle at 07:50Z, and node 2's fill queue has nothing that can use them: the only queued GPU job
is `pn2h-...mxf4-k2048-numa1-q0` with `on=4-7`, and GPUs 4-6 hold Commits while 7 is memory accounting's. NVF4 K=16384
step 1 is waiting in node 1's `provers` queue behind eight held GPUs. If it can run on node 2, submit it to node 2's fill
queue the way proofs-n2-hill does (`gpus=1 on=0-3`), with its CPU work under `vy-provers` (128-191, yours until 17:00Z).
