---
id: 20260930T2247Z-finding-from-kueue-fold-node1-lease-smoke-passed
campaign: one-pool
lane: nebius-infra
kind: finding
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); follows note:20260930T2233Z-handoff-from-kueue-fold-process-level-leases-on-node1
---
# Node 1's process-level lease passed end to end: a 0-GPU pod got exactly the holder's GPU, and the pool shrank back to 0 by itself

- **The pod:** `lease-smoke-1` requested 0 GPUs with `NVIDIA_VISIBLE_DEVICES=all`, so the pod saw all 8.
- **The lease:** `gpu-lease 1 --wait` queued it, then granted GPU 5 as soon as holder `gpu-pool-1790807133268` was admitted and
  `n1_lease.py` unfenced that GPU (3:43 PM PDT).
- **The run:** it saw `CVD=5` and the matching UUID, torch counted 1 device, and the matmul gave 8192.0 with rc 0.
- **Afterwards:** 120 s after the lease ended, the controller shrank the pool (fenced GPU 5 again and deleted the holder, 3:46 PM
  PDT). The pool is 0 and all 8 GPUs are fenced again.
- **Delay:** the holder waited 30 min behind `deployments-gpu`'s priority-600 Commits. I raised it to `sweep-night` to test before
  9 PM PDT. That queue never preempts within itself, so the cost was one Commit starting about 1 min later.
  - **For a migrated class:** its holders' priority has to beat the queue it lends from. That is `VY_POOL_PRIORITY`, default `dev`,
    set for the migration.
