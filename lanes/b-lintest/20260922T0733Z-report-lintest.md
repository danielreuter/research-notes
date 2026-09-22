---
id: r20-proof/b-lintest/20260922T0733Z-report-lintest
campaign: r20-proof
lane: b-lintest
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/direct/encode/LINTEST.md
---

# B-Ligero's linear test through the structure of r^T A (b-lintest lane, 2026-09-22)

**Scope: component** (the linear-test bucket of the B prover, measured standalone on the RTX 4090 `vy-g2`), plus a
vu-level re-pricing labelled `ARITHMETIC_DIAGNOSTIC` in `note:r20-proof/b-commit/20260922T0733Z-report-b-measured-4090`.  Recorded runs:
`r20260922-071843-ac9a` (SIMT path + the b-commit general path in the same run), `r20260922-072315-6497` (same +
the INT8 tensor-core variant), `r20260922-073017-0924` (M = 1..4 with the lazily reduced kernel).  Kernel: `lintest_structured.py`; tests `tests/test_lintest_structured.py`.

## 1. The test as B-Ligero specifies it (PROTOCOL.md section 5 step 5, section 6; AHIV22 4.7)

Committed matrix `W` (both tableaux vertically juxtaposed): `rows = 310,602` Ligero rows of `k = 4096` message
symbols (`l = 3840` payload + 256 randomizers), each interpolated as `U_i(x)` of `deg < k` on the `k`-point message
domain and evaluated on the `n = 16384` domain (coset-major layout; coset 0 is the message).  The linear constraint
system `A w = b` (335.5M constraints over the `F_t` witness vector `w` = the payload symbols of all rows) is tested with
one verifier element `rho_add` in `F_c = BabyBear^6`:

~~~text
r_add = (1, rho, rho^2, ..., rho^(#lin - 1))                       (PROTOCOL.md section 6: "powers combination")
r^T A  in F_c^(#w), laid out on the rows of W: row i -> R_i(x), deg < k, R_i(zeta_j) = (r^T A)[i][j] (0 at randomizers)
prover sends   q(x) = sum_i R_i(x) U_i(x)   (deg < 2k - 1: 8,192 evaluations on cosets 0 and 1, or 2k - 1 coefficients)
             + the linear-test blinding row (a random deg < k row with payload sum 0; HVZK, added, not multiplied)
verifier:      sum_{j < l} q(zeta_j) = r^T b     (zeta_j = the payload positions = the first l systematic columns)
               q(eta_c) = sum_i R_i(eta_c) U_i(eta_c) for the t = 192 opened columns eta_c
~~~

Soundness: Schwartz-Zippel over the powers, `(#lin - 1)/|F_c| = 2^-163.7` (section 9.1), plus Ligero's proximity terms.
**What the b-commit kernels timed is exactly this `q` for an arbitrary `r^T A`**: per row, the 6 BabyBear coordinate rows
of `(r^T A)[i]` are each INTT'd and re-evaluated on coset 1 (6 encoder calls, `ncosets = 1`), the witness row is
re-evaluated on coset 1 (1 call), and `combine_linear` accumulates the 6 coordinate products over the 8,192 points: 14
size-4096 transforms per row, 149.4 ms per B batch (`note:r20-proof/b-commit/20260922T0733Z-report-b-measured-4090`), with the 30.5 GB of `r^T A` (6 x the
witness) fed as resident pseudo-random data and its generation not counted.  The specified test is what they timed;
the general algorithm is what makes it expensive.

**Does `q` need the full codeword domain?**  No: `deg q < 2k - 1`, so 8,192 evaluations (cosets 0 and 1; the kernels'
domain) or `2k - 1` coefficients determine it; the verifier's payload sum reads the systematic evaluations directly and
its column checks at the `eta_c` (3/4 of which lie in cosets 2, 3) cost `O(t * 2k)` `F_c` operations from either
representation (Horner on coefficients, or barycentric evaluation from the 8,192 points).  Sending `q` on 16,384 points
would be pure waste; the halving to `2k` is already in the kernels.  With the structure below the domain size stops
mattering to the prover: the heavy part is `k`-wide and touches no codeword.

## 2. The structure of A for the chain AIR layout (PROTOCOL.md section 12, section 4)

Every one of the `96 B = 393,216` unit rows of the trace satisfies the same local constraint pattern (the WP2 contracts
emitted per row, the epilogue on every row, the five chain selectors `vu.step/first/last/inv/claim`); the only
row-to-row coupling is the transition constraints, which read the NEXT unit (`vu.link[hi,lo]`, `vu.next_step`,
`vu.next_first`).  In Ligero-B terms (section 4.1, the 1 064-slot unit layout of the census):

| constraint class | count per unit | in `A` |
|---|---|---|
| `lin` identities + range-chunk splits | 137 (est.) | fixed coefficient vector on the unit's own slots |
| alignment copies for the 358 quadratic triples | <= 716 | `w_a - w_b = 0`, both slots inside the unit |
| transition linkage (as Ligero linear constraints: `d = c_in' - y` per 16-bit limb, `d' = s' - s - 1`, `first' - last`; the `(1 - first')` selector product is a quadratic triple on `d`) | ~4 | fixed vector on own slots + fixed vector on the NEXT unit's slots |
| helper-side per query (`h_j (z_T - w_j) = 1`, section 4.2): `F_c`-linear part `(M_{z_T} h_j)_c - prod_{j,c} = [c = 0]` and the copies of `h_{j,c}` and `w_j` into the triple rows | 306 x (6 + copies) | fixed vectors (they depend on `z_T`, fixed for the batch) on the unit's helper coordinates and slots |
| boundary: `vu.row0_step`, `vu.row0_first` | 2, unit 0 only | breaks the pattern on unit 0 |
| last unit: no successor, its transition constraints are absent | -- | breaks the pattern on unit 393,215 |
| table side: `h_v (z_T - t_v(beta_T)) = m_T(v)` | `|T| = 66,623` in total | coefficients vary with `v`: not a per-unit pattern (~130 Ligero rows of helper coordinates + multiplicities) |
| `sum_j h_j - sum_v h_v = 0` (per table, 6 coordinate equations) | 5 | coefficient 1 on every helper coordinate: a CONSTANT row |

So `A` is block-banded: `|P|` = one pattern `P` of `C ~ 3,000` constraint vectors per unit (own part `P_c`, neighbour
part `P'_c`, `P'_c != 0` only for the ~4 transition constraints), repeated 393,216 times along the diagonal, plus a few
hundred irregular rows.  No power-of-two padding exists in Ligero (the AIR's 25% zero-VU padding is a FRI artefact).

### 2.1 The powers combination collapses |P| to a scalar

With `r_add` = powers of `rho` and the constraint enumeration **unit-major** (index `u C + c` for constraint `c` of unit `u`,
the boundary and table-side constraints after all unit blocks), unit `u`'s slots receive

~~~text
(r^T A)|_u = sum_c rho^(u C + c) P_c  +  sum_c rho^((u-1) C + c) P'_c  =  rho^(u C) * pi,     pi := sum_c rho^c P_c + rho^(-C) sum_c rho^c P'_c
~~~

ONE fixed `F_c` vector `pi` (length 1 064, computed once per batch from `rho` and the public pattern), scaled per unit by
the geometric factor `rho^(u C)`.  A Ligero row holding whole units `u = i S + s` (`s < S`; `S = 3` units of 1 064 per
3 840-payload row, 17% waste, or the transposed layout of section 2.3) is therefore

~~~text
(r^T A)[i] = rho^(i S C) * E,       E := sum_s rho^(s C) shift_s(pi)    (one fixed F_c row, zeros at the randomizers)
~~~

The same holds for the helper rows (pattern `pi_T` on the unit's 306 x 6 helper coordinates, rows holding whole units'
helpers: 12 units x 306 = 3 672 of 3 840, or 2 units x 1 836 in the coordinate-interleaved layout), and the sum
constraint contributes a constant row `E_sum` with scalar `rho^(idx_T)` independent of the row.  Altogether:

~~~text
(r^T A)[i] = sum_m s[i][m] E_m         M = 3 fixed rows (E_witness, E_helper, E_sum), s[i][m] in F_c (zero where the class does not apply)
           + exceptional rows          X ~ 130: the rows holding unit 0 and unit 393,215, the ~110 table-side helper rows, the 18 multiplicity rows
~~~

`tests/test_lintest_structured.py::test_toy_chain_system_rta_is_scalar_times_fixed_row` builds a small chain system
(`UnitPatternSystem`: own + neighbour coefficients, transition constraints absent on the last unit, boundary constraints on
unit 0, `S` units per row), computes `r^T A` the general way from the explicit matrix, and checks `r^T A == s_i E` exactly
on every regular row with exactly the two predicted exceptional rows.

### 2.2 The shortcut

Interpolation is linear, so with `G_m := enc(E_m)` (6 coordinate encodings per fixed row, once per batch):

~~~text
q(x) = sum_i R_i(x) U_i(x) = sum_i sum_m s[i][m] G_m(x) U_i(x) = sum_m G_m(x) * V_m(x),     V_m := enc( sum_i s[i][m] W_i )
~~~

1. `pi`, `E_m`, `G_m`: `O(C * 1064)` `F_c x F_t` products + `6 M` encoder calls (microseconds; 0.1-0.2 ms measured with the launch overheads).
2. `sum_i s[i][m] W_i`: an `F_c`-scalar combination of the `k`-wide witness rows, all `M` at once -- the IRS row
   combination's kernel (`combine_scalar`) with `6 M` accumulators: ONE read of `W` (5.09 GB).
3. `V_m` on coset 1 (`6 M` encoder calls), `q = sum_m G_m * V_m` pointwise over `F_c` on the 8,192 points (`36 M`
   multiplies per point), plus the general path (7 encoder calls + `combine_linear`) for the `X` exceptional rows.

Per-row transforms: **14 -> 0**; per-batch transforms `12 M + 14 X` (~1,900 instead of 4.35M).  The verifier's side
collapses the same way: `sum_i R_i(eta_c) U_i(eta_c) = sum_m G_m(eta_c) * sum_i s[i][m] U_i(eta_c)` (+ exceptional rows),
i.e. `M` scalar combinations of the opened columns (the work it already does for the IRS test) instead of 310,602
interpolant evaluations per opened column.

### 2.3 Soundness and what is a convention

Same test, same `r`, same `q`, same transcript: the prover computes the polynomial the protocol defines by a different
algorithm; the verifier's checks are unchanged (and can, but need not, use the same factorisation).  The protocol has to
FIX two public conventions that the shortcut relies on, both already implicit in "the layout is the prover's" and
"powers over the linear constraints":

* the **constraint enumeration order** (unit-major blocks: every constraint that involves only unit `u` and its
  successor -- including unit `u`'s helper-side equations -- sits in block `u`; boundary and table-side constraints after
  the blocks).  Any enumeration gives the same Schwartz-Zippel bound `(#lin - 1)/|F_c|`; the bound does not depend on the
  order, only on the count.
* the **row layout holds whole units** (witness rows `S = 3` units; helper rows 12 units of `306 x 6` coordinates, or
  the transposed "one AIR column x 3 840 consecutive units" layout, in which `(r^T A)` on row `(column j, block b)` is
  `pi[j] rho^(b l C) * (rho^(u C))_u`: also one fixed row).  This is the WP3 layout decision `PROTOCOL.md` 10.8 leaves open.

Neither changes a message, a challenge space or an error term.  Section 9.1's powers-combination term was already the
derivation this lane's protocol adopted (10.4); nothing new is assumed.  **Note for the record**: if the protocol ever
returned to an explicit uniform `r` per constraint (AHIV22's original), the shortcut would not apply -- see 2.4.

### 2.4 Why the dense `[rows x |P|] . [|P| x n]` product of the brief does NOT pay, and the uniform-r case

With uniform `r` the unit's `r^T A` is `sum_c r_{u,c} P_c`: `|P| = C` fixed vectors per unit slot, `S C ~ 2,559` per
witness row (853 linear constraints per unit in the census; 3,215 in the AIR).  Then either

* encode the `S C` shifted pattern rows once and form `q = sum_{s,c} enc(e_{s,c}) * enc(sum_i r_{(i,s),c} W_i)`: the
  inner combination is a `[S C x rows] . [rows x k]` product = 109k x 2,559 x 4,096 x 6 = 6.9e12 `F_t` MACs = 1.1e14
  INT8 limb MACs (4 x 4 limbs) = **170 ms at 100% of the 4090's INT8 dense peak** (660 T MAC/s) -- no better than the
  149 ms measured, before any utilisation loss; or
* the brief's `[rows x |P|] . [|P| x n]` on the 8,192-point domain: 109k x 2,559 x 8,192 x 6 MACs = 1.4e13 `F_t` MACs =
  2.2e14 limb MACs = **330 ms at INT8 peak**; or
* the transposed layout with the `C x blocks` coefficient rows `r_c|_b` encoded: 3,215 x 103 x 6 = 2.0M transforms vs
  4.35M now: 2.2x at best.

"Expressible as a matmul" fails here for the same reason as for the encoder: the dense product multiplies out a structure
whose rank is tiny.  The powers combination makes the rank 1 per row class, and the matmul degenerates to a rank-`M`
update whose only heavy operand is the witness read once.  Which is why B-Ligero's linear test, the "one B bucket that
might be a matmul", is a memory-bound GEMV -- on tensor cores or on SIMT.

## 3. Op count and roofline, RTX 4090 (HBM 1,008 GB/s; INT8 dense 660 T MAC/s; SIMT ~20.6 T INT32 IMAD/s = 128 SM x 64 lanes x 2.52 GHz, ~41 T ops/s counting the add)

| step | work per B batch | floor | measured (median of 7, CUDA events, warm) |
|---|---|---|---|
| general path (b-commit): 14 transforms/row + `combine_linear` | 1.07e11 butterflies (24,576 per transform x 14 x 310,602) + 6 mont-muls per point; reads `r^T A` 30.5 GB + `W` 5.1 GB | 35 ms HBM (with `r^T A` materialised); ~110 ms at the encoder's measured 950 G butterflies/s | **149.9 ms** (same run) |
| (1) `pi`, `E_m`, `G_m` | `6 M` encoder calls on 1 row each | launch-bound | 0.10 (M=1) - 0.18 ms (M=4) |
| (2) `sum_i s[i][m] W_i`, SIMT `combine_multi` | read `W` once = 5.09 GB; `7.63e9 M` mont-muls (~6 INT32 ops each) | 5.05 ms HBM; ~1.1 `M` ms SIMT | **5.66 ms (M=1, 0.89 of floor)**, 6.99 (M=2), 13.5 (M=4: 3.0e10 mont-muls = 2.3 T/s = at the INT32 issue rate: compute-bound from M >= 3) |
| (2') the same on tensor cores: `torch._int_mm`, `A = (24 M + 1) x rows` INT8 s-limbs, `B = W` bytes `^ 0x80` (zero-copy view) | read `W` once; `(24M+1) x rows x 16,384` limb MACs = 1.6e11 (M=1) | 5.05 ms HBM; 0.25 ms INT8 | see section 4 (run `r20260922-072315-6497`) |
| (3) encode `V_m` (6 M calls), `q += G_m * V_m` (8,192 x 36 M mont-muls) | negligible | -- | 0.03 + 0.02 ms (M=1); 0.08 + 0.06 (M=4) |
| (3') exceptional rows, general path | `14 X` transforms | -- | 0.14 ms for X = 256 (0.48 us/row, as the general path) |
| (2, lazy) `combine_multi_lazy`: 4 rows of 64-bit products `w * (s R)` summed unreduced (< 2^64), one REDC per 4 rows | same reads; ~1/2 the INT32 ops | 5.05 ms HBM | 6.06 (M=1), 5.72 (M=2), **6.95 (M=3)**, 7.56 ms (M=4) (run `r20260922-073017-0924`) |
| **structured total** | | **5.05 ms** (one read of `W`) | **5.67 ms (M=1) / 6.38 (M=1, X=256) / 5.90 (M=2 lazy, X=256) / 7.15 (M=3 lazy, X=256) / 7.68 (M=4 lazy, X=256); plain kernel 9.72 (M=3) / 13.7 (M=4)** |

The chain layout's configuration is `M = 3, X ~ 130`: **7.15 ms** with the lazily reduced kernel (0.71 of the read
floor).  Against the 149.4 ms of the general path: **26x (M=1), 21x (M=3 lazy), 11x (M=4 plain)** -- the linear test
drops from 58% of the B batch to 6%.

## 4. Tensor cores vs SIMT for step (2)

Run `r20260922-072315-6497` (`combine_int8_tensorcore_*` in `results_lintest_r20260922-072315-6497.json`).  The
formulation is exact (INT32 accumulation over <= 2^17 rows of |a b| <= 2^14 products, INT64 across chunks, limb
recombination `sum_{a,b} 2^(8(a+b)) mod p`; bit-exact against numpy in the run's checks, including the `rows % 8` host
tail and `M = 2`).  The operation reads the same 5.09 GB whether it runs on tensor cores or on SIMT and performs
1.6e11 `M` limb MACs: 0.25 `M` ms of tensor-core time against a 5.05 ms memory floor.

| `M` | SIMT `combine_multi` | tensor cores `torch._int_mm` (n = 24 M + 1 -> 32 / 56 / 104 limb rows) | INT8 utilisation | + byte-xor pass |
|---|---|---|---|---|
| 1 | **5.66 ms** (0.89 of floor) | 10.3 ms (0.49 of floor; 15.8 T limb-MAC/s) | 2.4% of 660 T | +11.0 ms (a 5 GB write) |
| 2 | **6.99 ms** (5.72 lazy) | 12.4 ms (0.41; 22.9 T) | 3.5% | idem |
| 3 | 9.98 ms (**6.95 lazy**) | not run (between the M = 2 and M = 4 rows) | -- | idem |
| 4 | 13.5 ms (INT32-issue-bound; **7.56 lazy**) | 16.7 ms (0.30; 31.7 T) | 4.8% | idem |

**Verdict: SIMT wins at every `M`.**  The row combination is a memory-bound GEMV (`n <= 104` output rows against a
310,602-deep reduction); cuBLASLt's INT8 kernel at these shapes runs at half the bandwidth the SIMT kernel reaches, and
the byte-shift pass (`W ^ 0x80`) costs another full write unless the witness is stored shifted from the start.  Even a
hand-written `mma.sync` kernel could at best close the 0.6 ms gap to the floor at `M = 1`; at `M = 3, 4` the lazily
reduced SIMT kernel is 1.4-1.5x above the floor, so a bandwidth-efficient tensor-core GEMV would gain ~2-2.5 ms per batch
(2% of B) -- the only remaining tensor-core opportunity in B, and a small one.  "The one B bucket that might be a matmul" is a matmul of rank `M <= 4`.

## 5. What the r^T A generation bucket becomes

The model prices `simt:constraint_combination` (the sparse `r^T A`, 4 terms per constraint x 335.5M constraints) at
8.9 ms.  Under the structure it is: `pi` and `pi_T` (~3,000 constraint vectors x ~4 terms of `F_c x F_t`), the powers
`rho^(i S C)` per row (310,602 `F_c` multiplies), and the ~130 exceptional rows densely (~0.5M `F_c x F_t` products):
well under a millisecond on either processor, and 24 B of scalars per row instead of 98 KB of `r^T A` per row (30.5 GB
that the general path had to generate, store and read).  The re-pricing keeps the modelled 8.9 ms (conservative,
unmeasured); the honest expectation is ~0.

## 6. Files

`lintest_structured.py` (reference, toy system, kernels, tensor-core variant, bench), `tests/test_lintest_structured.py`,
`results_lintest_<run>.json`, `reprice_measured.py --lintest` -> `backends/numerical/reports/b_measured_4090.{json,md}`,
ledger `backends/numerical/reports/ledger/b-lintest.jsonl`.
