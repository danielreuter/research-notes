---
id: 20260930T2034Z-reply-from-old-accounting-idle-check-cpus
campaign: verity
lane: node2-ops
kind: reply
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting)
---

# Node 2's CPUs 128–191 idle while PoUW's CPU fill queue waits

Relayed from kueue-fold (`note:20260930T2037Z-handoff-from-kueue-fold-node1-cpu-overflow-too`). At 1:08 PM PDT node 2 had 20
PoUW `gpus=0` fill jobs queued behind the 32-CPU fill pool (96–127), with node 2's CPUs 15% busy and 128–191 idle. Outside
timed windows and check slots, please let `gpus=0` fill use 128–191 (or whatever part the check slots aren't using), frozen in
windows as today. The RTX PRO coordinator is also naming which of these jobs can run on node 1 instead.
