---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: nebius-infra (steward bc-fd19a2fe) · kind: handoff · from: vllm-coordinator · created: 2026-09-30T19:09Z · Daniel 19:06Z

**The goal: node 1's GPUs permanently full of vLLM Commits.**
1. **GPU queue ordering by engine key** (my 16:09Z design) now matters: epoch-run submits about 130 Commit-only jobs soon, then a grid of about 740 deployments.
2. **CPU queue:** Builds and deferred replays. If Daniel approves node 2's spare CPU (asked of infra), add it as a CPU-only flavor for these jobs, on POUS's terms (frozen in PoUW windows, cgroup, preempted first).
3. **The three-task template** (build → commit → replay) goes live as soon as the TP2 lane's PR A/B are on a branch. Default new coverage submissions to it.
