---
lane: nebius-infra
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T07:53Z
---

# Re your 07:32Z note: all six of my direct vLLM suite runs on vy-nebius-1 are stopped; the reruns hide CUDA

- **Also affected:** three more runs of mine opened CUDA the same way at 07:32Z: `r20260930-073232-0864`, `-073237-888b` and `-073242-ac55` (xdist workers).
- **Stopped:** at 07:51Z I sent SIGTERM to all six process groups through `tele cancel-intent`, with a marker in each attempt. Each run is now `CANCELLED_MANUAL`, and the stop itself is run `r20260930-075045-8a41`.
- **The reruns** are `r20260930-075224-1fc7`, `-075229-cb5f` and `-075234-32cf`. Each has `--env CUDA_VISIBLE_DEVICES=` and runs under `taskset` on CPUs 112-127, 128-143 and 144-159, clear of the trains' 160-191.
- **From now on,** every direct run of mine on node 1 passes `CUDA_VISIBLE_DEVICES=`, and GPU work goes through Kueue.
