---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: infra (infra coordinator bc-17cc41f1) · kind: handoff (ask) · from: vllm-coordinator · created: 2026-09-30T19:09Z · Daniel 19:06Z: maximum vLLM deployment coverage, GPU idle not acceptable

**vLLM coverage is CPU-bound:** GPU Commits starve waiting for CPU Builds, and the grid grows to about 740 deployments.

**Ask 1, node 2's spare CPU and RAM** for vLLM Builds and replays.
- POUS said yes at 19:08Z on its terms (`lanes/infra/20260930T1908Z-reply-from-pouw-node2-spare-capacity-and-metrics.md`): CPU and RAM only, frozen in PoUW's timed windows, cgroup-capped, preempted first. We accept those terms.
- The SSH runner is an access change needing **Daniel's explicit yes**. Please bring it to him, or tell me you have it.
- **What we'd run there:** Builds (16–32 vCPU and 32–192 GB each, sized per deployment) and the CPU replays of deferred Commits, from a CPU-only queue. The Nebius steward (bc-fd19a2fe) owns the templates.

**Ask 2, only if node 2 isn't enough: an extra Nebius CPU VM.** **Not approved:** it goes to Daniel through root as a question. I'm not requesting it now.

Tell me the vCPU and RAM we can use on node 2, and from when.
