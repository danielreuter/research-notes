---
id: r20-proof/latency/20260922T1111Z-report-latency
campaign: r20-proof
lane: latency
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/latency.md
---

# End-to-end latency: design x RTT (lane latency, 2026-09-22)

Model: `t.e2e = t.prove + t.verify + depth x RTT + bytes / bandwidth` per batch (`verity_numerical.bench.latency`; the
protocol is interactive, note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction 3.3, so every critical-path verifier message is one round trip). Every row
carries its proof class and hardware; CPU rows are measured (vy-cpu2 shared with b-lookup and checker-min), GPU rows are
re-priced kernels with the CPU verifier's time (an assumption). Pipelining: `N_sat = ceil(t.e2e / t.prove)` batches in
flight saturate the prover if `N_sat x mem_per_batch` fits; otherwise memory binds.

## 1. Serial end-to-end latency per batch (s), link 25 Gb/s

| design | B | proof class | hardware | prove s | verify s | depth | bytes | rtt 0 ms | rtt 0.1 ms | rtt 1 ms | rtt 10 ms | rtt 50 ms | network share @50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | 4096 | NON_ZK_PROOF_DIAGNOSTIC | AMD EPYC 9654 96-Core Processor | 261 | 25.2 | 355 | 69.8 MB | 286 | 286 | 286 | 290 | 304 | 6% |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | 4096 | NON_ZK_PROOF_DIAGNOSTIC | AMD EPYC 9654 (vy-cpu2, 12 of 32 threads, shared with b-lookup and checker-min) | 319 | 45.0 | 355 | 33.5 MB | 364 | 364 | 365 | 368 | 382 | 5% |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | 4096 | ARITHMETIC_DIAGNOSTIC (re-pricing) | RTX 4090 24 GB | 0.866 | 45.0 | 355 | 36.1 MB | 45.9 | 45.9 | 46.2 | 49.4 | 63.6 | 28% |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | 4096 | ARITHMETIC_DIAGNOSTIC (re-pricing + verifier assumption) | RTX 4090 24 GB | 0.866 | 1.00 | 355 | 36.1 MB | 1.88 | 1.91 | 2.23 | 5.43 | 19.6 | 90% |
| A-GPU BabyBear^6, a-gpu2 prover (r20260922-094040-9e76, tree 5ad05fb, Python-verified) + independent Rust verifier (a-verifier-2, r20260922-105647-c947) | 4096 | MEASURED prover + MEASURED independent verifier | H100 80 GB + EPYC 9654 (vy-cpu2, 12 of 32 threads, shared) | 1.79 | 1.00 | 438 | 33.9 MB | 2.8 | 2.84 | 3.24 | 7.18 | 24.7 | 89% |
| A-GPU BabyBear^6, a-gpu recorded 4.43 s row (not Rust-verified from a committed tree; note:r20-proof/a-verifier-2/20260922T1054Z-finding-f1-triage) + Rust verifier | 4096 | MEASURED prover (unverified row) + MEASURED verifier | H100 80 GB + EPYC 9654 (vy-cpu2, 12 threads) | 4.43 | 1.00 | 438 | 33.9 MB | 5.44 | 5.48 | 5.88 | 9.82 | 27.3 | 80% |
| A-GPU BabyBear^6, torch path (`VERITY_GPU_TORCH_ONLY=1`, Rust-verified) + Rust verifier | 4096 | MEASURED prover + MEASURED independent verifier | H100 80 GB + EPYC 9654 (vy-cpu2, 12 threads) | 25.5 | 1.00 | 438 | 33.9 MB | 26.5 | 26.5 | 26.9 | 30.9 | 48.4 | 45% |
| A-GPU re-priced (H100 packed sumcheck, model) | 4096 | ARITHMETIC_DIAGNOSTIC (model) | H100 80 GB | 0.430 | 45.0 | 355 | 36.1 MB | 45.4 | 45.5 | 45.8 | 49.0 | 63.2 | 28% |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 4096 | NON_ZK_PROOF_DIAGNOSTIC | AMD EPYC 9654 96-Core Processor | 184 | 0.148 | 22 | 3.2 MB | 184 | 184 | 184 | 184 | 185 | 1% |
| B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 4096 | ARITHMETIC_DIAGNOSTIC (re-pricing, HVZK rows) | RTX 4090 24 GB | 0.259 | 0.400 | 3 | 240.1 MB | 0.736 | 0.736 | 0.739 | 0.766 | 0.886 | 17% |
| SP1 core (Fiat-Shamir, one VU per proof) | 1 | NON_ZK_PROOF (authentication included) | RTX 4090 (vy-sp1), SP1 6.4.0 cuda | 3.58 | 0.245 | 1 | 5.9 MB | 3.83 | 3.83 | 3.83 | 3.84 | 3.88 | 1% |
| C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 4096 | COMPLETE_ZK_BACKEND (designated-verifier) | AMD EPYC 9655P (vy-cpu, 1 thread) | 1673 | 1673 | 3 | 36.2 GB | 3357 | 3357 | 3357 | 3357 | 3357 | 0% |
| C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 4096 | cost model (designated-verifier) | H100 80 GB | 0.123 | 0.123 | 3 | 36.2 GB | 11.8 | 11.8 | 11.8 | 11.8 | 12.0 | 1% |

## 2. Bandwidth sensitivity: transfer time per batch (s) and the link speed at which transfer equals prover compute

| design | bytes / batch | 10 Gb/s | 25 Gb/s | 100 Gb/s | Gb/s for transfer = prove | bandwidth-bound below |
|---|---|---|---|---|---|---|
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | 69.8 MB | 0.056 | 0.022 | 0.006 | 0.00 | no |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | 33.5 MB | 0.027 | 0.011 | 0.003 | 0.00 | no |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | 36.1 MB | 0.029 | 0.012 | 0.003 | 0.33 | no |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | 36.1 MB | 0.029 | 0.012 | 0.003 | 0.33 | no |
| A-GPU re-priced (H100 packed sumcheck, model) | 36.1 MB | 0.029 | 0.012 | 0.003 | 0.67 | no |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 3.2 MB | 0.003 | 0.001 | 0.000 | 0.00 | no |
| B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 240.1 MB | 0.192 | 0.077 | 0.019 | 7.42 | no |
| SP1 core (Fiat-Shamir, one VU per proof) | 5.9 MB | 0.005 | 0.002 | 0.000 | 0.01 | no |
| C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 36.2 GB | 28.9 | 11.6 | 2.89 | 0.17 | no |
| C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 36.2 GB | 28.9 | 11.6 | 2.89 | 2352.25 | yes at [10.0, 25.0, 100.0] |

## 3. Pipelining: in-flight batches to saturate the prover, memory, resulting VU/s and overhead (link 25 Gb/s)

| design | mem / batch | capacity | N_sat @ 0 ms (mem, fits?) | N_sat @ 0.1 ms (mem, fits?) | N_sat @ 1 ms (mem, fits?) | N_sat @ 10 ms (mem, fits?) | N_sat @ 50 ms (mem, fits?) | VU/s @ 0 / 10 / 50 ms | overhead @ 0 / 10 / 50 ms | binding @ 50 ms | memory binds above RTT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | 33.9 GB | 256.0 GB | 2 (67.8 GB, yes) | 2 (67.8 GB, yes) | 2 (67.8 GB, yes) | 2 (67.8 GB, yes) | 2 (67.8 GB, yes) | 15.7 / 15.7 / 15.7 | 6.47e+09 / 6.47e+09 / 6.47e+09 | prover compute | 4337.01 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | 25.7 GB | 256.0 GB | 2 (51.4 GB, yes) | 2 (51.4 GB, yes) | 2 (51.4 GB, yes) | 2 (51.4 GB, yes) | 2 (51.4 GB, yes) | 12.8 / 12.8 / 12.8 | 7.92e+09 / 7.92e+09 / 7.92e+09 | prover compute | 7068.70 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | 18.6 GB | 24.0 GB | 53 (985.8 GB, NO) | 54 (1004.4 GB, NO) | 54 (1004.4 GB, NO) | 58 (1078.8 GB, NO) | 74 (1376.4 GB, NO) | 89.3 / 82.9 / 64.4 | 1.14e+09 / 1.23e+09 / 1.58e+09 | memory (cannot hold N_saturate batches) | 0.00 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | 18.6 GB | 24.0 GB | 3 (55.8 GB, NO) | 3 (55.8 GB, NO) | 3 (55.8 GB, NO) | 7 (130.2 GB, NO) | 23 (427.8 GB, NO) | 2.18e+03 / 755 / 209 | 4.66e+07 / 1.35e+08 / 4.87e+08 | memory (cannot hold N_saturate batches) | 0.00 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | 18.6 GB | 80.0 GB | 106 (1971.6 GB, NO) | 106 (1971.6 GB, NO) | 107 (1990.2 GB, NO) | 114 (2120.4 GB, NO) | 147 (2734.2 GB, NO) | 91 / 91 / 91 | 1.12e+09 / 1.12e+09 / 1.12e+09 | memory (cannot hold N_saturate batches) | 0.00 ms |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 59.8 GB | 256.0 GB | 2 (119.6 GB, yes) | 2 (119.6 GB, yes) | 2 (119.6 GB, yes) | 2 (119.6 GB, yes) | 2 (119.6 GB, yes) | 22.3 / 22.3 / 22.3 | 4.56e+09 / 4.56e+09 / 4.56e+09 | prover compute | 25052.00 ms |
| B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 22.1 GB | 24.0 GB | 3 (66.4 GB, NO) | 3 (66.4 GB, NO) | 3 (66.4 GB, NO) | 3 (66.4 GB, NO) | 4 (88.5 GB, NO) | 5.57e+03 / 5.35e+03 / 4.62e+03 | 1.82e+07 / 1.90e+07 / 2.20e+07 | memory (cannot hold N_saturate batches) | 0.00 ms |
| SP1 core (Fiat-Shamir, one VU per proof) | 9.9 GB | 24.0 GB | 2 (19.9 GB, yes) | 2 (19.9 GB, yes) | 2 (19.9 GB, yes) | 2 (19.9 GB, yes) | 2 (19.9 GB, yes) | 0.279 / 0.279 / 0.279 | 3.64e+11 / 3.64e+11 / 3.64e+11 | prover compute | 3333.11 ms |
| C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 1.4 GB | 128.0 GB | 3 (4.2 GB, yes) | 3 (4.2 GB, yes) | 3 (4.2 GB, yes) | 3 (4.2 GB, yes) | 3 (4.2 GB, yes) | 2.45 / 2.45 / 2.45 | 4.15e+10 / 4.15e+10 / 4.15e+10 | prover compute | 49616656.25 ms |
| C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 35.1 GB | 80.0 GB | 97 (3408.9 GB, NO) | 97 (3408.9 GB, NO) | 97 (3408.9 GB, NO) | 97 (3408.9 GB, NO) | 98 (3444.1 GB, NO) | 693 / 691 / 684 | 1.47e+08 / 1.47e+08 / 1.48e+08 | memory (cannot hold N_saturate batches) | 0.00 ms |

## 4. Crossovers: the RTT above which the shallower design has the lower serial e2e (link 25 Gb/s)

| deeper | shallower | e2e @ 0 ms deeper / shallower | crossover RTT |
|---|---|---|---|
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 286 / 184 | shallower already faster at 0 ms |
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 286 / 0.736 | shallower already faster at 0 ms |
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | SP1 core (Fiat-Shamir, one VU per proof) | 286 / 3.83 | shallower already faster at 0 ms |
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 286 / 3357 | 8.72e+03 ms |
| A-CPU Goldilocks^3 (GKR+logUp+Ligero) | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 286 / 11.8 | shallower already faster at 0 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 364 / 184 | shallower already faster at 0 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 364 / 0.736 | shallower already faster at 0 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | SP1 core (Fiat-Shamir, one VU per proof) | 364 / 3.83 | shallower already faster at 0 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 364 / 3357 | 8.5e+03 ms |
| A-CPU BabyBear^6 (GKR+logUp+Ligero) | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 364 / 11.8 | shallower already faster at 0 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 45.9 / 184 | 415 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 45.9 / 0.736 | shallower already faster at 0 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | SP1 core (Fiat-Shamir, one VU per proof) | 45.9 / 3.83 | shallower already faster at 0 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 45.9 / 3357 | 9.41e+03 ms |
| A-GPU re-priced (4090 fused SIMT sumcheck, BabyBear^6) | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 45.9 / 11.8 | shallower already faster at 0 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 1.88 / 184 | 547 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 1.88 / 0.736 | shallower already faster at 0 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | SP1 core (Fiat-Shamir, one VU per proof) | 1.88 / 3.83 | 5.51 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 1.88 / 3357 | 9.53e+03 ms |
| A-GPU re-priced (4090 fused SIMT) with a hypothetical 1 s verifier | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 1.88 / 11.8 | 28.2 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | 45.4 / 184 | 416 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 45.4 / 0.736 | shallower already faster at 0 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | SP1 core (Fiat-Shamir, one VU per proof) | 45.4 / 3.83 | shallower already faster at 0 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 45.4 / 3357 | 9.41e+03 ms |
| A-GPU re-priced (H100 packed sumcheck, model) | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 45.4 / 11.8 | shallower already faster at 0 ms |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | B-Ligero GPU re-priced (4090, BabyBear, helper columns) | 184 / 0.736 | shallower already faster at 0 ms |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | SP1 core (Fiat-Shamir, one VU per proof) | 184 / 3.83 | shallower already faster at 0 ms |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | 184 / 3357 | 1.67e+05 ms |
| B-CPU AIR (Plonky3 uni-stark FRI, Goldilocks^2) | C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | 184 / 11.8 | shallower already faster at 0 ms |
| B-Ligero GPU re-priced (4090, BabyBear, helper columns) | SP1 core (Fiat-Shamir, one VU per proof) | 0.736 / 3.83 | 1.55e+03 ms |
| C QuickSilver CPU (dietmc F61p, 2^-36 sensitivity point) | SP1 core (Fiat-Shamir, one VU per proof) | 3357 / 3.83 | shallower already faster at 0 ms |
| C QuickSilver GPU model (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor 3.05e6 overhead) | SP1 core (Fiat-Shamir, one VU per proof) | 11.8 / 3.83 | shallower already faster at 0 ms |

## 5. Measured vs model (the `--rtt-ms` runs on vy-cpu2)

| run | design | B | RTT ms | depth (measured trips) | legacy depth | t.total s (compute) | verify s | sleep s | e2e measured s | model (same run's compute) | predicted from the RTT-0 run | predicted / measured |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260922-072400-3993 | verity-gkr | 64 | 0 | 214 | 234 | 6.19 | 0.525 | -0.000 | 6.72 | 6.72 | 6.72 | 1.000 |
| r20260922-073027-abc0 | verity-gkr | 64 | 10 | 214 | 234 | 6.98 | 0.642 | 2.16 | 9.78 | 9.76 | 8.86 | 0.906 |
| r20260922-073131-bfd0 | verity-gkr | 64 | 50 | 214 | 234 | 7.20 | 0.526 | 10.7 | 18.4 | 18.4 | 17.4 | 0.944 |
| r20260922-073236-36c2 | verity-direct (plonky3 uni-stark) | 64 | 0 | 16 | 18 | 3.09 | 0.143 | 0.000 | 3.23 | 3.23 | 3.23 | 1.000 |
| r20260922-074151-4bf1 | verity-direct (plonky3 uni-stark) | 64 | 10 | 16 | 18 | 3.17 | 0.143 | 0.161 | 3.47 | 3.47 | 3.39 | 0.976 |
| r20260922-074228-5f7b | verity-direct (plonky3 uni-stark) | 64 | 50 | 16 | 18 | 3.04 | 0.143 | 0.802 | 3.98 | 3.98 | 4.03 | 1.012 |
| r20260922-074606-be7b | verity-gkr | 4096 | 0 | 355 | 381 | 261 | 25.2 | 0.000 | 286 | 286 | 286 | 1.000 |
| r20260922-075211-dc70 | verity-gkr | 4096 | 10 | 355 | 381 | 260 | 25.5 | 3.57 | 289 | 289 | 290 | 1.002 |
| r20260922-075743-78b5 | verity-gkr | 4096 | 50 | 355 | 381 | 258 | 25.3 | 17.8 | 301 | 301 | 304 | 1.010 |
| r20260922-080317-58e1 | verity-direct (plonky3 uni-stark) | 4096 | 0 | 22 | 24 | 184 | 0.148 | -0.000 | 184 | 184 | 184 | 1.000 |
| r20260922-080658-b587 | verity-direct (plonky3 uni-stark) | 4096 | 10 | 22 | 24 | 185 | 0.150 | 0.221 | 185 | 185 | 184 | 0.994 |
| r20260922-081039-71a5 | verity-direct (plonky3 uni-stark) | 4096 | 50 | 22 | 24 | 189 | 0.149 | 1.10 | 191 | 191 | 185 | 0.971 |

The sleep column is the measured wall-clock minus compute minus verify: `depth x RTT` to within the sleep overshoot (~0.1 ms per
trip). The last column is the honest test -- the RTT-0 run's compute plus `depth x RTT` against the wall-clock measured at
that RTT in a separate run; the residual is prover-compute drift on the shared box, not the network term.

## 6. Depth-reduction options for A (costed, not implemented)

| option | depth | prover work x | committed +% | e2e @ 10 ms (CPU / GPU) | e2e @ 50 ms (CPU / GPU) | RTT where it beats the baseline (GPU) | note |
|---|---|---|---|---|---|---|---|
| baseline (b): data-parallel units, query wires committed, c = 1 | 355 | 1 | +0.0 | 290 / 49.4 | 304 / 63.6 | never (deeper) | measured critical path |
| R16 sharding s = 1 (2^1 tables) | 329 | 1 | +0.0 | 289 / 49.2 | 302 / 62.3 | 0.00178 ms | +65,536 multiplicities; 2x the R16 transcript (+0.1 MB) |
| R16 sharding s = 2 (2^2 tables) | 304 | 1 | +0.1 | 289 / 48.9 | 301 / 61.1 | 0.00272 ms | +196,608 multiplicities; 4x the R16 transcript (+0.3 MB) |
| R16 sharding s = 5 (2^5 tables) | 235 | 1.002 | +1.1 | 289 / 48.2 | 298 / 57.6 | 0.0119 ms | +2,031,616 multiplicities; 32x the R16 transcript (+3.1 MB) |
| c = 2 variables per message | 199 | 1.62 | +0.0 | 512 / 48.4 | 520 / 56.4 | 3.44 ms | pads x2.5; sumcheck rounds send (d+1)^c - 1 values |
| c = 3 variables per message | 147 | 3.687 | +0.0 | 1259 / 49.7 | 1265 / 55.5 | 11.2 ms | pads x7.0; sumcheck rounds send (d+1)^c - 1 values |
| c = 2 + sharding s = 5 | 135 | 1.622 | +1.1 | 512 / 47.8 | 517 / 53.2 | 2.45 ms | PROTOCOL.md 5.4 'both' |
| cut the R16 tree at levels [20] [proposal] | 214 | 1.01 | +6.8 | 290 / 48.0 | 299 / 56.6 | 0.063 ms | commit p_l, q_l at the cut levels (12.6M elements); 2 more Ligero functionals; pieces run in parallel |
| cut the R16 tree at levels [16, 21] [proposal] | 200 | 1.021 | +14.1 | 293 / 47.9 | 301 / 55.9 | 0.118 ms | commit p_l, q_l at the cut levels (26.0M elements); 4 more Ligero functionals; pieces run in parallel |
| cut the R16 tree at levels [13, 17, 20, 22, 24] [proposal] | 200 | 1.217 | +144.5 | 337 / 48.1 | 345 / 56.1 | 1.21 ms | commit p_l, q_l at the cut levels (265.9M elements); 10 more Ligero functionals; pieces run in parallel |
| cut the tree at [16, 21] + commit depth>=3 checker wires (32/unit) [proposal] | 140 | 1.031 | +20.9 | 295 / 47.3 | 300 / 52.9 | 0.126 ms | checker chain halves too: the two levers that reach ~140 without extra sumcheck work |
| hint-free branch (query wires not committed; 5 layers after the lookups) | 520 | 0.895 | -30.0 | 265 / 51.0 | 286 / 71.8 | below 0.551 ms only | note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction 4: prover 0.94x, committed -30%, depth ~630 by the derived counter |
| checkpoints every m = 2 units (sub-chain as a deep circuit) | 386 | 1.5 | -0.2 | 420 / 50.2 | 436 / 65.6 | never (deeper) | PROTOCOL.md 12.4: checker depth x~2, wire evaluations x2: deeper AND slower at every RTT |
| checkpoints every m = 4 units (sub-chain as a deep circuit) | 746 | 2.5 | -0.1 | 685 / 54.6 | 715 / 84.5 | never (deeper) | PROTOCOL.md 12.4: checker depth x~4, wire evaluations x4: deeper AND slower at every RTT |

**Note on the B-Ligero verifier time (lane b-verifier, 2026-09-22).** The `verify s` of the B-Ligero row is the
Python/torch verifier on GPU hardware (0.40 s re-priced; 1.03 s measured on the L40S for the 25-sub-batch 4096-VU ZK
set). An independent Rust verifier (`backends/ligero-verify`, CPU only, no torch) verifies the same 25 proofs in
8.3-16 s at 1 thread / 5.9-6.7 s at 12 threads on `vy-cpu3` (EPYC 7713, contended container) and 3.4 s / 1.3 s (1 / 8
threads) on an idle laptop -- other hardware, so this is a note, not a replacement of the row; the row's serial e2e
would read 6-16 s with a CPU verifier of that speed. Details: `note:r20-proof/b-verifier/20260922T1132Z-report-b-verifier` section 3.

## 7. Reading the tables

**What the depth is.** `rounds.sequential_depth` is now *measured*: A counts `Transcript::round_trip()` at every
critical-path verifier message (the logUp `(mu, lambda)` pair is one message, so the derived counter's 381 is 355; the
lock-step instances -- 9 tables, 2 segments -- share their messages, only the longest chain counts), B counts every
`observe -> sample` boundary of the prover's Plonky3 challenger (22 at 2^19 rows, 16 at 2^13; the derived `log_n + 5`
over-counted by 2). Both provers sleep one RTT at each such boundary under `--rtt-ms`, so `t.e2e.rtt_<x>ms` in the
envelopes is wall-clock with the emulated link and `t.total` is the compute with the sleep subtracted.

**Serial e2e (section 1).** At 50 ms every design's network term is `depth x 0.05 s`: A 17.8 s, B-AIR 1.1 s, B-Ligero
0.15 s, SP1 0.05 s, C 0.15 s. On the CPU provers that is noise for A (261 s of compute) and for B-AIR (183 s); on the GPU
re-pricings it is the whole story for A: 0.87 s of kernels behind 17.8 s of waiting (plus the 45 s CPU verifier, which is
the honest serial number until a GPU verifier or deferred checks exist -- the table says so per row). B-Ligero at 0.26 s
compute + 0.15 s network + 0.4 s verify stays under a second at 50 ms; its 240 MB of opened columns cost 0.08 s at 25 Gb/s.
C is bandwidth-bound: 35 GB per batch of 4096 VUs needs ~2.3 Tb/s to hide behind 0.12 s of GPU compute (section 2).

The row *A-GPU with a hypothetical 1 s verifier* isolates the network term: 1.9 s at 0 ms, 5.4 s at 10 ms, 19.6 s at
50 ms -- 90% of the batch's wall-clock is waiting for coins.

**Pipelining (section 3).** `N_sat` is how many batches the prover must hold to keep busy. With the real (45 s CPU)
verifier A-GPU is verifier-bound at ~90 VU/s whatever the RTT. With the 1 s verifier it needs 3 batches in flight at
0-1 ms, 7 at 10 ms, 23 at 50 ms, at 18.6 GB each (phase-1 tables 15.6 GB + codeword store 3.0 GB): one 24 GB card holds
one batch, so memory binds at every RTT and A's throughput on a 4090 is one batch per e2e -- 2,200 VU/s at 0 ms, 750 at
10 ms, 210 at 50 ms (overhead 4.7e7 -> 4.9e8). B-Ligero needs 3-4 batches (22 GB each with the codeword store kept):
also more than one card holds, but its e2e is 0.74-0.89 s, so one batch per e2e is still 4,600-5,600 VU/s; the
re-encode-on-demand store (note:r20-proof/b-commit/20260922T0733Z-report-b-measured-4090, 5.6 GB) would fit 4 batches and remove the bind. The CPU rows saturate
at N = 2 (A: 68 GB, B-AIR: 120 GB of 256 GB) at every RTT up to 50 ms: compute-bound; memory binds only above
4.3 s (A) / 25 s (B) of RTT.

**Crossovers (section 4).** B-AIR (CPU) and B-Ligero (GPU) are already faster than A at 0 ms on the same class of
hardware, so there is no A -> B crossover in the e2e sense: the shallower design wins everywhere and the gap grows by
`(355 - depth_B) x RTT` -- 17 s per batch at 50 ms. The crossovers that exist: A-GPU (1 s verifier) loses to SP1's
single-VU 3.8 s proof above 5.5 ms RTT and to the C GPU model above 28 ms; A-GPU beats B-CPU AIR up to 0.4-0.5 s of
RTT (the CPU prover's 183 s is the gap). Within A, the RTT above which a depth-reduction option pays its extra prover
work back (section 6, last column): sharding and the committed-cut proposals below 0.15 ms, `c = 2` above 3.4 ms,
`c = 3` above 11 ms.

**Can the verifier pre-commit all coins so the prover never waits? No.** The HM96 step-0 commitment hides the coins;
opening coin `i` must follow the prover's message `i` or the prover learns it early and soundness is gone. The round trip
is inherent to every coin that binds a prover message. **Can rounds be batched?** Yes, exactly when the prover's messages
for those rounds do not depend on each other's coins: (i) the 9 tables and 2 segments already share messages (lock-step);
(ii) the levels of the fractional tree and the layers of the checker are serial *only because* each level's claim is
produced by the previous level's sumcheck -- committing an intermediate level (`p_l`, `q_l` of the tree, or the wires of
a checker layer) makes the pieces above and below it independent given the commitment, so their rounds share round
trips. That is the `cut` family in section 6: 26M committed elements (+14%) cut the lookup chain 352 -> 137, and 32
committed wires per unit (+7%) cut the checker chain 197 -> 129; together depth 355 -> 140 at ~+3% GPU prover time.
(iii) `c` variables per message halves or thirds the rounds of every sumcheck at 2x / 5.3x the sumcheck work. The
checkpointed variant (PROTOCOL.md 12.4) is deeper *and* slower at every RTT -- it does not win under a latency objective
either. The hint-free branch is 6% cheaper but ~170 rounds deeper: it wins only below ~0.5 ms RTT on the GPU.

## 8. Update (a-verifier-2, 2026-09-22 ~11:00Z): the independent Rust verifier at 1.00 s

The "hypothetical 1 s verifier" row of section 1 is now a measured one: `backends/gkr/verifier` (the independent
BabyBear^6 verifier, no code shared with the prover) accepts the a-gpu B = 4096 proof in **1.00 s on 12 threads of
vy-cpu2** (1.00 / 1.03 s over two reps with the pod at load 33 of 32 cores; 10.3 s on one thread; 0.077 s at B = 64),
down from the a-verifier lane's 3.02 s (r20260922-093721-1330) and the 45 s Goldilocks-Rust / 7.1 s Python rows
above.  Per stage at 12 threads: parse 0.035, transcript replay 0.007, functional value 0.116, Merkle + proximity
0.024, Ligero linear test 0.81 (CPU: fill 4.5 s + NTT eval 4.9 s over 12 threads, 11.5x scaling).  The three new rows
of section 1 join it with the three prover records that exist: the a-gpu2 1.79 s H100 prover (Python-verified, its
tree not yet Rust-verified at B = 4096 -- `main` is Rust-verified at B <= 512 on the 4090, `note:r20-proof/a-verifier-2/20260922T1054Z-finding-f1-triage`), the
a-gpu 4.43 s recorded row, and the torch path.  With the 1.79 s prover the verifier is 36% of the 2.82 s e2e at RTT 0
(`backends/gkr/verifier/results_e2e_agpu2.json`; `results_e2e_kernel.json`, `results_e2e_torch.json` for the other
two); the network term (438 round trips) passes the compute at 6.4 ms RTT.  How the 3x came about, and what is left
(the verifier is now at the machine's throughput for the 4-transform linear test; the levers that remain are
algorithmic), in `note:r20-proof/a-verifier-2/20260922T1110Z-report-a-verifier-2`.
