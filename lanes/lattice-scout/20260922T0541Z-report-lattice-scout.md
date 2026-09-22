---
id: r20-proof/lattice-scout/20260922T0541Z-report-lattice-scout
campaign: r20-proof
lane: lattice-scout
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/lattice_scout.md
---

# Lattice scout: is there a cheaper complete prover for the bounded-integer checker? (lane/lattice-scout, 2026-09-22)

Generator: `verity_numerical.explore.lattice` -> `notes-asset:campaigns/r20-proof/assets/lattice-scout/reports/lattice_scout.json`; pinned by `tests/explore/test_lattice.py`. Every
number is a cost-model estimate over the frozen WP2 census (K=1536 VU, B=4096, 2^-128) in `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor`'s units (UINT8 limb
MACs, H100 INT8 peak 989.5 T MAC/s at utilisation 0.172, native 9.85 ps/VU) unless it is a cited paper's CPU benchmark.
Nothing here was run on a GPU or a pod.

## Verdict

1. **Complete alternative lattice backend: NO, not worth a lane.** Every lattice system that can express the checker's
   coordinate-wise quadratic constraints (Hachi, Akita, Neo/SuperNeo, Symphony, LatticeFold+) is "a sumcheck over an
   extension field of Z_q + an Ajtai-committed witness". Its prover is A's prover with the commitment layer swapped:
   the checker sumcheck (5.4e9 limb MACs/VU, 60-70% of A) is untouched, so the ceiling on the gain is A's encoding +
   Merkle buckets (~20% of A at 50 GB/s Blake3) minus the lattice additions. The other family, LaBRADOR/Greyhound
   dot-product constraints, wastes d-1 = 63 coefficients of every ring element on a coordinate-wise relation and its
   r x N aggregation (`h_ij = <phi_i, s_j>`) prices at 7.8e11 MACs/VU, overhead 4.7e8: 40x above A. C (3.1e6,
   designated verifier, VOLE) is out of reach of any public-coin lattice system by 3x before the norm machinery.
2. **Reusable component: MAYBE, conditional on the hash rate.** A lattice PCS (Ajtai INT8 GEMM on the checker's own
   16-bit range chunks, Akita-style K-ary fold, exact digit range check on the folded response) replacing RS-Ligero +
   Merkle in A is hash-free and models at **0.74x A on the 64-bit-q / Goldilocks^3 row (9.3e6 vs 1.25e7)** and **1.01x A
   on the 32-bit-q / BabyBear^6 row (1.08e7 vs 1.07e7)**, both at 50 GB/s Blake3 and fold arity 64. The whole delta is
   inside the two known uncertainties: the reference hash rate (10 GB/s: A is 2.5e7 and the swap wins 2.7x; 190 GB/s:
   A is ~9.5e6 and the swap loses) and the fold arity (K=16: 1.46e7, K=256: 9.6e6). For B it is not a component: B's
   row tests are Ligero properties; with a lattice PCS B becomes an explicit-trace Spartan design (7.9e6 in the model,
   but that number is the flattening of A's layered GKR, obtainable with Ligero as well, not a lattice effect) and
   loses its local-proving depth story.
3. **Follow-up: nothing before the GPU Blake3/Poseidon2 rate is measured** (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor uncertainty 2). If it lands below
   ~30 GB/s, a lane would first (a) run `jolt-akita` (Rust, 32-bit profile) on A's committed object (44k 16-bit chunks x
   4096 VUs) on vy-cpu2 for a measured commit + open per VU beside the Ligero CPU number, (b) write the INT8 Ajtai GEMM
   kernel (shared A across the batch) and measure its utilisation on the L40S, (c) price the response range check against
   logUp on the same digits with Akita's real fold schedule. No lattice lane before that.

Soundness reached: 2^-120 .. 2^-125 at d = 64 (LaBRADOR Thm 5.1 per level; Akita's per-fold budget), not 2^-128 without a
larger ring or repetition. ZK: none in any implementation found (Akita: "not ZK"; Greyhound: sketch; LaBRADOR: LaZer shim).

## 1. Candidates

~~~text
construction (paper, year)             statement                     assumption / ring / q       prover dominant       proof     impl          ZK    measured prover
LaBRADOR (Beullens-Seiler, CRYPTO23,   dot-product constraints over  MSIS, Z_q[X]/(X^64+1),      O(N) ring mults +     47-58 KB  lattice-dogs  no    --
  ePrint 2022/1341)                    R_q + one global l2 bound;    q~2^32 single-prec, NOT     r x N aggregation     (R1CS     labrador (C,  (LaZer
                                       R1CS mod 2^64+1 by reduction  NTT-friendly (inertia)      products h_ij         2^20)     AVX-512)      shim)
Greyhound (Nguyen-Seiler, CRYPTO24,    univariate PCS: sqrt(N) x     MSIS, d=64, q~2^32          Ajtai commit + inner  46-53 KB  same repo     sketch commit 132 s + prove 41 s
  2024/1293)                           sqrt(N) reshape + LaBRADOR    (q = 5 mod 8)               products, NTTs                                     at N=2^30, 1 SPR core (T2)
Hachi (Nguyen-O'Rourke-Zhang, 2026/156) multilinear PCS over F_{q^k}, MSIS l_inf, q~2^32, d=2^10  Ajtai + ring-switched 55 KB     hachi-pcs     no    3-5x Greyhound commit (Fig 10)
                                       sumcheck via ring switching   (Lattice Estimator, 128 b)  sumcheck                        (Rust proto)
Akita (Dao...Thaler, 2026/1983)        multilinear PCS, K-ary fold   MSIS, per-matrix d=64/32/   Ajtai GEMM (pay-per-  61-72 KB  jolt-akita    no    commit 3.46 s + open 2.71 s,
                                       to completion, pay-per-bit,   16, q = 2^32-99 / 64 / 128  bit) + exact digit    per       (Rust, in           2^30 x 32-bit coeffs, 8 thr
                                       batched openings, in Jolt     bit profiles (Table 5)      range check O(bL)     opening   Jolt)               Ryzen 9950X (T8-9)
LatticeFold / + (Boneh-Chen, 2024/257, folding CCS/R1CS over a       MSIS                        Ajtai + monomial      ~110 KB   none public   no    none public
  CRYPTO25 2025/247)                   64-bit field                                              range proof           (L=5 est)
Neo / SuperNeo (Nethermind 2025/294,   CCS folding over ext. of a    MSIS                        Ajtai pay-per-bit +   --        none public   no    none public
  2026/242)                            small prime, one sumcheck                                 HyperNova sumcheck
Symphony (Chen, 2025/1905)             high-arity folding, degree-3  MSIS                        committing the input  --        none public   no    none public
                                       sumcheck over E                                           witnesses
Lova (Fenzi et al., 2024/1964)         Nova-style folding, exact l2  plain SIS, unstructured A,  dense Z_{2^k} matmul  --        Rust          no    none public
                                                                     power-of-two q              (lambda x wider A)
HyperWolf/* (Zhang-Gao-Xiao, 2025/922) k-dim tensor fold PCS, exact  MSIS over rings             Ajtai + tensor folds  ~53 KB    none          no    none public
                                       l2 via <f,f> lifting                                                            (2^30)
RoK family (Klooss-Lai-Nguyen-Osadnik  verifier-succinct RoKs, exact vanishing-SIS (structured,  Ajtai + RoK reduc-    109-115   RoKoKo in     no    RoKoKo 8.27 s commit / 4.43 s
  2025: SISsors, RoK&Roll, SALSAA,     norm bounds                   not plain MSIS)             tions                 KB        Akita T8            open at 2^35 bits (100-bit stat)
  RoKoKo)
~~~

Setup: all transparent (uniform matrices). Verifier: LaBRADOR/Greyhound linear-ish (2.8 s at 2^30); Hachi 227 ms;
Akita 8-33 ms. Two cross-cutting facts. (i) **The NTT-friendly-ring GPU shortcut is closed for LaBRADOR-style
aggregation**: zkSecurity (Raikos-Wong, 2026-04-30) showed `icicle-labrador` (GPU, BabyBear x KoalaBear composite q,
fully splitting ring) has ~31 bits of soundness, `condor-rs` ~6, `Lazarus` ~1; only the non-splitting `lattice-dogs`
and LaZer are unaffected. Sumcheck-based systems avoid this by aggregating over an extension field E instead of R_q.
(ii) The **relaxed-opening issue does not touch the exact checker** in a one-shot PCS use: binding holds for weak
openings (any `z` with `||z|| <= 2^16 x challenge slack`), and every committed value is the checker's own 16-bit range
chunk, already bounded by the lookups; the exact digit range check is needed only on the folded response. In a
recursive/IVC use (LatticeFold) the norm proof on the source is mandatory and the slack compounds per fold.

Tensor-core mapping, honestly: the Ajtai commitment is a dense INT8 GEMM `(kappa d) x (digits) x B` in the coefficient
domain (A entries 8 limbs at q=2^64, digits 2 limbs; NTT-domain evaluation would turn the short digits into full Z_q
elements and lose pay-per-bit); the fold opening and the digit range check are ordinary sumchecks (priced with
`tensor.sumcheck_macs`, degree 2 and 3); the norm/JL machinery of LaBRADOR is not a matmul and is not needed on the
sumcheck route; NTTs appear only in the LaBRADOR route, which is not a candidate.

## 2. Our relation in their language

~~~text
per K=1536 VU (census)          value        source
mul / lin / lookups             34,370 / 10,948 / 29,379     census_vu; 27,267 of the lookups are range predicates (7..32 bits)
committed bits (A object)       inputs 49,168 + hints 129,665 + lookup outputs 95,232 + query wires 433,152 = 707k
  -> 16-bit chunks              44,202 digits/VU (B object: +products/materialised 1.06M bits -> 110,442 digits)
  -> Ajtai output               kappa d = 896 Z_q coords = 7,168 B per commitment (q64_chunk16); 88 KB/VU of digits held
exactness                       widest hint 25 b, widest product 50 b, <= 16 terms per identity -> q > 2^54: q = 64-bit
                                is exact; q = 32-bit needs the fields lane's small-field repairs re-derived for a q = 5 mod 8
                                prime (BabyBear is fully splitting: not LaBRADOR/Greyhound's ring)
norm bound vs range checks      a lattice norm bound is one global l2/l_inf statement (slack ~2 by JL, exact by <f,f>
                                lifting); the 27,267 per-value range predicates stay constraints (digit vanishing
                                polynomials or logUp).  Nothing in the checker gets cheaper because w is short except the
                                commitment (pay-per-bit).
Z_q multiplications             commit 896 x 44,202 = 3.96e7 Z_q MACs/VU (6.3e8 limb MACs); response commit 3.5e7 limb
                                MACs; fold sumcheck 4.6e8; digit range check (degree-8 vanishing, 3 layers, 77k elems)
                                1.3e9; batch of 4096: 1.6e11 Z_q MACs on the commitment alone, one GEMM (896 x 44,202 x 4096)
ring / norm                     d = 64 (Akita first-level matrix; LaBRADOR challenge set > 2^128); committed digits
                                |z| <= 2^16, response coefficients 26 bits (16 + log2 K + 4 opnorm), 7 base-16 digits each
~~~

## 3. The number

~~~text
design                 q   field        digits/VU  MACs/VU   matmul%  depth  committed B/VU  overhead H100@0.172  reference (same field)
A+lattice-PCS         64   Goldilocks^3  44,202    9.2e9     59%      401    88,404 (7,168 out) 9.27e6             A 1.25e7  (0.74x)
A+lattice-PCS         32   BabyBear^6    44,202    9.1e9     50%      401    88,404             1.08e7             A 1.07e7  (1.01x)
A+lattice-PCS hex     64   Goldilocks^3 176,805    1.2e10    61%      403    88,403             1.16e7             A 1.25e7  (0.93x)
A+lattice-PCS, K=16   32   BabyBear^6    44,202    1.2e10    51%      401    88,404             1.46e7             A 1.07e7  (1.37x)
A+lattice-PCS, K=256  32   BabyBear^6    44,202    8.0e9     50%      401    88,404             9.57e6             A 1.07e7  (0.90x)
B+lattice-PCS (Spartan) 64 Goldilocks^3 110,442    8.5e9     64%      119    220,884            7.91e6             B 1.43e7 / A 1.25e7
LaBRADOR-direct       32   --            63,751 polys 7.8e11 --       --     --                 4.66e8             (Greyhound CPU anchor 6.7e10)
note:r20-proof/tensor-cost/20260922T0450Z-report-tensor rows                                                                                   A 1.07e7 (BabyBear) / 1.25e7 (Goldilocks), B 1.43e7, C 3.1e6
~~~

Component split of the 9.2e9 (64-bit row): checker GKR 5.4e9 (unchanged from A), logUp fractional GKR 1.3e9
(unchanged), digit range check 1.3e9, Ajtai commit 6.3e8, fold opening sumcheck 4.6e8, response commit 3.5e7; hash bytes 0
(A: 0.12 s/batch of Blake3 at 50 GB/s). Sequential depth 401 rounds vs A's 381 (+~20 fold/range rounds). Committed
bytes 88 KB/VU of digits vs B's 1.15 MB/VU of Ligero columns; the transmitted commitment is 7 KB per opening (Akita:
61-72 KB proof per batched opening).

Three biggest uncertainties (factor): **hash rate of the reference** (10-190 GB/s, 19x: it is the entire saving);
**the lattice sumchecks' pricing** (0.3-3x: fold + range check as tensor-core sumchecks at 0.172; Akita's O(bL) SIMT
range check and a real multi-level fold schedule are unmodelled); **MSIS output size** (0.3-3x on the GEMM: the raw
BKZ heuristic under-shoots Akita's Table 5 anchor by 3.6x and is scaled to it; the Lattice Estimator decides; the
commitment is 7% of the row so this does not flip the verdict, but a 64-bit q forces the Goldilocks^3 checker row, +17%).

## 4. What is NOT done

No lattice code was run; no GPU number; no Lattice Estimator run (heuristic kappa d = 896, anchored); ZK cost not
modelled (unbuilt everywhere); the 2^-128 union bound over folds + range layers + checker sumcheck not established
(2^-120..-125 delivered); B+lattice-PCS's Spartan sumcheck is a flat re-accounting that also applies to Ligero.
