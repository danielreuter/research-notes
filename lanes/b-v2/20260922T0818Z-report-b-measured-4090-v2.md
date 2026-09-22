---
id: r20-proof/b-v2/20260922T0818Z-report-b-measured-4090-v2
campaign: r20-proof
lane: b-v2
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/b_measured_4090_v2.md
---

# Candidate B on the RTX 4090 at the checker-v2 shape, every prover bucket measured (b-v2 lane, 2026-09-22)

**Label: `ARITHMETIC_DIAGNOSTIC`-level re-pricing, scope vu.**  vu-level re-pricing at the checker-v2 relation: tensor.py cost model (VERITY_CHECKER_VARIANT=v2) with the commitment, IRS, structured linear test, F_t and F_c quadratic tests, helper inversions and openings replaced by standalone measurements on the RTX 4090 at the V2_SHAPE.md shape (B = 4096, K = 1536, 2^-128, BabyBear / BabyBear^6, HVZK rows included, authentication excluded).  Device: NVIDIA GeForce RTX 4090 (128 SMs, driver 580.159.04, CUDA runtime 12090, cupy 14.2.0).  Run `r20260922-075021-2b1b` (v2 shape); v1 reference runs `r20260922-064722-07c7`, `r20260922-065537-279b`, `r20260922-073017-0924`.  CUDA-event timings, warm, median of 7; every kernel bit-exact against its numpy / Python reference in the run (`all_bit_exact = True`), including the new `F_c`-triple quadratic kernel (`buckets_v2.py`).  Layout and counts: `backends/direct/encode/V2_SHAPE.md`.

## v1 vs v2, same kernels, same card (B = 4096, K = 1536, 2^-128, BabyBear^6, HVZK rows, Blake3 leaves, openings from the kept store)

| | v1 shape (`note:r20-proof/b-commit/20260922T0733Z-report-b-measured-4090`) | v2 shape (this run) | v2 / v1 |
|---|---|---|---|
| Ligero rows x [16384, 4096] | 310,602 | **104,217** (34,093 witness + 58,710 helper + 11,408 table-side + 6 blinding) | 0.34x |
| committed bytes / VU | 1,164.7 kB | **388.8 kB** | 0.33x |
| quadratic rows | 33,485 `F_t` | 3,502 `F_t` + 9,785 `F_c` (6 coordinate rows each) | |
| helpers inverted | 125.9M | **43.6M** (37.4M queries + 6.26M table rows) | 0.35x |
| linear test structure | M = 3, X ~ 130-256 | M = 2, X = 9,780 (table-side inverse rows) | |
| commitment (fused encode -> Blake3 -> root, cosets kept) | 49.4 ms | **16.2 ms** (0.155 us/row) | 0.33x |
| linear test (structured, lazy) | 7.15 ms | **8.29 ms** (combine 2.03 + exceptional 6.17) | 1.16x |
| IRS row combination | 5.6 ms | **2.10 ms** | 0.37x |
| quadratic test | 7.8 ms | **5.4 ms** (`F_t` 0.84 + `F_c` helper triples 4.54 with coset 1 read from the kept store; 11.12 if re-encoded) | 0.69x |
| helper inversions | 28.8 ms | **5.2 ms** (0.12 ns/element, 0.70 of traffic floor) | 0.18x |
| openings (t = 192 + paths) | 5.1 ms | **2.5 ms** | |
| modelled remainder (r^T A scalars, hints, PRG) | 12.5 ms | 2.7 ms | |
| **total per 4096-VU batch** | **116.4 ms** (89% measured) | **42.4 ms** (94% measured) | **0.36x** |
| **overhead.vs_native_peak** | **2.89e+06** | **1.05e+06** | |
| per VU | 28.4 us | 10.3 us | |

Variant (b), public table coefficients (`V2_SHAPE.md` section 4; MODELLED layout, measured at its shape): 35.7 ms, overhead 8.86e+05 (94,439 rows, 352.1 kB / VU).

## Re-pricing rows

~~~text
table side           gpu       total ms  commit  lin+irs   quad    inv   open  model  meas%  overhead  label
helper_rows          RTX4090       42.4    16.2     10.4    5.4    5.2    2.5    2.7    94%  1.05e+06  MEASURED buckets on RTX 4090 at the checker-v2 shape (commitment, structured linear test, IRS, F_t + F_c quadratic tests, inversions, openings); r^T A scalars, witness / hint generation, PRG modelled
helper_rows          A100          91.9    34.2     22.0   11.4   11.0    5.3    8.0    91%  2.28e+06  SCALING: measured buckets / 0.47 (INT32 issue-rate ratio), modelled buckets at A100 peaks
helper_rows          H100          52.0    19.9     12.8    6.6    6.4    3.1    3.1    94%  1.29e+06  SCALING: measured buckets / 0.81 (INT32 issue-rate ratio), modelled buckets at H100 peaks
public_coefficients  RTX4090       35.7    16.2      5.2    5.4    3.8    2.5    2.7    92%  8.86e+05  MEASURED buckets on RTX 4090 at the checker-v2 shape (commitment, structured linear test, IRS, F_t + F_c quadratic tests, inversions, openings); r^T A scalars, witness / hint generation, PRG modelled; table side: public_coefficients (linear test, inversions at its shape; commitment / IRS / openings at the helper_rows row count: upper bound)
public_coefficients  A100          77.8    34.2     11.0   11.4    8.0    5.3    8.0    90%  1.93e+06  SCALING: measured buckets / 0.47 (INT32 issue-rate ratio), modelled buckets at A100 peaks; table side: public_coefficients
public_coefficients  H100          43.8    19.9      6.4    6.6    4.6    3.1    3.1    93%  1.09e+06  SCALING: measured buckets / 0.81 (INT32 issue-rate ratio), modelled buckets at H100 peaks; table side: public_coefficients
~~~

## Batch-size crossover

v2 pays the tables per proof: 11,408 table-side Ligero rows (multiplicities + inverses) and 6.26M table inversions, plus the exceptional linear-test rows: **9.1 ms fixed per proof** (measured per-row / per-element rates).  The rest is **8.1 us per VU** against v1's 28.4 us per VU.  time(v2, B) < time(v1, B) for **B > 446 VUs** (in committed rows the crossover is B > 215).  At B = 4096 the fixed part is 21% of the batch; at B = 64 v2 would cost 9.6 ms against v1's 1.8 ms.  Below the crossover the SHIFT table (57% of the rows) should be its split-u variant (`note:r20-proof/checker-min/20260922T0727Z-report-checker-min` section 4).

## What the measurements say

* **The relation change is worth 2.7x on B's measured buckets**, close to the 2.98x row ratio: every bucket is per-row streaming work, so 3x fewer committed rows is 3x less time; the tables cost 11% of the rows and one exceptional-row pass in the linear test.
* **Inversions shrink, not grow**: v1's 320 range-chunk lookups per unit were the helpers; v2's 95 lookups + 6.26M table rows are 0.35x as many elements.  Still 0.70 of the traffic floor.
* **The `F_c` helper triples are the quadratic test now**: 4.5 ms for 9,785 rows reading coset 1 from the kept store (0.46 us/row) -- the store the fused commitment already keeps for the openings; 11.1 ms if the coset is re-encoded instead (9 encoder calls per row on average).
* The linear test's exceptional rows (the table-side inverses, 9,780 through the general path) are 6.2 ms of its 8.3; variant (b) removes them (X = 1,632).
* Still modelled: r^T A scalars / pattern (O(rows + pattern)), witness / hint generation (v2 has 15 hints per unit, v1 225: the CPU anchor's 4.7 s per 4,096 units is a v1 number), prover randomness; the BabyBear repair rows are checker-min's modelled deltas (stated in `V2_SHAPE.md` section 2).

## Inversions: blocked Montgomery trick (`BatchInverterBlocked`, run `r20260922-080235-765c`)

One stored prefix per G = 4 elements instead of one per element: traffic (3 + 2/G) x 24 N bytes instead of 5 x 24 N, (4 - 1/G) `F_c` products per element instead of 3.  At the v2 helper count: **5.20 ms** (0.70 of its traffic floor 3.63 ms) against 7.78 ms for the plain kernel (0.67 of 5.19): 1.50x.  Bit-exact against `ref.batch_inverse` at N = 1000 / 4097 / 70000, G = 2 / 4 / 8 (`exact = True`).  At the v1 helper count (125.9M) the same kernel is 16.6 ms (G = 8, 0.59 of its floor) against 28.8 ms: v1's total becomes 104.2 ms.  The inversions bucket above uses the blocked kernel (the `batch_inverse` rows carry `ms_median_plain`).

## Encoder: radix-4 shared-memory stages (`RSEncoderSIMT(radix4=True)`, run `r20260922-081137-109d`)

The shared-memory stages (m < THREADS; the register stages m >= THREADS were already free of shared-memory traffic) are fused in pairs: the quad is closed under both radix-2 stages, so the arithmetic is unchanged (bit-exact, `exact = True`) with half the shared-memory traffic and half the `__syncthreads`.  Encoder alone at 104,217 rows: 10.26 -> **9.18 ms** (1.12x); fused commitment (Blake3, cosets kept): 16.27 -> **15.11 ms** (1.08x; the hash and the store write are unchanged).  At the v1 row count: 49.2 -> 45.6 ms.  The commitment bucket above is the run-`r20260922-075021-2b1b` measurement scaled by 0.929 (`ms_median_radix2` kept on the row); `commit_stream.py`'s default encoder is now radix-4.

## Files

`backends/direct/encode/V2_SHAPE.md`, `v2_shape.py` / `v2_shape.json`, `buckets_v2.py` (the `F_c`-triple kernel + reference), `v2_bench.py`, `results_v2_r20260922-075021-2b1b.json`, `reprice_v2.py` (this report); ledger `ledger/b-v2.jsonl`.
