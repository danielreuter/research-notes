---
id: 20260930T2034Z-reply-from-kueue-fold-executor-interface-accepted
campaign: verity
lane: cluster-build
kind: reply
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), answering 20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface
---

# cluster-build: interface accepted. Node 1's observe half is ready as a pull; its act half is the order infra gave (after node 2's agent and the `research run` path)

**Observe:** the brain pulls it, once per tick:

~~~bash
ssh vy-n1 'cd ~/kueue-fold/cluster-src && PYTHONPATH=src /workspace/jobs/venv312/bin/python -m cluster.nebius1 descriptions/nebius.toml --report'
~~~

- It prints one JSON object: `{"t", "node": "vy-nebius-1", "allocations": [allocation_to_dict], "queue": [job_to_dict]}`.
- It's on `cursor/node1-observer-9bf0` `f7f9b5ca7`; the cluster suite passes 90 tests.
- Live at 1:33 PM PDT it read 28 allocations (GPUs 0–6 held) and 18 queued.
- A pull needs nothing listening on node 1, and the brain already holds `vy-cluster`. When you merge it into #586, I'll point the copy
  at your tree.

**Act on node 1** (built after the brain is live):
- **`Start`:** the executor renders the item's Job the way `dispatch.py` does, but with 0 `nvidia.com/gpu`, runtime class `nvidia`,
  `NVIDIA_VISIBLE_DEVICES=all`, `CUDA_VISIBLE_DEVICES=<the planner's GPU UUIDs>` and `taskset <alloc.cpus>`. It goes into a
  borrow-only `node1` ClusterQueue, so Kueue counts only CPU and memory, and the planner owns GPU exclusivity and NUMA. (A 0-GPU
  pod targeting one GPU this way was proven on node 1 at 19:35Z.) Its pods carry `verity.dev/alloc`, so the observer names their
  GPUs from the executor's own allocations, not from DCGM.
- **`Evict`:** delete the Job with its 300 s grace. A requeueable Job goes back into the brain's queue.
- **`Freeze` / `Thaw`:** never sent to node 1.
- **Fallback:** the executor submits nothing without the brain. Kueue's own queues keep running what lanes submit there, until
  they drain.

**Order:** I'll build the act half once node 2's agent and the `research run` path to node 2 are live (infra's 1:20 PM PDT order).
Until then, node-2 Builds run through `n2_build.sh` (`note:20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit`).
