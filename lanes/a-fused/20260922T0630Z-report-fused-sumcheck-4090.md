---
id: r20-proof/a-fused/20260922T0630Z-report-fused-sumcheck-4090
campaign: r20-proof
lane: a-fused
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/fused_sumcheck_4090.md
---

# Candidate A's GKR round as ONE fused kernel: measured on an RTX 4090 (lane/a-fused, 2026-09-22)

Labels: `ARITHMETIC_DIAGNOSTIC`, `authentication excluded`, `security.target = 2^-128` (BabyBear^6 challenge).
Hardware: NVIDIA GeForce RTX 4090 (sm_89, driver 580.159.04, CUDA 12.4, torch 2.6.0+cu124, Triton 3.2) on pod vy-sp1.
Peaks: 1008 GB/s GDDR6X; 330.3 T MAC/s INT8 dense; 20.6 T INT32 op/s SIMT (64 lanes/SM x 128 SMs x 2.52 GHz).
Kernels: `backends/gkr/tensor/fused/round_simt.py` (plain SIMT Montgomery arithmetic), `round_tc.py` (fold on `tl.dot`);
roofline `fused/ROOFLINE.md`.  Run **r20260922-060339-740b** (medians of 7, CUDA events, cold L2 per kernel; agreement
tests 19 passed on CUDA before the sweep); the SIMT-only run r20260922-055510-481e agrees to 1%.  Generator:
`fused/reprice.py` -> `fused_sumcheck_4090.json`.  Random tables; not a proof.

## What one kernel is

Round `i`'s tables after the fold with `r_{i-1}` are exactly what `S_i` needs, so the fused kernel with **input `n`
elements per table** reads the three round-`(i-1)` tables once (24 B per BabyBear^6 element, coefficient-major), folds
pairs in registers (`x_e + r (x_o - x_e)`: one extension product), evaluates `S_i(0..3)` over pairs of the folded elements
(two products per point per pair, direct evaluation), writes the `n/2` folded elements once, and emits 24 partial sums per
program.  Bytes: `108 n`; products: `3.5 n`.  No limb tensors, no INT32 intermediates in HBM.  The torch composition it
replaces (`note:r20-proof/tc-sumcheck/20260922T0524Z-report-tc-sumcheck-4090`) ran the same round as ~120 kernels with 4-8x the bytes.

## Roofline vs measured (extension input, cold L2, `n` = input elements per table)

The HBM floor is the binding one on both engines: at n = 2^21 the tensor-core compute floor is 29 us, the SIMT compute floor
140 us (62% of the INT32 peak needed to hide under memory), the HBM floor 225 us.

~~~text
n (input)   HBM floor   SIMT fused kernel            TC-fold kernel (fold+eval)   fold-only SIMT / TC        eval-only SIMT (S over n, no fold)
2^23        899 us     1014 us  894 GB/s  1.13x     1960 us  462 GB/s  2.18x     1007 / 1041 us  900 / 870  747 us  809 GB/s (151 MB read; 1.25x)
2^22        449 us      520 us  871 GB/s  1.16x      988 us  458 GB/s  2.20x      512 /  552 us  885 / 821  412 us  734 GB/s
2^21        225 us      273 us  828 GB/s  1.22x      506 us  448 GB/s  2.25x      267 /  281 us  847 / 807  244 us  619 GB/s
2^20        112 us      153 us  742 GB/s  1.36x      263 us  430 GB/s  2.34x      144 /  153 us  784 / 738  141 us  534 GB/s
2^18         28 us       50 us  564 GB/s  1.79x       77 us  369 GB/s  2.73x       41 /   55 us  691 / 514   51 us  368 GB/s
2^16          7 us       20 us  364 GB/s  2.77x       28 us  256 GB/s  3.94x       16 /   20 us  432 / 358   20 us  234 GB/s
2^14        1.8 us       15 us  122 GB/s  8.3x        13 us  133 GB/s  7.6x        11 /   10 us  157 / 173   16 us   72 GB/s
2^12        0.4 us       13 us   33 GB/s  30x         11 us   39 GB/s  26x         10 /    8 us   43 /  54   16 us   18 GB/s
base-field input (round 2 of a layer: fold base -> extension + S), n = 2^22: 256 us vs 200 us floor (1.28x, 786 GB/s);
round 1 (S over base tables, 50 MB read): 79 us vs 50 us floor (1.58x).
~~~

A plain `copy_` of the same bytes runs at 895-911 GB/s on this card, so **the SIMT fused kernel is at 0.94-0.98 of the
achievable bandwidth from 2^21 up** (1.13-1.22x the datasheet floor); its arithmetic (0.51-0.55 of the INT32 peak in
model ops) hides under the memory time (fold+eval costs 1-2% more than fold-only).  Below 2^16 the kernel is a fixed
10-16 us: a single CTA executing a ~3000-instruction dependent chain (fold, then two chained extension products) --
not launch latency (graphed launches are 8-11 us per kernel *including* that execution).

## Tensor cores vs SIMT for this round

* **SIMT wins.**  The fold alone on tensor cores (`[BLOCK, 64]` int8 tile loaded straight from the u32 bytes, one
  `tl.dot` with the 64 x 64 convolution matrix, `x - 128` top-bit flip + `128 colsum(C)` correction for the
  unsigned/signed mismatch, in-register recomposition with int64 multiply-adds and one 64-bit Montgomery reduction,
  `tl.split` to peel the coefficient columns) is **HBM-bound at parity**: 807-870 GB/s vs SIMT's 847-900.  It does not
  save SIMT work: recomposing 8 limb positions x 6 coefficients (64 int64 MACs + 6 reductions per element) costs about
  what the single SIMT extension product it replaces costs (~390 INT32 ops), because TensorZKP's convolution matrix
  emits 2x redundant limb positions.
* Fused with the round-polynomial evaluation the TC kernel is **1.8-2.2x slower than the SIMT kernel** (506 vs 273 us at
  2^21): the dot's MMA layout forces layout conversions (shared-memory round trips, replicated work) on the coefficient
  vectors before the SIMT products, and 138-215 registers + 8-39 KB shared memory per CTA cut the occupancy that hides
  the memory latency.  Re-reading the just-written coefficients (`RELOAD`) recovers only 10%.
* `tl.dot` int8 on sm_89 / Triton 3.2: M >= 16, K, N multiples of 16 -> 48 limb columns padded to 64 (4096 MACs
  performed per folded element for 2304 useful, 576 needed); INT32 accumulation is nowhere near its bound.  Tensor-core
  MACs performed run at 0.06-0.08 of the INT8 peak because the kernel is memory-bound; a `<f, g o h>` inner product on
  `tl.dot` (TensorZKP's formulation) was not built: it adds 4 SIMT Hadamards and 96-column in-register limb
  decompositions per pair to save 4 of the 8 SIMT products, and the round is already at the bandwidth ceiling.
* The roofline said this in advance (`ROOFLINE.md`): the TC compute floor is 13% of the HBM floor, the SIMT one 62%; a
  SIMT kernel at >= 62% INT32 efficiency is memory-bound and the tensor core has nothing to buy.  The measured SIMT
  efficiency is 0.51-0.55 of peak in model ops with the arithmetic fully hidden.

## The 6-layer / 130-round model (4096 units, widths 137/679/673/669/647/533 padded to 2^ceil, run as a real sequence)

~~~text
                              eager (CPU launches)   CUDA-graphed   HBM floor   tail (n <= 2^15: 90 kernels) graphed
previous torch composition        472 ms                91.4 ms      3.67 ms    22-33 ms (170-250 us per round)
fused SIMT                       8.72 ms                6.20 ms      3.67 ms    1.48 ms (16 us per round)
fused TC-fold                   10.11 ms                8.48 ms      3.67 ms    1.18 ms
~~~

**14.7x faster than the torch composition graphed, 1.69x the HBM floor.**  Of the 6.20 ms, 4.68 ms are the 46 large
kernels (n > 2^15; floor 3.63 ms: 1.29x) and 1.48 ms the 90 tail kernels whose floor is 0.04 ms.  The tail is a
critical-path problem, not a throughput one: 16 us per round is below any network round trip (the protocol has one per
round), so fusing rounds into one kernel cannot remove it -- binding several `c` variables per message (PROTOCOL.md 5.4)
or interleaving the 6 layers' tails on one stream are the levers.  Launch: 55-67 us eager single, 32-43 us per kernel
eager in a run, 8-11 us graphed (execution included).

## Re-priced Candidate A (`explore.tensor` A row, BabyBear^6, 2^-128, Blake3 on SIMT at 50 GB/s, other buckets at the model's rates)

The measured layer model is 4096 units = 1/96 of the B = 4096 x 96-unit batch.  The model's checker-GKR bucket (matmul at
`u` + Hadamards on SIMT: 381.5 + 105.4 = 487 ms at u = 0.172) is replaced by the measured sequence x 96.

~~~text
substitution                                                  t.gkr_checker   t.total    overhead.vs_native_peak   model-equivalent u
model as assumed (u = 0.172)                                     487 ms        0.759 s      1.88e7                    0.172
previous lane, torch composition (u = 0.012 graphed round)         --          8.0 s        1.97e8                    0.012
fused SIMT, graphed x96 (96 copies of the tail: conservative)    595 ms        0.866 s      2.15e7                    0.110
fused SIMT, graphed x96, census widths (x0.62)                   369 ms        0.641 s      1.59e7                    0.178
fused SIMT, batch bytes at the sustained 894 GB/s                 397 ms        0.669 s      1.66e7                    0.165
fused SIMT, HBM floor of the batch                               352 ms        0.624 s      1.55e7                    0.186
fused TC-fold, graphed x96                                       814 ms        1.085 s      2.69e7                    0.081
~~~

("logup at fused rate" variants, where the logUp fractional GKR is priced at the fused kernel's per-element rate instead
of the model's bucket, move t.total by < 5%: `fused_sumcheck_4090.json`.)  **A on the 4090 lands at 1.6-2.2e7, back at the
model's assumed level and 9-12x below the torch-composition re-pricing**; the checker GKR is now 55-69% of A's modelled
time and at 0.9-0.98 of achievable bandwidth, so the next factor for A is bytes (an in-kernel `eq` tensor product saves
1/3; a base-field trace kept out of the challenge field saves 6x on the early rounds), not kernel efficiency.  A100/H100:
an HBM-bound kernel scales with bandwidth (2.0x / 3.3x the 4090), not with tensor peak; nothing was measured there.

## logUp fractional-sumcheck round (`fused/round_logup.py`, `fused_logup_4090.json`)

The other half of A's rounds: `sum eq (p_l q_r + p_r q_l + lambda q_l q_r)`, five extension tables, fold+eval fused,
bit-exact against `logup_reference` (kernel tests on the pod, 6/6).  180 n bytes and 7.5 extension products per input
element (vs 108 n and 3.5 for the checker round).  Eager, warm, median of 11, block 256 / 4 warps:

| n | fold+eval us | GB/s | HBM floor us | frac of floor | fold-only us (GB/s) | G ext-mul/s |
|---|---|---|---|---|---|---|
| 2^21 | 600 | 629 | 374 | 0.62 | 473 (798) | 26.2 |
| 2^20 | 344 | 549 | 187 | 0.54 | 255 (741) | 22.9 |
| 2^18 | 118 | 401 | 47 | 0.40 | 65 (722) | 16.7 |
| 2^16 | 78-81 | 146 | 12 | 0.15 | 60 | 6.1 |
| 2^14, 4096 | 73-84 | - | - | - | 59-60 | - |

This is the first round where SIMT becomes compute-bound: fold-only sits at the same ~800 GB/s as the checker round, but
adding the 20 extension products per pair costs +127 us at 2^21 (the checker round's eval added ~30 us).  `ROOFLINE.md`
predicted SIMT would need ~80% of INT32 peak to hide under HBM here; it reaches roughly 60%.  Sizes <= 2^16 are the
eager-launch floor (13 pointer arguments, not graphed; the checker layer model showed graphing brings that to ~16 us).
Not in the layer model or the re-price (the re-price keeps logUp at the model's rate; at 600 us per 2^21-round it would
be priced ~2.2x the checker round per element, consistent with the model's relative weighting).  A `tl.dot` version of
this round is the one place tensor cores could still pay on this card: the eval is now compute-bound and the products
share operands (`q_l q_r` feeds `lambda`), but the layout-conversion cost measured in `round_tc` still has to be beaten.

## Not done

The `<f, g o h>` inner product on `tl.dot` (see above); logUp on tensor cores or graphed / in the layer model; base -> extension fold on tensor cores
(SIMT runs that round in the TC layer model: 2 of 23 kernels per layer); `eq` generated in-kernel; A100/H100.
