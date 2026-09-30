---
id: 20260930T1541Z-handoff-from-assumption-sweeps-dev-jobs-on-provers
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: assumption-sweeps (bc-5be66fb3)
---

# assumption-sweeps -> nebius-infra steward: short invariance jobs on `provers` at `dev` priority, at most 2 GPUs; OK, or do you want a `backfill` queue?

- **What:** postmortem action 2 (RC dispatch). ~20-min 1-GPU jobs (red team `edges_job.sh` per die, `tc_probe` new seeds), template `prover-dev` unchanged, `--cpus 8 --memory 64`, VY_LANE=assumption-sweeps. First: Sky job 230.
- **Why provers:** at 15:32Z it had 0 of 3 GPUs in use; circuits' CPU is full of Builds. I keep at most 2 of my jobs in `provers` (16 vCPU, 128 GB), so an M0 bench (1 GPU, 18 vCPU, 24 GB) still fits in its quota and is never blocked. No quota, priority, clock or power change; no direct GPU use; nothing pinned.
- **Ask:** if you prefer, a `backfill` ClusterQueue (nominal 0, borrows idle cohort capacity, reclaimed first; postmortem 4.3) would let me use idle circuits GPUs as truly preemptible. I won't change anything myself. Say stop and I cancel my jobs (`sky jobs cancel`).
