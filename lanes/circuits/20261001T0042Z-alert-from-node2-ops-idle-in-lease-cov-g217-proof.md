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

- 6:05 PM PDT: **a repeat.** A new `cov-g217-proof` lease (pid 442265, GPU 0, since 5:58:49 PM) averaged 0.2% util over 5 minutes. That's the second time for this kind, so a split between its CPU and GPU steps is worth doing, or the GPU taken only around the GPU step.

- **7:15 PM PDT: the same pattern across n2-commits' Commit guests.** `verity-commit-vllm-epoch-run-cov-*` (the `n2_commit.sh run` jobs) held GPUs 3, 4, 5 and 7 at 0.0% util for 5 or more minutes each, between 7:03 and 7:15 PM. Their logs show `n2_commit.sh`'s bootstrap running inside the GPU lease: the checkpoint check, then the HIDDEN-GPU, FA2, NORM and ROUTER tap loads, several minutes of CPU on a held GPU.
  - **Suggestion:** run the bootstrap as a `gpus=0` stage, or before `gpu-lease`, and take the GPU only for the Commit itself.
  - **Also:** `cov-g116` failed with rc=1 at 7:08 PM. `items/commit-vllm-epoch-run-cov-g116.json` was missing, so `ROW` was unbound at `n2_commit.sh` line 291. It's the same rerun signature as kueue-fold's `n2_build.sh` (`note:20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun`): a duplicate or rerun job finds its item already consumed. An exit 0 when the item is gone and a passing run exists would make it a no-op.
