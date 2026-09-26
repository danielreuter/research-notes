---
lane: wgmma-bf16
kind: report
created: 2026-09-26T01:42Z
status: open
---

CHECKPOINT e3ddc7e0 (02:01Z) [open] first pair r20260926-015601-b530 (SS) / -015605-bc89 (RS): sweep 26.36M + chain4 2.88M + veritor replay 44,046, 0 mismatches vs hopper_bf16_wgmma_k16 each (Ampere control misses 3.15M); only failure a replay-bookkeeping false alarm (fixed e3ddc7e0); clean re-runs launched
CHECKPOINT ab9d3710 (01:51Z) [open] pod vy-wgmma-bf16-h100 (0fybv7cytq3at4, H100 80GB HBM3, $2.69/h) created 01:57Z, guard 45; branch cursor/wgmma-bf16-db07 @ ab9d3710; next: compile check, then sweep+chain+capture replay
CHECKPOINT 35560c88 (01:42Z) [open] started: model HOPPER_BF16_WGMMA_K16 exists (veritor lane HP capture, 307M words) but no sm90.wgmma bf16 registry id / census subcircuit; adding a BF16 wgmma m64n8k16 kernel to tools/tc_probe for a fresh H100 capture; branch cursor/wgmma-bf16-db07; agent bc-3a173b80
