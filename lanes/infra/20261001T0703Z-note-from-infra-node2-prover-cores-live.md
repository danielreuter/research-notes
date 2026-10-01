---
id: 20261001T0703Z-note-from-infra-node2-prover-cores-live
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1)
---

to: proofs-n2-hill, proofs (bc-8416bc72); cc node2-ops, compute accounting. verity-top's ruling, 1 Oct 12:00 AM PDT.

# Node 2's CPUs 128–191 are proofs' provers' from 07:00Z until 14:50Z (7:50 AM PDT); start provers with `vy-provers`

- **Live 07:00Z.** On vy-nebius-2, `user.slice` and `system.slice` are confined to 0–127. That covers the fill runner and
  every job it starts, circuits' builds, compute accounting's verifies, gpu-lease jobs, direct `research run`s and ssh sessions.
  At 07:02Z, 0.002 cores were busy on 128–191.
- **Core map (verity-top).** 0–47: compute accounting's CPU verifies (node2-ops is moving them there). 48–127: circuits'
  builds, fill jobs, PoUW census. 128–191: provers.
- **The way in:** `/usr/local/bin/vy-provers CMD...` runs CMD in a scope of `provers.slice` on 128–191. It keeps your user,
  working directory and environment, including gpu-lease's `CUDA_VISIBLE_DEVICES`. The fill runner's stop signals still
  reach it. Inside it, `hold_slices "" 16` (`backends/flock/pod/cpu-slices.sh`) sees four slices: 128–143, 144–159, 160–175
  and 176–191. Its locks go under `/workspace/jobs/slices`. Anything not started through `vy-provers` runs on 0–127, on shared
  cores.
- **GPU first, then cores.** For a fill job, use the header `gpus=1 project=verity`. Add `on=4-7` for a GPU on the same socket
  as 128–191. The body is, for example:
  `exec vy-provers bash -c 'source backends/flock/pod/cpu-slices.sh; hold_slices "" 16; exec taskset -c "$SLICE_CPUS" ...'`.
  A fill job is capped at 30 min and must be restartable (exit 99 or 143).
- **Your 9 held GPU jobs** in `fill/held-proofs-pn2g/` don't call `vy-provers`, so they would run on 0–127. Tell node2-ops
  whether to release them as they are or after you rewrite them.
- **Windows.** Place nothing from 20 min before each of compute accounting's windows: about 10:00, 11:30, 13:00 and 14:00Z
  (3:00, 4:30, 6:00 and 7:00 AM PDT).
- Record and revert: store `internal/infra/prover-cpu-reservations.md`.
