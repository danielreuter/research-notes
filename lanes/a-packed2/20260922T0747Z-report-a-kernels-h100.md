---
id: r20-proof/a-packed2/20260922T0747Z-report-a-kernels-h100
campaign: r20-proof
lane: a-packed2
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_kernels_h100.md
---

# Candidate A re-priced with two measured GPU buckets (H100): checker sumcheck + logUp GKR

Lane `a-packed2` (track A, second pass on the GPU sumcheck kernels).  Machine `vy-g4`: NVIDIA H100 80GB HBM3 SXM,
torch 2.6.0+cu124, Triton 3.2.  Numbers: `notes-asset:campaigns/r20-proof/assets/a-packed2/reports/a_kernels_h100.json` (`backends/gkr/packed/reprice_a.py`).  Labels:
`ARITHMETIC_DIAGNOSTIC`, authentication excluded, security target 2^-128 (the priced operating point; nothing is proved),
B = 4096 VUs of K = 1536 per batch (393,216 transition units).  Supersedes `packed_sumcheck_h100.md` (one bucket measured).

## 1. Checker sumcheck, 32-bit Montgomery: the k-table before / after

The a-packed kernels reduced every Hadamard product and fold with INT64 `%`.  This pass replaces them with 32-bit
subtractive Montgomery arithmetic (`R = 2^32`, a-fused's `field.py` algorithm: `mul.lo, umulhi, mul.lo, umulhi, sub, select`)
in every Triton pass -- packed and extension Hadamards, `fold_k`, the SIMT extension fold.  Tables stay plain; the
eq-weight limbs carry the compensating `R`; challenges and fold coefficients are pre-scaled by `R` on the host.
Transcripts are bit-identical to `reference.py` at every k (36 CUDA tests).

Whole sumcheck per layer table, CUDA-graphed rounds (device time), median of 9:

| k | 2^24 before -> after (ms) | 2^26 before -> after (ms) | **2^28 direct** (ms) | frac. INT8 peak (2^26 after) | peak mem (2^26) | per VU (six layers, padded) before -> after |
|---|---|---|---|---|---|---|
| 0 | 9.20 -> 4.61 (2.0x) | 30.87 -> 12.56 (2.46x) | -- (34.9 GB at 2^26) | 3.42% | 34.9 GB | 238 -> 90 us |
| 1 | 6.06 -> 4.10 | 18.47 -> 10.68 (1.73x) | -- | 2.35% | 18.0 GB | 138 -> 75 us |
| 2 | 4.35 -> 3.02 | 11.73 -> 6.43 (1.82x) | 19.78 | 2.53% | 9.7 GB | 84 -> 41 (39.8 direct) us |
| **3** | 3.71 -> 2.91 | 9.08 -> 5.97 (1.52x) | **17.69** | 2.48% (3.35% at 2^28) | 5.3 GB (18.0 at 2^28) | **62.7 -> 37.5 (35.6 direct) us** |
| 4 (unfused round 4) | 7.30 -> 3.71 | 23.37 -> 9.25 (2.53x) | 30.96 | 2.15% | 5.0 GB | 178 -> 64 (62.4 direct) us |

* Runs: before = r20260922-062108-4b25 (a-packed); after at 2^26 = r20260922-064917-c293; direct 2^28 = r20260922-065412-73be.
  "per VU" = the six c-round sumchecks of the batch (`393,216 x 2^read` padded layer tables) / 4096; the direct
  numbers use the 2^28 point instead of the linear fit over 2^20..2^26 (the fit was 5% pessimistic).
* **k = 3 at one full layer table (2^28): 17.69 ms; six layers 145.9 ms padded / 86.5 ms unpadded per batch = 35.6 us/VU,
  1.76x better than the a-packed 62.7 us (6.7x better than the plain a-packed k = 0).**
* Still not HBM-bound.  HBM traffic at 2^28, k = 3: packed rounds 3 x 2.15 GB (g, h re-read per round) + fold_k 2.15 + 1.6 GB
  + extension rounds and folds ~8 GB, ~18 GB total = 5.4 ms at 3.35 TB/s; measured 17.7 ms = 3.3x the HBM floor and 3.35%
  of the INT8 peak.  The residual is SIMT: the 4-limb decomposition of every Hadamard and the `tl.join` tree that lays the
  limbs out for `tl.dot` (probed: the loads alone run at the HBM rate, 0.040 ms per 2^22 chunk vs 0.19-0.27 with the
  limb/join/dot body).  Next levers, in order: (a) form limbs on 2 x 16-bit halves instead of 4 x 8 (halves the join
  tree; the INT8 dot becomes an INT16-emulated one or an FP16 one with exact accumulation), (b) keep the fold in registers
  by fusing round `i`'s Hadamard with round `i-1`'s fold (one read of the tables per two rounds), (c) fuse the three packed
  rounds into one pass over `g, h` (they read the same tables: 3 x 2.15 GB -> 2.15 GB).
* **Fused k = 4 (DESIGN.md's split of the 768-row block)**: implemented as a third grid axis over `x` (each program forms
  the 64 Hadamards of one `x`, 256 limb rows; `g, h` read three times).  Run r20260922-073702-b11f (46 tests bit-exact,
  the split kernel included): 2^26 **9.25 -> 7.57 ms**, 2^28 **30.96 -> 22.88 ms** -- fusing recovers 1.3x, but k = 4
  still loses to k = 3 (6.13 / 17.61 ms in the same run; per VU 44.7 vs 34.2 µs).  The fourth base round's 64 Hadamards
  per `x` cost more SIMT work than the extension round it replaces (16 Hadamards + 3 x 32-row `tl.dot` per `x` at k = 3 vs
  64 + 256 rows at k = 4), and the packed rounds are SIMT-bound.  **Verdict: drop as the default (k = 3 stays); the
  kernel is kept** because it halves the peak memory (11.0 vs 18.2 GB at 2^28: the extension table after the fold is
  2^24 x 6 instead of 2^25 x 6) -- a lever if a-gpu needs to hold more layers resident.  The fused `fold_k` was already
  in the first pass (`fold_k` = one Triton pass, 2.4 ms of the 427 ms logUp; 0.5 ms per layer at 2^26).

## 2. LogUp fractional GKR (first GPU measurement)

`backends/gkr/packed/logup_gpu.py` + `kernels_triton.py`; bit-exact against `logup_reference.py` (a transliteration of
`backends/gkr/src/logup.rs` with the low-bit-first binding the packed kernels stream; 10 tests on the H100, k = 0 and 3,
with and without padding).  Shape: 393,216 units x 306 lookups = 120,324,096 queries into one 65,536-row range table,
2^27 leaves (10% padding), 27 levels, 351 sumcheck rounds.  Run r20260922-073439-1f15, best of 3:

| | k = 3 | k = 0 |
|---|---|---|
| **total per batch** | **427 ms = 104 us/VU** | 447 ms = 109 us/VU |
| multiplicities (`bincount`) | 3.7 ms | 3.6 ms |
| tree values (leaf level from base queries + 26 `tree_level` passes) | 12.6 ms | 12.5 ms |
| level 26 (2^26 leaf pairs): packed rounds / fold_k / 23 extension rounds | 8.2 / 2.4 / 29.4 ms (51 ms with overhead) | 0 / 15.3 / 65.4 ms (92 ms) |
| level 25 (2^25 pairs, generic) | 48 ms | 45 ms |
| level 24 / 23 / 22 / 21 / 20 | 37 / 31 / 26 / 24 / 22 ms | 35 / 28 / 25 / 22 / 21 ms |
| the 20 smallest levels (<= 2^19 pairs) | 171 ms | 161 ms |
| peak device memory | 12.5 GB | 24.8 GB |

* The witness side of the big level is the packed trick applied to logUp: leaves `(1, z - w)` with `w` base give
  `A_x = 2 z - s_x`, `B_x = z^2 - z s_x + pi_x` with `s = w_e + w_o`, `pi = w_e w_o` base tables, so rounds 1-3 are
  `half^2` base Hadamards + `half` linear rows per `x` fed to `tl.dot` (8.2 ms for the three rounds over 2^26 pairs vs
  65 ms for the same rounds as extension rounds at k = 0: **the leaf level is 1.8x cheaper packed**).  The table region
  (65,536 leaves) runs the generic four-table extension kernel on its own eq-weight slice; the padding is a constant
  added analytically.  The leaves themselves are never materialised (the level below them is formed from `w` directly).
* **The bucket is launch-bound, not compute-bound.**  The 20 smallest levels do negligible device work but take 171 ms:
  each round is ~10 launches + one H2D copy from Python (Triton's launcher is 40-60 us), ~1 ms per round x 351 rounds.
  The device work is ~90-200 ms (estimates: the level-time slope over the smallest levels, 0.98 ms/round, gives 91 ms;
  the sum of the big-level phases plus a per-level halving model gives ~200 ms).  Lever: CUDA graphs per level shape or
  a C++ launcher, and one persistent kernel for all rounds of a level below 2^16 pairs -- this is engineering, not a
  kernel problem.  The a-gpu prover, which owns the launch loop, is the place to do it.
* Roofline of the device work: level 25's first extension round reads 4 x 2^25 x 24 B = 3.2 GB and forms 2^24 x 9 `F_{p^6}`
  Hadamards; at 3.35 TB/s the read is 1 ms; the round takes ~8 ms (same SIMT limb/join bound as the checker kernels).
* CPU reference point: the lookup bucket of the full-VU CPU prover was 92 s (`backends/gkr/README.md`): 215x.

## 3. A re-priced (`notes-asset:campaigns/r20-proof/assets/a-packed2/reports/a_kernels_h100.json`)

`explore.tensor` design A at H100 / 0.172, with the `gkr_checker` matmul + `gkr_hadamards` buckets replaced by the measured
six-layer sumcheck and the `logup_fractional_gkr` matmul + `logup_hadamards` + `logup_tree_build` buckets replaced by the
measured logUp x 1.086 (the model's leaves over all five tables / the measured 2^27; the four small tables add 8.6%).

| design A | overhead vs native peak | t.total per batch | checker sumcheck | logUp GKR | modelled remainder |
|---|---|---|---|---|---|
| model @ 0.172 (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor) | 1.07e7 | 0.432 s | 257 ms (model) | 86 ms (model) | 89 ms |
| a-packed (sumcheck measured, INT64 %) | 1.07e7 / 8.19e6 | 0.431 / 0.330 s | 257 / 156 ms | 86 (model) | 89 ms |
| **this pass, both measured (padded / unpadded sumcheck)** | **1.73e7 / 1.59e7** | 0.699 / 0.639 s | 146 / 86 ms | 464 ms | 89 ms |
| estimate: logUp launch overhead removed | 8.07e6 / 6.6e6 | 0.326 / 0.266 s | 146 / 86 ms | 91 ms (estimate) | 89 ms |
| A-hintfree-depth630, both measured | 1.67e7 / 1.52e7 | 0.673 / 0.613 s | 146 / 86 | 464 | 63 ms |

Read: the checker sumcheck came in **under** the model (146 vs 257 ms, 3.35% of INT8 peak with 3.8x fewer operations
than the plain algorithm); the logUp GKR as measured is **5.4x over** the model because its 351 rounds are launch-bound
from Python -- the measured A is 1.73e7, worse than the a-packed 1.07e7 *because a modelled bucket became a measured one*.
The estimate row is what the same kernels would give with the launch loop fixed (8.1e6 / 6.6e6); it is an estimate and
is labelled as one on the ledger.  What stays modelled (89 ms of the 0.7 s): Ligero encoding 22 ms, hashing 64 ms, row
combination, hint generation, PRG; plus the multiplicity commitment, Fiat-Shamir round trips and the relation checker's
assembly.

## Ledger (`backends/numerical/reports/ledger/a-packed2.jsonl`)

`32-bit Montgomery packed sumcheck, direct 2^28` (component, 35.6 us/VU, run r20260922-065412-73be);
`logUp GKR on the H100, full-VU shape (measured)` (component, 104 us/VU, run r20260922-073439-1f15);
`A re-priced, sumcheck+LogUp measured (H100)` (`ARITHMETIC_DIAGNOSTIC`, scope vu, overhead 1.73e7, omitted listed).
