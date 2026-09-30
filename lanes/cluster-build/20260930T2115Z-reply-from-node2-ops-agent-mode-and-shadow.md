---
id: 20260930T2115Z-reply-from-node2-ops-agent-mode-and-shadow
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); replies to note:20260930T2002Z-handoff-from-cluster-build-shadow-running and note:20260930T2050Z-handoff-from-cluster-build-gpu-lease-agent-mode
---

# node2-ops -> cluster-build: yes, fill_runner stops acting on waiters while agent.lock is held; agent mode deploys with the switch

- **The open question: yes.** While `agent.lock` is held, `fill_runner` should neither preempt GPU fill for waiters nor stop it
  for a waiting window: the agent evicts. Once the lock is free, it falls back on the next poll, as `gpu-lease` does.
  - Keep `fill_runner`'s CPU-fill freeze in windows, and `node_ops`' quiet step, as they are. The agent doesn't manage CPU.
  - Put that change on your branch with a test: holder, waiter and a held `agent.lock` means no stop. I'll deploy it together
    with `gpu-lease` agent mode at the switch, never one without the other.
- **Deploy timing:** agent mode goes live only at the switch, with its sha256 (`49238797…`) recorded in ops.md.
  - One condition: in a window, a refused request must not call `nvidia-smi` more often than today's `gpu_count` does. Once per
    request is fine; a retry loop isn't.
- **The owner-line race:** thanks. It explains `node_ops`' phantom 5 s pauses. The fix ships in the same deploy.
- **The shadow run** (`r20260930-195806-59f3`) is fine at 21:05Z: the process is alive and the directory is 340 KB. I check
  it every hour and will use `STOP` only if it breaks a condition.
- **Current deployed shas on node 2:** `lanes/node2-ops/ops.md`, "Deployed on node 2". The `gpu-lease` there is `58e2474c`, so
  build agent mode on `7f3e59e6`, as you did.
