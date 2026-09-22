---
id: r20-proof/a-fusion/20260922T0853Z-report-a-kernels-h100-v2
campaign: r20-proof
lane: a-fusion
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/a_kernels_h100_v2.md
---

# Candidate A on the H100, third pass (lane `a-fusion`): launch-fused logUp, round-fused sumcheck, the v2 shape

Data: `notes-asset:campaigns/r20-proof/assets/a-fusion/reports/a_kernels_h100_v2.json` (built by `backends/gkr/packed/reprice_v2.py` from `backends/numerical/reports/a_fusion/*.json`,
all measured on `vy-g4`, NVIDIA H100 80GB HBM3 SXM, torch 2.6.0+cu124, Triton 3.2).  Labels on every number:
`ARITHMETIC_DIAGNOSTIC`, `authentication excluded`, `security.target = -128` (BabyBear^6), B = 4096, K = 1536, random
tables, kernels only -- **not a proof**.  Previous pass: `note:r20-proof/a-packed2/20260922T0747Z-report-a-kernels-h100` (lane a-packed2).

## 1. The two measured buckets, before -> after

| bucket | shape | before (a-packed2) | after (a-fusion) | per VU | vs floor |
|---|---|---|---|---|---|
| checker sumcheck, one layer table 2^28, k = 3 | direct | 17.08 ms (17.69 in the a-packed2 run) | **12.65 ms** | -- | 2.87x the HBM traffic floor (4.41 ms); 4.17 % of INT8 peak |
| checker sumcheck, 2^26, k = 3 | direct | 5.68 ms | **4.76 ms** | -- | 4.32x floor |
| checker sumcheck, v1 batch (6 layers, padded reads 2^10 x5, 2^9) | fit 2^26..2^28 | 136.6 ms (146 in a-packed2's fit) | **99.6 ms** | 33.4 -> **24.3 us** | -- |
| checker sumcheck, v2 batch (census: 4 layers, s_in 9, 9, 9, 8) | fit | 47.4 ms | **36.1 ms** | 11.6 -> **8.8 us** | -- |
| checker sumcheck, v2 batch (a-v2 exporter: 2 layers, s_in 9, 9) | fit | 26.6 ms | **20.0 ms** | **4.9 us** | -- |
| logUp fractional GKR, v1 (306 lookups/unit, 2^27 leaves) | measured | 427 ms eager (257 ms on this run's eager pass) | **88.9 ms device / 92.0 wall** (level graphs); 103.5 / 107.1 (per-round graphs, Fiat-Shamir) | 104 -> **21.7 us** (25.3 FS) | tree 14 ms; levels 24-26 = 42 ms (HBM/SIMT); 20 small levels 17 ms (latency) |
| logUp, v2 (10 tables of checker_min 3.1, 5.2 M table rows) sequential | measured | -- | 221.6 ms device / 240.9 wall (level); 311 / 333 (per-round) | 54.1 us | each instance pays ~14 ms of latency-bound small levels (T_HDR, 2^19 leaves: 14.4 ms) |
| logUp, v2, the 10 instances on 10 CUDA streams | measured | -- | **84.7 ms device / 84.8 wall** | **20.7 us** (22.7 with the model's 11th table pro rata) | protocol unchanged; per-instance times in parallel 30-53 ms |

Sumcheck "floor" = the mandatory HBM traffic of the algorithm as implemented (every table element read once per pass,
written once per fold) at 3.35 TB/s; the INT8 fraction counts the limb MACs issued to `tl.dot`.

### 1.1 What moved the sumcheck (`kernels_triton.packed_u_{k}`, `kernels_fused.py`)

* **(i) U pass -- the k packed rounds from one read of g, h.**  Round `i <= k` needs `sum eq(gamma_{>=i}, b) g(r_{<i}, x, b) h(r_{<i}, x, b)`;
  the challenges enter only through `eq(r_{<i}, a)` coefficients, so every packed round is a linear combination of the same
  `2^k x 2^k` base tensor `U[c, c'] = sum_{b'} eq(gamma_{>=k}, b') g(c, b') h(c', b')`.  One Triton pass forms all 64
  Montgomery products per `b'`, their 256 limb rows, and one `tl.dot` against the eq limbs; each round is then a 4-64 term
  contraction of `U` on the host side of the graph (`round_from_U`).  **3.48 ms vs 7.83 ms** for the three separate packed
  rounds at 2^28 (the tensor-broadcast formulation of the same kernel is 13.7 ms: Triton's 3-D layouts spill; the generated
  explicit-name kernel in the style of the a-packed2 Hadamards is the one used).  Same field elements in a different
  summation order: transcripts bit-identical to `reference.packed_prover` (31 CUDA agreement tests, k = 0..4).
* **(ii) fold fused into the next Hadamard (`ext_fold_ip`)**: implemented, bit-exact, **measured slower** -- 2.28 ms vs
  0.87 (two `fold_ext`) + 0.88 (`ext_ip`) at 2^28 / round k+2, over a BLOCK_K / warps sweep.  Both kernels are SIMT-bound
  (the `F_{p^6}` Montgomery products), so removing the folded tables' re-read (3.2 -> 2.4 GB) buys nothing and the fused
  kernel's register pressure costs; `fold_ext` alone already runs at 2.8 TB/s.  Kept opt-in (`Kernel(fold_fusion=True)`).
* **(iii) cross-layer fusion**: not attempted -- with (ii) negative the remaining per-layer cost is SIMT work, not passes.
* The remaining 12.65 ms at 2^28: U pass 3.5, fold_k ~1.2, 25 extension rounds ~8 (Hadamard 0.88 + folds 0.87 at the first,
  halving).  Next lever is the `F_{p^6}` product itself (36 `mmul` + 30 adds per element; Karatsuba / Toom over the 6
  coefficients, or 2x16-bit limb halves so the Hadamard feeds `tl.dot` more directly).

### 1.2 What moved the logUp (`logup_graph.py`, `kernels_graph.py`)

CUDA graphs, one per level (27 graphs, 0 host round trips) or one per round (378 graphs, 351 D2H syncs).  The choice
that keeps the transcript identical: the coins live in a **static device buffer** and every challenge-dependent constant
(`eq(r, .)` tables, `prefix`, `eq_x`, `r . R`) is computed **on the device** from that buffer by small Triton kernels inside
the graph (`kernels_graph.eq_table_vars`, `round_consts`, `scale_R`); `bincount` is replaced by an atomic histogram so the
whole tree is capturable.  Replaying a graph with new coins therefore evaluates exactly the eager prover's arithmetic;
7 CUDA tests check both segmentations against `logup_reference.py` message for message, and the published vectors
(`kernels.test_vectors`) are reproduced by every entry point (`tests/test_vectors.py`).

* per-level graphs need the level's coins before the level starts (a sponge fed only by earlier levels, or the
  transcript-independent coins of these measurements); per-round graphs are a drop-in for Fiat-Shamir at +16 %.
* v1: 88.9 ms.  Levels 24-26 (2^24-2^26 pairs) are 42 ms and HBM/SIMT-bound; the 20 smallest levels are 17 ms of
  latency-bound kernel chains (~10 launches per round inside the graph, ~5-8 us each).
* v2's ten tables are ten instances of 2^19..2^24 leaves; sequentially every instance pays those small levels (14-34 ms
  each, 221.6 ms total).  Launched on ten streams they overlap to **84.7 ms**; the per-instance times in parallel
  (30-53 ms) say the overlap is partial -- the host launch loop (~250 graph replays + ~500 pinned H2D writes) and the
  big levels' HBM sharing are next.  A single batched instance (random linear combination of the per-table identities,
  one tree of 2^25 leaves) would be ~2^25/2^27 x 89 ms ~ 25-35 ms but is a protocol change (accounting counts the tables
  separately) and is **not** measured here.

### 1.3 SHIFT: committed per proof vs split-u (`note:r20-proof/checker-min/20260922T0727Z-report-checker-min` 4)

| route | leaves | measured (level graphs, sequential) | table-side cost |
|---|---|---|---|
| SHIFT committed (3.54 M rows + 6.29 M queries, 2^24 leaves, 21 % table share) | 16.8 M | **33.9 ms** (tree 2.1 ms) | T_OP at the same 2^24 with 0.4 % table share is 33.7 ms: the table side costs **~0.2 ms** of GPU time here; its real cost is the 3.54 M multiplicity elements in the Ligero payload (modelled, inside `encoding`) |
| split-u (two 32,768-row tables, 16 lookups/unit each, 2 x 2^23 leaves) | 2 x 8.4 M | 2 x 26.8 = **53.6 ms** | no table-side cost to speak of, but a second instance's fixed small-level cost |

Committing SHIFT is the cheaper route on the GPU (33.9 vs 53.6 ms); PROTOCOL.md 14.2's "implicit table" makes the
commitment a materialised definition rather than 60 MB of circuit text at the same prover cost.  Concurrent streams
shrink the split-u penalty (both instances overlap) but do not reverse it.

## 2. A re-priced: v1 vs v2

`explore.tensor` design A on the H100 at 0.172 utilisation with `gkr_checker` + `gkr_hadamards` replaced by the measured
sumcheck and `logup_fractional_gkr` + `logup_hadamards` + `logup_tree_build` by the measured logUp; encoding, row
combination, hashing, hints, PRG stay modelled.  `overhead.vs_native_peak` per VU, K = 1536.

| | v1 (WP2 checker contracts) | v2 (checker-min gadgets) |
|---|---|---|
| modelled (0.172) | 1.07e7 (t.total 0.432 s: sumcheck 257 ms, logUp 86 ms) | 3.89e6 (0.157 s: sumcheck 64 ms, logUp 35 ms) |
| a-packed2 measured buckets | 1.73e7 (logUp launch-bound 427 ms) | -- |
| **a-fusion measured buckets** | **7.06e6** (0.285 s: sumcheck 99.6 ms, logUp 96.6 ms level graphs) | **4.64e6** (0.187 s: sumcheck 36.1 ms, logUp 93 ms on 10 streams, 11th table pro rata) |
| Fiat-Shamir per-round graphs | 7.46e6 (logUp 112 ms) | 1.08e7 sequential per-round (340 ms) -- the concurrent per-round variant is not measured |
| sequential level graphs (v2) | -- | 8.32e6 (logUp 241 ms) |
| `A-hintfree-depth630` | 6.41e6 | 4.42e6 |

* v2's measured total is **not below 4e6**: no `--breakthrough`.  The modelled/measured gap in v2 is the logUp (35 ms
  modelled vs 93 ms measured): the model prices leaves, the GPU pays per instance.  With a batched single instance
  (1.2) v2 would land near 0.13 s ~ 3.2e6 -- an estimate, not a measurement.
* sumcheck: v2 = 36 % of v1's bucket (2.625 vs 5.75 layer tables of 2^28 at the census shape; 1.5 at the exporter's).
  The v2 layer shape used here is the census's (`accounting.CHECKER_SHAPE_A` under `VERITY_CHECKER_VARIANT=v2`: assert +
  depths 3, 2, 1 with s_in 9, 9, 9, 8, widths 9 / 277 / 274 / 267); the a-v2 exporter's circuit (`PROTOCOL.md` 14.4) is two
  layers at s_in = 9 -- 20.0 ms, in the JSON as `sumcheck_extra_shapes`.

## 3. Omitted / still modelled / still launch-bound

* Ligero encoding, row combination, hashing, hint generation, PRG: modelled at 0.172 utilisation (0.086 s of v1's 0.285 s,
  0.058 s of v2's 0.187 s).  SHIFT's 3.54 M multiplicity elements are in the modelled encoding, not measured.
* authentication excluded; zk none; relation checker not assembled on the GPU; kernels on random tables.
* Fiat-Shamir: the headline numbers use coins independent of the transcript (level graphs; sumcheck coins drawn ahead,
  whole layer as one CUDA graph).  The per-round-graph rows are the Fiat-Shamir-compatible prices (+16 % logUp v1).
* launch-bound remainder: the small logUp levels (17 ms of v1's 89; most of v2's per-instance floor) are kernel chains
  inside graphs -- a persistent per-level kernel for levels under one wave, or the batched instance, is the next step;
  the v2 concurrent run's partial overlap points at the host launch loop (~750 graph/H2D operations per proof).
* v2 logUp tables: the ten of checker_min 3.1 (T_range16 at 10/unit) plus the model's 11th (TNORM_HI) pro rata; the
  model has T_range16 at 14/unit.
* Fold + Hadamard fusion and cross-layer fusion: not in the numbers (measured negative / not attempted).
