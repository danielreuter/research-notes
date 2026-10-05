---
id: proofs/20261005T2336Z-friction-cpu-phase-idle-weight
lane: proofs
kind: friction
status: open
---

# On node 1, a job that leases its GPU per prove runs its verifier at CPUWeight=idle, so its timings move with other jobs' load

Infra's rule (proofs coordinator, 2026-10-05) is that a GPU is leased around each prove invocation only, and never around a
whole STEP. To follow it, `backends/flock/pod/85-rec-reprice.sh` (100633247 on `cursor/rec-step2-95d4`) is launched without
`--gpus` and takes `gpu-lease` inside the job.

The catch is that `tools/cluster`'s `submit.wrappers` gives every node-1 job without `--gpus` `CPUWeight=idle`.
- The prover still runs at normal weight, because gpu-lease moves it into its own scope.
- serve and replay stay in the job's scope at idle weight.

The cost shows in check run r20261005-233027-873a, with the prover cores 99% busy with other work before it:
- L6's serve verify was 2.75 s (sessions 1.50 to 3.33 s), and its session time 1.50 s.
- Under a whole-job GPU lease at 12% load (r20261005-221419-ad0a), serve verify was 0.92 s and the session 0.76 s.
- The prover was unaffected: 0.497 s against 0.467 s.

For now, timings from such runs are read together with `prover_cores_busy_before`. The better fix would be a way to ask the
queue for normal CPU weight for a job that leases its own GPU, for example a flag beside `--phase cpu`, so that following the
lease rule doesn't cost measurement fidelity.
