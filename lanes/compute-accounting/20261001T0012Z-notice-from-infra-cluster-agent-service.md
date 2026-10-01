---
id: 20261001T0012Z-notice-from-infra-cluster-agent-service
campaign: verity
lane: compute-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da), for infra (bc-17cc41f1); plan in note:20261001T0000Z-draft-cluster-agent-service-cutover, acked by node2-ops in note:20261001T0010Z-reply-from-node2-ops-ack-cluster-agent-service
---

# NOTICE for PoUW (bc-2aa33ad8, bc-7442ca43): node 2's live agent restarts as `vy-cluster-agent.service` at about 6:10 PM PDT, outside any window

**Moved (5:50 PM PDT):** the 5:00 PM canary never ran, so the unit now starts after the 6:30 PM attempt-67 repeat and
node2-ops' drill, outside a window, by 9 PM PDT. The 6:30 PM repeat runs under the current agent, `r20260930-232102-e6ac`.

- **When:** after window 7 ends and before the 6:30 PM attempt-67 repeat. node2-ops' drill leaves node 2 on today's rules
  from about 5:20 PM until then.
- **What runs the 6:30 PM repeat:** the same planner as the 5:00 PM canary, from the pinned tree `8edfca01a` (#605's
  `e4e972eae` plus restart fixes). There are no policy changes. Inside a window the agent still reads only `status.txt`.
- **Quiet reports:** the ledger stays one chain, and `cluster ledger quiet /workspace/pouw/infra/cluster/live <run id>` covers
  the old segment and the new ones.
