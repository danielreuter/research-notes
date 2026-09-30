---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: node1-dispatcher
kind: handoff
from: coordinator (relaying root)
to: node1-dispatcher (bc-70706bc3); cc Kueue worker (bc-c445c55b)
created: 2026-09-30T15:36Z
---

# The dispatcher ships with a standing low-priority backfill tier (root, 15:34Z)

Root, relaying Daniel: the dispatcher is the permanent fix for idle GPUs, and it lands first, ahead of manual stopgaps. It's measured by node 1's GPU-busy % (DCGM, the steward's definition).

- **Backfill tier:** the dispatcher ships with a standing low-priority tier that any lane's work preempts cleanly. When a GPU has no lane work, the tier fills it automatically.
- **What fills it, in priority order:**
  1. invariance sweeps from `assumption-sweeps` (bc-5be66fb3; job list from red-team-vllm-semantics bc-05c0bb3e);
  2. then backend-sweep shapes (bc-ea1c2c4f with M0 bc-ff572e70; Llama-3.2-1B sm_120, one-shape jobs on M0's #554 build).
- **Preempting cleanly:** each backfill job is short, writes a labelled Attempt when it finishes, and requeues when preempted (exit 99), as in POUS's `fill_runner.py`.
- **Unchanged:** the CPU map (0–7 k3s; 8–95 the RC's three train-check slots) and the rule that quota or clock changes go through the nebius-infra steward (bc-fd19a2fe).
