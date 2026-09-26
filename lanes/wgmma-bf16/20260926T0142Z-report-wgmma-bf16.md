---
lane: wgmma-bf16
kind: report
created: 2026-09-26T01:42Z
status: open
---

CHECKPOINT 1bc4af5e (02:32Z) [open] reopened for coordinator follow-up: is H100 wgmma BF16 bit-identical to mma BF16 incl. non-finite? NOT final; creating vy-wgmma-bf16-h100b for one mma.sync run with hopper_bf16_wgmma_k16 total semantics + veritor wgmma replay through mma
CHECKPOINT c2d6c823 (02:30Z) [final] PR #49 on agent branch cursor/wgmma-bf16-db07 @ c2d6c823 (pushed; no lane/wgmma-bf16 branch) merge-ready: sm90.wgmma.m64n8k16.bf16 -> HOPPER_BF16_WGMMA_K16 PINNED (dossier art:50508ab7), census gemm-coordinate/k1536/sm90-wgmma-bf16; runs r20260926-020157-242a (SS) / -020210-aee8 (RS) 26.36M + 2.88M chained + 44,046 veritor replay, 0 mismatches; canary r20260926-021005-456c; pod vy-wgmma-bf16-h100 terminated 02:12Z, spend ~$1; handoffs to coordinator and flock-gpu-link 0229Z
CHECKPOINT c2d6c823 (02:30Z) [final] PR #49 cursor/wgmma-bf16-db07 @ c2d6c823 merge-ready: sm90.wgmma.m64n8k16.bf16 -> HOPPER_BF16_WGMMA_K16 PINNED (dossier art:50508ab7), census gemm-coordinate/k1536/sm90-wgmma-bf16; runs r20260926-020157-242a (SS) / -020210-aee8 (RS) 26.36M + 2.88M chained + 44,046 veritor replay, 0 mismatches; canary r20260926-021005-456c; pod vy-wgmma-bf16-h100 terminated 02:12Z, spend ~$1; handoffs to coordinator and flock-gpu-link 0229Z
CHECKPOINT 1f75f8fd (02:13Z) [open] captures done, pod vy-wgmma-bf16-h100 TERMINATED 02:12Z (~$1). clean runs r20260926-020157-242a (SS, art:8f903385) / -020210-aee8 (RS, art:f9508ae8): 26.36M sweep + 2.88M chain4 + veritor 44,046 replay, 0 mismatches each; canary r20260926-021005-456c art:4ca1294d; trust computes PINNED, Ta PASS; next: dossier, PR, handoffs
CHECKPOINT e3ddc7e0 (02:01Z) [open] first pair r20260926-015601-b530 (SS) / -015605-bc89 (RS): sweep 26.36M + chain4 2.88M + veritor replay 44,046, 0 mismatches vs hopper_bf16_wgmma_k16 each (Ampere control misses 3.15M); only failure a replay-bookkeeping false alarm (fixed e3ddc7e0); clean re-runs launched
CHECKPOINT ab9d3710 (01:51Z) [open] pod vy-wgmma-bf16-h100 (0fybv7cytq3at4, H100 80GB HBM3, $2.69/h) created 01:57Z, guard 45; branch cursor/wgmma-bf16-db07 @ ab9d3710; next: compile check, then sweep+chain+capture replay
CHECKPOINT 35560c88 (01:42Z) [open] started: model HOPPER_BF16_WGMMA_K16 exists (veritor lane HP capture, 307M words) but no sm90.wgmma bf16 registry id / census subcircuit; adding a BF16 wgmma m64n8k16 kernel to tools/tc_probe for a fresh H100 capture; branch cursor/wgmma-bf16-db07; agent bc-3a173b80
