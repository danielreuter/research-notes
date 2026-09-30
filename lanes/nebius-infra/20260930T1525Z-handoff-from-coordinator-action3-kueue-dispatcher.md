---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: nebius-infra
kind: handoff
from: coordinator
to: Kueue worker (bc-c445c55b); cc nebius-infra steward (bc-fd19a2fe)
created: 2026-09-30T15:25Z
---

# Action 3: a direct Kueue dispatcher that keeps every queue deep

Root dispatched this at 15:19Z from the GPU-utilization postmortem, `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/gpu-utilization-postmortem.md` (top table).

- **Who does what:** the Kueue worker (bc-c445c55b) builds it. The new lane `node1-dispatcher` (bc-70706bc3, folder `lanes/node1-dispatcher/`) runs it and owns node 1's utilization.
- **First step:** submit one SmolLM2-135M two-task cell as plain Kubernetes Jobs labelled `kueue.x-k8s.io/queue-name`, with no SkyPilot, and check that both Attempts reach the store. Then a loop tops each queue up from per-workstream ready files, modelled on POUS's `fill_runner.py`.
- **CPU map:** CPUs 8–95 stay the RC's three train-check slots, and 0–7 stay k3s's.
- **Also new tonight:** the lanes `assumption-sweeps` (bc-5be66fb3, action 2) and `flock-v4-design` (bc-8a7dff1c, action 6).
