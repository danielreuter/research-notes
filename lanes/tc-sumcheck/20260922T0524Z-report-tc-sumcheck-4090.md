---
id: r20-proof/tc-sumcheck/20260922T0524Z-report-tc-sumcheck-4090
campaign: r20-proof
lane: tc-sumcheck
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/tc_sumcheck_4090.md
---

# Candidate A's GKR sumcheck round on INT8 tensor cores: measured on an RTX 4090 (lane/tc-sumcheck, 2026-09-22)

Labels: `ARITHMETIC_DIAGNOSTIC`, `authentication excluded`, `security.target = 2^-128` (BabyBear^6 challenge, 24 limbs).
Hardware: NVIDIA GeForce RTX 4090 (sm_89, driver 580.159.04, CUDA 12.4, torch 2.6.0+cu124, triton 3.2) on pod vy-sp1.
Peaks used: 660.6 TOPS INT8 dense = 330.3 T MAC/s; 1008 GB/s GDDR6X (Ada datasheet, no sparsity).  Kernel:
`backends/gkr/tensor/sumcheck_int8.py` (TensorZKP layout, signed balanced 8-bit limbs, INT32 accumulation over
<= 32768-row chunks, INT64 chunk sums, one reduction per inner product; fold as limb matmul).  Runs:
**r20260922-051730-15d4** (the table; Triton split-K inner product, torch.compile'd SIMT passes, median of 7),
r20260922-052015-a62d (cuBLAS `_int_mm` inner product only: 6.5x slower per round).  Generator: `bench.py --reprice` ->
`tc_sumcheck_4090.json`.  This is a kernel measurement of random tables, not a proof.

## Per-round table (GPU kernel time from the CUDA profiler; the round = 8 triple inner products + 3 folds + 4 Hadamards)

`frac` = performed limb MACs / (330.3 T MAC/s x time).  `tensor bucket` = matmuls + limb decomposition + INT64 chunk sums +
reductions (everything the cost model prices on the tensor side); `graphed round` = wall time of the whole round replayed
as one CUDA graph (Hadamards included, CPU launch gaps excluded).

~~~text
t (elements)  deg  MACs      matmul us  tensor-bucket us  Hadamard us  graphed round us  T MAC/s(matmul)  frac(matmul)  frac(tensor)  frac(round)
4194304 (2^22) 1   2.68e9     1600        3858              (in other)   3879              1.7              0.0051        0.0021        0.0021
2097152 (2^21) 6   1.21e10    1014        3971              666          4636             11.9              0.0361        0.0092        0.0079
1048576        6   6.04e9      458        1901              283          2220             13.2              0.0400        0.0096        0.0082
 524288        6   3.02e9      215         905              120          1050             14.1              0.0426        0.0101        0.0087
 262144        6   1.51e9      100         498               76           602             15.1              0.0458        0.0092        0.0076
 131072        6   7.55e8       52         322               60           383             14.5              0.0438        0.0071        0.0060
  65536        6   3.77e8       31         228               49           298             12.3              0.0372        0.0050        0.0038
  32768        6   1.89e8       22         190               50           278              8.5              0.0256        0.0030        0.0021
   4096        6   2.36e7       19         171               53           257              1.3              0.0038        0.0004        0.0003
    512        6   2.95e6       19         168               46           255              0.2              0.0005        0.0001        0.0000
     64        6   3.69e5       18         167               45           252              0.0              0.0001        0.0000        0.0000
      2        6   1.15e4       19         174                0           207              0.0              0.0000        0.0000        0.0000
~~~

Below t = 2^15 every round is a fixed ~170 us of kernel time (121 kernels of ~1.4 us each: launch latency of an unfused
torch implementation) and ~250 us graphed; the tensor cores are idle.  Peak device memory 1.73 GB.

**Ceilings**: plain `_int_mm` 8192^3 = 6.59 ms = 83.5 T MAC/s = **0.253 of peak** (4096^3: 0.246) -- the library's
best on this card is a quarter of the datasheet.  The round's own shapes: `_int_mm(48, 32768, 96)` (one inner-product
chunk) = 821 us = **0.00056 of peak** (cuBLAS runs a skinny-M/N long-K INT8 GEMM on one SM, no split-K; a 1M-row
inner product took 25 ms as 32 launches), which is why the inner product is a 30-line Triton split-K kernel
(191 us for 1M rows x 48 x 96: 7.6% of peak, **0.79 TB/s = HBM-bound**).  `_int_mm(2^21, 48, 48)` (the fold) = 583 us =
0.025 of peak, 0.91 TB/s: HBM-bound on its INT32 output (192 B per element written for 24 B of limbs read).

**Layer model** (6 layers, tables 4096 x 2^ceil(log2 width) = 2^22 x5 and 2^20, 130 U-parallel rounds, 1.41e11
performed MACs = 2.07e11 with tile padding; the cost model counts 3.64e11 for the same padded widths, 2.26e11 for the
census widths): GPU kernel time **87.4 ms** (matmul 19.7 ms: inner 2.3, fold 17.4; reductions 16.6; limb decomposition
+ copies 35.5; Hadamards 10.6; other 2.9); graphed wall **91.4 ms**; CUDA-event segments with CPU launch gaps 472 ms.

## Effective utilisation (batch-weighted over the 130 rounds) and re-priced Candidate A

~~~text
achieved fraction of INT8 peak, performed MACs:   matmul kernels only 0.0216   tensor bucket 0.0056   whole round (graphed) 0.0047
model-equivalent (plug into explore.tensor):       matmul only 0.0559          tensor bucket 0.0143   whole round (graphed) 0.0120
~~~

The model-equivalent number is what `explore.tensor.Priced.times(utilisation=...)` needs because the model's
`sumcheck_macs` counts 32 t dl^2 per round while the TensorZKP formulation performs 16 t dl^2 (inner products and
folds run over t/2 element pairs) -- the two factors of 2 that cancel in the model's layer total (it also takes
`units x width` as the sum over rounds) do not cancel per round.  Re-priced overhead (`overhead.vs_native_peak`, A at
2^-128, BabyBear^6, Blake3 at 50 GB/s, hint generation and Hadamards at the model's own SIMT rates):

~~~text
GPU        u = 0.172 (assumed)   u = 0.0143 (tensor bucket)   u = 0.0120 (graphed round)   u = 0.0559 (matmul only)
RTX 4090   1.88e7  (0.76 s)      1.67e8  (6.7 s)              1.97e8  (8.0 s)              4.68e7  (1.9 s)
A100 *     3.17e7                1.88e8                       2.21e8                       6.13e7
H100 *     1.07e7                6.01e7                       7.03e7                       2.00e7
~~~

`*` peak-ratio scaling only (the 4090 utilisation applied to the A100/H100 INT8 peaks); nothing was measured there and
their HBM:tensor ratios differ (A100 2.0 TB/s : 312 T; H100 3.35 : 990; 4090 1.0 : 330), so an HBM-bound kernel scales
with bandwidth, not with peak: on that axis the H100 is 3.3x the 4090, the A100 2x.  At the measured utilisation the
matmul bucket is 90-97% of A's time; A lands at ~1e8 (4090/A100) to 6e7 (H100), not 1e7-3e7.

## What surprised

1. cuBLAS/`_int_mm` is unusable for the inner-product shape (0.06% of peak): INT8 GEMM with M, N ~ 50-100 and K in the
   tens of thousands gets no split-K.  The fold shape (huge M, K = N = 48) is fine for cuBLAS but HBM-bound.
2. Nothing in the round is compute-bound: the two matmuls, the reductions and the limb passes all run at 0.6-0.9 TB/s.
   The INT32 output of the limb layout (8x the operand bytes) is the traffic; the tensor cores see < 4% even in the
   large rounds.  TensorZKP's 17% (H100, HBM-bound at 80% of 3.35 TB/s, 32-limb elements) does not transfer to a
   24-limb degree-3 round on a 1 TB/s card: we get 2.2% for the matmuls alone.
3. Half of the layer's 130 rounds (t < 2^15) are pure launch latency (170-250 us each = 22-33 ms of the 87-91 ms);
   the batch dimension B = 4096 does not save the tail, because the tail rounds are the ones that have folded B away.

## Three things that would move the number most

1. **Fuse the fold's recomposition into the GEMM epilogue** (a CUTLASS/Triton kernel writing 24 B of limbs per element
   instead of 192 B of INT32 then reading them back): removes ~34 ms of the 87 ms (fold + reduce) and most of the limb
   passes; the round becomes a read of the three tables (~3x) at HBM speed: ~0.5 ms at 2^21 instead of 4.6.
2. **Fuse the whole small-round tail into one persistent kernel** (or run the 6 layers' tails in one launch):
   rounds below 2^15 cost 250 us of latency for < 20 us of work; 65 such rounds per batch.  Alternatively bind
   several variables per message (PROTOCOL.md 5.4 `c` variables) to halve the round count.
3. **Cut the challenge limbs on the hot path**: at 2^-128 every element is 24 limbs and 576 MACs per product; the
   inner product's HBM floor is set by 48 + 96 bytes per element pair.  Keeping trace x trace products in the base
   field (packed / small-field GKR, `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor` "out of scope") or a degree-4 challenge at a lower operating point
   cuts the bytes 2-4x.  An H100 (3.35 TB/s) is the same kernel at ~3x.

Not measured: A100/H100 (scaled only); the `l, r` per-circuit rounds and the logUp fractional GKR (same kernel shape,
not run); the eq-table factor as an extension-valued first-round operand (round 1 was base x base x base as
specified); Hadamards on a real SIMT kernel (torch.compile'd int64 arithmetic: 10.6 ms per layer model, 0.6 TB/s);
the paper's 96-column fold layout at scale (`--layout paper`; tested for agreement only); chunk sizes above 32768.
