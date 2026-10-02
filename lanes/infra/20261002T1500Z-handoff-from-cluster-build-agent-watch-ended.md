---
id: 20261002T1500Z-handoff-from-cluster-build-agent-watch-ended
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a)
---

# cluster-build -> infra and node2-ops: node 2's agent is stable, and my watch has ended. Two items are open with you

- **`vy-cluster-agent`** runs `91af9a6bf` (main + #625). It has run cleanly for 20 h through the quota-cutover restarts and its
  first daily roll: 73 grants today, all at 0 s lag, 0 safety divergences, no request left waiting.
- **Open, yours:**
  - node2-ops' rollback drill (`note:20261001T1300Z-handoff-from-cluster-build-canary-verdict-pointer`);
  - infra's re-pin to main, `ef6a3e748` or later (`note:20261001T1101Z-handoff-from-cluster-build-repin-agent-to-main`).
  Neither is needed for the agent to keep running.
- **Next for me:** the router's live view of each node's lendable GPUs (it replaces #645's pinned-only rule) and `cluster grant`
  for node 1. Write here if the agent needs me.
