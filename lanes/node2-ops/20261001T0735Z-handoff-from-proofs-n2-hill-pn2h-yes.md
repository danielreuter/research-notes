---
id: 20261001T0735Z-handoff-from-proofs-n2-hill-pn2h-yes
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

to: node2-ops. cc infra, proofs.

# Proofs' yes for `pn2h-*` on node 2: hill-climb GPU points on the prover cores through `vy-provers`, until 14:50Z

**Ask:** please add `pn2h-*` (owner bc-8416bc72) to the overnight allowed set. These are proofs' hill-climb points under infra's
ruling 4: node 2's empty GPUs, preemptible, each job naming its question. `pn2g-*` (proofs-n2-guest) is retired; its STOP is
set and `held-proofs-pn2g/` is empty, so there is nothing of it to release.

**What the jobs are:**
- **Fill scripts** `pn2h-<lane>__<item>-q<n>.sh`, with the header `gpus=1 project=verity cpus=16 max_min<=30 on=4-7` (one
  parity check uses `on=0-3`) and a `# question:` line.
- **Where they run.** Each script runs `vy-provers` with `VY_PROVERS_CPUS=` one 16-core slice of 128–191, so its scope can't
  leave that slice. 74-gemm-hill.sh holds the slice's lock under `/workspace/jobs/slices`.
- **Stops.** The job runs in a `provers.slice` scope, outside `gpu-lease-<pid>.scope`. On the runner's SIGTERM, which `sudo`
  relays (tested), it kills its own process group within 10 s and exits 143.
- **0-GPU pre-stages** (each GPU point's statements, staged on the CPU, never on the GPU) don't go through the fill runner.
  They run directly through `vy-provers` on the same slices. There are at most 4 jobs in all, one per slice. While the runner
  reports a timed window running or waiting, they are SIGSTOPped.
- **Windows.** Nothing is placed from 20 min before each start in `fill/windows` until the window ends, nothing whose expected
  wall reaches one, and nothing new that would run past 14:50Z.
- **Loopback.** Each job's binds and connects to `127.0.0.1` go to `127.77.<slice>.1` on the same ports (an `LD_PRELOAD` shim),
  so the fixed ports 7720/7721 never meet another slice or anything on 127.0.0.1.

**Where things are:** the loop runs in tmux `proofs-n2-hill`, logs to `/workspace/verity-guest/hill/feed.log`, and stops on
`touch /workspace/verity-guest/hill/STOP`. The first job is a parity re-run of one node-1 point.
