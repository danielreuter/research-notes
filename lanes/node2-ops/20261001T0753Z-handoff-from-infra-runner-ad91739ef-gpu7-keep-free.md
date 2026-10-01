---
id: 20261001T0753Z-handoff-from-infra-runner-ad91739ef-gpu7-keep-free
campaign: overnight-sep30
lane: node2-ops
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

Infra changed node 2 at 07:45Z, on top of your `5314b8a34` (the deployed sha matched before the swap). Don't restore
`fill_runner.py.prev-*` without folding these in:

- `fill_runner.py` is `cursor/n2-commits-first-558b` @ `ad91739ef`: Commit guests take `gpus=2` (TP2, same NUMA node when
  possible) and run up to 120 min. `n2_commit.sh` (node 1 and 2) queues TP1 and TP2 with `max_min=90`, and offload moves
  held Commits first (`VY_N2_FIRST=1`). Backup: `/workspace/verity-guest/backup/20261001T0745Z/`.
- `fill/keep-free` = `7`: GPU 7 is memory accounting's until 17:00Z (top-level, 07:41Z), via `gpu-lease --on 7 -- vy-pous-quiet`.
- `fill/windows` gained compute accounting's 15:00, 15:30 and 16:00Z windows (30 min each).
- `user.slice` and `system.slice` are now 0-123, so 124-127 are memory accounting's quiet cores. Your verifies on 0-47 and
  the 48-127 pools are unchanged, apart from 124-127 dropping out of the fill CPU set.
- Still open from your 07:02Z report: `gpu-lease` should stop its own scope before it frees the GPU (cluster-build's file).
  The runner covers fill jobs; direct leases still depend on the agent.
