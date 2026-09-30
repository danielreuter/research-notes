---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-netlist
kind: handoff
from: coordinator
to: backend-sweep lane (bc-ea1c2c4f) and M0 (bc-ff572e70)
created: 2026-09-30T15:25Z
---

# Action 1: resume the backend sweep on node 1's `provers` queue as its GPU backfill

Root dispatched this at 15:19Z from the GPU-utilization postmortem, `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/gpu-utilization-postmortem.md` (top table).

- **Goal:** prove one whole passing sm_120 config, shape by shape, with the current prover. The per-shape runner (#182, #212) was drained for the epoch and never resumed.
- **First step:** cut the shape list of Llama-3.2-1B's passing sm_120 config and submit its first 20 shapes as one-shape Kueue jobs on `provers`, on M0's #554 build, with `ov.noisy=true`. Check the first shape's selftest and byte identity before queueing the rest. M0's pinned benches keep priority over the sweep.
- **Owners:** backend-sweep lane (bc-ea1c2c4f), with M0 (bc-ff572e70) for the prover build.
- **Queue:** the new `node1-dispatcher` lane (bc-70706bc3) will keep it queued once its loop runs.
