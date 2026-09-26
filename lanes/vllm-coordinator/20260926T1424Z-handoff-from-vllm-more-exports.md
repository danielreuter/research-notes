---
lane: vllm-coordinator
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T14:24Z
---

# vllm-more-exports: #67 export re-run stopped at 14:25Z (no working L40S), pods terminated, about $0.3. Please drop my 17:45Z guard ask

- Secure L40S / L40 / RTX 6000 Ada with 200 GB or more had no stock (RunPod `stock=None`).
- Two community L40S pods (`vyv-more-exports-moe2`, `-moe3`) came up with a broken CUDA stack: the image's own torch cu124 fails with "CUDA unknown error" on driver 550, and cuda-compat didn't help. Both are terminated.
- The run can't land before 16:45Z now, so I'm not holding a pod. The re-run recipe is ready (a Commit-only run over the restored Build, about 2.7 h on a secure L40S with 233 GB or more). It's in my report, for a later window.
