---
lane: arith
kind: report
created: 2026-09-24T19:04Z
brief: campaigns/afternoon/BRIEF.md (### arith)
branch: lane/arith (worktree ~/projects/verity-main-wt/arith), base main@22741456
final: 01:10Z hard; budget $10
status: open
---

CHECKPOINT none (19:42Z) [open] step1 quad_v4+reduce kernel (lane/arith 9d1a7f15) bit-exact; micro quad_general 1.40->0.785ms, quad_p0 1.88->~1.25ms; base on pod: 4090 v3x4 p8 total .1014 arith .0481; A/B r20260924-194155-a3a0 running
CHECKPOINT 99a3b82 (19:10Z) [open] started; pod vy-arith (4090 EU-RO-1, 5q4d3ealzkud5d, guard 90) up, syncing worktree; next: bootstrap, profile tests graph of fp8-ada-v3x4 p8 baseline
# arith: hill-climb the arithmetic phase of B-Ligero

Inbox at startup: nothing new.

## Baseline (Table 2 / Table 3 at the 1800Z render, B-Ligero column, authentication excluded)
| target | cell art | config | t.total s | arithmetic s | overhead x |
|---|---|---|---|---|---|
| A100 BF16 | art:e1fcf643 | bf16-ampere-v3 fused l=16384 | 0.2413 | 0.164 | 6.0e6 |
| H100 BF16 | art:aadcd93f | bf16-hopper-v3x4 fused l=4096 | 0.1292 | 0.0799 | 1.0e7 |
| H100 E4M3 | art:85569708 | fp8-hopper-v3x4 fused l=4096 | 0.0738 | 0.0426 | 1.2e7 |
| 4090 E4M3 | art:fb4934af | fp8-ada-v3x4 fused l=4096 p8 | 0.0907 | 0.045 | 2.4e6 |
| 5090 NVFP4 | art:d5c9e1f3 | fp4-nvf4 l=8192 p8 | 0.0340 | 0.0222 | 4.5e6 |

## Pods
- vy-arith 5q4d3ealzkud5d: RTX 4090 reference part, SECURE EU-RO-1, 8 vCPU, host Ryzen 9 7950X, $0.74/h, created 19:10Z,
  `guard = 90` in machines.toml.

## Log
