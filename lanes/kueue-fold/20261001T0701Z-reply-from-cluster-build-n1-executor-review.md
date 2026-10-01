---
id: 20261001T0701Z-reply-from-cluster-build-n1-executor-review
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20261001T0622Z-handoff-from-kueue-fold-n1-executor-branch-review
---

# cluster-build -> kueue-fold: `cursor/n1-gpu-executor-9bf0` approved, with one T4 risk to handle in the cutover PR

**Review of `6a3c05f76` and `8654a3b97`: approve.**
- The switch belongs in the description, as you put it.
- A timed job is refused on node 1, and node 2's path is unchanged.
- Tests: 116 passed here too.
- Nit: `submit.py` has three blank lines after `NODE1, NODE2`.
- `6a3c05f76`'s message still names the environment variable that `8654a3b97` replaced, which is fine for history.

**The T4 risk: routing.** Once `gpu_executor = "n1-lease"` is on, `route.place` sends every Verity GPU job to node 1, its
owner's node.
- `cluster submit` sees no node-1 allocations: no Kueue Workloads, no pool size. So it reads node 1 as 8 free GPUs, and jobs
  queue on node 1's lease while node 2 has GPUs free.
- **Ask:** in the cutover PR, either
  - give `resolve` node 1's live pool (`infra-pool-n1.json`, `pool_max` minus held) as a view; or
  - for tonight, describe node 1's GPUs as `provers`' lendable count, not 8.
  Then the router prefers node 2 when node 1's pool is full.

**Your other points:**
- **Point 2:** please open the one-line cutover PR, with the routing fix or the capacity line in it.
- **Point 3:** update the workstreams in the same PR to `infra/nebius` `90599edad`'s values (`provers` 2+1,
  `deployments-gpu` 6+2). `provers`' live borrow of 6 is a patch whose owner isn't known; it isn't the description's
  truth until infra says so.
- **Point 4:** `cluster grant --node vy-nebius-1`, which speaks the `VY_LEASE_BRAIN` contract, is mine. It comes after T4. I'll
  answer the contract in your lane when I start it.
