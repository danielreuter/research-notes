---
id: r20-proof/checker-min/20260922T0727Z-report-checker-min
campaign: r20-proof
lane: checker-min
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/checker_min.md
---

# checker-min: a smaller sound checker for the frozen relation (lane/checker-min, 2026-09-21/22)

Scope: the arithmetisation of the WP2 transition unit (16 BF16 products into one FP32 accumulator, Ampere
m16n8k16 semantics per `verity.ml.tc.silicon`) and of the K=1536 verification unit (96 chained units from
c_0 = 0). The function and the domain are unchanged: every accepted (inputs, output) pair of v2 is an accepted pair
of v1 and of the reference, and vice versa; only the hints and the predicates differ. Code: `checker/v2/`
(`params.py`, `tables.py`, `gadgets.py`, `step.py`, `search.py`, `bench.py`), `tests/checker/test_v2.py`,
`security/census.py` (`census_unit_v2`, `census_vu_v2`, per-gadget breakdown, `VERITY_CHECKER_VARIANT=v2`),
`redteam/checker_target.py` (`checker-v2` target), `explore/fields.py` (v2 small-field deltas). v1 is intact and
remains the default everywhere.

Status labels follow `backends/AGENTS.md`: MEASURED = run on the pod or the laptop and recorded; MODELLED = cost-model
output; every overhead number below is MODELLED (no kernel was built in this lane).

## 1. Where v1 spends (census_unit by gadget, REAL widths)

`census_unit()` now attributes every primitive to the gadget whose `check` emitted it (`UnitCensus.by_gadget`).
`lin` below is `lin + lin_range_splits` (the brief's 137); `lookups` is range chunks (16-bit table) plus fixed-table
lookups.

~~~
gadget          mul   lin  range  fixed  hints   note
bf16_decode      96    64     96      0    128   32 words x (3 mul, 2 lin, 3 range chunks, 4 hints)
product          80    16     16      0     16   16 x (mantissa mul + 4 mul for the (1-z_a)(1-z_b) masks)
align_product    64    16     64     16     32   16 x (q, r hints: 2 range chunks each, 4 mul, POW/ALIGN lookup)
group_max        38     4     22      0     22   16 d_i range checks + one-hot selector (10 hints, 19 mul)
signed_sum       28     8      8      0      4   sign split, |S| range, (1-2sgn) products
state_out        16     4      6      0      4   zero/overflow flags and their proofs
normalise        14     4     10      2      6   k hint, 2^k lookup, remainder range checks
pack              8     2      2      0      2   hidden bit, overflow blend
align_state       6    10     16      2      4   two POW lookups, quotient/remainder splits
fp32_decode       6     5      6      0      5   incoming accumulator word
leading_bit       2     2      4      2      2   LEAD lookup on the top bits
composition       0     2     34      0      0   range checks on carried wires
total           358   137    284     22    225   depth 5, 34 input columns, 100 materialised columns
~~~

Top 5 targets by mul: `bf16_decode` (27%), `product` (22%), `align_product` (18%), `group_max` (11%), `signed_sum`
(8%). Together 85% of the multiplications, 72% of the lookups and 90% of the hints. Everything in this list is a
*decomposition*: a value is split into hinted pieces, each piece is range-checked, and the pieces are recombined
with multiplications. The v2 design replaces decompositions by fixed-table lookups whose outputs are bound by the
lookup argument itself, so there is nothing left to recombine or to range-check.

## 2. Ideas evaluated (sketch / predicted saving / soundness risk), verdicts

**(a) Range checks: wider tables, sharing, implication.** v1 checks 284 chunks per unit against a 16-bit table
(`T_range16`); 34 of them are on wires carried between gadgets. Predicted: sharing removes the 34 composition chunks;
widening to a 24-bit table removes another ~60. Risk: none for sharing (same predicate), the 24-bit table's
commitment cost is the price. *Verdict: subsumed.* Almost every range check in v1 bounds a hint that v2 no longer
has; v2 has 10 range chunks per unit (the 23/24-bit state-decode halves, two 4-bit `attained` checks, and the
12/13-bit halves of the state magnitude -- see 3.2 on why the latter are not implied by their lookup keys over a
field). The implied-by-others
question was answered by z3 rather than by sharing: for every dropped v1 predicate class the v2 gadget is UNSAT
without it being restated (section 3).

**(b) Alignment: power-of-two lookup vs bit decomposition; one decomposition of E\*.** v1: per product a (q, r)
division by 2^(E\*-e_i) with 4 mul, 4 range chunks, one POW lookup. Predicted: keying a table on the *shift amount*
and the *value* directly returns the aligned term (0 mul, 1 lookup). Risk: the table is large (value 2^16 x shift
range 27 x sign 2 = 3.5M rows) and the shift must be provably in range (E\* - e_i >= 0) before it is used as a key.
*Verdict: accepted.* `ALIGN4` (3120 rows) keyed on 4(E-e_i)+s4_i (s4 packs the two operand signs) proves
E-e_i >= 0 and returns (min(E-e_i, DT), product sign, [E-e_i = 0]); `SHIFT` keyed on (u_i, d~_i, sign) returns the
signed aligned term. The 16 products share nothing but the key layout; sharing one decomposition of E\* was not
needed because E\* is never decomposed. The state term uses the same idea on two halves (`SSHIFT_HI/LO`, 221k rows
each) so the 2^31 magnitude never meets a single table.

**(c) "E\* attained" chain.** v1: one-hot selector (10 hints, 19 mul) plus prod(E\*-e_i)=0. Proposed in the brief:
an index j with e_j = E\* and 16 inequalities. *Verdict: accepted in a cheaper form.* `ALIGN4` already emits
[d_i = 0] for every candidate; attained := sum_i [d_i=0] + [E\* = floor] >= 1, one 4-bit range check on (sum - 1),
zero multiplications. The [E\*=floor] term is from `LEADNORM` (the all-zero group must accept E\* = floor). z3: dropping
`attained` is SAT (excessive E\* forges a wrong rounding), keeping it is UNSAT.

**(d) Products: packing two 16-bit products into one field multiplication.** Predicted: -8 mul per unit on Goldilocks
(two products of 16 bits in one 64-bit word; BabyBear/M31 cannot hold 2 x 2^16 + a carry-free separation: 2^32 > p).
Risk: separating the packed word back into two 16-bit halves needs a 2-chunk range decomposition (2 hints, 2 lookups,
1 lin) per pair, costing more than the saved multiplication under every cost model in `explore.tensor`. *Verdict:
rejected on cost, per field: not possible on BabyBear/M31; net negative on Goldilocks.* The v2 product is one
multiplication per pair (16 per unit), down from 5 in v1, because the operand decode (e) removed the zero masks.

**(e) Zero-operand mask and NaN/Inf exclusion.** v1: z_a, z_b booleans, (1-z_a)(1-z_b) mask (4 mul per product),
exponent masks, non-finite excluded by an exponent range check. Proposed: encode "zero" as a sentinel exponent.
*Verdict: accepted.* `T_OP` (65280 rows: every finite BF16 word; NaN/Inf words have no row so the lookup fails)
returns (s, m, e_op) with e_op = e_zero for +-0, where e_zero = floor - e_max - 1 is below every finite operand exponent, so
2 e_zero is below every reachable product exponent: the product of a zero operand lands at 2 e_zero, `ALIGN4` clamps its shift to DT and
`SHIFT` returns 0 for any u at shift DT. No flag, no mask, no multiplication; the zero operand's *mantissa* m = 0 is
also in the row so the product is 0 regardless. Subnormal BF16 words are in the table with their exact (m, e).

**(f) Fixed-K structure.** Predicted: the first unit's incoming decode disappears (c_0 = 0 is a constant), the 95
intermediate FP32 re-pack/decodes disappear if the state is chained in its (s, e, M, z) form, one Pack at the end.
Risk: the intermediate FP32 words are no longer wires, so the per-unit finiteness of the accumulator must be kept by an
explicit identity (v1 got it from the FP32 decode). *Verdict: accepted.* v2's VU chains (s, e_hat, M, z), asserts
ovf_eff = 0 per unit (`LEADNORM` emits it), decodes no word, packs once; unit 0 takes the constant zero state (no
hints, `static=True`). The relation is the same because `silicon` itself rounds to FP32 at every unit and v2 rounds
the same M at every unit; the pack is a bijection on the reachable states (z3 `pack` UNSAT).

**(g) Leading bit / normalisation / rounding.** v1: LEAD lookup on the top bits, k hint, 2^k lookup, remainder range
checks, separate state_out flags. *Verdict: accepted.* v = (1-2 sgn) S is split into two 15-bit halves, each through
`LEAD` (range check and bit length in one lookup; 32k rows); `LEADNORM(l, E)` (12k rows) returns
(k, 2^(vb+k), e_hat, z, ovf_eff, [E=floor]) and `TNORM(v_lo, k)` (1M rows) the low part of the normalised mantissa.
The rounding is the documented Ampere behaviour exactly as `silicon.py` implements it (truncation of the wide sum
after alignment to E\*, then the FP32 rounding rule of the reference): v2 is differentially tested against `silicon`
and z3-UNSAT against the same reference function as v1, so no rounding rule was re-derived by hand.

## 3. What was implemented and how it was checked

### 3.1 Census, v1 -> v2 per unit (MEASURED by `census_unit` on the contracts)

~~~
                       v1                          v2
gadget            mul  lin  lkp  hints      mul  lin  lkp  hints   v2 primitives
bf16_decode /       96   64   96   128        0    0   32     0    op_decode: 32 x T_OP
product             80   16   16    16       16    0    0     0    16 x (m_a m_b), e = e_a + e_b linear
align_product       64   16   80    32        0    0   16     0    product_shift: 16 x SHIFT
group_max           38    4   22    22        0    0   20     2    16+2 ALIGN4 (18 candidates incl. state), attained range
align_state          6   10   18     4        0    2    8     4    state_shift: halves range-checked, SSHIFT_HI/LO
signed_sum          28    8    8     4        6    2    4     6    sgn boolean, (1-2sgn)S, halves through LEAD
leading_bit +        2    2    6     2        2    0    4     0    normalise: LEADNORM x2, TNORM x2, v_hi A
normalise           14    4   12     6
state_out           16    4    6     4        0    0    0     0    z, ovf_eff are LEADNORM outputs
fp32_decode          6    5    6     5        3    4    5     3    state_decode (word-in unit only; absent in the VU)
pack                 8    2    2     2        4    0    0     0    linear in (s, e_hat, M, z) + hidden bit
composition          0    2   34     0        2    1    0     0
total              358  137  306   225       33    9   89    15
                                            -91% -93% -71%  -93%
multiplicative depth 5 -> 3; materialised columns 100 -> 45; lookup-output columns 62 -> 195
~~~

`lookups_by_table` v2: T_OP 32, ALIGN4 18, SHIFT 16, LEAD 4, SSHIFT_HI 2, SSHIFT_LO 2, LEADNORM 2, TNORM 2, T_HDR 1,
T_range16 10. Table sizes (rows): T_OP 65 280, T_HDR 510, ALIGN4 3 120, SHIFT 3 538 944, SSHIFT_HI/LO 221 184 each,
LEAD 32 768, LEADNORM 12 152, TNORM 1 048 576; total 5.2M rows against v1's 65k+ (T_range16, ALIGN, POW, LEAD, NORM).
This is the trade: -71% lookup *rows queried* per unit for +80x fixed-table rows committed once per proof.

VU (K=1536, 96 units, MEASURED by `census_vu`): 34 370 / 13 059 / 29 379 mul/lin/lookups, 21 606 hints (v1) ->
2 502 / 577 / 8 067, 1 156 hints (v2): -93% / -96% / -73%. Predicates per VU 76 808 -> 11 146 (-85%), so the
`--breakthrough` threshold (> 25%) is met on every count.

### 3.2 z3 at REAL widths (MEASURED on vy-cpu2, z3 4.x, `checker.v2.search`, `out/search_v2.log`)

Each gadget: two hint copies against the reference function, "output differs" must be UNSAT. Tables enter z3 through
their symbolic definitions (`Table.sym`; `table_selfcheck` compares `sym` to the enumerated rows: exhaustive below 20k
rows, 3000 samples plus boundaries above, 0 mismatches on all 9 tables).

~~~
gadget         query                              status   s
op_decode      differs-from-reference             UNSAT    0.002
state_decode   differs-from-reference             UNSAT    0.006
product        differs-from-reference             UNSAT    0.000
group_max      differs-from-reference             UNSAT    0.28
product_shift  differs-from-reference             UNSAT    2.51
state_shift    differs-from-reference             UNSAT    7.56      (60 s timeout run in the redteam campaign: UNKNOWN; 600 s run: UNSAT)
signed_sum     differs-from-reference             UNSAT    0.025
normalise      differs-from-reference             UNSAT    1.12
pack           differs-from-reference             UNSAT    0.001
epilogue       differs-from-reference             UNSAT    0.004
group_max      without `attained`                 SAT      0.022     (load-bearing, as intended)
state_shift    without `split`                    SAT      0.034
signed_sum     without `split`                    SAT      0.003
state_decode   without `z1`                       SAT      0.006
state_decode   without `f`                        SAT      0.002
group_step     two witnesses, two outputs, concrete x   UNSAT   57.8 / 11.9 (rerun)
group_step     two witnesses, two outputs, symbolic x   UNKNOWN 60 s (not rerun longer)
~~~

10/10 gadgets UNSAT over Z at REAL widths; every deliberately dropped predicate flips to SAT. The whole-group
two-witness query with symbolic inputs is UNKNOWN at 60 s, as v1's was at 300 s (v1 Z56-Z61 all UNKNOWN); it is not
counted as a pass. The per-gadget UNSATs compose because every wire between gadgets is a lookup output or a range-
checked hint (the composition census has zero unbounded wires), which is the same argument v1 rests on.

Field embedding. Two z3 readings of every gadget over F_p (hints are field elements in [0, p), identities and
lookups hold modulo p):

- *direct* (`modular_queries_v2`, as v1's): "an accepted assignment whose output residue differs from the
  reference's";
- *wrap-free* (`wrapfree_queries_v2`, new): "an accepted assignment in which some congruence holds with a non-zero
  multiple of p". UNSAT means the field reading of the predicates *is* the integer reading on the same values, so the
  integer UNSAT above transfers. It is a linear query whenever every lookup key is a linear function of bounded
  quantities, which is the v2 shape, and it closes what the direct product query leaves UNKNOWN.

~~~
gadget         direct F_goldilocks (600 s)   wrap-free F_goldilocks   direct F_m31 (600 s)   wrap-free F_m31
state_decode   UNSAT  0.2                    UNSAT 0.003              SAT   0.1              SAT (word arithmetic)
group_max      UNSAT  10.1                   SAT (see note)           UNSAT 5.8              SAT (see note)
state_shift    UNSAT 381 (after the fix)     UNSAT 0.002 (after)      SAT 52.7 (before); UNKNOWN 1800 (after)   UNSAT 0.001 (after)
signed_sum     UNSAT  0.4                    UNSAT 0.003              UNSAT 0.2              UNSAT 0.003
normalise      UNSAT 152 (1800 s run)        UNSAT 0.003              UNSAT 57 (1800 s run)  UNSAT 0.003
pack           UNSAT  0.02                   UNSAT (0 congruences)    UNSAT 0.02             UNSAT
epilogue       UNSAT  0.02                   UNSAT 0.002              SAT   0.004            SAT (word arithmetic)
~~~

The direct 600 s results are the main search job (`out/search_v2.log`); the 60 s redteam run had `signed_sum` M31
and `state_shift` Z UNKNOWN where the 600 s run has UNSAT (z3 variance, both recorded).

**A real finding, fixed.** `state_shift` as first written keyed its two SSHIFT lookups on M_hi R + 2 dt + s and
M_lo R + 2 dt + s with M_hi, M_lo hints bounded *only* through those keys. Over Z the key range bounds the hint; over
F_p the key is linear in the hint, so every table row kk has the field solution M_hi = (kk - 2dt - s) / R, and the
two rows are tied only by the split congruence M_hi 2^mb + M_lo = M (mod p). Over M31 z3 found the forgery in 53 s
(2^48 row pairs against 2^31 residues); over Goldilocks it is a counting argument (2^48 pairs against 2^64), not a
proof, and z3 returned UNKNOWN at 600 s (on the fixed gadget the direct Goldilocks query is UNSAT in 381 s). Fix: range-check the two halves themselves (two 16-bit chunks per group,
+4 lookups per unit, 85 -> 89); then every key is below p, the wrap-free query is UNSAT over both fields in
milliseconds, and the M31 direct query flips from SAT to (by transfer) UNSAT. The bench-instances (4096 tu-k16,
256 vu-k1536, 52 negatives) and the pytest suite were rerun on the fixed gadget; the red-team campaign rerun is
recorded in 3.4. Lesson recorded in the gadget's docstring: a lookup key proves a *linear combination* of hints is in
range, not the hints; in a field that is weaker.

Notes on the remaining rows. `group_max` wrap-free SAT is expected and harmless: E is a hint that enters 18 ALIGN4
keys as 4(E - e_i) + s4_i; a wrapped E' = E'' + m p satisfies every key congruence with the same rows as the small
E'' and every other use of E is a congruence too, so E' behaves as E'' -- the direct query, which is the one that
matters, is UNSAT over both fields. `normalise` wrap-free UNSAT over M31 means the product v_hi A never exceeds p
on admissible inputs (l = bit_length(v) is enforced by the LEAD outputs), i.e. the `_v2_norm_lookup` delta that
`explore.fields` charges 31-bit fields for v2 is a conservative overcharge: the M31 re-pricing in section 4 is an
upper bound. The M31 SATs that remain (`state_decode`, `epilogue`) are the word-arithmetic class v1 has too
(fp32 word = s 2^31 + e 2^23 + f wraps in a 31-bit field; v1's F4 limb repair), present in the word-in unit and the
epilogue only, absent in the state-chained VU body; 31-bit v2 is proven for the VU body, modelled for the ends.

### 3.3 Differential tests against the reference (MEASURED)

~~~
set                                       n        result
structured (zero groups, ties, carries)   27       agree with silicon
random groups                             2000     agree
golden groups (fixtures)                  360      agree
bench-instances/v1 tu-k16                 4096     4096 accepted, outputs equal (pod, 3.0 s)
bench-instances/v1 vu-k1536               256      256 accepted, all 96 intermediate states equal (pod, 16.9 s)
bench-instances/v1 vu-k1536-neg           52       52 rejected (44 verdict wrong-output, 8 verdict reject)
~~~

(`notes-asset:campaigns/r20-proof/assets/checker-min/reports/checker_v2_bench.json`; 44 "wrong" = in-domain with a wrong claimed word, 8 "reject" = out of domain (non-finite
operand, saturated intermediate) -- the instance set's own labelling; v2 rejects every one, as v1 did.)

### 3.4 Red team against v2 (MEASURED, `redteam.campaign --target checker-v2`, `notes-asset:campaigns/r20-proof/assets/red-team-checker/reports/redteam_checker_v2.json`)

Rerun on the fixed `state_shift` (the file is the rerun). Unit target (word in / word out) and VU target (3 chained
units + Pack + epilogue), over Z, Goldilocks, M31: completeness PASS (87 unit cases, 3 VU cases); mutation of every
hint column: no accepted forgery in any field (2555 mutations per field; NOTE = mutations that change no output are
recorded, as in v1), VU mutations 666/666 rejected; coordinated two-outputs-one-input PASS over Z and Goldilocks,
SAT over M31 (as v1's X12: the word-arithmetic class of `state_decode`/`epilogue`). Tally: UNSAT 17, PASS 9, NOTE 8,
SAT 3 (X9, Z29 `state_decode` M31, Z41 `epilogue` M31 -- all the F4 word class; the `state_shift` M31 SAT of the
first run is gone), UNKNOWN 7 (60 s direct modular queries, all resolved by the 600 s run or by wrap-free transfer
above, plus the two 60 s group-step queries). No accepted negative over Z or Goldilocks; over M31 none outside the
known word-arithmetic class.

### 3.5 Open items at writing

- Every v2 gadget is now UNSAT over Goldilocks by the direct query (`state_shift` 381 s, `normalise` 152 s at
  1800 s timeout) *and* by wrap-free transfer. Over M31 the direct `state_shift` query is UNKNOWN at 1800 s and is
  covered by wrap-free transfer only (UNSAT in 1 ms; the composition step "wrap-free + integer UNSAT => field UNSAT"
  is a one-line argument, stated in `z3_gadget_wrapfree`'s docstring).
- Whole-group two-witness query: concrete inputs UNSAT (57.8 s first run, 11.9 s at 1800 s timeout; the 60 s
  redteam rerun hit UNKNOWN -- z3 variance); symbolic inputs UNKNOWN at 60 s (as v1's Z56-Z61), not a pass.
- 31-bit fields: modelled repairs only (as v1).

## 4. Re-pricing (MODELLED: `explore.tensor`, `explore.vole` with `VERITY_CHECKER_VARIANT=v2`; 2^-128, B=4096)

~~~
design   field       limb MACs/VU (v1 -> v2)     committed/VU (v1 -> v2)   overhead (v1 -> v2)     s/VU
A        M31         7.52e9 -> 1.86e9  (-75%)    183 kB -> 119 kB          1.07e7 -> 3.18e6 (-70%) 0.431 -> 0.128
A        BabyBear    same as M31                                            -> 3.82e6
A        Goldilocks                                                         -> 5.45e6
B        M31         5.81e9 -> 1.89e9  (-67%)    1.155 MB -> 0.385 MB      1.42e7 -> 4.70e6 (-67%) 0.574 -> 0.190
~~~

A's sequential depth 381 -> 303 rounds. B's modelled time is now 71% Merkle hashing: the next lever for B is the
hash, not the arithmetic. VOLE (designated verifier, logup ranges, QuickSilver anchor): 220 s -> 65.9 s per
4096-VU batch (0.054 -> 0.016 s/VU, -70%); at B=1 v2 is *worse* (0.078 -> 1.91 s/VU) because the 5.2M table rows
are paid per proof -- v2 needs batching above ~B=64 to win under VOLE, and above ~B=500 the SHIFT table should be
replaced by its split-u variant (two 21k-row lookups per product, +16 lookups per unit) for small batches.

Ledger (`reports/ledger/checker-min.jsonl`): 5 `component` entries (T_OP decode; ALIGN4+SHIFT alignment;
LEAD/LEADNORM/TNORM sum+normalise; state-chained VU; unit total) and 4 `vu` ARITHMETIC_DIAGNOSTIC entries (A and B
baselines on v1, A and B re-priced on v2, `--breakthrough`).

## 5. Rejected, and not tried

Rejected:
- Packing two 16-bit products into one field multiplication (2d): impossible on 31-bit fields, net negative on
  Goldilocks once the separation is priced.
- A witness index j for "E\* attained" (2c): correct but costlier than the [d_i=0] indicator sum that `ALIGN4`
  already provides.
- A single SHIFT-style table for the state term (2^31 x 27 shifts): 5.8e10 rows; replaced by two 221k-row halves.
- Keeping intermediate FP32 words as VU wires with a cheaper decode: the word is redundant once the state tuple is
  chained; decoding it costs more than the per-unit ovf_eff = 0 identity that replaces its finiteness guarantee.

Not tried (candidates for a second pass):
- Small-field (31-bit) v2 as a verified gadget set rather than modelled deltas (the F4-style limb split of the
  state-decode / epilogue word arithmetic and the TNORM_HI lookup for v_hi A).
- The split-u SHIFT variant for small batches, and pricing table commitment against batch size explicitly in
  `explore.tensor` rather than through the amortised row count.
- Sharing one `LEAD` range/bit-length lookup between the two 15-bit halves when the high half is zero.
- Merging `ALIGN4` and `SHIFT` into a single lookup keyed on (u, E - e, s4) (95M rows: only if the commitment model
  says row count is nearly free at B=4096).
- A GKR-layered census (mul_by_depth is recorded: 23 at depth 1, 7 at depth 2, 3 at depth 3) to size Candidate A's
  layers on v2 precisely.
- Resolving the whole-group symbolic two-witness query by case-splitting on E\* (16 concrete E\* values x symbolic
  rest), which the per-gadget structure now makes tractable.
