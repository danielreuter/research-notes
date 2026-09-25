---
lane: agkr-bound
kind: handoff
from: flock-bench
created: 2026-09-25T09:46Z
---

# flock-bench results: Flock proves our 4,096-VU row leaves in BLAKE3 2.33 s / SHA-256 5.47 s (16-vCPU Zen4) and BLAKE3 0.29 s (Flock-CUDA 5090; zorch ~0.14 s extrapolated). Proofs are 0.3-0.5 MB and verify in 4-24 ms. The §3.8 link would add ~2x the hash proof on CPU; its O(N) verifier (0.7-1.4 s) dominates verify.

Report: `lanes/flock-bench/20260925T0805Z-report-flock-bench.md`. Copies of this note: `lanes/agkr-bound/`,
`lanes/b-ligero-standard-hash/`.

**Shape.** The frame-v3 row leaves of the frozen sets: an x row plus a W column per VU, K = 1536.
- `blake3-keyed/row/v2`: 48 compressions per leaf (BF16) or 24 (FP8).
- `sha256/row/v1`: 49 (BF16) or 25 (FP8).
- N = 4096 BF16 is 393,216 BLAKE3 or 401,408 SHA-256 compressions.
- Every row digest is checked against the reference crate before proving.
- Chaining wiring and public endpoints are not modelled (paper: IO glue under 5 %).

| hash, prec | platform | prove s, N = 64 / 1024 / 4096 | verify ms | proof KB (4096) | peak memory (4096) |
| --- | --- | --- | --- | --- | --- |
| BLAKE3 BF16 | CPU Zen4 16 vCPU (EPYC 4564P), 16T | 0.058 / 0.584 / **2.33** (1T 9.84) | 11-15 | 433 | 16.4 GiB heap |
| BLAKE3 FP8 | same | 0.043 / 0.305 / **1.15** (1T 5.19) | 11-13 | 418 | 8.0 GiB |
| SHA-256 BF16 | same | 0.128 / 1.22 / **5.47** (1T 22.8) | 13 | 479 | 30.2 GiB |
| SHA-256 FP8 | same | 0.076 / 0.641 / **2.55** (1T 11.6) | 12-17 | 449 | 17.2 GiB |
| BLAKE3 BF16 | CPU EPYC 9654 32 vCPU, 32T | 0.077 / 0.364 / **1.26** | 6-8 | 433 | 16.8 GB |
| BLAKE3 FP8 | same | 0.120 / 0.236 / **0.672** | 7-8 | 418 | 8.2 GB |
| BLAKE3 BF16 | RTX 5090, Flock-CUDA (m27 / m31 / m33) | 0.057 / 0.140 / **0.291** | 16-18 | 534 | device 15.6 GB |
| BLAKE3 FP8 | same (m26 / m30 / m32) | 0.105 / 0.107 / **0.096** | 14-18 | 518 | device 8.2 GB |
| BLAKE3 | RTX 5090, flock-zorch (m27 / m31) | 0.021 / 0.036 / (~0.14 extrapolated) | - | - | host 5.8 GB |

- SHA-256 costs 2.2-2.35x BLAKE3 per VU.
- Flock-CUDA's configs are hard-coded per m and are not monotone: FP8 4096 at m32 is faster than m31. There is no m29
  config.
- 5090 `clmad`: 1.00 T CLMAD/s; GF(2^128) mul 143 G/s. Driver 580 plus the CUDA 13.3 toolkit works.
- Artifacts:
  - CPU: art:aa24c7eb, art:59d7c080, art:0bd23b01.
  - Flock-CUDA: art:9be695b0.
  - zorch: art:1e54492e.
  - clmad: art:85d4fb7a.
  - GPU memory: art:3f5173a2.
  - link primitives: art:1ef9ac52.

**Link to a prime-field relation (survey §3.8), estimate only, not built.** This uses measured GF(2^128) primitives on
Zen4 16T for the 2.01e8 shared bits of BF16 N = 4096.
- Prover, per challenge point: about 0.51 s on CPU (eq expansion 1.98 ns/bit, dense 128-way combination 0.53 ns/bit).
  On GPU it is a few ms, derived from the 143 G/s mul rate, not run. 2^-128 needs 2 points: about 1.0 s on CPU.
- Verifier: O(N), about 0.72 s per point on CPU (about 30 ms with eq streamed), so 1.4 s for 2 points. That is 30-170x
  Flock's own verify.
- Prime side:
  - B-Ligero: +512 bit rows per BF16 unit (+14 %, about +0.04 s on 0.261 s bare).
  - A-GKR: +512/k elements per unit.
  - About 3.7k elements per point for the u_t commitment.
- Flock + link, BF16 N = 4096 on a 5090: 0.45-0.60 s, 1.7-2.3x B-Ligero bare, against the survey's ~2x. For agkr-bound
  on CPU, BLAKE3 2.33 s (16 vCPU) or 1.26 s (32 vCPU) plus about 1 s of link, against A-GKR's 54 s CPU prover: about
  4-6 %, the survey's 3-6 %.

**Survey vs measured (details in the report):**
- Holds: SHA about 2x BLAKE3; proof size; zorch (its README floor is beaten, 3.64 M/s); Flock + link about 2x on GPU.
- Optimistic by 1.5-2x: the CPU projections, "0.6 s on 32 cores" and "1.5 s on 12 threads".
- Now measured where the survey had nothing: the 5090 `clmad` rate and Flock-CUDA throughput.

Binary-backend (census unit) numbers: separate handoff "flock-bench: binary backend numbers" (09:45Z).
