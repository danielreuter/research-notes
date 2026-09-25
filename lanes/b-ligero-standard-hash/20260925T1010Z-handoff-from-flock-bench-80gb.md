---
lane: b-ligero-standard-hash
kind: handoff
from: flock-bench-80gb
created: 2026-09-25T10:10Z
---

# flock-bench-80gb: numbers. At 4,096 VUs, the binary backend (census unit + BLAKE3 leaves, Flock-CUDA) runs 3.1x B-Ligero bare on A100 BF16, 6.6x on H100 BF16 and 4.7x on H100 FP8. Its GPU kernel time alone is 1.0-1.2x bare on all three lines, so host glue and witness upload are the gap.

Full report: `lanes/flock-bench-80gb/20260925T0913Z-report-flock-bench-80gb.md`. Method is the same as flock-bench
(`lanes/coordinator/20260925T0945Z-handoff-from-flock-bench.md`, which has the 5090 and CPU column):
- the census unit is exported to a Flock GF(2) R1CS, bit-exact against verity.ml.tc;
- CPU runs prove one union of the unit table and the BLAKE3 row leaves;
- GPU runs make two separate Flock-CUDA proofs, with the unit witness built on the host and uploaded (flock-bench's port).

Every proof verified, and every tamper control was rejected. Flock b684b12, CUDA 13.3.

Flock-CUDA builds for sm_90 and sm_80 after one sed on `build.rs`, which only targets sm_120 upstream.

**Hardware (clmad, GF(2^128)):**

| | clmad | GF(2^128) mul |
|---|---|---|
| H100 | 8.4 T/s | 695 G/s |
| A100 | 3.9 T/s | 399 G/s |
| 5090 | 1.0 T/s | 143 G/s |

**At 4,096 VUs, in seconds (multiple of bare in parentheses):**

| line | B-Ligero bare | CPU, one union proof | GPU as shipped: unit + BLAKE3 | GPU without the H2D upload | GPU kernel time only (nsys) |
|---|---|---|---|---|---|
| A100 BF16 (ampere_bf16) | 0.2374 | 5.37 (22.6x), Zen2 host, 13 threads | 0.339 + 0.406 = 0.745 (3.1x) | 0.59 (2.5x) | 0.082 + 0.162 = 0.244 (1.03x) |
| H100 BF16 (hopper_bf16) | 0.1131 | 1.32 (11.6x), SPR host, 16 threads | 0.445 + 0.30 = 0.745 (6.6x) | 0.47 (4.2x) | 0.045 + 0.092 = 0.137 (1.2x) |
| H100 FP8 (hopper_e4m3) | 0.0706 | 0.74 (10.5x) | 0.232 + 0.098 = 0.330 (4.7x) | 0.20 (2.9x) | 0.024 + 0.047 = 0.071 (1.0x) |

Proofs are 0.40-0.53 MB. Verify takes 5-24 ms. Peak heap on the CPU union is 15-26 GB; GPU RSS is 0.8-2.2 GB.

**How to read it:**
- **Host-bound on every GPU.** BF16 wall time is about 0.75 s on both the A100 and the H100, even though their CLMAD
  rates differ by 2.1x and their kernel times by 1.8x. The 5090 comes in at about 0.55 s.
  - On the H100 at BLAKE3 m33: 0.31 s of wall against 0.092 s of kernels. The rest is cudaDeviceSynchronize and
    cudaMemcpy around host code.
  - The unit's 2.15 GB pageable upload costs 0.15-0.29 s.
- **The census's "~1x bare" holds only at the kernel floor.** Reaching it needs three things Flock-CUDA does not have:
  unit witness generation on the device, pinned or no upload, and no host glue. The census assumed 38.7 G slot-bit/s;
  end-to-end at m33 the measured rate is 28.6 G on the H100 and 21.2 G on the A100.
- **Same-SKU ratios.** Bare was measured on the same GPU SKU, unlike the 5090 against 4090 comparison.
- **Not modelled.** Chain glue and relation-hash region equality are left out, as in flock-bench, so these times are
  lower bounds.
- **The CPU column tracks the host.** The A100 pod's EPYC 7742 has no VPCLMULQDQ and is 2.8-3.9x slower than the
  H100 pod's Xeon 8468.
- **Still missing from Flock:** a GPU union prover, zero knowledge, and a fast Ligerito config at m29.

**Artifacts (all preserved):**

| art | what |
|---|---|
| art:7b941558 | H100 clmad and harness cross-check |
| art:8b4c35bf | H100 CPU sweep |
| art:876ab350 | H100 Flock-CUDA BLAKE3 and unit |
| art:b6148b4a | H100 nsys, BF16 |
| art:83f2d55d | H100 nsys, FP8 |
| art:2a541cd8 | A100 full line |
| art:2428284b | A100 nsys |

**Cost:** two pods, both terminated. About $3.2 total: H100 roughly 0.7 h at $3.49/h, A100 roughly 0.5 h at $1.59/h.
