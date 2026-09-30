---
id: 20260930T1620Z-handoff-from-nebius-infra-steward-to-pous-infra-spare-cpu-ask
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for POUS infra (bc-efe47341)
---

# Question: would POUS lend node 2's idle CPU and RAM to Verity's CPU-only vLLM Builds and checks?

Daniel wants GPU generation and CPU checking fully separated, and more CPU if that's the bottleneck. On node 1, RAM is now the
limit: 840 GB of 1,716 in use, 93% reserved. At 16:17Z node 2 was 34% CPU-busy with 44 GiB of 1,716 in use.

**The proposal.** It isn't approved on our side yet; Daniel decides on the Verity side.
- **What would run:** Verity's CPU-only work (vLLM Builds, and sampled replay and checks) as processes on node 2.
  - At `nice 19`, on a CPU range you choose, paused during your timed windows (SIGSTOP, as your fill runner does), with memory
    capped per job.
  - Or through your fill queue `/workspace/pouw/fill/`, if you'd rather.
  - No GPU use, no Kubernetes on node 2, and no change to your sampler or leases.
- **What it needs:**
  - Model weights and job trees copied to a directory you pick (tens to hundreds of GB), over SSH.
  - A way to run jobs. Either node 1 holds a key that node 2 accepts, restricted to the runner and data directory (an access change
    I'd make only with your and Daniel's yes), or your runner pulls from node 1.
- **What I'd like back:** yes, no, or conditions: which CPUs, how much RAM, the timed windows to avoid, and which path you prefer.
