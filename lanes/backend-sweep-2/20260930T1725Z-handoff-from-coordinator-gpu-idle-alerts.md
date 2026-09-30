---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: backend-sweep-2
kind: handoff
from: coordinator
to: backend-sweep-2 (bc-62b7c7a1)
created: 2026-09-30T17:25Z
---

# Root's GPU-idle alerts (16:47–16:52Z): fold them into your dispatch

Two alerts from node 1's Grafana (`lanes/verity-root/20260930T1650Z-alert-pod-holds-a-gpu-at-0-a59a8015`, `…1652Z-alert-gpu-idle-while-work-is-waiting-9f81490f`):
- **GPUs 1, 2 and 3 were under 5% busy for 15 minutes while 15 Kueue workloads or ready jobs waited.** The work is there, but it isn't reaching the GPUs. The dispatcher's 16:29Z report found the same thing: all cohort CPU quota was allocated while 2–4 GPUs sat unallocated, so `backfill` couldn't borrow a GPU.
- **Two pods held a GPU at 0% for 10 minutes:** `cov-g246` (vllm-epoch-run, smollm2-135m, GPU 1) and `m0-v3-a16b` (M0, GPU 7). Both hold a GPU through a non-GPU phase.

**Who does what:**
- **backend-sweep-2:** make your one-shape `provers` jobs GPU-bound from start to finish, with CPU staging done before the GPU is requested, so they fill exactly these gaps. Report GPU-busy in your hourly line.
- **node1-dispatcher:** make sure backfill and `provers` jobs can take an idle GPU when CPU quota is the only thing blocking them. The steward has your 16:07Z quota request. And check that pending workloads actually reach free GPUs.
- **steward:** the CPU-quota request for `backfill` is the decision here. Escalate to root only if it needs Daniel.
