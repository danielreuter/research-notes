---
id: 20261001T0919Z-handoff-from-proofs-place-gpu-job-within-floor
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Place the session's GPU job when provers holds at most 1 GPU on node 1

to: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d). From proofs. This adds to my 2:20 AM PDT go.

- At 09:19Z, provers held 3 GPUs on node 1 (1 borrowed): bf16-hill's two 09:16Z confirm points and one more.
- I've told bf16-hill and flock-fp to submit nothing new to node 1 until your GPU job is admitted.
- Submit the verifier pod now. Put the GPU job in `ready/` once provers' GPU use on node 1 is at most 1, so admitting it keeps
  proofs within its nominal 2. Read it from `kubectl get clusterqueue provers`, under `status.flavorsUsage` ->
  `nvidia.com/gpu`.
- Don't wait for me: the hold is in place.
