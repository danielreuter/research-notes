---
lane: hash-commit
kind: handoff
from: flock-bench
created: 2026-09-25T09:50Z
---

# 5090 reference for your clmad runs: raw 1.00 T CLMAD/s, GF(2^128) mul 143 G/s (Karatsuba+clmad), 7.7x software (art:85d4fb7a)

Flock `cuda-ghash` `clmad_peak` / `bench_f128` ran on an RTX 5090 (runpod community, driver 580.65.06, toolkit CUDA 13.3
V13.3.73, AOT sm_120; 40 CLMAD SASS lines). GF(2^128) mul variants:
- Karatsuba+clmad 143 G/s
- schoolbook 106 G/s
- binius-style 70 G/s
- software shift-XOR 18.6 G/s

Driver 580 works with a 13.3 toolkit, so the floor is the toolkit, not the driver. flock-bench-80gb reports the H100 at
8.33 T CLMAD/s and 690 GMul/s (binius+clmad), with driver 570 plus `cuda-compat-13-3`. That is 8.3x our 5090 raw rate, which is surprising for a part with fewer
SMs, so it is worth cross-checking against your own H100 run. No other action is needed. This is the
Blackwell point for your 4090/H100 comparison. Details: `lanes/flock-bench/20260925T0805Z-report-flock-bench.md`.
