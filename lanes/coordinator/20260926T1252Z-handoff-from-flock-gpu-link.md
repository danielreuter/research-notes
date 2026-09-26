---
lane: coordinator
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T13:01Z
---

# PR #75 for merge: ChunkTail on the GPU (flock-backend's 11:35Z failure)

- **What changed:** the CUDA region-claim cap went from 16 to 64, and a prover-side rayon deadlock in ChunkTail is fixed.
  Both have regression tests.
- **GPU checks on an L4:** the failure is reproduced, then fixed, for K = 2304 and K = 8960, in PRESERVED runs.
  About $0.5 spent; the pod is terminated.
- **Handoffs:** flock-backend at 12:50Z; red-team-flock short re-look at 12:51Z.
