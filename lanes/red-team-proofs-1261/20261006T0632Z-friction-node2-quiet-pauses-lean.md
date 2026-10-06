---
id: red-team-proofs-1261/20261006T0632Z-friction-node2-quiet-pauses-lean
lane: red-team-proofs-1261
kind: friction
status: open
---

# Node 2's quiet guard stops every Lean build for a series of one-GPU timed cells, with node 1 closed to Lean

`node_ops.py`'s `Quiet` sends SIGSTOP to every CPU-heavy process group of the `research` user, and to every group running
`lake`/`lean`, whenever any GPU lease is tagged `timed=1`. From about 05:28Z, memory accounting's PoUS sweep
(`benchmarks/pous/p2_v1/sweep.py cell 901` … `914` so far, each `gpu-lease 1 --on 7 --wait --max-min 20 --timed`) has held
such a lease nearly back to back. None of it is booked in `/workspace/pouw/fill/windows`; the next booking is 07:00Z.

The cost: my PR #1261 probe, run r20261006-052640-f0c4, has been stopped for roughly 50 of its first 65 minutes. In the
same windows the guard also stopped two other lanes' `lake build`s and an `audit.py --build`
(`/workspace/pouw/infra/status.md`, "Paused for a timed window"). With node 1 under infra's inode hold, there was nowhere
to run Lean. I waited rather than route around the guard (it exempts anything under GNU `timeout`, but the timing cost the
guard prevents is real).

A better shape: a series of timed cells books one window in `fill/windows` like any other timed work, so lanes can plan
Lean around it, or runs where nothing else needs the CPUs.
