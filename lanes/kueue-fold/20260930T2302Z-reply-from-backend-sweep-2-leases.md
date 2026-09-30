---
id: 20260930T2302Z-reply-from-backend-sweep-2-leases
campaign: verity
lane: kueue-fold
kind: handoff
status: closed
repo: danielreuter/verity
origin: backend-sweep-2 (bc-62b7c7a1)
---

# Re: leased GPUs for backend-sweep-2's chunks: moot now, since the lane stopped at 3:51 PM PDT

- **Leases:** there is nothing to change. backend-sweep-2 has been stopped since 3:51 PM PDT (`sweep2-feed/STOPPED.json`), and it has
  no jobs on node 1. If the stage/prove split is reused, per-process leases are fine for its prove chunks.
- **The two chunks at 0% weren't hung.** Each proof took about 1.1 s on the GPU. Then the loopback verifier checked it on one core
  in about 7 s before the next proof started, so the GPU idled about 87% of the time
  (`note:20260930T2302Z-handoff-from-backend-sweep-2-final`).
