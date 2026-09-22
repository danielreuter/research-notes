---
id: r20-proof/red-team-babybear/20260922T0605Z-report-babybear-rules
campaign: r20-proof
lane: red-team-babybear
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/babybear_rules.md
---

# BabyBear embedding rules for the WP2 checker (red-team-babybear)

p = 2^31 - 2^27 + 1 = 2013265921 (log2 p = 30.907). Every predicate of every gadget contract was run on
integer intervals (`verity_numerical.redteam.babybear.analyse`): inputs and hints at their declared ranges, table
columns at their row extremes; the mod-p reading of a predicate is sound iff the interval of what it constrains lies
in a window of width p (identity: `a - b` in (-p, p); range check on an expression: in `[hi - p, lo + p)`; the
product realisation of a variable bound: `x * ipow` in `[2^B - p, p)`). Widths: acc_bits = 25, prod_bits = 26, s_bits = 30, |S| <= s_max = 570417150 (2^29.x), norm remainder 7 bits, k in [-7, 24].

## 1. Predicates whose integer bound exceeds p as stated, and the rule that closes each

| gadget | predicate | as-stated interval | bits | rule | embedded bits | embedded sound | added columns / lookups |
|---|---|---|---|---|---|---|---|
| fp32_decode | `acc.word` | [-4294967295, 4286578687] | 32 | LIMB16 | 16 | yes | +2 hint columns (f_lo 16 b, f_hi 7 b), +2 16/7-bit ranges, -1 23-bit range, +1 identity; c as 2 public limbs |
| align_state | `align_state.rem` | [0, 1125899873288192] | 50 | LT_DIRECT | 25 | yes | no multiplication; one 25-bit range (2 chunk lookups) on a linear wire, as before |
| align_state | `align_state.quot` | [0, 1125899873288192] | 50 | LT_DIRECT+QUOT_TIGHT | 25 | yes | no multiplication; one 25-bit range on a linear wire |
| align_product | `align_prod.rem` | [0, 4294901760] | 32 | LT_DIRECT | 16 | yes | no multiplication; one 16-bit range on a linear wire |
| align_product | `align_prod.quot` | [0, 4294901760] | 32 | LT_DIRECT+QUOT_TIGHT | 16 | yes | no multiplication; one 16-bit range on a linear wire |
| leading_bit | `lead.window` | [-576460752303423488, 1152921503533105152] | 60 | LT_DIRECT+V_PREMISE | 30 | yes | LEAD gains column span; no multiplication; two 30-bit ranges (4 chunk lookups) on the linear wire v - lo (>= 0 and < span) |
| normalise | `norm.div` | [-18014398492704768, 2147483647] | 54 | NORM_MBND+NORM_VBND(redundant)+V_PREMISE | 31 | yes | NORM gains columns mbnd (and vbnd); +1 30-bit range (2 chunk lookups) per group [+1 if vbnd kept]; 0 hints, 0 multiplications |
| pack | `pack.y[0]` | [-5351931903, 5435817983] | 33 | LIMB16 | 16 | yes | +2 hint columns (low_lo, low_hi), +1 identity; y as 2 public limbs |
| epilogue | `cast.split` | [-4294967295, 4294967295] | 32 | LIMB16 | 0 | yes | -2 hint columns (hi, lo are the public limbs), -1 identity, -2 ranges |

## 2. The rules

- **LIMB16**: the word is two public 16-bit limbs; the identity is stated per limb (fraction limbs f_lo/f_hi or low_lo/low_hi as hints)
- **LT_DIRECT**: direct variable-bound check rng(bnd - 1 - x, 0, 2^B) against the table's bound column (POW/ALIGN: the partner column; LEAD: new column span), plus rng(x, 0, 2^B) when x is not a range-checked hint (the leading-bit window v - lo: the direct form alone loses v >= lo -- z3 found it)
- **QUOT_TIGHT**: the tight quotient bound q < 2^B / pow (direct) keeps q * pow + r below 2^B, so the division identity stays inside (-p, p)
- **NORM_MBND**: NORM column mbnd = 2^30 / div and rng(mbnd - 1 - M', 0, 2^30): the quotient is tight relative to the dividend v < 2^30
- **NORM_VBND**: NORM column vbnd = 2^24 / mul (k >= 0) and rng(vbnd - 1 - v, 0, 2^30): v * mul < 2^24 (redundant given leading_bit; see z3)
- **V_PREMISE**: v is the signed-sum wire, |v| <= s_max = 570,417,150 < 2^29.1 by the ranges of its terms; leading_bit/normalise are stated for v in [0, s_max]

## 3. Safe as stated over BabyBear (bound < p): no change for the lanes

| gadget | predicate | kind | interval | bits |
|---|---|---|---|---|
| bf16_decode | `s` | boolean | [0, 1] | 1 |
| bf16_decode | `nz` | boolean | [0, 1] | 1 |
| bf16_decode | `bf16.t` | rng | [0, 254] | 8 |
| bf16_decode | `bf16.f` | rng | [0, 127] | 7 |
| bf16_decode | `bf16.word` | eq | [-65535, 65407] | 16 |
| bf16_decode | `bf16.nz0` | eq | [0, 254] | 8 |
| bf16_decode | `bf16.nz1` | rng | [-1, 254] | 8 |
| fp32_decode | `s` | boolean | [0, 1] | 1 |
| fp32_decode | `nz` | boolean | [0, 1] | 1 |
| fp32_decode | `z` | boolean | [0, 1] | 1 |
| fp32_decode | `acc.t` | rng | [0, 254] | 8 |
| fp32_decode | `acc.f` | rng | [0, 8388607] | 23 |
| fp32_decode | `acc.nz0` | eq | [0, 254] | 8 |
| fp32_decode | `acc.nz1` | rng | [-1, 254] | 8 |
| fp32_decode | `acc.z0` | eq | [0, 16777215] | 24 |
| fp32_decode | `acc.z1` | rng | [-1, 16777215] | 24 |
| product | `s_a` | boolean | [0, 1] | 1 |
| product | `s_b` | boolean | [0, 1] | 1 |
| product | `z` | boolean | [0, 1] | 1 |
| product | `prod.z0` | eq | [0, 65025] | 16 |
| product | `prod.z1` | rng | [-1, 65025] | 16 |
| group_max | `sel[0]` | boolean | [0, 1] | 1 |
| group_max | `sel[1]` | boolean | [0, 1] | 1 |
| group_max | `sel[2]` | boolean | [0, 1] | 1 |
| group_max | `sel[3]` | boolean | [0, 1] | 1 |
| group_max | `sel[4]` | boolean | [0, 1] | 1 |
| group_max | `sel[5]` | boolean | [0, 1] | 1 |
| group_max | `sel[6]` | boolean | [0, 1] | 1 |
| group_max | `sel[7]` | boolean | [0, 1] | 1 |
| group_max | `sel[8]` | boolean | [0, 1] | 1 |
| group_max | `sel[9]` | boolean | [0, 1] | 1 |
| group_max | `max.E` | rng | [-132, 259] | 9 |
| group_max | `max.attained` | eq | [-2659, 2463] | 12 |
| group_max | `max.d[0]` | rng | [-391, 511] | 9 |
| group_max | `max.d[1]` | rng | [-391, 511] | 9 |
| group_max | `max.d[2]` | rng | [-391, 511] | 9 |
| group_max | `max.d[3]` | rng | [-391, 511] | 9 |
| group_max | `max.d[4]` | rng | [-391, 511] | 9 |
| group_max | `max.d[5]` | rng | [-391, 511] | 9 |
| group_max | `max.d[6]` | rng | [-391, 511] | 9 |
| group_max | `max.d[7]` | rng | [-391, 511] | 9 |
| group_max | `max.d[8]` | rng | [-391, 511] | 9 |
| group_max | `max.d_floor` | rng | [0, 391] | 9 |
| align_state | `align_state.q` | rng | [0, 33554431] | 25 |
| align_state | `align_state.r` | rng | [0, 33554431] | 25 |
| align_state | `align_state.pow` | lookup | [0, 511] | 9 |
| align_state | `align_state.div` | eq | [-33554430, 67108862] | 26 |
| align_product | `align_prod.q` | rng | [0, 65535] | 16 |
| align_product | `align_prod.r` | rng | [0, 65535] | 16 |
| align_product | `align_prod.align` | lookup | [0, 511] | 9 |
| align_product | `align_prod.div` | eq | [-65535, 131070] | 17 |
| signed_sum | `s[0]` | boolean | [0, 1] | 1 |
| signed_sum | `s[1]` | boolean | [0, 1] | 1 |
| signed_sum | `s[2]` | boolean | [0, 1] | 1 |
| signed_sum | `s[3]` | boolean | [0, 1] | 1 |
| signed_sum | `s[4]` | boolean | [0, 1] | 1 |
| signed_sum | `s[5]` | boolean | [0, 1] | 1 |
| signed_sum | `s[6]` | boolean | [0, 1] | 1 |
| signed_sum | `s[7]` | boolean | [0, 1] | 1 |
| signed_sum | `s[8]` | boolean | [0, 1] | 1 |
| signed_sum | `sgn` | boolean | [0, 1] | 1 |
| signed_sum | `z` | boolean | [0, 1] | 1 |
| signed_sum | `sum.v` | rng | [-570425335, 570425335] | 30 |
| signed_sum | `sum.z0` | eq | [-570425335, 570425335] | 30 |
| signed_sum | `sum.z1` | rng | [-570425336, 570425335] | 30 |
| leading_bit | `lead.lead` | lookup | [0, 30] | 5 |
| normalise | `clamp` | boolean | [0, 1] | 1 |
| normalise | `norm.M` | rng | [0, 16777215] | 24 |
| normalise | `norm.r` | rng | [0, 127] | 7 |
| normalise | `norm.clamp_proof` | rng | [-391, 390] | 9 |
| normalise | `norm.norm` | lookup | [-7, 384] | 9 |
| normalise | `norm.rem` | lt_pow | [0, 16256] | 14 |
| state_out | `sgn` | boolean | [0, 1] | 1 |
| state_out | `z` | boolean | [0, 1] | 1 |
| state_out | `ovf` | boolean | [0, 1] | 1 |
| state_out | `out.z0` | eq | [0, 16777215] | 24 |
| state_out | `out.z1` | rng | [-1, 16777215] | 24 |
| state_out | `out.ovf_proof` | rng | [-254, 253] | 8 |
| pack | `s` | boolean | [0, 1] | 1 |
| pack | `z` | boolean | [0, 1] | 1 |
| pack | `ovf[0]` | boolean | [0, 1] | 1 |
| pack | `ovf[1]` | boolean | [0, 1] | 1 |
| pack | `sgn[0]` | boolean | [0, 1] | 1 |
| pack | `sgn[1]` | boolean | [0, 1] | 1 |
| pack | `hidden` | boolean | [0, 1] | 1 |
| pack | `pack.low` | rng | [0, 8388607] | 23 |
| pack | `pack.M` | eq | [-16777215, 16777215] | 24 |
| epilogue | `lsb` | boolean | [0, 1] | 1 |
| epilogue | `carry` | boolean | [0, 1] | 1 |
| epilogue | `cast.hi` | rng | [0, 65535] | 16 |
| epilogue | `cast.lo` | rng | [0, 65535] | 16 |
| epilogue | `cast.hi2` | rng | [0, 32767] | 15 |
| epilogue | `cast.rem` | rng | [0, 65535] | 16 |
| epilogue | `cast.lsb_split` | eq | [-65535, 65535] | 16 |
| epilogue | `cast.round` | eq | [-98303, 98304] | 17 |
| epilogue | `cast.y16` | rng | [0, 65536] | 17 |

## 4. Under the full rule set every one of the 109 predicates lies inside its window.

## 5. Dropping one rule at a time: predicates that leave their window (interval verdict; z3 in `z3_babybear` decides)

| rule dropped | predicates outside the window by interval arithmetic |
|---|---|
| LIMB16 | `fp32_decode.acc.word`, `pack.pack.y[0]`, `epilogue.cast.split` |
| LT_DIRECT | `align_state.align_state.rem`, `align_state.align_state.quot`, `align_product.align_prod.rem`, `align_product.align_prod.quot`, `leading_bit.lead.window` |
| QUOT_TIGHT | `align_state.align_state.div`, `align_product.align_prod.div` |
| NORM_MBND | `normalise.norm.div` |
| NORM_VBND | `normalise.norm.div` |
| V_PREMISE | `leading_bit.lead.window`, `normalise.norm.vbnd` |


<!-- hand-written appendix: z3 verdicts, battery, accounting -->

## 6. z3 over F_p = BabyBear: every embedded gadget, all rules, then each rule dropped

Run `r20260922-054949-dcc0` on vy-cpu3 (12 procs, 300 s per job, tree 91ec50e; `z3_babybear.py --json`, raw in
`notes-asset:campaigns/r20-proof/assets/red-team-babybear/reports/z3_babybear.json`).  Each gadget's *embedded* `check` (limbs, direct bounds, tight quotient) is asserted
modulo p on the declared hint ranges read mod p; z3 searches for an accepted witness whose outputs differ from the
integer reference.  Jobs are split on the table row (POW/ALIGN/LEAD/NORM pinned) and on every bit-valued input/hint,
as wave 2 did for the U2 selector split; a gadget is UNSAT iff every job is.  `lead_norm` is `leading_bit` composed
with `normalise` with `l` a free hint (the composition the `NORM_VBND` redundancy claim rests on).

~~~
gadget         rules        verdict   jobs   unsat/sat/unknown   z3 s (sum)  max
bf16_decode    all          UNSAT        4   4/0/0                0.1   0.04
fp32_decode    all          UNSAT        8   8/0/0                0.2   0.05
product        all          UNSAT        8   8/0/0                0.0   0.01
group_max      all          UNSAT     1024   1024/0/0             2.6   0.33
align_state    all          UNSAT      512   512/0/0              4.0   0.04
align_product  all          UNSAT      512   512/0/0              4.8   0.03
signed_sum     all          UNSAT     2048   2048/0/0            11.6   0.02
leading_bit    all          UNSAT       31   31/0/0               0.5   0.03
normalise      all          UNSAT       64   64/0/0              22.2   1.47
lead_norm      all          UNSAT     1984   1984/0/0           139.0   2.69
state_out      all          UNSAT        8   8/0/0                0.0   0.01
pack           all          UNSAT      128   128/0/0              1.8   0.27
epilogue       all          UNSAT        4   4/0/0                0.1   0.03

fp32_decode    -LIMB16      SAT          8   2/6/0     c = (0, 61568): f = 2^23 - 2 read as the word's fraction
pack           -LIMB16      UNSAT      128   128/0/0   (the output limbs are a layout, not a soundness rule)
epilogue       -LIMB16      SAT          4   0/4/0     y32 = 32767 -> hi 30720, lo 32768, rem 65535: y16 = 30720 (ref 0)
align_state    -LT_DIRECT   SAT        512   0/512/0   M = 2^24 - 1, d = 0: q = 33554369, r = 61 (ref q = 33554430)
align_product  -LT_DIRECT   SAT        512   13/499/0  u = 65535, d = 0: q = 34814, r = 30721
leading_bit    -LT_DIRECT   SAT         31   0/31/0    v = 16, l = 0 (ref 5)
lead_norm      -LT_DIRECT   SAT       1984   1954/30/0 E = -100, v = 0, l = 1: e1 = -124 (ref -125)
align_state    -QUOT_TIGHT  SAT        512   6/506/0   M = 0, d = 6: q = 31457280, r = 1 (q 2^6 + r = p + 0)
align_product  -QUOT_TIGHT  SAT        512   25/487/0  u = 0, d = 25: q = 61440, r = 1
normalise      -NORM_MBND   SAT         64   63/1/0    E = -132, l = 19, v = 2^18, clamp: M = 15730688 (ref 2048)
lead_norm      -NORM_MBND   SAT       1984   1956/28/0 E = -132, v = 0, clamp: M = 15728640 (ref 0)
normalise      -NORM_VBND   UNSAT       64   64/0/0    REDUNDANT
lead_norm      -NORM_VBND   UNSAT     1984   1984/0/0  REDUNDANT (also with l free)
leading_bit    -V_PREMISE   SAT         31   4/27/0    v = 939524098 = p - 2^30 + 1, l = 0 (ref 30)
normalise      -V_PREMISE   UNSAT       64   64/0/0
lead_norm      -V_PREMISE   SAT       1984   1684/299/1  E = -124, v = 1006633088, l = 0, clamp (1 job timed out at 300 s; verdict SAT regardless)
~~~

Verdicts:

* **All 13 embedded gadgets UNSAT under the six rules** (5,375 jobs, 187 s of z3, no UNKNOWN).
* **Necessary** (dropping it is SAT with a concrete forgery): `LIMB16` (fp32_decode, epilogue), `LT_DIRECT`
  (align_state, align_product, leading_bit), `QUOT_TIGHT` (align_state, align_product), `NORM_MBND` (normalise),
  `V_PREMISE` (leading_bit; it is a guarantee of `signed_sum`'s ranges, |v| <= s_max = 570,417,150, not a check).
* **Redundant**: `NORM_VBND` -- the extra bound `v < 2^l` in `normalise` stays UNSAT without it, in isolation *and*
  composed with `leading_bit` with `l` a free hint.  Lanes may drop the `vbnd` column of NORM and its 30-bit range
  (1 column, 2 chunk lookups per group).  `pack`'s limb output is a layout choice, not a soundness rule (UNSAT
  without it); the limbs are still what the chained unit consumes.
* **Found by z3 and fixed in this spec (run 1 -> run 2)**: the direct realisation of the leading-bit window,
  `rng(span - 1 - (v - lo), 0, 2^30)`, bounds `v - lo` only from above; `v = p - 2^30 + 1`, `l = 0` passed.  The
  rule now reads: the direct form of `0 <= x < bnd` for an `x` that is not itself a range-checked hint is **two**
  ranges, `rng(x, 0, 2^B)` and `rng(bnd - 1 - x, 0, 2^B)` (section 2, `LT_DIRECT`).  A lane that implemented the
  first draft of this table would have shipped that hole: relayed as a breakthrough ledger entry
  (`leading_bit window lower bound`).

## 7. The forgery battery (`redteam/battery_babybear.py`, `fixtures/redteam/babybear-battery/v1/`)

83 cases, every expected verdict **reject**; `run_battery(prover_accepts) -> report` takes a callable on a `Case`
(`level` step / vu / gadget, WP2 hint layout of `gen_step` plus the limb hints, claimed output = what the mutated
witness leads a congruence-only checker to).  Honest instances are the Ada golden records (finite ones).

~~~
class        cases  what                                                                       naive mod-p  embedded
wrap            58  (u, w) hints of one gadget re-split with u' 2^s + w' = u 2^s + w + p,        reject       reject
                    every downstream hint re-derived honestly from the wrong value
fractional       1  x -> (x 2^s + j p)/2^s on a single hint                                       reject       reject
zero_swap        4  +0 <-> -0 in an operand / the accumulator, honest hints kept                  reject       reject
hint_swap        3  another instance's hints under these operands (whole tree / one operand)      reject       reject
chain            4  unit-2 accumulator handed as c + p (a valid FP32 word != c; unit-2 decodes it)  ACCEPT     reject
epilogue         1  RN-even tie 0x....8000 with lsb/carry toggled                                  reject       reject
z3              12  the SAT models above, one per (gadget, dropped rule)                       n/a (gadget) reject; ACCEPTED without the rule
~~~

Teeth: the naive checker (every WP2 predicate mod p as written, products read mod p, a range wider than p left
unchecked because it has no in-field realisation) accepts the four `chain` forgeries -- the +p shadow of the
accumulator word between units, exactly the autoproof class -- and each of the 12 z3 models is accepted by the
embedding with its rule removed.  The WP2 integer checker rejects all 71 step/vu cases; the embedded BabyBear
checker (all rules) rejects all 83.  Per-hint `wrap`/`fractional` mutations mostly die on the hint's *own* range
check (WP2 declares a range for every hint), which is why those classes are small: the wraps that survive a
per-hint range are precisely the product-realised bounds, and those are the z3 rows.

Not in v1: bench-instances/v1 operands (the golden groups stand in), Hopper params (the rules table is per-params;
REAL = Ampere is what the lanes are building).

## 8. Soundness accounting for BabyBear^d (`security.accounting`, K = 1536, B = 4096, 393,216 units)

Ligero n = 2^14, k = 2^12, l = 3840 (the test-suite parameters); union bound over every term; exact rationals.

~~~
challenge field   Ligero t   candidate   lookup (T_range16, 65,536 rows, 1.12e8 queries)   total        meets 2^-128   meets 2^-80
BabyBear^4          121      A / B       2^-96.5  (identity term alone 2^-96.9)             2^-82.0      no             yes
BabyBear^4          192      A / B       2^-96.5                                            2^-96.5/-94.8 no            yes
BabyBear^5          192      A / B       2^-127.4                                           2^-126.6/-125.4 no          yes
BabyBear^6          192      A / B       2^-158.3 (identity term alone 2^-158.7)            2^-127.7     no*            yes
BabyBear^6 (hash 2^60 queries) 192  A/B  2^-158.3                                           2^-130.2     yes            yes
first_configuration(-128): degree 6, t = 191, total 2^-129.5 (A and B); first_configuration(-80): degree 4, t = 120, total 2^-81.4
~~~

\* at the default hash model (2^64 adversary queries against a 256-bit hash) the collision term is exactly 2^-128 on
its own, so no configuration meets 2^-128 -- a modelling choice, not a field property.  With 2^60 queries (what
`first_configuration` uses) **note:r20-proof/tensor-cost/20260922T0450Z-report-tensor's claim stands: BabyBear^6 is the first degree that reaches 2^-128**, and
degree 5 misses on the lookup identity term (2^-127.4).  At 2^-80 degree 4 is right with the lookup term at
2^-96.5 and the Ligero opening term (2^-82.0 at t = 121) the binding one.
