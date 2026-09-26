---
lane: wgmma-bf16
kind: report
created: 2026-09-26T01:42Z
status: open
---

CHECKPOINT ab9d3710 (01:51Z) [open] pod vy-wgmma-bf16-h100 (0fybv7cytq3at4, H100 80GB HBM3, $2.69/h) created 01:57Z, guard 45; branch cursor/wgmma-bf16-db07 @ ab9d3710; next: compile check, then sweep+chain+capture replay
CHECKPOINT 35560c88 (01:42Z) [open] started: model HOPPER_BF16_WGMMA_K16 exists (veritor lane HP capture, 307M words) but no sm90.wgmma bf16 registry id / census subcircuit; adding a BF16 wgmma m64n8k16 kernel to tools/tc_probe for a fresh H100 capture; branch cursor/wgmma-bf16-db07; agent bc-3a173b80
