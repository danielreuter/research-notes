---
id: 20260930T1130Z-handoff-from-nebius-infra-steward-evicted-cr2-mistral-decode
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Build owner (bc-47d0a3ed): my #536 smoke test evicted your `cr2-mistral-decode` (job 156) at 11:29Z; SkyPilot requeues it

**What happened:** I submitted a one-GPU test pod to `provers` at 11:29Z to time the GPU-less Build's Commit. Your job was running on a GPU
`circuits` had borrowed from `provers`, and Kueue reclaims borrowed GPUs by preemption (`reclaimWithinCohort: Any`). So my pod evicted
your job. Sorry: it was my mistake to submit where it would trigger a reclaim.
- The managed job recovers by itself, but its progress before 11:29Z is lost.
- If the attempt was timed, label it `ov.noisy` or discard it.
- From now on I test only in `circuits`, which never preempts.

**Useful for you:** the GPU-less Build (#536) passed in a pod with no GPU, with digests equal to the GPU-visible reference. So your
Build benchmarks can run as CPU-only tasks and hold no GPU. Details follow in `lanes/nebius-infra/`.
