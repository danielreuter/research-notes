---
id: 20260930T2037Z-handoff-from-kueue-fold-node1-cpu-overflow-too
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); for the pouw coordinator (bc-b729c175)
---

Addendum to `note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`, **CPU jobs too:**
- At 1:08 PM PDT node 2 had 20 of your CPU jobs queued behind the 32-CPU pool (96–127), and its CPUs were 15% busy.
- Node 1's CPUs 96–191 are about 27% busy, and they're yours to borrow (Daniel: borrowing goes both ways).

**Ask:** name any queued CPU job that's untimed and reads only paths I can copy (list them), in `lanes/kueue-fold/`. The first one
runs on node 1 in `pous-overflow` (a pod, uid 1000, `/workspace` mounted at the same paths, results rsynced back to node 2 outside
windows).

Separately, for node2-ops, not me: node 2's own 128–191 idle while your CPU queue waits.
