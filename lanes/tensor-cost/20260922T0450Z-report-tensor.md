---
id: r20-proof/tensor-cost/20260922T0450Z-report-tensor
campaign: r20-proof
lane: tensor-cost
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/tensor.md
---

# Tensor-core re-pricing of the design space (lane/tensor-cost, 2026-09-21)

Generator: `verity_numerical.explore.tensor` -> `notes-asset:campaigns/r20-proof/assets/tensor-cost/reports/tensor.json`. Every number is a cost-model estimate; the relation is
the frozen WP2 checker census (358 mul / 137 lin / 306 lookups per unit, 76 808 predicates per K=1536 VU). Unit of
matmul work: one UINT8 x UINT8 -> INT32 limb MAC. Peaks used: A100 SXM 624 TOPS INT8 dense (312 T MAC/s, 2.0 TB/s
HBM2e, 19.5 TFLOPS FP32); H100 SXM 1979 TOPS INT8 dense (989.5 T MAC/s, 3.35 TB/s HBM3, 67 TFLOPS FP32). Native
reference: 9.85 ps per VU at the A100 dense BF16 peak (`bench.contract`).

## Price list (limb MACs)

8-bit limbs are the only usable width: INT32 accumulates N <= 33 025 products (TensorZKP's 2^15 bound); 16-bit limbs
overflow on a single product, 12-bit limbs give N <= 128, BF16/FP16 with FP32 accumulate are exact only to N < 256.
Deferred modular reduction costs one 32-bit word per limb-pair column per inner product (256 words at 2^-80,
576 at 2^-128), i.e. O(1) per inner product and negligible next to the MACs.

~~~
field       bits limbs  base x base   2^-80 ext (d)  trace x chal / chal x chal   2^-128 ext (d)  trace x chal / chal x chal
Goldilocks   64    8        64          2 (128 b)          128 / 256                3 (192 b)          192 / 576
BabyBear     31    4        16          4 (124 b)           64 / 256                6 (186 b)           96 / 576
Mersenne-31  31    4        16          4 (124 b)           64 / 256                6 (186 b)           96 / 576
~~~

Extension degrees are `accounting.first_extension` for the frozen target's soundness terms. At 2^-128 both families
need 24 challenge limbs, so challenge x challenge costs the same; the 31-bit fields win only on trace x challenge
(2x) and on encoding / base products (4x), and pay +9% lookups and +4% committed columns (fields lane's F1/F3/F4
repairs, imported not re-derived).

## Calibration against TensorZKP (H100, BabyBear^4, 2^25 gates)

Measured vs INT8 peak: inner product 0.85 ms = 4.1% of peak (75% of the HBM floor), scalar-vector 0.91 ms = 15%,
degree-2 sumcheck 4.04 ms = 17.2% (79% HBM-bound), expander encoder 11.58 ms = 9.2% (on `explore.pcs`'s 20-MAC
Brakedown assumption). Realistic utilisation adopted: 0.172 dense, 0.092 gather. Merkle: 8.59 ms at 2^25 -> 192 GB/s
implied hash rate. Mapping our relation as a HyperPlonk circuit (one gate per predicate, 437 VUs per 2^25-gate
proof): 215.28 ms -> 0.49 ms per VU -> overhead 5.0e7 end to end; zero-check (sumcheck) part alone 3.9e6. The user's
~5e7 / ~4e6 estimates are confirmed. 62% of TensorZKP's time is the wiring permutation check, which neither A (GKR)
nor B (trace AIR) has, and HyperPlonk has no lookup argument (29k range chunks per VU counted as gates: undercount).

## Ranking at 2^-128, Blake3 on SIMT at 50 GB/s (overhead = prover s per VU / 9.85 ps)

~~~
design                field       ext  limb MACs/VU  matmul share  committed B/VU  A100@1   A100@0.17  H100@1   H100@0.17
A-hintfree(depth 630) BabyBear     6     7.25e9         43%          129 kB       1.93e7   3.06e7     6.46e6   1.00e7
A-hintfree(depth 630) M31          6     7.25e9         43%          129 kB       1.93e7   3.06e7     6.46e6   1.00e7
A                     M31          6     7.52e9         42%          183 kB       1.99e7   3.17e7     6.97e6   1.07e7
A                     BabyBear     6     7.52e9         42%          183 kB       1.99e7   3.17e7     6.97e6   1.07e7
A-hintfree(depth 630) Goldilocks   3     9.18e9         50%          247 kB       1.64e7   3.08e7     6.36e6   1.09e7
A                     Goldilocks   3     1.02e10        49%          354 kB       1.77e7   3.38e7     7.42e6   1.25e7
B                     M31          6     5.81e9         24%         1.15 MB       1.45e7   2.36e7     1.14e7   1.42e7
B                     BabyBear     6     5.86e9         24%         1.16 MB       1.46e7   2.38e7     1.14e7   1.43e7
B                     Goldilocks   3     1.52e10        39%         1.52 MB       2.08e7   4.45e7     1.55e7   2.30e7
A (Brakedown enc.)    Goldilocks   3     7.00e9         55%          354 kB       1.65e7   3.90e7     7.02e6   1.41e7
B (Brakedown enc.)    Goldilocks   3     1.22e9          9%         1.52 MB       1.52e7   1.91e7     1.38e7   1.49e7
~~~

Matmul share is the fraction of prover time in the tensor bucket at H100@0.172; the rest is SIMT Hadamards
(A: 130-185 ms per batch), Merkle hashing (A: 45-124 ms; B: 400-530 ms) and hint generation (0.5 ms per batch,
anchored to 451 s of CPU in the SIMT lanes -- trivially parallel, unmeasured on GPU). Hint-free, branch 1 (+140
committed query-wire columns per unit) is Candidate A's default layout (PROTOCOL.md 4.3) and is the "A" row; branch 2
(nothing extra committed, depth 630) is the "A-hintfree" row: -6% (BabyBear) to -13% (Goldilocks) overhead for
630 sequential rounds versus 381. At 2^-80 the same ordering holds at
~0.7x the overhead (see `notes-asset:campaigns/r20-proof/assets/tensor-cost/reports/tensor.json`). Hash-rate sensitivity (H100@0.172, A/BabyBear): 1.7e7 at 20 GB/s, 1.07e7 at
50 GB/s, 9.5e6 at 192 GB/s; for B/BabyBear: 5.5e7 / 1.43e7 / 6.9e6 -- B is a hashing problem, A is a sumcheck problem.

## Field verdict on tensor cores

31-bit fields win in every cell: A 1.17x (M31, 2^-128), A-hintfree 1.09x, B 1.62x; at 2^-80 1.36x / 1.24x / 1.74x.
BabyBear and M31 are within 0.1% of each other (M31 needs a circle FFT or a non-RS code; BabyBear has 2^27 two-adicity).
This FLIPS "Goldilocks stays": that conclusion rested on the SIMT extension-multiply penalty (a degree-6 tower at 8.5
Goldilocks-multiplies vs 6 for the cubic), which does not exist when a 2^-128 challenge is 24 limbs in either family.
The margin is modest for A because challenge x challenge (576 MACs) dominates the GKR sumcheck either way; it is
large for B because B is encoding-bound and base products are 4x cheaper.

## VOLE / IT-MAC (designated-verifier)

QuickSilver-style online prover over F_{2^61-1} with degree-3 MACs (186 bits): 83 434 correlations and 63 749
multiplication checks per VU; online Hadamards 7.6e5 SIMT field mults, batch check 7.3e7 limb MACs (one long inner
product, negligible). sVOLE expansion: dense dual LPN (n=2^22 -> 2^20, matrix-vector over limbs) costs 3.1e12
MACs/VU -- not viable; a d=10 regular-noise primal code (Wolverine/Ferret, t=1 319 noise weight, 2^20 outputs) costs
5.3e7 MACs/VU but is a gather, and its GGM PRG needs 2.7 MB/VU of AES-CTR output (0.11 s per batch at an ASSUMED
100 GB/s). Result: overhead 3.1e6 (H100@0.172), 3.9e6 (A100@0.172), matmul share 2.5%; 3x below A but the proof is
designated-verifier and moves 667 kB per VU prover-to-verifier (5 kB with Antman SIMD, 21 MB per 4096-VU batch).

## What flipped

1. "Goldilocks stays" -> 31-bit fields win (1.1-1.6x), caveats above.
2. "Commitment/hashing dominates" -> for A, the hash bucket (124 ms) is below the tensor bucket (247 ms) at 50 GB/s;
   for B it stays the largest bucket below ~100 GB/s. A's new bottleneck is the GKR sumcheck over the checker, then
   the SIMT Hadamards.
3. "Ligero stays" holds, encoder changed: RS encoding as a two-stage dense matrix DFT (287 base MACs per symbol) at 17%
   utilisation beats Brakedown's expander (20 MACs per symbol at 9%) for A; for B (encoding-bound) Brakedown is
   ~1.5x better on the tensor bucket but hashing hides it.
4. "VOLE out" -> in scope as designated-verifier; the tensor core does not help it (SIMT Hadamards + PRG), so its
   3e6 overhead comes from having no commitment, not from matmul.
5. A's overhead advantage over B narrows from ~4x (SIMT) to 1.3-1.8x (H100@0.172) and inverts at A100@0.172 for
   BabyBear (3.2e7 vs 2.4e7) because B has almost no extension-field Hadamards.

## Three largest uncertainties

1. Realistic utilisation of the sumcheck matmuls (0.172 from a degree-2, HBM-bound TensorZKP kernel applied to our
   degree-3, 24-limb-challenge GKR rounds; the rounds shrink by 2x each, the small late rounds run far below peak).
   Factor 2-4x on the A rows.
2. Merkle hash rate on SIMT (20 to 192 GB/s spans 1.7e7 to 9.5e6 for A/BabyBear and 5.5e7 to 6.9e6 for B). Factor
   1.8x on A, 8x on B; a Poseidon2-on-tensor-core or a GPU Blake3 measurement settles it.
3. The Hadamard (SIMT) bucket: priced at 1 Goldilocks multiply = 1/4 of an FP32 FLOP-equivalent at 30 GOPS-per-TFLOP
   (unmeasured); it is 37-43% of A's time. Factor 2x. Also unpriced: hint generation on GPU (CPU anchor only),
   INT32 -> field reduction passes, HBM traffic for the limb-decomposed operands (4-8x the field-element bytes).

## First action for a build lane

Build the Candidate A GKR checker sumcheck over BabyBear^6 as INT8 tensor-core matmuls (TensorZKP's limb layout, 8-bit
limbs, INT32 accumulate, N <= 32 768 chunks, deferred reduction) for one batch of 4096 units, and measure the achieved
fraction of H100 INT8 peak per round. That single kernel is 5.4e9 of the 7.5e9 limb MACs per VU and carries the
largest uncertainty; a measured utilisation replaces the 0.172 calibration and settles whether A lands at ~1e7 or
~3e7. Keep the hash on SIMT Blake3 until that number is in.

## Out of scope, promising

The 24-limb challenge dominates A's sumcheck (challenge x challenge = 576 MACs per product). A small-field
"packed" GKR that keeps round polynomials in the base field until the last log(d) rounds (as in TensorZKP's degree-2
kernel, where trace x trace is 16 MACs) would cut the checker sumcheck by up to 6x for the early rounds; it is a
protocol change (basefold-style folding of the challenge into the trace layout) and was not priced.
