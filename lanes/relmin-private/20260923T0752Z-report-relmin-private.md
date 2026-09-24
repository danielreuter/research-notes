CHECKPOINT 78daae8 (final, 12:12Z) four v3 (private-operand) relations: bf16-hopper-v3 1519 rows/unit (v1 3292, 2.17x), bf16-ampere-v3 1629 (3516, 2.16x), fp8-hopper-v3 1673 (3396, 2.03x), fp8-ada-v3 1806 (3769, 2.09x); operands stay committed witness wires bound by pin rows (the words themselves; 3 E4M3 words per pin); Rust pins + fixtures + tests (cargo test green), D13.  **The 1e5 differential found a completeness gap** (an exact-zero sum with E > acc_e_min + width has no shift on v2's subnormal grid: the honest unit was rejected at `g0.norm.clamp`; **fp8-hopper-v2 in main rejects the same unit** -- relmin-lookup's normalisation rule, §4b); fixed in 78daae8 with no row (`(1 - hid - nsel[t_lo]) (t - tc) = 0`), regression test, digests re-pinned.  Evidence on the pre-fix systems (9a42e39): all four GPU gates PASSED (r20260923-092224-1e88: 49/87/0, 25/92/0, 25/92/0, 49/87/0), the pod pytest of the same run failed exactly at the differential (fp8-ada-v3 unit 874, the same gap).  **On 78daae8**: the 1e5 differentials PASSED for all four (laptop, 10:33-10:43Z); 11 benches on the same 4090 (§5): fp8-ada v1 -> v3 int-ZK l=4096 **0.686 -> 0.593 s** (proof 181.5 -> 103.4 MB), l=16384 2.148 -> 1.147 s; bf16-hopper l=16384 3.552 -> 1.873 s, fp8-hopper 1.949 -> 1.062 s, bf16-ampere-v3 2.023 s -- every dump Rust + Python batch-verified at 128 bits on the pod (33 + 11 verdicts, `system pinned`); the l=16384 absolute times are on main 02c3321's encoder, 15x slower at n = 65536 on the 4090 than relmin-lookup's tree (§5 caveat, cross-lane).  **Gates on 78daae8 all four PASSED** (r20260923-110015-4eb2, 11:00-11:46Z: fp8-hopper-v3 25 / 92 / 0, fp8-ada-v3 25 / 92 / 0, bf16-ampere-v3 49 / 87 / 0, bf16-hopper-v3 49 / 87 / 0) and the pod's **`pytest backends/direct/ligero`: 156 passed, 1 skipped** (19 min, the same run); local `privsel/relation_test.py` 36 passed.  Snapshot **relmin-private-v3 = art:2920f7a0c313439fed869316c86e432ecb1672cd6693122c6bdcabfe4d13de57** (23 members: the 11 benches' result + run_files with dumps, the gate run's files + verify verdicts art:56d667e0...).  Pod terminated 12:10Z (~3.75 pod-hours).  Branch `lane/relmin-private` at 78daae8, `git status` clean, mergeable.

# Lane relmin-private -- private-operand row-minimal units (2026-09-23, 07:24Z-12:30Z)

Worktree `~/projects/verity-main-wt/relmin-private`, branch `lane/relmin-private` off main `02c3321` (= main + relmin-lookup
0055c41).  Commits: 89ca9ea (first four v3 units: 1567 / 1677 / 1864 / 1986), 34e1b1e (no `zero` option, `K` in bits, packed
E4M3 pins, FP8 group `hi` flag: 1535 / 1645 / 1705 / 1838), 196bc6f (Rust: `Decode::PrivSel`, four pins, fixtures, tests),
de8c459 (signed aligned product as one hint under two row-free quadratics: **1519 / 1629 / 1673 / 1806**, the final systems),
9a42e39 (`rust_verifiable`, D13), e64dd71 (a docstring), 78daae8 (the exact-zero-sum fix, §4b; one quadratic changed, rows unchanged, digests re-pinned).  Code: `backends/direct/ligero/privsel/` (`relation.py` the compiler + the verifier's word
pins, `hints.py` torch + Python-integer hint generators, `relation_test.py` 30 tests), `relations.py` (four names beside v1 / v2,
`_v3_of`), `run.py` (choices only), `backends/ligero-verify` (`privsel::PrivSel`, `Decode::PrivSel`, `verify.rs
public_pins_privsel`, four pins + fixtures + tests, D13).  v1, v2, `compile.py`, `relchain.py`, the protocol: untouched.
`git status --short` empty at 78daae8.

## 0. What is different from v2 (and why v2's 10x does not carry)

v2 pins, per group, `G` and `Q[j]` for every extra shift -- the verifier recomputes the products, their zero flags, the group
maximum and the truncated product sums.  With private operands none of that is available: the operand words are committed
wires and the relation must prove the decode, every product, every truncating alignment, the group maximum, the exact sum, the
normalisation and the epilogue -- v1's statement.  The v3 unit keeps v2's private half (accumulator window, sum, normalisation,
flags, packing, RN-even epilogue: imported helpers, unchanged) and rebuilds the public half with row-free tools only: `_pick`
(one hint row + one row-free quadratic per candidate), bit windows of committed bits, zero-products and inverses for flags, and a
digit representation in which a shift by a multiple of the radix is a digit selection.  **Pin variant**: the operand words are
witness wires `a_words[i]` (the weighted sum of the word's hint bits) and the statement's words enter through pin rows holding
the words themselves -- `a[i]` (one BF16 word per pin) or `a[lo:hi]` (three E4M3 words packed little-endian per pin) -- with one
linear constraint per pin.  Lane hash-relation replaces those pin rows by a sponge over the same wires (§3).

## 1. Where the rows go (chain mode, per unit; `fp8.census.census` + scope census of the final systems)

| relation | v1 rows | v3 rows | ratio | hint | bit | inv | prod | sel | pin | lin / quad | quad nonzeros v1 -> v3 (max terms) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16-hopper-v3 | 3292 | **1519** | 2.17x | 1285 | 119 | 38 | 18 | 27 | 32 | 110 / 2245 | 11292 -> 12008 (34 -> 35) |
| bf16-ampere-v3 | 3516 | **1629** | 2.16x | 1290 | 191 | 40 | 24 | 52 | 32 | 116 / 2322 | 11955 -> 13550 (32 -> 59) |
| fp8-hopper-v3 | 3396 | **1673** | 2.03x | 1452 | 101 | 69 | 14 | 15 | 22 | 120 / 2366 | 11540 -> 10715 (67 -> 29) |
| fp8-ada-v3 | 3769 | **1806** | 2.09x | 1491 | 169 | 71 | 23 | 30 | 22 | 130 / 2542 | 12764 -> 11939 (35 -> 44) |

By gadget, bf16-hopper-v3 (1519): **words 576** = 32 x 18 (per word: `s`, 8 bits of `x = t - nz`, 7 bits of `f`, `nz`, one
inverse `floor(x/2) != 127`); **products 672** = 16 x 42 (per product: 16 bits of `u = m_a m_b`, fine one-hot `r` 8, digits `D0..D2`
3, coarse one-hot `c` 5, aligned limbs `XL`/`XH` 2, dead quotient `K` 6 bits, signed limbs `XsL`/`XsH` 2); pins 32; acc 76 (v2's);
group maximum 20 (`E`, `which` 17, `C` + inverse); sum 46 (`sgn`, `vL`, `vH`, 42 bits, `carry`); normalisation 68 (`nsel` 34, `hid`,
`fo`, 32 bits); out / pack / epi 14 + 6 + 5.  fp8-hopper-v3 (1673): words 640 = 64 x 10 (`s`, 4 bits of `x`, 3 of `f`, `nz`,
inverse `x != 15`), products 800 = 32 x 25 (`u` 8, `r` 4, `D` 3, `c` 5, `X` 1, `K` 3, `Xs` 1), pins 22, acc 64, `hi` cap 12, maximum
35 (`which` 33), sum 24, normalisation 51, out / pack 20.  The private operands' own cost -- decode + product bits + alignment --
is 1248 of 1519 (82 %) and 1440 of 1673 (86 %): 16 (8) bits of information per word and 16 (8) bits per product are the floor of
any bit-based range argument; what is left to squeeze is the 26 (17) rows of alignment per product.

Row history (per commit): 89ca9ea 1567 / 1677 / 1864 / 1986 -> 34e1b1e -32 / -32 / -159 / -148 (the `zero` coarse option
dropped: the exponent constraint is `u (E - e_i - d) = 0`, so a zero product takes any option; `K` as bits instead of a ranged
hint; FP8 pins packed 3 words per row (64 -> 22); the FP8 group flag `hi = [E >= 31]` capping `E_eff = min(E, 31)` so the dead
range needs 3 `K` bits instead of 5) -> de8c459 -16 / -16 / -32 / -32 (the signed aligned product `(1 - 2 (s_a xor s_b)) X` as one
hint `Xs` under `(Xs - X)(1 - s_a - s_b) = 0` and `(Xs + X)(s_a - s_b) = 0` -- exactly one factor is nonzero for every sign pair --
instead of a sign hint, a row-free XOR and a product row).

## 2. Design (privsel/relation.py, one code path for the four relations)

* **Operand decode** (`_decode_word`): hint bits `s`, `x[j]` (8 / 4 bits), `f[j]` (7 / 3 bits), `nz`; the word wire
  `w = s 2^(W-1) + (x + nz) 2^F + f` (the `(x, nz)` split makes `m = f + nz 2^F` and `e = x - (bias - 1)` affine); `nz = 0 -> x = 0`
  by the zero-product `(1 - nz) x = 0`; the top of `x` by ONE inverse: BF16 `floor(x/2) != 127` (the inverse of the affine form
  `sum_{j>=1} 2^(j-1) x[j] - 127`, excluding `x in {254, 255}`, i.e. `t = 255` (inf / NaN) and `t = 256`, the encoding's collision
  with the sign bit); E4M3 `x != 15`.  The E4M3 NaN (`t = 15, f = 7`) is the one off-domain word the relation admits; the verifier's word check refuses it
  in the pin variant (§3 for the sponge variant).  Off the domain otherwise means: nothing -- every word wire encodes exactly
  one finite word, and `test_committed_words_are_bound_and_canonical` edits `x`, `nz`, `f` bits of a satisfying witness and sees
  the pin's linear constraint fail.
* **Product**: `m_a m_b = sum_j 2^j u_j` as one row-free quadratic on `UB = 2 (F + 1)` hint bits of `u` (the bits are what the
  shifter windows read); no zero flag.
* **Alignment** (`_align`; `AlignProduct`: `X = floor(u 2^(PS - d))`, `d = E - e_i`, `X = 0` for `d >= PB`): radix `2^RB`,
  `RB = UB / 2` (8 / 4).  Fine: the one-hot `r` over `R in [0, RB)` picks the `ND = 3` digits of `Y = u 2^R` as windows of `u`'s
  bits (`_pick`, one hint per digit).  Coarse: the one-hot `c` over `{-1, 0, 1, 2, dead}` picks `X = floor(Y / 2^(RB c))` -- affine
  in the digits -- as one hint (`XL`/`XH` limbs at `2^LIMB` for the wide Hopper sum), so `L = PS - d = R - RB c`; `dead`: `d = PB +
  (RB - 1 - R) + RB K` with `K` in `kb` hint bits (the fine one-hot is reused as the residue of the dead range); `(c = -1, R)` pairs
  with `R + RB > PS` are forbidden by row-free `sel_c sel_R = 0`.  One exponent constraint per product, `u (E_eff - e_i - d(c, R,
  K)) = 0`: a nonzero product's exponent satisfies `E_eff >= e_i` (live: `d in [0, PB)`; dead: `d >= PB`) -- the group maximum's
  lower bound is a theorem of the one-hots -- and a zero product is unconstrained (its exponent does not enter the maximum, as in
  v1).  `X`'s interval is learned per option (`ctx.learn`), which keeps the wide sum's linear identities inside `(-p, p)`.
* **Sign**: `Xs = (1 - 2 (s_a xor s_b)) X` as a hint under the two quadratics above (no sign row; §1).
* **Group maximum**: `E` a hint; `E >= e_i` for nonzero products and `E >= e_acc` from the accumulator's window lookup
  (`tsel` over `min(E - e_acc, W)`, `range_key=False`); `E` equals a candidate by the one-hot `which` over {accumulator, products}
  (`_pick` with target `E`) whose chosen product is nonzero: `C = pick(which, [1, X_1, .., X_k])` inverted (a live product at `d = 0`
  has `X = u 2^PS != 0`).  FP8: `hi = [E >= 31]` (hint bit; `31 = ep_hi + PB` is where every product is dead), `pe = hi (E - 31)`
  (one product), `(30 - E) + 2 pe + hi in [0, 2^9)` (one 9-bit range: `hi = 0 -> E <= 30`, `hi = 1 -> E >= 31`), `E_eff = E - pe`.
* **Sum, normalisation, flags, packing, epilogue**: v2's (`pubsel` helpers): `(1 - 2 s_acc) q_acc + sum_i Xs_i = (1 - 2 sgn) v`
  in two limbs with a carry for the wide unit, `v` in bits, `nsel` picks the normalised significand from `v`'s windows, RN-even
  picked from the sum's bits.

Soundness argument per constraint is in the module comment and inline; the audit (`LigeroCtx._linear`) accepts every linear
identity inside `(-p, p)` (the first bf16-ampere-v3 compile failed it -- the digit picks' hull intervals were too loose for the
wide sum -- fixed by learning `X`'s per-option bound).  Constraint density: `_pick` and the digit windows make the quadratics
denser (max 35-59 nonzeros per constraint; totals within +-15 % of v1's), which is what the arithmetic test pays for.

## 3. How a hash gadget attaches (lane hash-relation)

The operand words are already witness wires: `a_words[i] = sum_j 2^j bit_j` (BF16, 16 bits) and the E4M3 wires likewise; the
pin rows are the only place the statement's words touch the unit (`compile_v3_unit`: 32 / 22 pin rows and as many linear
constraints).  A Poseidon2 sponge over BabyBear attaches by taking the *same affine expressions* as its rate inputs -- one BF16
word per element, or the pin packing `a_words[lo] + 2^8 a_words[lo+1] + 2^16 a_words[lo+2]` (24 bits < p) for E4M3 -- and
dropping the pin rows: 32 (22) elements per unit, so with rate 8 four (three) permutations, with rate 16 two (two).  Nothing else
in the unit changes.  Two things move: (i) the E4M3 NaN exclusion, which the verifier's word check does in the pin variant, must
be a relation constraint (one inverse per word of `(14 - x) + 8 (7 - f) + 64 (1 - nz)`, zero exactly at `t = 15, f = 7`: +64 rows for
the FP8 units); (ii) the words' statement digest becomes the sponge's output, one field element per unit (or per VU if the sponge
runs across the chain -- the `a_words` wires of every unit are available, so a VU-wide absorption is the same construction with
the state carried through the chain link like `c`).  Cost, honestly: a Poseidon2 permutation (width 16, x^7, 8 full + 13 partial
rounds) under row-free quadratics needs the S-box intermediates `x^2, x^4, x^6` as hint rows and the next state as hints (the
final `x^7 = x^6 x` is a quadratic against the affine pre-image of the next state), about 64 rows per full round and 4 per partial
round: ~570 rows per permutation, ~1700-2300 per unit -- more than the unit itself.  The pin variant's 1519 / 1673 rows are what a
private-operand relation *has to* spend besides the hash; the hash is the larger half, and the way to amortise it is a wider rate
or a VU-level sponge, not the unit.  Note that the Ligero commitment already binds the operand rows (they are committed columns):
the sponge is needed only when the operands must be bound to an *external* commitment (a weights digest).

## 4. Evidence

* **Rust pin** (`backends/ligero-verify`): `privsel::PrivSel { op, k, words_per_pin }` with `unit_pins` (the packed runs of both
  operands after `Operand::decode`'s finiteness check), `pin_index` (`a[i]` / `a[lo:hi]` -> position; anything else refused),
  `Decode::PrivSel`, `verify.rs public_pins_privsel` (every column, pad columns included; K from the relation); the four systems
  pinned by `sys_id` / table digest (78daae8) bf16-hopper-v3 `a8174ff5 / a2015d49`, bf16-ampere-v3 `e3ff1f9f / 87ec0bfd`,
  fp8-hopper-v3 `c961ba70 / 72cc7c90`, fp8-ada-v3 `c5668bcf / 36680ea2` (the pre-fix 9a42e39 values were `2279f2ac / 0caba95a`,
  `f962956b / 35fe22ff`, `bc6f8780 / a21f5b46`, `adaea5d9 / c62f82e0`; laptop compilations, torch-free, twice, byte-identical; fixtures `fixtures/systems/<name>.system.bin`; `system-digest` names
  each); `cargo test --release` green (relation 21, verify 7, tests/relations.rs 10 incl. `privsel_unit_pins_match_public_vectors_v3`
  on hand-computed words: BF16 pins = the words, E4M3 runs `[0:3] .. [30:32]`, non-finite words refused, wrong names refused).
  End to end on CPU dumps of every relation (`bench-vu --zk --batch 768 --total-vus 8 --dump-dir`, Fiat-Shamir and interactive):
  `ligero-verify batch` ACCEPT, `system pinned (<name>)`, python agreement 1/1, union bound 2^-128.01; seven statement
  tamperings per relation (an operand bit, a sign bit, a claimed-word bit, two words swapped, `a` and `b` swapped, a pad column's
  word, a NaN word) all rejected -- the transcript binds the statement digest ("column challenge mismatch"), the NaN with the
  decode's reason (`/tmp/relmin-priv/rust_tamper_all.json`).
* **Local tests** (`pytest backends/direct/ligero/privsel/relation_test.py`, CPU, on 78daae8: **36 passed in 62 s**,
  `/tmp/relmin-priv/pytest_privsel_78daae8.log`): census bounds incl. `2 x v3 <= v1` for every relation; differential v1 vs v3
  at 3000 units (every claimed bit flipped, +-1 ulp, the other pipeline's word: both accept exactly the model's word); the
  exact-zero sums of §4b accepted; off-domain operands refused by both decodes; committed words bound and canonical; torch hints
  == Python-integer reference; two VUs proved and verified on CPU (interactive; FS + ZK); the chain negative battery rejected.
  The pod's `pytest backends/direct/ligero` (the whole backend, in the gate run) is the wider check.
* **GPU gates on the pre-fix systems 9a42e39** (`run.py --relation <v3> gate-vu --device cuda --vus 2048 --batch 4096`, every
  negative family of the generic runner): run **r20260923-092224-1e88**, 09:23-10:19Z, **all four PASSED**: bf16-hopper-v3 49
  honest sub-batches / 87 negatives (60 row mutations, 18 claimed-word bits, 4 off-domain, accumulator, operand, link, c_0) / 0
  failures (24.7 min), fp8-ada-v3 25 / 92 / 0 (8.4 min), fp8-hopper-v3 25 / 92 / 0 (8.2 min), bf16-ampere-v3 49 / 87 / 0
  (14.8 min).  The run's `pytest backends/direct/ligero` then failed at exactly the gap of §4b (`test_differential_v1_v3[fp8-ada-v3]`,
  the 3000-unit default: honest unit 874 rejected, y = +0; 70 passed, 1 skipped before it).  The 2048 x 32 honest units of a
  gate never contain an exact-zero sum: the gate cannot see this class, the differential can.
* **GPU gates on the final systems 78daae8**: run **r20260923-110015-4eb2** (`gates-v3-fixed`, 11:00Z-), same command, same
  negative families: **all four PASSED** -- fp8-hopper-v3 25 honest sub-batches / 92 negatives / 0 failures (8.3 min), fp8-ada-v3
  25 / 92 / 0 (8.4 min), bf16-ampere-v3 49 / 87 / 0 (14.5 min), bf16-hopper-v3 49 / 87 / 0 (14.3 min: 10 minutes faster than on
  9a42e39 because nothing else ran on the pod's cores this time); then **`pytest backends/direct/ligero` on the pod: 156 passed,
  1 skipped in 1138 s** (11:46-12:05Z; v1, v2 and v3 tests, the v3 differential at 3000 units and the exact-zero regression
  included).  The run's files (`gate_<rel>.json`, stdout, the verify verdicts) are `art:56d667e01674cef2705a919be18fdc6e63925a0cc55c96eb0d6c6c3aac044f47`.
* **Differential at 1e5 units per relation** (`RELMIN_DIFF_N=100000`, `privsel/relation_test.py::test_differential_v1_v3`, CPU
  torch, seeds 3000 + lo per 4096-unit batch, every claimed bit flipped, +-1 ulp, the other pipeline's word, v1 and v3 both
  checked against the model): on 9a42e39 (the pod, `/workspace/diff-1e5/`, logs in `/tmp/relmin-priv/pod-diff-1e5/`)
  **fp8-hopper-v3 FAILED** at 25.4 min -- the honest unit 92536 (batch 90112, index 2424) rejected; §4b -- and **fp8-ada-v3
  FAILED** at 34 min on another honest unit (index 87 of a later batch, the same class: it passes on 78daae8); the two BF16 runs
  were stopped (SIGTERM) to give the gate the cores.  **On 78daae8 all four PASSED** (the laptop, 4 processes x 3 threads,
  10:33-10:43Z; `/tmp/relmin-priv/diff-1e5-local/diff_<rel>.log`): bf16-hopper-v3 1 passed in 533 s, bf16-ampere-v3 555 s,
  fp8-hopper-v3 449 s, fp8-ada-v3 485 s -- 1e5 honest units accepted by v1 and v3, every wrong claim (>= 10 x 1e5 negatives per
  relation: 32 / 25 bit flips, +-1 ulp, the other pipeline's word) rejected by both.  Pod note: the first pod launch used 24 torch
  threads per process on a pod whose cgroup quota is 13.6 cores (`nproc` says 24 / 128) and thrashed the gate to 15 % of a core;
  relaunched at 2 threads; the laptop is the faster differential machine anyway (12 s per 4096-unit batch at 4 threads).
* **Every bench dump of §5 verified by the Rust verifier built from 78daae8 on the pod** (`/tmp/relmin-priv/verify.sh` over ssh
  alongside the gates, 11:00-11:02Z; `ligero-verify batch --target-bits 128 --threads 8` on every rep directory, `serialize
  verify-batch --device cuda --target-bits 128` on rep1): 33 Rust verdicts (11 runs x 3 reps) all `batch_accepted`, 49 (fp8-ada at
  l=4096) / 13 (fp8-ada at l=16384) / 25 (the BF16 and fp8-hopper units at l=16384) sub-batches accepted and 0 rejected per rep,
  every dump `system pinned (<name>)` against the fixtures' digests (the four v3 names 18 times, the v1 names 15 times, one
  binary, sha256 941f680e...), python agreement n/n (0 disagree) on every rep; 11 Python verdicts `accepted`
  (`/tmp/relmin-priv/verify_pod.json`, the pod's `/workspace/verify-v3/verify.stdout`).
* **D13** in `backends/ligero-verify/DISCREPANCIES.md` (incl. the zero-sum rule and the v2 finding).

### 4b. The exact-zero sum: a completeness gap in v2's normalisation, inherited by v3, fixed in v3 (78daae8)

The unit: `c = 0`, 32 E4M3 products of which two are live and cancel exactly, the rest dead (truncated to zero at the group
maximum); the model's word is `+0`; v1 accepts.  v3 (and v2) normalise by a one-hot over the shift `t in [t_lo, t_hi] =
[-nb, -k_lo]` with `Mn = window_t(v)`, `Mn = hid 2^(nb-1) + fo`, and the subnormal rule `hid = 0 -> t = tc(E) = acc_e_min - E +
width - nb` (the clamped grid; `t >= tc` always by the 9-bit range on `t - tc`).  With `v = 0` every window is 0, `hid = 0`,
and the rule demands `t = tc`; when `E - width > acc_e_min` (a large group maximum, the sum zero) `tc < t_lo` and no selectable
`t` satisfies it: the honest witness fails `g0.norm.clamp`.  Frequency: about 1 in 1e5 random E4M3 units (one hit in the seeded
1e5 for fp8-hopper-v3, one in the first 3000 for fp8-ada-v3 on the pod's pytest -- unit 874, `c` nonzero and tiny), none in
1e5 for the BF16 units (a 16-bit mantissa product cancels less often).  **`fp8-hopper-v2` in `main` (02c3321) rejects unit
92536 at the same constraint** (`/tmp/relmin-priv/unit_92536.json`; checked with `pubsel`'s own `_witness_accepts`): the v2
relations carry the gap and relmin-lookup's 1e5 differentials did not draw such a unit.  The fix (v3 only; `pubsel` is not this
lane's): `(1 - hid - nsel[t_lo]) (t - tc) = 0`.  At `t = t_lo = -nb` the window is `2^nb x popcount(v)` (every bit of `v` is
above the window and `_norm_window` carries each at weight `2^nb`), so `Mn < 2^nb` forces `v = 0`, hence `Mn = 0`, `hid = 0`,
`z = 1` and the zero output whatever `t`; `hid = 1` at `t_lo` is unsatisfiable, so the factor is never -1; when `t != t_lo`
the rule is the old one.  The honest prover already picks `t = max(t_lo, tc)`.  No new row, no new hint; the systems' bytes
changed by one quadratic (digests re-pinned, fixtures regenerated, `cargo test --release` green: 21 + 7 + 10).  Regression:
`test_exact_zero_sum_accepted` (every operand exponent field, `a w, a w` against `b w, b -w`, plus unit 92536 for the E4M3
units: v3 and v1 accept, torch hints == the integer reference).  For v2 the same one-line change applies to
`pubsel/relation.py` line 385 (rows unchanged, digests change).

## 5. v1 vs v3 on the same RTX 4090 (vy-relmin-priv), 4096 VUs, 3 reps, dumps, interactive

Tree 78daae8 (main 02c3321's prover, encoder and protocol; only the relation differs between the paired rows).  `run.py
--relation <r> bench-vu --mode interactive --batch <l> --total-vus 4096 --reps 3 --dump-dir <run>/proofs` with `--zk` (int-ZK) or
without; fp8-ada with `--tool bench_vu_fp8 --scratch triton` (the FP8 v1 witness tool, its scratch), the other v1 / v3 pairs
the Python model.  Medians of 3 reps of `prover_seconds`; the split columns are the median rep's `split.*`; every run's own
`verify` PASSED (`valid` = the run's Fiat-Shamir + interactive self-check); all 11 runs' dumps Rust + Python batch-verified
below.  `overhead` = `overhead.vs_native_peak` from `result.json`.

| run | relation | zk | l | prover median (reps) | verifier | witness (hints) | encode+commit | arithmetic | serialise | openings | proof | overhead | peak dev |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260923-104236-e44f | fp8-ada v1 | int-ZK | 4096 | **0.686** (0.822, 0.686, 0.681) | 1.098 | 0.251 (0.203) | 0.108 | 0.226 | 0.052 | 0.050 | 181.5 MB | 1.80e7 | 978 MB |
| r20260923-104128-ff0f | fp8-ada-v3 | int-ZK | 4096 | **0.593** (0.682, 0.593, 0.586) | 1.054 | 0.231 (0.203) | 0.065 | 0.213 | 0.047 | 0.046 | 103.4 MB | 1.56e7 | 688 MB |
| r20260923-104744-0a5e | fp8-ada v1 | non-ZK | 4096 | 0.607 (0.690, 0.604, 0.607) | 1.131 | 0.254 (0.205) | 0.078 | 0.178 | 0.053 | 0.051 | 169.9 MB | 1.59e7 | 789 MB |
| r20260923-104635-c38b | fp8-ada-v3 | non-ZK | 4096 | 0.520 (0.577, 0.520, 0.511) | 1.042 | 0.229 (0.200) | 0.046 | 0.166 | 0.046 | 0.044 | 93.7 MB | 1.36e7 | 688 MB |
| r20260923-104558-8dff | fp8-ada v1 | int-ZK | 16384 | **2.148** (2.188, 2.148, 2.140) | 0.411 | 0.077 (0.059) | 1.833 | 0.185 | 0.016 | 0.016 | 66.1 MB | 5.64e7 | 8703 MB |
| r20260923-104346-b283 | fp8-ada-v3 | int-ZK | 16384 | **1.147** (1.166, 1.141, 1.147) | 0.449 | 0.075 (0.064) | 0.859 | 0.183 | 0.017 | 0.016 | 46.0 MB | 3.01e7 | 4668 MB |
| r20260923-105042-4785 | bf16-hopper v1 | int-ZK | 16384 | **3.552** (3.643, 3.552, 3.539) | 0.715 | 0.035 (0.018) | 3.070 | 0.343 | 0.030 | 0.029 | 118.0 MB | 2.79e8 | 7669 MB |
| r20260923-104831-4423 | bf16-hopper-v3 | int-ZK | 16384 | **1.873** (1.899, 1.864, 1.873) | 0.693 | 0.118 (0.104) | 1.369 | 0.338 | 0.029 | 0.028 | 83.1 MB | 1.47e8 | 3939 MB |
| r20260923-105437-9cc2 | fp8-hopper v1 | int-ZK | 16384 | **1.949** (1.986, 1.928, 1.949) | 0.392 | 0.058 (0.042) | 1.645 | 0.185 | 0.021 | 0.021 | 62.3 MB | 3.06e8 | 7896 MB |
| r20260923-105223-2643 | fp8-hopper-v3 | int-ZK | 16384 | **1.062** (1.079, 1.062, 1.060) | 0.403 | 0.070 (0.061) | 0.788 | 0.179 | 0.015 | 0.014 | 44.7 MB | 1.67e8 | 4251 MB |
| r20260923-105756-8502 | bf16-ampere-v3 | int-ZK | 16384 | 2.023 (2.030, 2.002, 2.023) | 0.740 | 0.128 (0.112) | 1.477 | 0.348 | 0.031 | 0.030 | 85.3 MB | 5.02e7 | 4178 MB |

Reading: at l=4096 (the FP8 v1 witness tool for both) v3 is 1.16x faster int-ZK (0.686 -> 0.593 s) and 1.17x non-ZK, the
proof 1.75x smaller (181.5 -> 103.4 MB), the device peak 978 -> 688 MB; the encode+commit halves (0.108 -> 0.065), the rest is
the sub-batch-independent cost that relmin-lookup §5 measured (hints 0.203 s in both: the `bench_vu_fp8` tool + the torch hint
generator dominate at this l).  At l=16384 the rows are the whole story: v3 is **1.87x** (fp8-ada), **1.90x** (bf16-hopper),
**1.84x** (fp8-hopper) faster than v1 with proofs 1.4x smaller and half the device memory, because the encode+commit phase is
proportional to the rows here (see the caveat).  The 2x rows buy 1.8-1.9x time where the encoder dominates and 1.16x where the
fixed costs do.

**Caveat, not this lane's** -- the encoder on this tree at l=16384: main 02c3321 carries enc-hopper 429f8ea (H100 tuning of the
encoder + protocol Blake3 commit) and hp2-host a1f199d / 0244332 (CUDA-graphed NTT chains, stage generator), which relmin-lookup's
tree c7d32e0 (off 0055c41) did not.  On the same GPU model and the same v1 fp8-ada relation at l=16384 int-ZK, relmin-lookup
measured 0.490 s (encode+commit 0.124 s; r20260923-080045-7450) and this tree measures 2.148 s (encode+commit 1.833 s, device peak
8.7 GB): the merged encoder is 15x slower at n = 65536 columns on the RTX 4090 (and 1.3x faster at l=4096: 0.142 -> 0.108 s).
The v1/v3 ratios at l=16384 above are ratios of that slow path; the absolute times are not the tree's best.  A bisect of
`encode_simt.py` / `protocol.py` between 0055c41 and 02c3321 on a 4090 at l=16384 is the first thing to run; the slow path
looks like the H100-sized configuration (shared memory / graph capture / a 2x larger `coefs` working set: 8.7 GB peak where
c7d32e0 fit l=16384 comfortably) falling back on the 24 GB part.

## 6. Pod accounting

vy-relmin-priv `1zrj2w7usqb8bj` (RTX 4090 reference part, 24 vCPU, 100 GB, $0.74/h), created ~08:25Z, registered in
machines.toml by hand (`pods create` had been backgrounded).  Runs: r20260923-082957-4559 / -083207-1503 (bootstrap: venv312
torch 2.6.0+cu124 + cupy + blake3 + pytest, rustup + ligero-verify, the instance caches), -084444-35c2 (gates on 34e1b1e,
cancelled manually after bf16-hopper-v3 passed: `cancel_result` recorded), -092019-dfcc (mis-launch without `--source`, exited
at once), -092224-1e88 (gates + pytest on 9a42e39, 57 min), the 11 benches of §5 (10:41-11:00Z, 1.5-2.5 min each, exclusive,
sequential), -110015-4eb2 (gates + pytest on 78daae8, from 11:00Z; the Rust verify pass ran beside it over ssh at nice 5).
The 1e5 differentials on 9a42e39 ran on the pod outside `research` (`/workspace/diff-1e5/`, 4 processes; the failing one is
the finding of §4b), those on 78daae8 on the laptop.  Source shipping: `research run --source .` stalled twice on the git-archive
upload (a 24 MB tar at a few kB/s; the tar process on the pod killed by hand), so the 78daae8 tree was rebuilt on the pod from
the 9a42e39 tree + the changed files (`git archive --name-only` -> `tar` over ssh; `.complete` written by hand; the tree check
`/tmp/relmin-priv/{local,pod}_hashes.txt` compares every file's sha256 against the laptop's worktree: 1603 files, one differs,
`packages/verity/tests/ml/fixtures/tc-hopper-2026-09-07/special.reduced.json.gz`, an ML test fixture on no code path of this
lane).  Budget <= 4.5 pod-hours; terminated 12:10Z after 3.75 h (~$2.80), everything pulled first (11 bench runs, the gate
run's files, the differential logs).

**Artifacts** (pulled to the laptop store 11:00-11:19Z, labelled `tree` / `row` / `note` by relmin-private, pushed to R2;
`result` artifacts, each run's `run_files` holds `proofs/` with `system.bin`, `manifest.json` and the three rep dump directories):
fp8-ada v1 int-ZK l=4096 `art:b28771e1...`, v3 `art:54c0e694...`; v1 non-ZK `art:0c41b194...`, v3 `art:06a81c63...`; v1
int-ZK l=16384 `art:79dec2cc...`, v3 `art:7c1e8905...`; bf16-hopper v1 `art:8aa21110...`, v3 `art:89184d0f...`; fp8-hopper v1
`art:be177197...`, v3 `art:dfc99152...`; bf16-ampere-v3 `art:d765f54c...` (full ids: `research data show <run>`; the runs are
in §5's table); the gate run's files `art:56d667e0...`.  Snapshot `relmin-private-v3` =
`art:2920f7a0c313439fed869316c86e432ecb1672cd6693122c6bdcabfe4d13de57` (23 members).  Pushed to R2 and verified by 12:27Z (three `push
--pending --verify head` passes, the last reporting nothing pending; the snapshot and the gate artifact `remote present
verified=2026-09-23T12:26Z`).

## 7. What remains, ranked (hypotheses with the test that decides each)

1. **v2's exact-zero-sum gap (§4b) in `main`**: apply the one-quadratic change to `pubsel/relation.py` (line 385), re-pin the
   four v2 digests + fixtures, add unit 92536 to `pubsel`'s tests.  Decides itself: `pubsel`'s `_witness_accepts` on
   `/tmp/relmin-priv/unit_92536.json` flips from reject to accept; a 1e6-unit E4M3 differential (about 10 such units expected)
   passes.  Owner: relmin-lookup or whoever merges v2; 30 min.
2. **The encoder at n = 65536 on the 4090 (§5 caveat)**: bisect 0055c41..02c3321 on `bench-vu --relation fp8-ada --batch
   16384` on a 4090; predicted culprit 429f8ea's H100 configuration (or a1f199d's graph capture) taking a slow / oversized path
   at this n.  Decides: encode+commit 1.83 s -> ~0.12 s at l=16384 with device peak back under 4 GB.  Owner: enc-hopper / hp2-host.
3. **Alignment rows** (26 / 17 per product: 416 of 1519 and 544 of 1673, 27-33 % of a unit): the coarse one-hot (5 rows) and
   the fine one-hot (`RB` rows) could become one one-hot over the composite shift with a two-level `_pick` whose first level
   selects a digit *window* rather than a digit, and the aligned limb pair `XL`/`XH` + `XsL`/`XsH` (4 rows on the wide units)
   could be signed before the limb split (2 rows + one carry) -- about 4-5 rows per product (70-130 / unit, 5-8 %) if the
   quadratic term count stays under the audit's bound.  Decides: census + the same gate.  Half a day.
4. **E4M3 NaN exclusion inside the relation** (+1 inverse per word, 64 rows) is what the sponge variant needs (§3): the pin
   variant has the verifier refuse NaN words, a sponge cannot.  Lane hash-relation's call; the rows are budgeted in §3.
5. **Gate cost**: the 57-minute GPU gate is the torch hint generator's Python-integer reference (`check=True`) at 24 threads on a
   13.6-core cgroup, not the systems (bench hints 0.06-0.11 s per 4096 VUs).  `OMP_NUM_THREADS` = the cgroup quota, or the
   reference only on the first sub-batch, would bring the gate under 15 minutes.  Decides: one gate run.

**Spec notes.**  (a) The brief's "at least 2x fewer rows" is met by every relation (2.03-2.17x) but the margin on fp8-hopper-v3
(1673 vs 1698 = 3396 / 2) is 25 rows; the `_signed` rewrite of de8c459 is what carried it over.  (b) The brief's pin variant
binds the operand *words*; the alternative -- pinning the decoded fields (sign, exponent, fraction as three witness wires per
word) -- would save the 8 / 16 word bits per operand (about 400 rows per BF16 unit, 1.6x more) at the price of a verifier that
decodes IEEE words itself (which `ligero-verify` already does for v2's `Operand::decode`).  Worth a decision before the sponge
variant fixes the wire layout.  (c) The differential, not the gate, found the completeness bug: the gate's honest units are
random and an exact-zero E4M3 sum is a 1e-5 event; a gate family of *constructed* honest edge units (exact cancellation, all-dead
groups, the subnormal grid's ends, the largest finite result) would catch this class in seconds.  Proposed as a generic runner
family (it applies to v1, v2 and v3 alike; `test_exact_zero_sum_accepted` is the v3-local version).
