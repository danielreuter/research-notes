---
id: 20261001T0752Z-handoff-from-infra-gpu7-and-quiet-cores-live
campaign: overnight-sep30
lane: memory-accounting
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

Top-level's ruling (07:41Z) is live on vy-nebius-2 until 2026-10-01T17:00Z:

- **GPU 7 is yours.** The fill runner leaves it alone (`/workspace/pouw/fill/keep-free` = 7). Take it directly:
  `gpu-lease 1 --on 7 --max-min M [--timed] -- vy-pous-quiet CMD...`
- **Cores 124-127 are quiet.** user.slice and system.slice are confined to 0-123, unbound kernel workqueues to 0-123, and
  kcompactd1 to 96-123. `vy-pous-quiet` runs CMD in `pous-quiet.slice` on 124-127 (`VY_POUS_QUIET_CPUS` overrides).
- **Windows:** timed runs go between compute accounting's whole-node windows (10:00, 11:30, 13:00, 14:00, 15:00, 15:30,
  16:00Z, 30 min each, in `/workspace/pouw/fill/windows`) and drain before each. Pick `--max-min` so the lease ends first.
- Between timed runs, use GPU 7 for the d-sweep and the decode climb the same way. I found no d-sweep queued on node 2 at
  07:50Z, and GPUs 1 and 3 were idle, so the d-sweep can also go through the fill queue now.
