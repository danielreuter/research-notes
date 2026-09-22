---
id: r20-proof/hash-gpu/20260922T0554Z-report-hash-gpu
campaign: r20-proof
lane: hash-gpu
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/hash_gpu.md
---

# hash-gpu: measured GPU Merkle-commitment rates on an RTX 4090 (2026-09-22)

**Scope: component.** Proof-internal Merkle commitment hashing only (leaf = hash of one Ligero codeword column, tree over
the columns). Every "overhead" below is `explore.tensor`'s cost model with exactly one input -- the assumed hash rate --
replaced by a measurement. Nothing here is a proof. Verity's external commitments (`verity.commitments.merkle`) are unchanged.

Device: NVIDIA GeForce RTX 4090 (128 SMs, 24 GB GDDR6X, 1,008 GB/s), driver 580.159.04, CUDA runtime 12.9, torch 2.4.1+cu124,
cupy 14.2.0. Recorded run `r20260922-054241-b966` (`research run --on vy-g2`, tree `dd01419`); CUDA-event timings, warm,
median of 5. Data: `notes-asset:campaigns/r20-proof/assets/hash-gpu/reports/hash_gpu.json` (this directory), raw `backends/shared/hash_gpu/results_r20260922-054241-b966.json`.
Every GPU hash is bit-exact against a CPU reference (`hashlib`, the `blake3` package, a Python Poseidon2 matching Plonky3's
test vectors) in `backends/shared/hash_gpu/tests`.

## Full-tree rates at the campaign's Ligero shapes (B = 4096, K = 1536, BabyBear, 2^-128; N = 16,384 columns)

Candidate B commits 310,602 rows (20.36 GB hashed per batch = 4.97 MB/VU; 1.24 MB per leaf); Candidate A 48,873 rows (3.20 GB).

| hash (leaf function) | B: tree GB/s | B: ms/batch | B: us/VU | A: tree GB/s | A: ms/batch | peak dev. mem (B) |
|---|---|---|---|---|---|---|
| SHA-256 (sequential over column) | **446** | 45.6 | 11.1 | 425 | 7.5 | 19.6 GiB |
| SHA-256, chunked leaf (1 KiB sub-chunks + SHA tree) | **624** | 32.6 | 8.0 | 603 | 5.3 | 21.1 GiB |
| Blake3 (spec chunk tree) | **359** | 56.6 | 13.8 | 347 | 9.2 | 20.6 GiB |
| Poseidon2/BabyBear w16, fused CUDA | **57.7** | 352.6 | 86 | 55.5 | 57.8 | 21.3 GiB |
| Poseidon2/BabyBear w24, fused CUDA | 34.2 | 595.9 | 146 | 33.0 | 97.0 | 21.3 GiB |
| Poseidon2 w16, torch int64 elementwise (`blocks`) | 0.38 | 53,050* | 12,950 | 0.36 | 8,974* | -- |
| Poseidon2 w16, torch INT8-limb tensor-core MDS (`_int_mm`) | 0.27 | 76,400* | 18,660 | 0.25 | 12,640* | -- |

\* torch rows measured on a 1,024-column slice of the same rows and scaled x16 (labelled `scaled_from_columns` in the JSON).
Leaf-hash time is >= 98% of tree time at these shapes (the 16,384-leaf tree is negligible). Peak memory includes the 20.36 GB
input matrix itself; the trees add < 1 GiB.

Generic trees (32-byte leaves, 2^20 .. 2^27 leaves; tree-dominated): SHA-256 146 GB/s / 4.6 G leaves/s, Blake3 87 GB/s / 2.7 G
leaves/s, Poseidon2-16 24-27 GB/s / 0.75-0.86 G leaves/s, Poseidon2-24 15 GB/s / 0.47 G leaves/s at 2^27 (14.5 GiB in use).
Poseidon2 permutation throughput (fused CUDA, 2^22 states): w16 1.68 G perm/s, w24 0.97 G perm/s.

## Re-pricing (`reprice.py`; utilisation 0.172, `rs_matrix_ntt`, overhead vs the GPU's native peak)

| design | hash rate | GPU | hash share of time | overhead |
|---|---|---|---|---|
| B | assumed 50 GB/s (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor) | H100 | 70.4% | 1.43e7 |
| B | SHA-256 446 GB/s measured | RTX 4090 | 9.3% | 1.22e7 |
| B | SHA-256 x3.32 = 1,484 GB/s, **bandwidth SCALING** | H100 | 7.4% | 4.6e6 |
| B | Blake3 359 GB/s measured | RTX 4090 | 11.3% | 1.25e7 |
| B | Poseidon2-16 57.7 GB/s measured | RTX 4090 | 44.1% | 1.98e7 |
| B | Poseidon2-16 x3.32 = 192 GB/s, **bandwidth SCALING** | H100 | 38.3% | 6.9e6 |
| A | assumed 50 GB/s (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor) | H100 | 14.9% | 1.07e7 |
| A | SHA-256 425 GB/s measured | RTX 4090 | 1.1% | 1.74e7 |
| A | SHA-256 x3.32, **bandwidth SCALING** | H100 | 0.6% | 9.2e6 |
| A | Poseidon2-16 55.5 GB/s measured | RTX 4090 | 7.7% | 1.86e7 |

The A100/H100 rows multiply the 4090 rate by the HBM/GDDR bandwidth ratio (2,039/1,008 = 2.02; 3,350/1,008 = 3.32). The SHA-256
and Blake3 kernels are SIMT-compute-bound (they hash 20 GB in 46 ms, well under the 4090's 1 TB/s), so this scaling is an
upper bound for them, not a measurement.

## What changed

* **B is no longer a hashing problem with SHA-256/Blake3 leaves.** At the measured 446 GB/s the hash bucket is 9% of B's time on
  the 4090 (was 70% of the H100 model at 50 GB/s); B's time is matmul (86%). The 4090 SHA-256 number is 9x the assumed rate and
  2.3x TensorZKP's implied 192 GB/s on H100.
* **Poseidon2 does not get there.** The best Poseidon2 (fused CUDA, Montgomery, width 16) is 58 GB/s -- hashing is 44% of B on the
  4090 -- and would need > 200 GB/s to leave the picture. If the leaves must be algebraic (recursion / in-circuit verification,
  see `authentication.py`), hashing stays B's bucket. Width 24 is 1.7x slower than width 16 for a 2:1 compression.
* **Tensor-core Poseidon2 loses.** The INT8-limb `torch._int_mm` MDS is 2x slower than the int64 elementwise MDS (8.6 ms vs
  4.4 ms per 2^20 width-16 states, MDS only) and the whole torch permutation is 100-200x slower than the fused kernel: limb
  split / recombine and the deferred reduction cost more than the 16x16 multiply they replace, and the S-box and reductions
  run as separate elementwise kernels either way. Not a breakthrough.
* **Openings (deliverable 5, computed, not measured):** `Tree.open` / `Tree.opening_bytes` exist and are tested. For B a
  column is 1.24 MB plus 14 x 32 B of path, so 200-600 openings are 248-745 MB per batch = 61-182 kB/VU; for A (195 kB per
  column) 39-117 MB per batch. B's proof size is the columns, not the paths; the gather is < 1 ms of bandwidth.

Ledger: `backends/reports/ledger/hash-gpu.jsonl` (3 component entries; SHA-256 flagged `--breakthrough` for the picture flip above).
