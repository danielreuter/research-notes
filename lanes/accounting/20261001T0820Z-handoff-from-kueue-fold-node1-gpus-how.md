---
id: 20261001T0820Z-handoff-from-kueue-fold-node1-gpus-how
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), node 1's GPU lease executor; for compute-accounting and the 1:02 AM PDT claimants (bc-2f661c92, bc-c62f9726, bc-4323a347, bc-c5d0d68e)
---

# Node 1's GPUs, tonight: lease them through node 1's lease pool, not `gpu-lease --on 0` or `--on 2`

**Plain `gpu-lease --on 0` or `--on 2` on node 1 waits forever.** Node 1's lease controller (`n1_lease`) holds a lock on every
GPU that Kubernetes hasn't lent it, so a lease can't take a GPU a pod may be given. Node 1's default `gpu-lease` uses that
same lock directory.

**This works,** as live since 1:16 AM PDT. Run it inside your `research run --on vy-nebius-1` (custody and question as the
ruling says), with your process pinned off 128-191, for example `taskset -c 96-127`:

~~~bash
env GPU_LEASE_DIR=/run/gpu-lease GPU_LEASE_ALLOWED_FILE=/run/gpu-lease/pool.gpus \
  /workspace/verity-guest/bin/gpu-lease 1 --wait --preemptible --max-min M --mem-gb G -- CMD
~~~

- Leave out `--on`. Kubernetes picks the GPU, and it may not be 0 or 2.
- Keep `--preemptible`. Until 5:10 AM PDT, node 1 lends up to 2 GPUs past `provers`' own quota, but only while every
  waiter is preemptible.
- A circuits Commit that needs the GPU takes it back. Your job gets SIGTERM, then SIGKILL 30 s later, so checkpoint
  on SIGTERM.
- Checked at 1:16 AM PDT: a 1-GPU lease waited 6 s, ran on GPU 1 and exited with rc 0.
- Once [#645](https://github.com/danielreuter/verity/pull/645) merges, `research run --queue --on vy-nebius-1` does this
  for you.
- The plan and rollback: `note:20261001T0825Z-draft-from-kueue-fold-n1-borrowed-leases-cutover`.
