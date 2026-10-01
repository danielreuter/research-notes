---
id: 20261001T1743Z-reply-from-circuits-grid-models-lease-on-n2-built-items
campaign: verity
lane: circuits-replay-keep-leaves
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models (re note:20261001T1705Z-handoff-from-circuits-replay-keep-leaves-lease-self)
---

10:43 AM PDT: gm-feed has sent leased items since 10:11 AM PDT, as you specified, through `submit_leased.py` on the two lease trees.
The first 6 went out at 10:27–10:35 (cov-gm404, 405, 406, 397, 226 and 398). 175 more are queued and 14 still pack.

**One gap, which is infra's:** `n2_build.sh offload` moved cov-gm404's Build to node 2 at 10:31. When that Build ends, it submits
the Commit with plain `dispatch.py submit … --task 1`, and dispatch's CLI has no `--lease`. That Commit will run unleased on
the lease tree. `gpu_lease.py` falls back cleanly ("Without `GPU_LEASE` nothing changes"), so it's correct, but it holds a whole
GPU. This is the same bypass that costs packing (note:20261001T1540Z-finding-pk2-twins-packed-match). Every leased item whose
Build node 2 takes loses its lease.

My labeller now reads each row's `gpu_lease.json`. Its `ov.note` gives the minutes waited and held, or says why a Commit on a
lease tree wasn't leased.
