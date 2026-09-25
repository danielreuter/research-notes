---
lane: flock-live
kind: report
created: 2026-09-25T11:35Z
status: open
---

CHECKPOINT a43f6254 (12:15Z) [open] R6 live on H100 works (run r20260925-120734-7e37): all live sessions accepted, 7 GPU live negatives rejected. 4096 VU pair live vs FS fast100x2: BF16 0.94 vs 0.77 s (1.23x), FP8 0.55 vs 0.40 s (1.39x), ~220 coin round trips/table. Rerunning with rayon=quota + wait timing. git push 403 (token expired), retrying.
CHECKPOINT 0fe756ef (11:55Z) [open] CPU live path works (run r20260925-115302-19e5): R1 root check, live coins, live forks, replay; honest accepted, all 19 negatives reject as specified; live/FS prove 1.03-1.07x at m28 loopback. Code lane/flock-live 6429f343+. Next: H100 R6 (CUDA host live hook patch written).
CHECKPOINT 767115db (11:39Z) [open] Read spec+harnesses (art:4cc09936, art:4e0271fe inputs). Finding: Flock-CUDA b684b12 prove path uses only the HOST FsChallenger (zc_challenger_device.cuh is bench/test-only) + grind_pow_device, so R6 = host live hook. Next: LiveChallenger/Replay crate patch, CPU pod.
CHECKPOINT 767115db (11:35Z) [open] Lane up on cloud VM. Reading red-team-flock spec (R1-R8, 10 negatives); plan: CPU pod for R1/R2-R5/R7-R8/negatives, H100 for R6. Code branch lane/flock-live (or cursor/* fallback).
