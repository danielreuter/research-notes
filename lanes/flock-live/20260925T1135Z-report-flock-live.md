---
lane: flock-live
kind: report
created: 2026-09-25T11:35Z
status: open
---

CHECKPOINT 767115db (11:39Z) [open] Read spec+harnesses (art:4cc09936, art:4e0271fe inputs). Finding: Flock-CUDA b684b12 prove path uses only the HOST FsChallenger (zc_challenger_device.cuh is bench/test-only) + grind_pow_device, so R6 = host live hook. Next: LiveChallenger/Replay crate patch, CPU pod.
CHECKPOINT 767115db (11:35Z) [open] Lane up on cloud VM. Reading red-team-flock spec (R1-R8, 10 negatives); plan: CPU pod for R1/R2-R5/R7-R8/negatives, H100 for R6. Code branch lane/flock-live (or cursor/* fallback).
