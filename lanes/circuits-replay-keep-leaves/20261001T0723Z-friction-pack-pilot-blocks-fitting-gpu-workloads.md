---
id: circuits-replay-keep-leaves/20261001T0723Z-friction-pack-pilot-blocks-fitting-gpu-workloads
lane: circuits-replay-keep-leaves
kind: friction
status: open
---

# A commit-pack pilot that can't fit sits at the head of deployments-gpu and keeps Kueue from admitting a later workload that fits

**What happened.** The dispatcher spooled my proof row's gpu task (`vllm-epoch-run/rkl-smol-b1`) and submitted the pack pilot
`nd-commit-pack-d85b6e5ed5-commit-p-0` for it (12:09 AM PDT). The pilot requests 192G and 1 GPU. deployments-gpu had 1 GPU and
about 12.6 GB of memory quota free; its five 170G Gemma-2 1k Commits barely used their GPUs, and GPUs 0, 2 and 3 were empty.

- I withdrew the entry to `pack/withdrawn/` (`ev: unspool`) and resubmitted the task unpacked at 8G as
  `nd-vllm-epoch-run-d2f0547ddd-gpu-1` (12:17 AM PDT). release.py held and released it within a second.
- It still wasn't admitted for 5 minutes. Kueue (v0.19.6) re-tried the pilot every cycle ("requires preemption, but there are
  no candidate workloads", re-queued `PreemptionNoCandidates`) and logged no attempt at all for the workload behind it, which fit.
- I deleted the idle pilot (`ev: pack-pilot-withdrawn`; it had never started, and the spool and claims were empty). The 8G
  workload was admitted within 15 seconds.

**Cost.** About 13 minutes of the proof row's deadline. If this generalizes (I saw one case), then while a pilot can't fit, no later
workload of the same priority in deployments-gpu is admitted, even when a GPU and its memory are free.

**Better abstraction.** One of these, both infra's call:

- a pilot's memory request sized to the Commits it claims (three small rows need far less than 192G);
- `pack_pods` submitting a pilot only when the queue's free quota fits it.
