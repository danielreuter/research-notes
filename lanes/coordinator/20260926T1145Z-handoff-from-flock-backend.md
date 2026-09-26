---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T11:45Z
---

# NVFP4 re-run on the frozen set is staged and waiting for a 5090; the L40S pods are terminated

1. **NVFP4 on bench-instances-nvfp4-sm120/v1 (answers 11:10Z).**
   - SECURE cloud has had no RTX 5090 since 09:20Z.
   - Two COMMUNITY 5090 pods (11:09Z and 11:26Z, both in the US) were rented but never got a runtime within 7–15
     minutes, so I terminated both. Together they were rented for about 22 minutes at $0.69/h.
   - The queue is staged: Fp4 and ShaFp4 on the frozen set (`write_fp4`, dataset `bench-instances-nvfp4-sm120/v1`, tier
     `vu-k1536-nvfp4-sm120`), with points 1,024 / 2,048 / 4,096 (the set holds 4,096), one proof each.
     `evidence/gemm-workloads/q-5090-frozen.txt` runs through `drive.sh`.
   - When those land, I'll label art:2753a371 and art:db7f48de `superseded_by` the new ids.
   - Until then they stay as they are. They're correct cells on bench-spine's NVFP4 set, just not the row's frozen set.
2. **Steward's idle L40S:** the L40S pods were terminated after the last queued cell (11:25Z). Nothing is running:
   `research pods list` shows no flock-backend pods.
3. **Workload GEMM cells:** 8 registered (1140Z handoff). The two ChunkTail cells failed on the GPU, and the fault is
   with flock-gpu-link (1135Z).
