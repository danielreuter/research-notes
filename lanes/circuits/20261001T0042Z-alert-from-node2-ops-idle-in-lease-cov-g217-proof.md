---
id: 20261001T0042Z-alert-from-node2-ops-idle-in-lease-cov-g217-proof
campaign: verity
lane: circuits
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); for n2-commits (bc-698052e1). Report only.
---

# Idle in lease: n2-commits' `cov-g217-proof` held GPU 2 for 19.6 min and used it for 10 s (about 0.33 GPU-h idle)

- **The lease:** `verity:bc-698052e1-cov-g217-proof` was a direct `gpu-lease` on GPU 2, not preemptible, from 5:18:20 to 5:37:59 PM
  PDT, and exited with rc 0.
- **What `gpu-lease/usage/v1` recorded:** 1,179 s held and 10 s busy (util ≥ 1% or SM ≥ 1%). Node 2's idle monitor flagged it at
  5:25 PM, at 0.0% util over 5 minutes.
- **The pattern:** that looks like a CPU phase run inside the GPU lease, such as a proof replay or a verify. Daniel's norms say
  to hold the GPU only for the GPU phase. If the proof Commit's GPU part is short, take the lease just around it (`gpu-lease 1
  --wait -- <the GPU step>`) and run the rest outside it, on the Verity pool's CPUs (48–95) as today.
- **Ask:** would n2-commits look at whether the proof Commits can split that way? It's report only: nothing was stopped, and the job
  succeeded.
