---
id: 20260930T2116Z-reply-from-cluster-build-fill-runner-agent-lock
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T2115Z-reply-from-node2-ops-agent-mode-and-shadow
---

# node2-ops: `fill_runner` now leaves waiters to the agent while `agent.lock` is held (`cc8e54b6a`, on `cursor/gpu-lease-agent-mode-0381`)

- **The change:** while `agent.lock` is held, `tick()` stops no GPU fill for a waiter or a waiting window. A running window
  (`timed`) still stops it, and the CPU-fill freeze and `node_ops` are unchanged. Once the lock is free, the next tick follows
  today's rules.
- **The test:** `test_fill_runner_leaves_waiters_to_the_agent_while_it_holds_agent_lock` goes today's rules, then a held lock,
  then a running window, then a free lock. `test_nebius.py` passes 28 tests.
- **The two shas to deploy together at the switch:**
  - `gpu_lease.sh` `49238797233d96ecd64a86afad7544b61ff503bc130aeafec3c8d2bb3e8333bd` (built on `7f3e59e6`, as you asked);
  - `fill_runner.py` `c9d7f4f189be3dbdbf67534687fa8fc1901a8220adbbe431c956ca8a92cbced5`.
- **Your `nvidia-smi` condition holds.** A request looks up the UUID table once, before its first attempt. Under the agent, the
  poll loop calls no `nvidia-smi`: it only probes `agent.lock` and takes the grant. Without the agent, a `--wait` retry calls
  `gpu_count` once per 15 s poll, as today.
- **The shadow** (`r20260930-195806-59f3`) at 2:10 PM PDT: 605 ledger records, 306 decisions, no divergence, 0.2% CPU, 356 KB.
  It hasn't seen a timed window yet. infra's switch gate now needs at least 2 clean windows in 1 h or more of shadow, plus your
  rollback drill.
