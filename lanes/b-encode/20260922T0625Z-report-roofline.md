---
id: r20-proof/b-encode/20260922T0625Z-report-roofline
campaign: r20-proof
lane: b-encode
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/direct/encode/ROOFLINE.md
---

# Roofline: Reed-Solomon encoding of the Ligero witness matrix on an RTX 4090 (b-encode lane, 2026-09-22)

Generated numbers: `python backends/direct/encode/roofline.py` (pure Python).  Peaks used (Ada datasheet / whitepaper):
1,008 GB/s GDDR6X; INT8 dense tensor 660.6 TOPS = 330.3 T MAC/s; FP32 82.6 TFLOPS; INT32 ALU rate taken as
128 SMs x 64 INT32 lanes x 2.52 GHz = **20.6 T int32 op/s** (the other 64 lanes per SM are FP32-only on Ada);
shared-memory bandwidth 128 B/clk/SM = 41 TB/s aggregate.

## The problem

The code is the protocols' `[n = 16384, k = 4096]` RS code over BabyBear (`backends/direct/PROTOCOL.md` section 3,
same as Candidate A section 3).  A row is `k` **values** on the message domain: `l = 3840` payload symbols plus
`k - l = 256` randomizers, all values (the linear constraints read the payload as values and the quadratic test
multiplies rows pointwise).  So the encoder must interpolate (INTT over the `k`-point domain) and evaluate on the
`n`-point domain: **the protocol does not let the INTT be skipped** (a row defined directly by coefficients would break
the constraint system).  What the domain structure *does* give for free: with the message domain the index-4 subgroup
`H` of the evaluation domain `D`, coset 0 of `D/H` is the message itself (the code is systematic) and the other three
cosets are three size-`k` NTTs of the shifted coefficients.  That is the formulation both kernels use.

~~~text
per row (k = 4096 -> n = 16384, 4-byte elements)
  bytes in / out                          16,384 / 65,536   (49,152 if the caller keeps the systematic part)
  (a) radix-2 butterflies, textbook       139,264           INTT_k + zero-padded NTT_n
  (a) radix-2 butterflies, coset form      98,304 + 12,288 twiddle muls    INTT_k + 3 x NTT_k  (-30%)
  (b) matrix-DFT base MACs, model       4,718,592           tensor.py ENCODERS['rs_matrix_ntt']: 64x64 interpolate + zero-padded 128x128 evaluate
  (b) matrix-DFT base MACs, coset form  2,097,152           4 DFTs x 2 stages x k x sqrt(k)  (x16 = 33.6 M INT8 limb MACs)
  (c) dense generator matrix           50,331,648           (n - k) x k  (the systematic part needs no MACs)
  (d) expander, 20 MACs/symbol            327,680           Brakedown assumption (explore.pcs)
~~~

## Floors per batch (B = 4096 VUs)

~~~text
                                              Candidate B (310,602 rows)          Candidate A (48,873 rows)
bytes in / out                                5.09 GB / 20.36 GB                  0.80 GB / 3.20 GB
HBM floor: read in + write codeword           25.2 ms  (write alone 20.2)         4.0 ms  (write alone 3.2)
HBM floor: cosets only (caller keeps payload) 20.2 ms                             3.2 ms

(a) NTT, coset form   3.05e10 butterflies    SIMT 14.4 ms   smem 11.8 ms          SIMT 2.3 ms   smem 1.9 ms
(a) NTT, textbook     4.33e10 butterflies    SIMT 18.9 ms   smem 16.8 ms          SIMT 3.0 ms   smem 2.6 ms
(b) matrix DFT coset  1.04e13 limb MACs      TC@1.0 31.6 ms  @0.25 126 ms  @0.172 183 ms      5.0 / 19.9 / 28.9 ms
(b) matrix DFT model  2.34e13 limb MACs      TC@1.0 71.0 ms  @0.25 284 ms  @0.172 413 ms     11.2 / 44.7 / 64.9 ms
(b) unfused INT32 intermediates               1,384 GB of HBM traffic = 1,373 ms   218 GB = 216 ms
(c) dense generator   2.50e14 limb MACs      TC@1.0 757 ms                        119 ms
(d) expander          1.63e12 limb MACs      TC@1.0 4.9 ms; SIMT 39 ms; gather from HBM 3.2 s   0.8 / 6.2 / 508 ms
~~~

SIMT floors assume 9 INT32-class ops per butterfly (Montgomery multiply ~6: two `mul.lo`, one `mul.hi`, add, shift,
conditional subtract; add/sub with correction ~3) and 6 per twiddle multiply.  The shared-memory floor counts 2 words
read + 2 written per butterfly.  `@0.25` is the cuBLAS `_int_mm` ceiling measured on this card
(`note:r20-proof/tc-sumcheck/20260922T0524Z-report-tc-sumcheck-4090`: 8192^3 INT8 GEMM = 0.253 of peak); `@0.172` is the cost model's TensorZKP calibration.

## Which regime each encoder is in

* **(a) SIMT NTT: memory-bound.**  Its arithmetic floor (14 ms) and shared-memory floor (12 ms) are both below the
  HBM floor of the problem (25 ms).  The row (16 KiB) fits in shared memory, so the only HBM traffic is the input read
  and the codeword write: the roofline of the whole encoding is *writing 20 GB at 1 TB/s*, 20-25 ms per B batch,
  and the NTT is the one encoder that can reach it.  Achieved fraction of that floor is the figure of merit.
* **(b) INT8 matrix DFT on tensor cores: compute-bound, and its compute floor is above the memory floor.**  Even the
  cheapest formulation (coset form, 33.6 M limb MACs per row) needs 31.6 ms at 100% of the INT8 peak -- already 1.25x
  the HBM floor -- and 126-183 ms at the utilisations this card has shown (25% cuBLAS ceiling, 17% TensorZKP
  calibration).  The model's zero-padded formulation is 2.2x worse (71 ms at peak).  This is the sense in which "it
  can be written as a matrix multiplication" does not make it efficient: the O(N sqrt N) matrix DFT does 21x the
  base multiplications of the O(N log N) NTT (2.1 M vs 0.1 M per row), and 16 limb products each, i.e. 340x the
  INT32 multiply count; the tensor core's 16x rate advantage over the INT32 pipes does not cover 340x.  Unfused
  (cuBLASLt with INT32 intermediates in HBM) it is a different problem again: 64 B of INT32 per element per stage,
  1.4 TB of traffic per B batch = 1.4 s.  A fused kernel (limbs and recombination in registers, `tl.dot`) removes the
  traffic and is bounded by the tensor-core floor above.
* **(c) dense generator: hopeless**, 757 ms at 100% of peak (30x the memory floor), stated for completeness.
* **(d) Brakedown/Spielman expander: not a tensor-core operation and not fewer multiplies than the NTT at this k.**
  20 MACs per symbol x 16,384 symbols = 327,680 base multiplies per row vs the NTT's 110,592: at `k = 4096` the
  NTT's `log k / 2 = 6` multiplies per output symbol is below the expander's 20 (the expander wins only above
  `k ~ 2^40`).  As a gather from HBM it is 3.2 s per batch (32-B sectors for 4-B loads); from shared memory (the
  row is resident) it is SIMT-bound at ~39 ms, above the NTT's 14 ms.  It also changes the Ligero test to
  Brakedown's parameters (rate 0.65, distance 0.07: more opened columns, `explore.pcs.brakedown_row`).  Not built.

## What this predicts (before measuring)

1. The order is NTT (SIMT) << fused matrix DFT (tensor cores) << unfused matrix DFT, by ~4x and ~50x, with the NTT
   within 2x of the write floor if the kernel streams well.  The cost model's `rs_matrix_ntt` entry (17% utilisation
   of the tensor-core formulation) over-prices B's encoding by ~10x relative to what a SIMT NTT does on the same
   card; **the "B is matmul-bound" conclusion of note:r20-proof/hash-gpu/20260922T0554Z-report-hash-gpu rests on that entry and flips.**
2. For B the encoder cannot be faster than ~20-25 ms per batch on this card whatever the arithmetic; the next lever is
   not arithmetic but *not writing the codeword*: fusing the encode with the column-hash (SHA-256 sequential over a
   column is streaming-friendly: encode a slice of rows, update 16,384 column-hash states, discard the slice) removes
   the 20 GB write and the hash lane's 20 GB read.  Then B's commitment is bounded by the hash rate (446 GB/s) and the
   input read, ~50 ms per batch for encode + hash together.
3. On A100/H100 the memory-bound NTT scales with bandwidth (2.0x / 3.3x), not with tensor peak.

## Measured (run `r20260922-062016-6bdf`, README.md for the full table)

Prediction 1 held: SIMT NTT v2 **32.2 ms** per B batch (0.78 of the 25.2 ms read+write floor; 948 G butterflies/s),
fused Triton INT8 matrix DFT 171.7 ms (0.184 of the INT8 peak -- the model's utilisation, and still 5.3x slower),
unfused cuBLAS 15.2 s.  B re-priced: 1.22e7 -> 2.57e6 on the 4090 (`notes-asset:campaigns/r20-proof/assets/b-encode/reports/encode_gpu.json`).
