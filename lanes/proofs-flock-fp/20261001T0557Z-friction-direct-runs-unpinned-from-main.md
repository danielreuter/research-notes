---
id: proofs-flock-fp/20261001T0557Z-friction-direct-runs-unpinned-from-main
lane: proofs-flock-fp
kind: friction
status: open
recurs: note:20261001T0137Z-handoff-from-proofs-flock-fp-vllm-jobs-on-prover-slices
---

# A `research run --on vy-nebius-1` from a main-based tree starts on all 192 CPUs, onto the prover slices

`r20261001-055012-7395` (campaign `pouw`, `sass_inventory.py`, 24 pool workers each spawning `nvdisasm`) ran on node 1 with
affinity 0-191 from 05:50Z and loaded cores 144-175. It re-flagged E4M3 K=8192's clean re-run `r20261001-054832-9c8c`
(`cpu-slice-shared`, 0.84 others on 160-175), so that point is re-run once the cores are quiet. Cost: one GPU point re-run.
Tracked from 05:50Z, with NVF4 and MXF4 K=8192 held until it ends.

The cause is not the `pouw` lane. Node 1 has `/etc/vy/direct-cpus` = `0-95`, and nebius-infra's utilization summary lists the
placement as fixed (`84fb8a7b`, `259acc56`). Neither commit is on `main`: they are on `origin/infra/nebius` and the branches
that merged it. None of the tool snapshots shipped to node 1 since 2026-09-30 23:00Z (`/workspace/research/tool/*`, newest
`d98f39d7698045fc`) reads `DIRECT_CPUS_FILE` or blanks `CUDA_VISIBLE_DEVICES`. So every direct run from a main-based checkout
lands on any core and can open CUDA on Kueue's GPUs.

The fix is to land those two commits on `main`. A run launched from a lane's own tree would then pick up the placement. It
is nebius-infra's to land, through the coordinator.
