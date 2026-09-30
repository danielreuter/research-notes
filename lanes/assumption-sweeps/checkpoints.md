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
- 20260930T1645Z open: edges_job.sh Attempts passed on 6/8 dies (0,1,3,5,6,7; all edge counts and MUFU ex2/rcp sha256 identical); as_digest.py (GPU-only, backfill, 1 vCPU) on dies 2,6: 8 MUFU ops + mma seeds 1-4 identical; switched to dispatcher ready files (4 edges, 8 digest, tc_probe seeds 1-8, backfill)
- 20260930T1755Z open: edges_job.sh passed on 7/8 dies (die 4 preempted mid-run once; 3 more queued), identical measurements on all 7; as_digest.py 8/8 dies: 8 MUFU ops + mma seeds 1-4 one digest each, stable across repeats/streams; tc_probe seeds 1-8 failed on PYTHONPATH (families run: 0 mismatches), requeued as tcp2-s1..8
- 20260930T1856Z open: edges_job.sh passed on 7/8 dies (die 4 pending; edges-p04/p05 running on provers/dev); as_digest 8/8 dies one digest per op/seed; tc_probe seed 1 passed (die 6), seeds 2-8 staged behind 2-job gate.
- 20260930T1935Z first 8-die pass done: edges_job.sh passed on all 8 dies (die 4 r20260930-191715-b6b0), identical measurements; digest 8/8 identical; tc_probe seeds 1-5 passed, 6-8 running/staged; handoff note:assumption-sweeps-20260930T1935Z-first-8-die-pass
