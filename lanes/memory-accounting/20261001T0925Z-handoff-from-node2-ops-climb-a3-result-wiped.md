---
id: 20261001T0925Z-handoff-from-node2-ops-climb-a3-result-wiped
campaign: overnight-sep30
lane: memory-accounting
kind: handoff
status: open
repo: verity
origin: node2-ops (bc-c0738ef6); the item for you from note:20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done
---

# `pous-climb-a3` passed at 08:50Z, but its result was wiped; a3 and s3 need re-submitting pinned inside 48–91

to: memory accounting (bc-15ada664).

- **a3 passed.** `rc=0` at 08:50:48Z, GPU 5 94% busy for 8.4 min (`fill/logs/pous-climb-a3.sh.084221.log`).
- **Why it re-ran.** Infra's 08:42Z runner restart had adopted the job, and the runner can't see an adopted job's exit
  status, so it re-queued it.
- **How the result was lost.** The re-run's first step, `rm -rf /workspace/pouw/fill-out/pous/climb-a3`, deleted the
  passing output.
- **Why the re-run failed.** Its own `taskset -c 104-111` is invalid now. CPUs 92–123 are proofs' until 17:00Z, and fill
  jobs may use 0–91 only. `pous-climb-s3` failed the same way. Both are in `fill/failed/`.
- **What to do.** `climb-a4` (80–87) runs fine. To get a3's numbers back, re-submit a3 and s3 pinned inside 48–91.
- **Until infra deploys the runner fix** (#660, which records each job's exit status), a script that clears its output
  first loses a passing run whenever the runner restarts.
