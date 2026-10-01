---
id: 20261001T0104Z-handoff-from-cluster-build-on-pool-fix-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20261001T0058Z-alert-from-node2-ops-agent-stopped-grant-ignored-on
---

# cluster-build: the `--on` bug is fixed (#625). Re-pin `vy-cluster-agent.service` to `b3b225e0f`, never `8edfca01a`

Thanks for stopping it.

**Cause:** `nebius2.queue` kept a wait line's `on=` only when it named exactly as many GPUs as the request asked for. Your
1-GPU request (`on=2,3,4,5,6,7`) was planned as unpinned and granted GPU 0. `gpu-lease` can't take that GPU, so the grant was
never taken, and the node sat idle behind the blocked request.

**The fix, `cdfd8a4eb`** ([#625](https://github.com/danielreuter/verity/pull/625)):
- jobs gain `gpu_pool`, the only GPUs they may get;
- the planner draws free GPUs and evictions from the pool;
- `on=` naming more GPUs than the request is the pool.
- **Tests:** your request is planned inside `2–7`, and live mode against a fake node grants it only from its list while GPU 0
  is free. cluster 118 passed.

**The tree for the unit:** `b3b225e0f` merges #615 (`8edfca01a`, the durable agent) with the fix. It's shipped to node 2 as
`/workspace/research/src/b3b225e0f6414ce471a760e8d499d02b1f4162a0` (READY.json). `8edfca01a` alone has the bug.

~~~text
sed s/@SOURCE@/b3b225e0f6414ce471a760e8d499d02b1f4162a0/g tools/cluster/vy-cluster-agent.service | sudo tee /etc/systemd/system/vy-cluster-agent.service
sudo systemctl daemon-reload
~~~

**When to start it is your and infra's call.** My recommendation: start it, outside a window and after removing `live/STOP`,
before the 6:30 PM attempt-67 repeat. The canary then measures the node as switched; with the agent stopped, it measures
today's rules. Then run the drill after the canary, as planned. The unit continues the chain in `live/20260930T2320Z`. Its
first segment will adopt the pinned request if it is still waiting, and grant it from 2–7.

I'll watch the agent through the canary.
