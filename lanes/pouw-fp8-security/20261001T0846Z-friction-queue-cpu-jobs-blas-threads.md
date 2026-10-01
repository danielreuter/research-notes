---
id: pouw-fp8-security/20261001T0846Z-friction-queue-cpu-jobs-blas-threads
lane: pouw-fp8-security
kind: friction
status: open
---

# `research run --queue` CPU jobs on vy-nebius-1 don't size BLAS/OpenMP pools to `--cpus`, so a numpy job ran 3.5× slower and timed out

`r20261001-073938-d76d` (`--cpus 4`, numpy, `swar_window.py`) ran 32 Python threads in its scope. That gave 0.54 cores of
useful work, and 78% of the cgroup's CPU time was system time. Each family took about 2 min, against about 35 s on a 4-core VM,
and the job hit its 60-min `STAGE_TIMEOUT` after 8 of 29 families. `r20261001-074853-2d6b` has the same shape.

I reran it as `r20261001-084416-b304` with `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` and
`NUMEXPR_NUM_THREADS` set to 4 inside the command.

The better fix is in the node executor (`tools/cluster`): set those variables to the job's `--cpus`, as `pod_bootstrap.sh`
does for pods (`kb/ops-tools.md`).
