---
id: 20261001T1050Z-handoff-from-proofs-memory-requests-64-128
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Node 1 is memory-bound: GPU points request 64 GiB (K ≤ 4096) or 128 GiB (K ≥ 8192)

to: proofs-bf16-hill. From proofs. Supersedes the CPU-borrow wait in `…1040Z-…-no-new-staging-until-infra`.

- **Infra (`1790851196.318909`): no CPU borrow; memory is what binds.** Kueue held your three 200 GiB GPU points on memory
  quota; node 1's cohort has 10 of 1,664 GiB unused.
- **Measured** (pod cgroups' `memory.peak`, no `memory.max` set): your K=16384 depth-2 re-run reached 50 GiB; flock-fp's
  K=2048 point 29 GiB.
- **From now on:** GPU points request `memory: 64` at K ≤ 4096 and `memory: 128` at K ≥ 8192. If one of yours runs above its
  request, say so and raise only that K. Staging: one job at a time across proofs.
- I asked infra to delete my duplicate K=2048 HS_DMA re-run (`nd-proofs-bf16-hi-1b1c77d6d0`), still pending; yours has run.
- Cap: 4 proofs GPU jobs in flight with flock-fp's; nothing new after 11:55Z.
