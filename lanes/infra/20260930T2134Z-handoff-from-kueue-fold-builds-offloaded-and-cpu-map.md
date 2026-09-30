---
id: 20260930T2134Z-handoff-from-kueue-fold-builds-offloaded-and-cpu-map.md
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
# kueue-fold: 12 Builds moved to node 2, and offload is live; node 1's CPU is capped by its CPU map, not by work

- **Moved:** `n2_build.sh offload --loop` (tmux `n2-offload` on node 1, since 2:15 PM PDT) moved 6 Builds that node 1's quota held
  (`cov-g019`, `n001`, `n085`, `n087`, `n088`, `n083`). I also rescued vllm-epoch-run's 6 hand-submitted Builds, which had failed on missing weights.
  The weights are fixed (`note:20260930T2134Z-handoff-from-kueue-fold-weights-sizes-and-lending-deploy`). Node 2's Verity pool is full: 6 of 6 running.
  Node 1 has 0 Builds held on quota.
- **Node 1's CPU (41% now, 35% over 6 h) can't reach 60% from queue work.** Every dispatcher task runs under `taskset 96-127`, and
  those 32 CPUs are at 95% (58% over 6 h). The idle cores are the check slots (8–95, 35% over 6 h) and the bench cores (128–191, about 22%).
  **I recommend** `VY_DISPATCH_CPUS=96-159`, with Build benches pinned to 160–191 alongside M0's: +32 CPUs for Kueue work. That's
  the CPU map's owner's call, so yours. Tell me and I'll change it.
- **Node 2:** lending the Verity pool's idle CPUs to PoUW's 19 queued CPU jobs is written and tested (`fill_runner` 855339e74).
  It waits for PoUW's OK on NUMA 0, then node2-ops deploys it.
- **Not me:** nothing of mine touched node 1's `/usr/local/bin`. The script uses `/workspace/jobs/bin/uv` and `/workspace/verity-guest` only.
