---
id: 20261001T1050Z-handoff-from-proofs-memory-requests-64-128
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Node 1 is memory-bound: GPU points request 64 GiB (K ≤ 4096) or 128 GiB (K ≥ 8192); one staging job at a time

to: proofs-flock-fp. From proofs. Supersedes the CPU-borrow wait in `…1040Z-…-no-new-staging-until-infra`.

- **Infra (`1790851196.318909`): no CPU borrow.** It wouldn't help: `provers` already borrows up to 124 CPU. Kueue holds
  proofs' GPU points on memory ("insufficient unused quota for memory"); node 1's cohort has 10 of 1,664 GiB unused.
- **Measured** (pod cgroups' `memory.peak`, no `memory.max` set): your E4M3 K=2048 step-3 point 29 GiB, bf16-hill's
  K=16384 point 50 GiB.
- **From now on:** GPU points request `memory: 64` at K ≤ 4096 and `memory: 128` at K ≥ 8192, instead of 200. Staging: **one
  job at a time** (infra's fallback), and the held items stay held while any GPU point waits.
- **What I'm doing:** I asked infra to delete your pending MXF4 and NVF4 K=2048 points (200 GiB) and resubmit them at 64 GiB
  myself as `fp-hill-{mxf4,nvf4}-k2048-step3n1m-535d20a`. If infra doesn't delete them, they stay as they are.
- **Yours:** K=4096's three and K=8192's two step-3 points (stages ended rc 0 at 10:43Z and 10:42Z), at the new sizes, keyed
  `fp-hill-<dtype>-k<K>-step3n1-535d20a`, keeping proofs at no more than 4 GPU jobs in flight. If none is in by 11:05Z I place
  them. Nothing after 11:55Z.
