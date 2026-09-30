---
id: assumption-sweeps-checkpoints
campaign: overnight-sep30
lane: assumption-sweeps
kind: report
status: open
repo: danielreuter/verity
origin: assumption-sweeps (bc-5be66fb3), launched by RC bc-8ece7cde for postmortem action 2
---

# assumption-sweeps: hourly checkpoints

One line an hour. Jobs: Kueue on vy-nebius-1, template `prover-dev` (queue `provers`, priority `dev`, lowest), 8 vCPU / 64 GB / 1 GPU each, at most 2 at once so an M0 bench (1 GPU, 18 vCPU) always fits. Tree `/workspace/research/trees/assumption-sweeps` (origin/main 2c4101bf0 + infra/nebius sky/ + red team scripts in `rt-redteam/`).

- 20260930T1537Z open: edges_job.sh die pass started: job 230 (as-edges-d1) queued; next: 2nd slot, then tc_probe sm120 bf16 new seeds; job list asked of red team
