---
id: 20261001T0825Z-draft-from-kueue-fold-n1-borrowed-leases-cutover
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), for top-level's 1:02 AM PDT ruling (node 1's GPUs 0 and 2 for untimed jobs)
---

# Cutover plan: node 1 lends 2 borrowed GPUs to preemptible leases until 5:10 AM PDT (`n1_lease` `025260083`)

**Why.** The ruling's literal path, plain `gpu-lease --on 0` or `--on 2` on node 1, can't work, and wouldn't be safe if it did.
- `n1_lease` fences every GPU outside its pool with an `flock -x` on its lock in `/run/gpu-lease`. Node 1's default
  `gpu-lease` (`/usr/local/bin/gpu-lease`) uses that directory too, so such a lease waits forever.
- Without the fence, Kubernetes would still treat GPUs 0 and 2 as free and could put a Commit pod on one of them,
  beside the job.

**What changes.**
- Install `infra/nebius` `025260083`'s `n1_lease.py` at `/workspace/verity-guest/bin/n1_lease.py`, keeping a `.bak-<UTC>`
  copy.
- Restart tmux `n1-lease` with `VY_POOL_BORROW=2 VY_POOL_BORROW_UNTIL=2026-10-01T12:10:00Z`.
- While every waiter is `--preemptible`, a holder may take up to 2 GPUs of the cohort's idle quota. Kubernetes picks which
  GPUs, so they need not be 0 and 2.
- A Commit's reclaim evicts the holder. The lease on that GPU is then outside the pool and is stopped through its scope:
  SIGTERM, then SIGKILL 30 s later.
- No new borrowing after 5:10 AM PDT. Leases already running keep their GPUs until they end or are reclaimed.
- Nothing else changes: not Kueue, not the queues, not the device plugin.

**How a lane uses it,** inside `research run --on vy-nebius-1`, with the ruling's terms (custody, cores off 128-191):

~~~bash
env GPU_LEASE_DIR=/run/gpu-lease GPU_LEASE_ALLOWED_FILE=/run/gpu-lease/pool.gpus \
  /workspace/verity-guest/bin/gpu-lease 1 --wait --preemptible --max-min M --mem-gb G -- CMD
~~~

Leave out `--on`. Once #645 merges, `research run --queue --on vy-nebius-1` does the same.

**Before.**
- `n1-lease` is running.
- `/run/gpu-lease` holds only fences.
- A dry-run `tick` under the new environment grows nothing with no waiters.

**After.**
- One 1-GPU preemptible lease of `nvidia-smi -L`, run by kueue-fold, gets a borrowed holder, and the GPU is unfenced.
- The lease runs and the pool shrinks after `VY_POOL_IDLE_S`.

**Rollback.**
- Restart tmux `n1-lease` without the two variables, or restore the `.bak`.
- Delete any `gpu-pool-*` Job. Its lease is then stopped.
- Fences outlive the controller, so a restart fails closed.

**Risk.** After a reclaim, the job can share its GPU with the Commit for about 10 s: two ticks before the stop, plus up to
30 s more for a job that ignores SIGTERM. That is shorter than a Commit's start-up. To end it sooner, set
`VY_POOL_BORROW=0`.
