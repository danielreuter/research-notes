---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: node1-dispatcher
kind: handoff
from: coordinator (relaying root)
to: node1-dispatcher (bc-70706bc3); cc Kueue worker (bc-c445c55b)
created: 2026-09-30T16:10Z
---

# Design for a GPU-only queue and a CPU queue; and "cell" is now "vLLM deployment"

**Terminology (Daniel, via root 16:08Z):** what we've been calling a "cell" is a **vLLM deployment**. Use "vLLM deployment" in new notes, code, labels you choose and reports from now on. Existing identifiers (for example `vyv-cov-`, `row run`) stay as they are.

**Two queues (Daniel approved):** the vLLM coordinator (bc-ecac3029) is splitting GPU generation from CPU checking into separate queues. Design the dispatcher for both:
- **GPU-only queue:** GPU generation work only. A job holds its GPU only for its GPU phase, so no GPU sits allocated through a CPU Build, bootstrap or check. That was the 47% "allocated, no memory held" loss in the postmortem.
- **CPU queue:** CPU checking and Builds, on node 1's non-slot CPUs. Keep off 0–7 (k3s) and 8–95 (the RC's train-check slots). Take the core range from the nebius-infra steward.
- **Backfill:** each queue keeps its own low-priority, cleanly preemptible backfill tier. The GPU tier is invariance sweeps (`assumption-sweeps`), then backend-sweep shapes, per the 15:36Z handoff.
- **Measures:** GPU-busy % for the GPU queue and CPU-busy % for the CPU queue.
- **First step:** agree the job boundary with the vLLM coordinator: what each vLLM deployment submits to each queue, and how the CPU check learns the GPU generation is done.
