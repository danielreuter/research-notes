CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/relmin-lookup pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT 2ef2409 four v2 relations mergeable: bf16-hopper-v2 282 rows/unit (v1 3292, 11.7x), bf16-ampere-v2 449 (3516, 7.8x), fp8-hopper-v2 185 (3396, 18.4x), fp8-ada-v2 337 (3769, 11.2x); on 2ef2409: GPU gates 2048 VUs + every negative family 0 failures (r20260923-090448-945a), pod pytest 91 passed 1 skipped (same run), 1e5-unit differentials v1 vs v2 passed for all four (/tmp/relmin/diff2_1e5_*.log), Rust pins + fixtures + tests (cargo test green), D12; fp8-ada v1 vs v2 on the same 4090, int-ZK medians per 4096 VUs: l=4096 0.982 -> 0.765 s (overhead 2.58e7 -> 2.01e7), l=16384 0.490 -> 0.333 s (1.29e7 -> 8.70e6); Python-model at l=16384: bf16-hopper 0.815 -> 0.608 s, fp8-hopper 0.437 -> 0.313 s, bf16-ampere-v2 0.626 s; every dump Rust + Python batch-verified at 128 bits; snapshots relmin-lookup-v1 = art:ee10a986cd23372e025d6da599135e2cdac4f4d8fa8b42064aab3a47467a37cf, relmin-lookup-v1-final = art:e00ac19217a20cf3606426ddab87984957c47b4a16c2458c0b1803dfb55b687c.  Previous checkpoint c7d32e0 (292 / 469 / 195 / 357 rows) stands with its own evidence (ec6a gates, 897c pytest, first differentials).
POST-CHECKPOINT (after the 10:30Z freeze; gated, pinned, benched -- mergeable as the next step): commits 6b79b06 + 87c94b6 add the folded `-v2x4` relations (four instruction steps per column: bf16-hopper-v2x4 1045 rows / 24 columns per VU, bf16-ampere-v2x4 1717 / 24, fp8-hopper-v2x4 647 / 12, fp8-ada-v2x4 1255 / 12), the four base v2 systems byte-identical.  Evidence: model-fold equivalence 0 mismatches on 1e5 chains x 8 configs; GPU gates 2048 VUs + every negative family 0 failures for all four (r20260923-104801-fc96) + pod pytest 103 passed; Rust pins + fixtures + cargo green; 12 new pytest tests.  **Measured on the same 4090 (int-ZK, l=16384, per 4096 VUs): fp8-ada-v2x4 0.162 s vs fp8-ada-v2 0.329 s vs v1 0.490 s (overhead 4.25e6; 3.48e6 = 0.133 s with whole sub-batches), bf16-hopper-v2x4 0.302 s vs 0.608 vs 0.815 (Python model), fp8-hopper-v2x4 0.168 vs 0.313 vs 0.437, bf16-ampere-v2x4 0.283 vs 0.626; proofs 12.4 vs 31.1 MB; verifier 0.148 vs 0.355 s; every dump Rust + Python batch-verified at 128 bits; snapshot relmin-lookup-x4 = art:31567c64a8afee81df8667b1fba0feaa42d515920338b13f9acd1fa3dc056f69.**  Second pod vy-relmin2 10:28-11:31Z (1.05 h); total 4.6 pod-hours ≈ $3.41.

# Lane relmin-lookup -- rows per unit by public selection (2026-09-23, 05:55Z-12:30Z)

Worktree `~/projects/verity-main-wt/relmin-lookup`, branch `lane/relmin-lookup` off main `6babe27`.  Commits (all on the lane):
bee4c6d (first four v2 units), 5d1e779 / 524950e (Rust pins, D12), bb74daa (`_pick`, `lookup(range_key=False)`), 0055c41 (BF16
epilogue without remainder rows), 9a869b3 (zero-sum completeness fix + families), 6ef1d3d / d4ef0f9 (last group without fraction
bits, epilogue picked from the sum's bits), c7d32e0 (the verifier's public vectors in one broadcast; systems unchanged),
2ef2409 (one one-hot for the group maximum and both alignment shifts: the final systems).  Code: `backends/direct/ligero/pubsel/` (`relation.py` the compiler + the verifier's public work, `hints.py` torch +
Python-integer hint generators, `relation_test.py` 34 tests), `relations.py` (four new names beside v1), `run.py` (choices only),
`compile.py` (`lookup(range_key=)`, default byte-identical: every existing system unchanged), `backends/ligero-verify` (`pubsel`
decode, four pins, fixtures, tests, D12).  v1 untouched; `relchain.py` not touched (the generic runner dispatches through the
`Relation` object, so no registry hook was needed).  `git status --short` empty at 2ef2409.

## 1. What the v1 units spend their rows on (chain mode, per unit)

| relation | rows | bit | prod | sel | pin | hint | inv | lin | quad |
|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper v1 | 3292 | 2391 | 166 | 542 | 96 | 97 | 0 | 339 | 3164 |
| bf16-ampere v1 (`unit.compile_unit` at REAL) | 3516 | 2534 | 173 | 610 | 96 | 103 | 0 | 347 | 3387 |
| fp8-hopper v1 | 3396 | 2196 | 282 | 577 | 192 | 148 | 1 | 554 | 3164 |
| fp8-ada v1 | 3769 | 2474 | 301 | 640 | 192 | 161 | 1 | 589 | 3532 |

bf16-hopper v1 by gadget: `align_prod` 1697 (1168 bits, 448 sels, 49 prods, 32 hints: 16 quotient/remainder pairs each range-checked
twice through `lt_pow`), `max` 360 (324 bits: 17 shifts x 9 bits x 2 for the non-power-of-two `shift_rows` = 507), `prod` 336 (256 bits:
the zero flags' `u + z - 1` ranges), `sum` 163, `lead` 109, `align_state` 143, `norm` 160, `x` 87, `epi` 60, `out` 50, pins 96.  fp8-ada v1
is the same story twice (two groups of 16): `align_prod` 2·976, `max` 2·207, `prod` 416.

What public selection removes: **every row that is a function of the public operands alone** -- the operand pins (s, m, e), the
products and their zero flags, the alignment of every product (quotient, remainder, `ALIGN` lookup, two `lt_pow` checks), and the
group maximum of the products.  The verifier computes those (`public_vectors_v2`: per group `G = max(floor, e_i)` and
`Q[j] = sum_i (1 - 2 s_i) align(u_i, j + G - e_i)` for every extra shift `j in [0, prod_bits)`) and pins them; the prover selects
`Q[E - G]` with one lookup one-hot.  What stays private: the accumulator's alignment (a *window* of the accumulator's own bit rows
selected by `min(dacc, W)` -- no quotient/remainder/POW table), the exact sum `v` in bits, the RZ normalisation (a window of `v`'s
bits selected by the shift `t`; `hid = 1` *is* the leading-bit proof, `t = tc(E)` when `hid = 0` is the subnormal clamp), the flags.
The digit/`lt_pow` shifter of fp4 is not needed for these units: every private shift is of a quantity whose bits are already committed,
so the shift is a selection of affine windows rather than a quotient/remainder proof -- and with `_pick` the selection costs no rows at
all (one hint row for the selected value, one row-free quadratic `sel_i (X - value_i) = 0` per candidate).

## 2. Design (pubsel/relation.py, one code path for the four relations)

Per unit (chain mode): accumulator components `acc.s/t/f/nz/z` (t 8 bits + `t != 255` by inverse, f 23 bits, flags by zero-products
and inverses); per group `g`: pins `G` and `Q[j]` (bf16-hopper: two 16-bit limbs each, `|Q| < 2^31 > p`); hints `delta = E - G`,
`dacc = E - e_acc` with `delta * dacc = 0`, `G + delta = e_acc + dacc`, each ranged only by its lookup's one-hot + key-difference
constraint (`lookup(range_key=False)`: the key is `sum_i sel_i k_i` or `k0 + diff` with `diff` in 9 bits); the `Q` one-hot over
`min(delta, PB)` picks `Q` (hint `Q`, or `QL`/`QH` for hopper); the `dacc` one-hot over `min(dacc, W)` picks the window
`floor(Mt 2^ss / 2^t)` of the state bits (hint `q` / `qL`,`qH`); `sgn`, `v` (bits; hopper: `vL`, `vH`, `carry`) with
`(1 - 2 s_acc) q_acc + Q = (1 - 2 sgn) v`; the normalisation one-hot `nsel[t]` (t in `[-nb, -k_lo]`: 34 / 32 / 28 values) picks
`M = floor(v / 2^t)` from the nb-bit windows of `v` (intermediate group of a two-group unit: `M = hid 2^(nb-1) + fo` with `fo` in bits,
the next alignment window reads them; last group: no fraction bits -- `M` is a hint picked from the windows, the bits of `v` above the
selected window are forced to zero by `sel_t H_t = 0`, `hid` is picked from the window's top bit, `f = M - hid 2^(nb-1)`);
`dt = e1m - acc_e_min >= 0` (9 bits) and `(1 - hid) dt = 0` on the z-masked exponent `e1m` (a zero sum is the zero word whatever `t`
the one-hot picked -- the completeness fix of 9a869b3, found by the fp8-ada differential at unit 1235: a cancelling sum with `E` high
enough that `tc(E)` fell outside the shift range); `z = [M = 0]` (zero-product + inverse), `ovf` by the masked comparison (one
product, 9 bits).  Pack as v1 on the components.  BF16 epilogue (RN-even to the 16-bit word, chain mode only): `fhi`, `half`, `sticky =
rest + lsb` picked from the sum's bits with the normalisation one-hot, `carry = half AND NOT [sticky = 0]` (one boolean hint `zl`,
zero-product + inverse), `fhi` and `carry` masked by `live` -- no remainder, no second decomposition: 5 rows where v1 spends 60.
Soundness argument per constraint is in the module comment and inline; the audit (`LigeroCtx._linear`) accepts every linear identity
inside `(-p, p)`; `_pick` records the hull interval of the picked value with `learn` (a theorem of the one-hot).

## 3. Running table (chain mode; census = `fp8.census.census` of the Relation's system, the bench's `relation.census.*`)

| relation | rows/unit v1 -> v2 -> v2' -> v2'' -> v2''' -> v2'''' | bit | prod | sel | pin | hint | inv | lookups/unit | lin / quad | gate (GPU, 2048 VUs) | differential 1e5 | Rust pin sys_id / table |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper-v2 | 3292 -> 466 -> 328 -> 312 -> 292 -> **282** (11.7x) | 93 | 19 | 0 | 55 | 110 (56 max one-hot + 34 nsel) | 5 | 0 lookups: 2 hint one-hots (56 + 34) | 67 / 585 | 0 fail (945a on 2ef2409; ec6a on d4ef0f9; c78c, 664d) | passed (404 s on d4ef0f9; 2ef2409: see §4) | cf99d1ce / bc4b95ec (d4ef0f9: 066c6696 / e9b1b7b4) |
| bf16-ampere-v2 | 3516 -> 703 -> 505 -> 489 -> 469 -> **449** (7.8x) | 168 | 26 | 0 | 54 | 195 | 6 | 4 hint one-hots | 71 / 821 | 0 fail (945a; ec6a) | passed (400 s; §4) | 15d793e7 / e70b77d5 |
| fp8-hopper-v2 | 3396 -> 281 -> 208 -> 195 -> **185** (18.4x) | 79 | 14 | 0 | 16 | 72 | 4 | 2 hint one-hots | 25 / 305 | 0 fail (945a; ec6a) | passed (331 s; §4) | e2a1573b / a473c735 |
| fp8-ada-v2 | 3769 -> 516 -> 370 -> 357 -> **337** (11.2x) | 138 | 23 | 0 | 32 | 139 | 5 | 4 hint one-hots | 49 / 527 | 0 fail (945a; ec6a) | passed (382 s; §4) | f23461f8 / 82b3041e (d4ef0f9: 11a7194b / 215e1beb, the benched system) |

Constraint nonzeros (a, b, c parts of every constraint) at d4ef0f9: fp8-ada-v2 3322 vs v1 18967, bf16-hopper-v2 3859 vs 16575,
fp8-hopper-v2 1784 vs 17165 -- `_pick` trades rows for denser quadratics (max 33-39 nonzeros in one constraint), which is what
the arithmetic test pays for at large l (§5).  Steps: v2 = summed one-hot selections (product
rows), v2' = `_pick` (row-free quadratics) + `lookup(range_key=False)` (-138 / -198 / -73 / -146 rows), v2'' = the BF16 epilogue without
remainder rows (-16 each), v2''' = the last group without fraction bits and the epilogue picked from the sum's bits (-20 / -20 / -13 /
-13), v2'''' = one one-hot for the group maximum and both alignment shifts (2ef2409: `c = clamp(e_acc - G, -W, PB)` with the
key an affine expression of the state and the pin -- no `delta` / `dacc` hints, no `delta dacc = 0`, one signed key-difference check
`(1 - 2 sel_lo) diff in [0, 2^9)` for both ends instead of two 9-bit key differences: -10 rows per group; `LigeroCtx.lookup` is no
longer used by the v2 units, `range_key=` stays as a tested, default-off option).  bf16-hopper-v2 by gadget at d4ef0f9 (292): pins 55, acc 40 (31 bits, 5 hints, 3 inv, 1 prod), qsel 28 sels + 9 keydiff bits + 2 limb
hints, acc-term 27 sels + 9 bits + 2 hints, max 2 hints, sum 35 bits + 4 prods + 4 hints (sgn, vL, vH, carry), norm 34 nsel hints +
2 hints (M, hid), out 9 bits + 4 prods + 1 inv + 2 hints (z, ovf), pack 6 prods, epi 5 (fhi, half, sticky, zl, 1 prod).  Committed
elements per FLOP: 292 / 32 = 9.1 (v1 103; fp4-nvf4 49 at K=64; fp8-hopper-v2 195 / 64 = 3.0).  Lookups cost one selector row per
*distinct output group* of the table (the one-hot), not log(size): a 2^16-entry table is cheap only if its outputs collapse into few
groups; that is why the shifts are one-hots over 27-34 values, not digit tables.  The three one-hots (qsel, acc-term, nsel) are now
89 of bf16-hopper-v2's 292 rows, the bits 102 (acc 31, sum 35, keydiff 9 + 9, dt 9, ovf 9), the pins 55.

## 3b. Folding four instruction steps into one column (post-checkpoint, 10:05Z-10:40Z)

§5 says the v2 prover is 94-97 % per-sub-batch fixed cost, and the number of sub-batches is `VUs x columns_per_VU / l` --
independent of rows.  The one lever left inside the compiled unit is therefore **columns per VU**: put `m` instruction steps in
one column.  `GroupSum(groups x m).step == m` chained steps of the model (the FP32 pack / decode between steps is the identity
on the adder-side state; a group leaving the FP32 range saturates in both): **0 mismatches on 1e5 random chains** per relation
for m = 2 and 4 with accumulators at the products' scale (`/tmp/relmin/fold_equiv.py`; in-repo `test_folded_model_equals_four_chained_steps`).
So the v2 compiler, whose intermediate-group path already exists for the two-group units, compiles the folded unit unchanged
(only the key-difference range check widens to 10 bits for BF16, whose conservative shift range passes 512 -- the four base
systems stay byte-identical, fixtures `cmp`-equal).  Census (chain mode; `/tmp/relmin/fold_census.py`):

| relation | m | K / column | columns / VU | rows | bit | pin | hint | lin / quad | rows / FLOP | rows x columns / VU |
|---|---|---|---|---|---|---|---|---|---|---|
| fp8-hopper-v2 | 1 / 2 / **4** / 8 | 32 / 64 / 128 / 256 | 48 / 24 / 12 / 6 | 185 / 339 / **647** / 1263 | 79 / 140 / 262 / 506 | 16 / 32 / 64 / 128 | 72 / 139 / 273 / 541 | 25/305 .. 193/1880 | 5.78 / 5.30 / 5.05 / 4.93 | 8880 / 8136 / 7764 / 7578 |
| bf16-hopper-v2 | 1 / 2 / **4** / 8 | 16 / 32 / 64 / 128 | 96 / 48 / 24 / 12 | 282 / 537 / **1045** / 2061 | 93 / 180 / 352 / 696 | 55 / 110 / 220 / 440 | 110 / 211 / 413 / 817 | 67/585 .. 529/3323 | 17.6 / 16.8 / 16.3 / 16.1 | 27072 / 25776 / 25080 / 24732 |
| fp8-ada-v2 | 1 / 2 / **4** / 8 | 32 / 64 / 128 / 256 | 48 / 24 / 12 / 6 | 337 / 643 / **1255** / 2479 | 138 / 258 / 498 / 978 | 32 / 64 / 128 / 256 | 139 / 273 / 541 / 1077 | 49/527 .. 385/3663 | 10.5 / 10.1 / 9.8 / 9.7 | 16176 / 15432 / 15060 / 14874 |
| bf16-ampere-v2 | 1 / 2 / **4** / 8 | 16 / 32 / 64 / 128 | 96 / 48 / 24 / 12 | 449 / 873 / **1717** / 3405 | 168 / 332 / 656 / 1304 | 54 / 108 / 216 / 432 | 195 / 381 / 753 / 1497 | 71/821 .. 561/5289 | 28.1 / 27.3 / 26.8 / 26.6 | 43104 / 41904 / 41208 / 40860 |

Rows per column grow *sub-linearly* (the accumulator decode is shared; an intermediate group commits its fraction, 14 / 24 bits,
which costs less than the 40-row decode it replaces), so committed elements per VU fall a further 5-10 % while the sub-batch count
falls m-fold.  Registered (additive) as `bf16-hopper-v2x4`, `bf16-ampere-v2x4`, `fp8-hopper-v2x4`, `fp8-ada-v2x4` (`relations.py
_folded`; `run.py` choices), the same instance sets and final words as the base relation (`instances()` draws the same operands;
the recorded accumulators are every fourth base accumulator).  Evidence so far (CPU, no pod): unit mode, hints against the folded
model, 20000 honest units accepted / 20000 bit-flipped claims rejected for fp8-hopper-v2x4 (`/tmp/relmin/fold_test_x4_2e4.log`;
the other three at 256 in-repo, 2e4 running at the deadline); chain runner two VUs proved + verified interactive and FS+ZK, the
generic negative battery (67-72 negatives) rejected, for all four (`/tmp/relmin/fold_chain.log`); Rust pins + fixtures
(`f1211dba / dbb92408`, `8ce6ca34 / c9611303`, `3463ce9f / 8d679547`, `d2272d3f / 87be1aea`), `cargo test --release` green (37
tests), 12 new pytest tests green, D12 addendum; local `pytest backends/direct/ligero` 100 passed 4 skipped on 6b79b06.
**GPU gates (second pod vy-relmin2 `aowctc5bfqyw1s`, created 10:28Z; run r20260923-104801-fc96 on 6b79b06): fp8-ada-v2x4 7 honest
sub-batches / 92 negatives / 0 failures, bf16-hopper-v2x4 13 / 87 / 0, fp8-hopper-v2x4 7 / 92 / 0, bf16-ampere-v2x4 13 / 87 / 0;
`pytest backends/direct/ligero` on the pod 103 passed 1 skipped (651 s: torch CPU tests on a 128-thread host).**  Every negative
family of the generic runner (word bits, ulps, off-domain, operand flip, broken link, c0 != 0, accumulator bits, row mutations)
is run per relation, as for the base v2 gates.  The 1e5-unit v1-vs-v2 differential was not re-run for the folded units: the
folded unit is the v2 unit compiled over more groups, and the fold equivalence (1e5 chains x 8 configs, 0 mismatches) plus
the 2e4-unit acceptance per relation stand in for it.

**Measured (vy-relmin2, RTX 4090 reference part, 4096 VUs = K=1536 each, 3 reps, medians, dumps; source 6b79b06, the BF16 pair
re-run at 87c94b6 for the statement-tag convention; all Rust + Python batch-verified at 128 bits in r20260923-111908-82f4 /
-112805-c591):**

| run | relation | zk | l | sub-batches | prover / 4096 VUs | overhead vs 330.3e12 | verifier | hints | encode | tests | openings | proof | peak dev |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260923-110522-551a | **fp8-ada-v2x4** (1255 rows, 12 col/VU) | int-ZK | 16384 | 4 (3 x 1365 VUs + 1 x 1 VU) | **0.162 s** | **4.25e6** | 0.148 | 0.051 | 0.010 | 0.052 | 0.010 | 12.4 MB | 2.43 GB |
| r20260923-110636-f70e | fp8-ada-v2 (337 rows, 48 col/VU) -- control | int-ZK | 16384 | 13 | 0.329 s | 8.65e6 | 0.355 | 0.053 | 0.030 | 0.167 | 0.031 | 31.1 MB | 0.65 GB |
| r20260923-111258-a44d | fp8-ada-v2x4, **4095 VUs** (3 whole sub-batches) | int-ZK | 16384 | 3 | **0.133 s** / 4095 VUs | **3.48e6** | 0.120 | 0.047 | 0.007 | 0.040 | 0.008 | 9.3 MB | 2.43 GB |
| r20260923-110718-8762 | fp8-ada-v2x4 | non-ZK | 16384 | 4 | 0.166 s | 4.37e6 | 0.156 | 0.060 | 0.010 | 0.046 | 0.009 | 10.5 MB | 2.43 GB |
| r20260923-111019-1a1d | fp8-ada-v2x4 | int-ZK | 4096 | 13 | 0.287 s | 7.54e6 | 0.303 | 0.091 | 0.026 | 0.096 | 0.036 | 21.4 MB | 0.61 GB |
| r20260923-110825-ad06 | fp8-ada-v2x4 | int-ZK | 32768 | 2 | 0.357 s | 9.36e6 | 0.115 | 0.066 | **0.177** | 0.060 | 0.005 | 10.1 MB | 6.39 GB |
| r20260923-111405-2869 | fp8-ada-v2x4, 8190 VUs (3 whole sub-batches) | int-ZK | 32768 | 3 | 0.258 s per 4096 | 6.78e6 | 0.164 | 0.084 | **0.265** | 0.088 | 0.009 | 15.2 MB | 6.12 GB |
| r20260923-112540-31a1 | **bf16-hopper-v2x4** (1045 rows, 24 col/VU), Python model | int-ZK | 16384 | 7 | **0.302 s** (v2 0.608, v1 0.815) | (H100 peak: n/a) | 0.265 | 0.093 | 0.018 | 0.099 | 0.020 | 20.6 MB | 2.43 GB |
| r20260923-112637-2377 | **bf16-ampere-v2x4** (1717 rows), Python model | int-ZK | 16384 | 7 | **0.283 s** (v2 0.626) | n/a | 0.250 | 0.076 | 0.022 | 0.095 | 0.017 | 24.3 MB | 3.96 GB |
| r20260923-111207-2181 | **fp8-hopper-v2x4** (647 rows, 12 col/VU), Python model | int-ZK | 16384 | 4 | **0.168 s** (v2 0.313, v1 0.437) | n/a | 0.143 | 0.058 | 0.010 | 0.050 | 0.010 | 10.5 MB | 1.28 GB |
| r20260923-111112-0d0d | bf16-hopper-v2x4 at 6b79b06 (SUPERSEDED: statement tag `|rel=...|v1` vs the Rust pin's empty BF16 tag -> Rust "column challenge mismatch", Python accepts) | int-ZK | 16384 | 7 | 0.290 s | n/a | 0.246 | | | | | 20.6 MB | |

So: **fp8-ada v1 0.490 -> v2 0.329 -> v2x4 0.162 s (0.133 s without the 1-VU tail sub-batch): 3.0x (3.7x) over v1 on the same
4090, overhead 1.29e7 -> 8.65e6 -> 4.25e6 (3.48e6)**; bf16-hopper 0.815 -> 0.608 -> 0.302 (2.7x); fp8-hopper 0.437 -> 0.313 ->
0.168 (2.6x); bf16-ampere-v2 0.626 -> 0.283.  The verifier halves as well (0.355 -> 0.148 s) and the proof is 2.5x smaller.  Where the
4x prediction became 2x: the arithmetic tests did fall with the sub-batch count (0.167 -> 0.052 s: ~13 ms per sub-batch, fixed as
§5 said), encode / openings / Merkle 3x; but **hint generation did not move (0.053 -> 0.051 s)** -- it is per *group*, not per
sub-batch (the CUDA graph replays per sub-batch with 4x the groups per unit), so at x4 hints are a third of the prover (0.051 of
0.162; 0.047 of 0.133) and are the next thing to cut (`pubsel/hints.py`, mine: one graph per relation over all groups, fewer
kernels per group -- the group loop launches ~60 small kernels per group).  The 4096-VU contract size costs a fourth sub-batch of
1 VU at l=16384 for 12-column units (1365 VUs per proof; 4096 = 3 x 1365 + 1): 22 % of the x4 prover time is that tail -- a
sub-batch layout that packs 4096 VUs into 3 proofs (l = 16384 fits 1365, 4096 / 3 = 1366: one column short) or a contract of 4095 /
8190 VUs would measure 0.133 s.  l=32768 hits the n = 131072 encoder cliff again (encode 0.177 / 0.265 s, 6 GB): l=16384 stays the
optimum; l=4096 (13 sub-batches) 0.287 s.

Prediction that was made before the measurement, from §5's fit (`time = sub-batches x (a + b rows)`, a = 22 ms, b = 4.1 us/row at l = 16384 on the 4090): fp8-ada-v2x4
at l=16384: 4096 VUs x 12 columns / 16384 = 3 sub-batches x (22 + 5.1) ms = **0.08 s vs 0.333 s measured for v2** (4x;
overhead 2.1e6 vs 8.7e6); bf16-hopper-v2x4: 6 sub-batches x (22 + 4.3) = 0.16 s vs 0.608 s (Python model).  The risk is the
arithmetic test's dependence on nonzeros x n (1255 rows, 1871 denser quadratics per column: §5's l=32768 cliff came from that
term) -- the bench decides, and m = 2 is the fallback.  Memory per sub-batch grows m-fold in rows only (the same n columns).

## 4. Evidence

* GPU gates on vy-relmin (`run.py --relation <v2> gate-vu --device cuda --vus 2048`, every negative family of the generic runner:
  word bits, ulps, off-domain, operand flip, broken link, c0 != 0, accumulator bits, row mutations), final systems (2ef2409, run
  r20260923-090448-945a, then `pytest backends/direct/ligero` 91 passed 1 skipped in the same run): bf16-hopper-v2 49 / 87 / 0,
  fp8-ada-v2 25 / 92 / 0, fp8-hopper-v2 25 / 92 / 0, bf16-ampere-v2 49 / 87 / 0.  The d4ef0f9 systems (run r20260923-073946-ec6a): bf16-hopper-v2 49 honest sub-batches, 87 negatives, 0 failures; fp8-ada-v2 25 / 92 / 0; fp8-hopper-v2 25 /
  92 / 0; bf16-ampere-v2 49 / 87 / 0.  Earlier systems: r20260923-064454-c78c (5d1e779), r20260923-071035-664d (0055c41).
* `pytest backends/direct/ligero` on the pod at c7d32e0: 91 passed, 1 skipped (r20260923-080931-897c, 09:05).  Locally
  `pubsel/relation_test.py` 34 tests green on CPU: census bounds; differential v1 vs v2 (unit mode, per column) with every claimed-word
  bit flipped, +-1 ulp, the other pipeline's word, zero-sum families -- both accept exactly the model's word; off-domain operands
  refused by both public decodes; torch hints == Python-integer reference; two VUs proved + verified on CPU (interactive, FS+ZK);
  the chain negative battery rejected; the RN-even epilogue on every rounding pattern (ties both ways) == `f32_to_bf16_word`; zero
  sums accepted in unit and chain mode.
* Differential at 1e5 units per relation (`RELMIN_DIFF_N=100000`, four detached pytest processes): on 2ef2409 logs
  `/tmp/relmin/diff2_1e5_<rel>.log` (finished 09:10Z-09:11Z, 289-352 s, 1 passed each); on d4ef0f9 `/tmp/relmin/diff_1e5_<rel>.log`
  (07:45Z-07:46Z, 331-405 s, 1 passed each).
* Rust: `pubsel::PubSel` (unit_pins = `public_pins_int`, pinned by hand-computed vectors), `Decode::PubSel`, `verify.rs
  public_pins_pubsel`; four systems pinned (sys_id == `protocol.system_id`, recomputed torch-free, byte-identical fixtures
  `fixtures/systems/<name>.system.bin`); `cargo test --release` green (relation, verify, tests/relations.rs incl. `system_digest`
  naming every pinned relation); the pod build from c7d32e0 reports `system_pinned: true, pinned_relation: fp8-ada-v2` on the dumps.
* D12 in `backends/ligero-verify/DISCREPANCIES.md`: the pins are derived values (G, Q[j]); K from the relation; tags; digests; the
  zero-sum masking and the fraction-free last group.
* Batch verification of every bench dump: Rust `ligero-verify batch --target-bits 128` on every rep directory (18 runs x 3 reps)
  rc=0 and Python `serialize verify-batch --device cuda --target-bits 128` on rep1 of each -- every sub-batch accepted, union bound
  2^-128.3 .. 2^-128.65 <= 2^-128: r20260923-080931-897c (the 11 runs of the 357-row system and v1, verifiers built from c7d32e0),
  r20260923-092349-c341 (the 337-row system, the l-sweep v1 runs; verifiers from 2ef2409), r20260923-092534-a0f7 (the l=8192
  357-row dump with the c7d32e0 verifiers: a 2ef2409 verifier refuses it as unpinned / malformed, as it must -- the pinned
  fp8-ada-v2 is now f23461f8).  The five Python-model timing runs (§5) are self-checked by the bench's own file verifier only.

## 5. fp8-ada v1 vs v2 on the same RTX 4090 (vy-relmin), 4096 VUs (K=1536), 3 reps, dumps, interactive

| run | relation | zk | l | prover median (reps) | verifier | witness (hints) | encode+commit | arithmetic | serialise | openings | proof | overhead vs 330.3e12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260923-074902-ae71 | fp8-ada v1 | int-ZK | 4096 | **0.982** (1.250, 0.976, 0.982) | 1.081 | 0.306 (0.259) | 0.142 | 0.372 | 0.131 | 0.110 | 181.5 MB | 2.58e7 |
| r20260923-075857-ad95 | fp8-ada-v2 | int-ZK | 4096 | **0.790** (0.790, 0.797, 0.749) | 0.958 | 0.121 (0.107) | 0.121 | 0.375 | 0.123 | 0.101 | 45.7 MB | 2.07e7 |
| r20260923-075244-69cc | fp8-ada v1 | non-ZK | 4096 | 0.897 (1.220, 0.859, 0.897) | 1.152 | 0.326 (0.278) | 0.086 | 0.334 | 0.135 | 0.114 | 169.9 MB | 2.35e7 |
| r20260923-080544-1b3f | fp8-ada-v2 | non-ZK | 4096 | 0.583 (0.615, 0.578, 0.583) | 0.971 | 0.120 (0.107) | 0.031 | 0.317 | 0.115 | 0.095 | 37.5 MB | 1.53e7 |
| r20260923-080045-7450 | fp8-ada v1 | int-ZK | 16384 | **0.490** (0.502, 0.490, 0.484) | 0.414 | 0.107 (0.088) | 0.124 | 0.180 | 0.068 | 0.047 | 66.1 MB | 1.29e7 |
| r20260923-075925-d7b6 | fp8-ada-v2 | int-ZK | 16384 | **0.307** (0.345, 0.307, 0.307) | 0.354 | 0.055 (0.050) | 0.037 | 0.160 | 0.048 | 0.028 | 31.3 MB | 8.11e6 |
| r20260923-080613-2467 | fp8-ada v1 | non-ZK | 16384 | 0.467 (0.494, 0.466, 0.467) | 0.412 | 0.108 (0.089) | 0.138 | 0.161 | 0.060 | 0.039 | 60.0 MB | 1.24e7 |
| r20260923-080005-f51b | fp8-ada-v2 | non-ZK | 16384 | 0.273 (0.299, 0.269, 0.273) | 0.365 | 0.055 (0.050) | 0.017 | 0.149 | 0.050 | 0.030 | 25.4 MB | 7.11e6 |
| r20260923-080114-4108 | fp8-ada-v2 | int-ZK | 32768 | 0.608 (0.868, 0.608, 0.515) | 0.268 | 0.064 | 0.187 | 0.284 | 0.044 | 0.020 | 30.6 MB | 1.60e7 |
| r20260923-085403-362d | fp8-ada-v2 | int-ZK | 8192 | 0.507 (0.526, 0.507, 0.474) | 0.576 | 0.094 (0.086) | 0.067 | 0.252 | 0.077 | 0.057 | 35.6 MB | 1.33e7 |
| r20260923-090155-2813 | fp8-ada v1 | int-ZK | 8192 | 0.637 (0.686, 0.629, 0.637) | 0.630 | 0.168 (0.140) | 0.123 | 0.244 | 0.086 | 0.065 | 103.5 MB | 1.66e7 |
| r20260923-090244-c9da | fp8-ada v1 | int-ZK | 32768 | 2.593 (2.796, 2.593, 2.448) | 0.346 | 0.078 | 2.064 (encode 1.977; 16.6 GB peak) | 0.383 | 0.047 | 0.023 | 49.2 MB | 6.82e7 |
| r20260923-090323-35ec | fp8-ada-v2 | int-ZK | 65536 | 0.541 (0.552, 0.541, 0.531) | 0.240 | 0.067 | 0.215 (encode 0.204; 3.5 GB peak) | 0.187 | 0.041 | 0.012 | 33.2 MB | 1.42e7 |
| r20260923-074442-edbe / -074523-5bac | fp8-ada-v2 on d4ef0f9 (public vectors still a Python loop) | int-ZK / non-ZK | 4096 | 0.913 / 0.741 | | 0.275 (0.261) | | | | | | superseded |
| r20260923-092147-d927 | fp8-ada-v2 **337 rows (2ef2409)** | int-ZK | 4096 | **0.765** (0.795, 0.759, 0.765) | 0.957 | 0.130 (0.116) | 0.120 | 0.370 | 0.121 | 0.100 | 44.9 MB | 2.01e7 |
| r20260923-092215-ec8e | fp8-ada-v2 337 rows | int-ZK | 16384 | **0.333** (0.341, 0.330, 0.333) | 0.357 | 0.058 (0.052) | 0.038 | 0.169 | 0.054 | 0.033 | 31.1 MB | 8.70e6 |
| r20260923-092254-126a | fp8-ada-v2 337 rows | non-ZK | 16384 | 0.276 (0.293, 0.272, 0.276) | 0.363 | 0.057 (0.051) | 0.016 | 0.149 | 0.050 | 0.030 | 25.2 MB | 7.16e6 |

Rows above without a "337 rows" mark are the 357-row system (d4ef0f9 / c7d32e0, sys_id 11a7194b).  The 337-row system times the same
within noise (0.765 vs 0.790, 0.333 vs 0.307, 0.276 vs 0.273): 20 rows are 0.1 ms of a 24 ms sub-batch.

Python-model timings of the other relations on the same 4090 (int-ZK, l=16384, 4096 VUs, 3 reps, medians; the `overhead` column
of these rows is against the H100 peak the relation names, so only the seconds are meaningful here; 2ef2409 systems):
bf16-hopper v1 0.815 s (r20260923-093423-b7d3, 118.0 MB) -> **bf16-hopper-v2 0.608 s** (r20260923-093331-e895, 58.7 MB; 25 sub-batches
of 170 VUs: K=1536 is 96 BF16 units); **bf16-ampere-v2 0.626 s** (r20260923-093514-5474, 62.0 MB; no `relations.py` v1 to compare);
fp8-hopper v1 0.437 s (r20260923-093622-3eef, 62.3 MB) -> **fp8-hopper-v2 0.313 s** (r20260923-093553-b44d, 29.5 MB).

All rows contract-valid (`validation.status = passed`, soundness 128.3-128.6 bits, batch accept), Rust + Python batch-verified (§4).
Source c7d32e0 except the two superseded d4ef0f9 runs (same systems).  Sub-batches: 49 at l=4096 (85 VUs per proof), 13 at l=16384
(341), 7 at l=32768 (682) -- **the same for v1 and v2**: a unit is one column, so VUs per proof = l / 48 whatever the row count; rows
only shrink m (357 x 16384 int32 = 23 MB per v2 sub-batch at l=16384).

**Where the time went.**  A 10.6x cut in rows bought 1.24x (l=4096) / 1.6x (l=16384) in prover time, because the v2 prover is almost
entirely per-sub-batch fixed cost.  Fit `time_per_subbatch = a + b rows` on v1/v2: at l=16384 a = 22 ms, b = 4.1 us/row (v2 = 94 % a);
at l=4096 a = 15.7 ms, b = 1.1 us/row (v2 = 97 % a).  The fixed part is the arithmetic tests (0.160 s = 12 ms/sub-batch at l=16384:
`_challenge1`, the r-combination, `quad_p0`, two INTTs, the chain test's encode, `.cpu().numpy()` syncs -- v1 3532 sparse quadratics
and v2 489 denser ones cost the same), serialisation (0.05 s), hints (0.05 s: a CUDA graph per sub-batch, launch-bound), openings.
The rows still bought what rows buy: proof size 181.5 -> 45.7 MB (l=4096) and 66.1 -> 31.3 MB (l=16384), peak device memory 148 MB
at l=4096, encode+commit 0.142 -> 0.121 / 0.124 -> 0.037 s, hints 0.259 -> 0.107 s, and the headroom to run wider: l=16384 is where v2
is 1.6x and 8.1e6 overhead.  The l-sweep (int-ZK, prover medians v1 -> v2): l=4096 0.982 -> 0.790, 8192 0.637 -> 0.507, 16384 0.490 -> 0.307, 32768 2.593 -> 0.608,
65536 (v2 only) 0.541.  Two cliffs: the *encoder* at n = 131072 columns (v1 encode 0.079 s at l=8192 -> 1.977 s at l=32768 with a
16.6 GB peak; v2 0.054 -> 0.187 -> 0.204 s at l=65536: the 3769-row matrix falls off first, the 337-row one survives to l=65536
with 3.5 GB), and the *arithmetic test* per sub-batch (7.6 / 10 / 12 / 40 / 47 ms at l = 4096 .. 65536: fixed up to l=16384, then
growing with n -- INTTs over n and `quad_p0` over nonzeros x n, where `_pick`'s denser quadratics start to matter).  v2's optimum on
this pod is l=16384 (0.307 s, 8.1e6); v1's is also l=16384 (0.490 s).  Protocol-side observations (not mine to fix).  The verifier is slower than the v2 prover at l=4096 (0.958 vs
0.790 s): it now computes the public vectors (PB = 25 truncated sums of 16 products per group per unit) -- cheap on the GPU, but
per-sub-batch launch-bound like everything else here.

## 6. Pod accounting

vy-relmin `8k2epqw8dk5oih` (RTX 4090 reference part, US-NC-1, host EPYC 75F3), created 06:32:30Z, $0.74/h; registered in
machines.toml by hand.  Bootstrap = hostphase's recipe (venv312 torch 2.6.0+cu124 + cupy + blake3 + pytest, rustup + ligero-verify).
Runs: r20260923-063533-15f6 (bootstrap), -064454-c78c (gates + pytest, 5d1e779), -071035-664d (BF16 re-gates, 0055c41), -073946-ec6a
(gates, d4ef0f9), -090448-945a (gates + pytest, 2ef2409), 23 bench runs (§5: 11 + 4 l-sweep + 3 at 2ef2409 + 5 Python-model),
-080931-897c / -092349-c341 / -092534-a0f7 (Rust builds + batch verifies + Python verify-batch; 897c also pytest at c7d32e0).
Terminated at ~10:05Z after the last pull: ~3.55 pod-hours ≈ $2.63 of the 7 h budget.  Store: 23 bench attempts pulled (`research data
pull --project verity`), every artifact PRESERVED on R2 (`push --pending`), labels on each `result`
(relation, candidate, K, B, zk, mode, campaign, track, scope, hardware, soundness, proof_class, authentication, label, note) and on
each `run_files` (relation, note) `--by relmin-lookup --ref <run>`, no `verified=`; snapshots `relmin-lookup-v1` =
art:ee10a986cd23372e025d6da599135e2cdac4f4d8fa8b42064aab3a47467a37cf (22 members: the first 11 results + run_files) and
`relmin-lookup-v1-final` = art:e00ac19217a20cf3606426ddab87984957c47b4a16c2458c0b1803dfb55b687c (36 members: 18 fp8-ada runs).  The
five Python-model runs are pulled, pushed and labelled but not in a snapshot.

**Second pod** vy-relmin2 `aowctc5bfqyw1s` (RTX 4090 reference part, EPYC 75F3 host), created 10:27:58Z (two `pods create`
attempts: "no instances currently available" then success; registered in machines.toml by hand), terminated 11:30:50Z: 1.05 h ≈
$0.78.  Runs: r20260923-104240-94ad (bootstrap, 1 min: the image had most of it), -104801-fc96 (x4 gates + pytest), 11 bench runs
(§3b), -111908-82f4 / -112805-c591 (Rust + Python batch verifies).  The `research run --source .` push ran at ~50 KB/s (97 MB
archive; another lane pushing at the same time): the tree was pushed by hand as `git archive | gzip -1 | ssh tar -xzf` into
`/workspace/research/src/<sha>` + `.complete` (47 s; 3.5 min the second time), after which `--source .` found it.  All 14 runs
pulled (`--project verity`), pushed (`push --pending`, one push interleaved with other lanes' pushes -- `database is locked` on one
pull, retried), labelled as before (`hardware=` names the pod and whether the timing is native or Python-model; 0d0d relabelled
SUPERSEDED), snapshot `relmin-lookup-x4` = art:31567c64a8afee81df8667b1fba0feaa42d515920338b13f9acd1fa3dc056f69 (22 members: 11
results + 11 run_files).  The `push --pending` of the second pod's 14 runs was still uploading at 12:14Z (61 artifacts PRESERVED, the
run_files dumps on a shared ~100 KB/s uplink; detached process `python -m research data push --pending`, log /tmp/relmin/push4.out):
re-run `research data push --pending` if it is not complete when read.  **Total: 3.55 + 1.05 = 4.6 pod-hours ≈ $3.41 of the 7 h / $5 budget; both pods gone from `pods list`
(vy-relmin-priv is another lane's).**

## 7. fp4-nvf4 with fresh eyes (1583 rows, not implemented; fp4-fast owns `fp4/`)

The relation pins 128 numerators + 4 `sm` + 4 `X` + 4 `part` + `G` = 141 pin rows, multiplies the numerators in the circuit (64
product rows `na_i nb_i`, 4 more `gd sm`), and runs five truncating shifters (four 19-bit groups with n_j = 3, the 24-bit accumulator
with n_j = 2) plus the output shifter run backwards (n_j = 4, digits, R digits, five carries).  Every one of the group shifters is a
function of public data and one private integer (`lsb`), exactly the situation public selection removes:

1. **Pin the group mantissas, not the numerators** (`mant_g = gd_g sm_g`, |mant| < 2^19: 4 pins) -- the 128 numerator pins, the 68
   product rows and the 4 `sm` pins go (about -200 rows).  Better: pin `Q[j] = sum_g part_g trunc(mant_g 2^(X_g - G - j))` for every
   extra shift `j = lsb - G in [0, 47)` (the top group sits at 2^27 above G and |mant| < 2^19, so j >= 46 shifts everything out): the
   four group shifters (each ~100 rows: `u` one-hot ~20, `q` / `rem` lt_pow 2 x 19 bits, fine-shift one-hots, two 12-bit digits,
   placement one-hot) become one 47-way one-hot on `delta = lsb - G` and one pick -- **about 400 rows for ~50 pins + 50 selectors**.
   `|Q| < 2^47` needs two limbs (as bf16-hopper-v2's `QL/QH`), or one limb per `j >= 16` where the sum already fits in 31 bits.
2. **The accumulator's shifter is a window of its own digits' bits.**  `fh` / `fl` are already range-checked (11 + 12 bit rows); the
   aligned term `floor(M 2^(acc_e - lsb))` is a pick over `min(lsb - acc_e, W)` with W = 36 (`ACC_WINDOW`) of windows of those bits:
   one 37-way one-hot + one hint instead of the 24-bit shifter (~100 rows -> ~40).
3. **Normalise from the exact sum's bits, not the shifter backwards.**  Commit `v = |T|` in 49 bits (two limbs and a carry like
   bf16-hopper-v2, since 2^49 > p), then `M` = a picked nb-bit window of `v` over the shift `t` (~50 values), `hid` picked from the
   window's top bit, the bits above the window forced to zero -- replaces the out shifter, the `R` digits, `r.above`, `r.top`, `t1/t2`
   and the five carries (~250 rows -> ~110).  The six-position digit adder disappears with it: `T = Q + (1 - 2 s) q_acc` is a two-limb
   addition with one carry.
4. **Zero flags by `_pick`-style row-free quadratics** where the fp4 code sums selections with product rows (`r_sel`, `above`).

Estimate: 1583 -> ~650-750 rows (2.1-2.4x), 972 -> ~200 bit rows, with the verifier computing 47 truncated group sums per unit
(it already computes 128 numerators).  The same caveats as here apply: the gains in prover *time* are bounded by the per-sub-batch
fixed costs (§5) until those are cut.

## 8. What remains, ranked

0. ~~Gate and bench the folded `-v2x4` relations~~ -- done (§3b): gates 0 failures, fp8-ada 0.329 -> 0.162 s (0.133 s in whole
   sub-batches).  **Next, in order:** (a) `pubsel/hints.py`: hints are now 1/3 of the x4 prover (0.05 s per 4096 VUs, flat in the
   sub-batch count -- per-group kernel launches inside one CUDA graph per sub-batch); one fused per-group kernel or a torch.compile'd
   group body should take it to ~0.01 s: predicted 0.162 -> ~0.12 s.  (b) m = 8 (`_folded(rel, 8)`: fp8-ada 2479 rows, 6 columns
   per VU, 2 sub-batches of 2730 VUs at l=16384 for 4096 VUs -- rows x n = 2479 x 65536 int32 = 650 MB per sub-batch, the encoder
   at n = 65536 is still on the fast side of its cliff) -- predicted ~0.10 s if the tests stay per-sub-batch; census exists (§3b
   table), 20 minutes of pod to gate + bench.  (c) The 1-VU tail: 4096 VUs / 1365 per proof; `--total-vus 4095` or a layout that
   uses l = 16384 with 1366 VUs... needs 16392 columns: not a power of two; the honest fix is m = 8 (2730 per proof: 4096 = 1 x
   2730 + 1366, still a tail) or l = 32768 without the encoder cliff (item 2).  (d) Switch the default fp8-ada relation to
   `fp8-ada-v2x4` once the coordinator wants it: same instance set, same claim, same statement format, its own Rust pin.
1. **Cut the per-sub-batch fixed cost of the prover** (protocol.py: the arithmetic tests' `_challenge1` / INTT / chain-encode chain,
   the `.cpu().numpy()` syncs, the per-sub-batch hint graph; serialisation) -- with v2 rows this is 94-97 % of the prover.  Evidence:
   §5 fit; v1 and v2 arithmetic tests cost the same (0.16-0.18 s) with 7x fewer quadratics and 5.7x fewer nonzeros.  Owner: hp2-host /
   protocol lanes.  Expected: 0.307 -> ~0.1 s per 4096 VUs at l=16384 (overhead ~2.5e6).
2. **Fix the l=32768 cliff** (encode 0.187 s for 7 sub-batches vs 0.037 s for 13 at l=16384; tests 0.284) and then run v2 at l=65536:
   sub-batches 4, fixed cost /3.  The rows make the memory fit (148 MB peak at l=4096, 584 MB at l=16384 for v2).
3. ~~One one-hot for the group max and both alignments~~ -- done in 2ef2409 (-10 rows/group: 282 / 449 / 185 / 337), a hand-built
   one-hot in `pubsel/` with a signed key-difference check `(1 - 2 sel_lo) diff in [0, 2^9)` (one product row) rather than a
   `lookup` extension.  Prover time unchanged within noise, as §5 predicts.
4. **Two-group units (fp8-ada-v2 337, bf16-ampere-v2 449)**: the intermediate group commits its fraction (24 / 23 bits) because the
   second alignment window reads it; a single 32-wide group sum pinned by the verifier for the *pair* is not possible (the two group
   maxima are taken separately by the model), but the intermediate normalisation could be skipped when the model's two-group
   semantics allow the exact intermediate to flow (it does not for fp8-ada: the lossy rescale between groups is the model).
5. **bf16-hopper-v2 limbs**: `Q[j]` in two 16-bit limbs (55 pins) because `|Q| < 2^31 > p`; pinning `Q[j]` for `j >= 4` in one limb
   (`|Q[j]| < 2^(31-j)`) saves ~24 pin rows; the sum's limb split stays.
6. **fp4-nvf4** as in §7 (fp4-fast).
7. The negative families for the v2 pins (a wrong `Q[j]` pin, a wrong `G`) are covered by the operand-flip family (the pins are
   recomputed from the words by both verifiers) -- a *targeted* pin-mutation family in the gate would make the argument direct.

## 9. Spec issues found

* "lookup tables up to 2^16 entries are cheap in Ligero" -- not in this compiler: `LigeroCtx.lookup` is a one-hot with one selector
  row per distinct output group (and `rng` on the key), so table size enters *linearly* in rows; digit tables were the wrong tool for
  these units and the fp4 shifter was not what to port -- selection of windows of already-committed bits was.
* The premise "prover cost ∝ rows per unit x (n/l)" holds for encode / Merkle / openings / proof size / memory, not for the prover's
  wall time at these sizes: the arithmetic tests, hints and serialisation are per-sub-batch fixed costs, and sub-batch count is
  independent of rows (§5).  A 10x row cut is a 1.6x prover cut until item 8.1 is done.
* bf16-ampere v1 has no `relations.py` entry (it is `unit.compile_unit` at REAL through `vu.py`); its spec census "3516 (2401 bit
  rows)" is 3516 rows with 2534 bit rows by `fp8.census.census`.  bf16-ampere-v2 is registered with the AMPERE model / FIRST target.
* `research data pull` needs `--project verity` for a remote run; `research run --tool` needs a registered tool name (`bench_vu_fp8`,
  `ligero_verify_batch`); `bench-vu` has `--zk` only (non-ZK = omit it).
