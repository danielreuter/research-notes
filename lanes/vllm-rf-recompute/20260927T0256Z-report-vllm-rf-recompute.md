---
lane: vllm-rf-recompute
kind: report
created: 2026-09-27T02:56Z
status: open
---

CHECKPOINT 3040ac1f (03:04Z) [open] plan: FP8 #74 = new ScaledMmFp8BlockSharedScale_v1 (products once per (weight block,kb) in a tile node, committed; same signature), Gemma #57 = Build emits AddScalarBf16 once per norm weight (selector), both default-off; checker reproduces #74 on VM (508 gates at K=N=256); branches cursor/vllm-rf-recompute-{fp8,gemma}-cbba off main 3040ac1f
CHECKPOINT fa662029 (02:56Z) [open] started 02:57Z agent bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba; reading cross-call-check handoff + #98 tree; CPU only, no pods
