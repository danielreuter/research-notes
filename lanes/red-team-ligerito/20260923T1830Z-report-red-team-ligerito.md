---
lane: red-team-ligerito
kind: report
created: 2026-09-23T18:30Z
status: final (19:54Z; will append if lanes land fixes before 22:30Z)
---

CHECKPOINT c41f23d (19:54Z) — F3 fix (ligerito-zk 318ec9b `EqSumcheckMask`) verified: it matches brute force on every method and the cross
block is load-bearing (`redteam_eqmask_check.py`, ce370b3). Production-shape |S| (pow2 ± ZK, 2^-128/2^-129) computed (c41f23d). `## FINAL` written.
CHECKPOINT 361a9de (19:07Z) — code-level verifier review done. Two BREAKs in the **reference** verifier `ref.py` (F10: statement not in the
transcript, so z is chosen after the coins; F11: non-canonical words + int64 overflow forge `v − 2^64 mod p` even with the statement bound).
Both demoed end to end. Rust `refpcs.rs` (0254f65 binary) accepts the F10 forgeries and rejects F11's. The production chain (pcs-fast proto `pcs.py` over
bytes + the relation's `lgto/params || stmt || vk || root` binding + union gate) is NOT affected. F12 (relation reports 2^-128 for FS/local/
cold-live modes) is a WEAKENING. Handoffs 19:05Z: verify-rs, pcs-fast, relation. Already fixed upstream: F3 (ligerito-zk 318ec9b cross block),
F5(ii) (verify-rs 0254f65 target default), F7 (318ec9b). Next: red-team the F3 fix with `redteam_libra_bivariate.py`, then `## FINAL`.
CHECKPOINT 9182132 (18:50Z) — independent recomputation done (`redteam_soundness.py`), Libra demo done (`redteam_libra_bivariate.py`).
Set B as specified (radix-3, no column padding, interactive) = fp8 2^-128.011 / bf16 2^-128.026 / fp4 2^-128.026 — reproduces
params.py to 3 decimals, proven bounds only, **0.01–0.03 bits of margin**. Two SOUNDNESS-LOSS (F1 ZK padding → 2^-119.3; F2 pow2
shapes → 2^-99.2) and one ZK BREAK (F3 Libra on the bivariate opening round) posted as handoffs at 18:50Z to ligerito-pcs-fast,
ligerito-zk, ligerito-relation, ligerito-sumcheck. Next: code-level review of ref.py / proto pcs.py `verify` (final check, index
sampling, Merkle binding), then `## FINAL`.
CHECKPOINT none (18:36Z) — started 18:22Z. Worktree `~/projects/verity-main-wt/red-team-ligerito` on `lane/red-team-ligerito` @ 760260d.

# red-team-ligerito — adversarial soundness review of the Ligerito design (parameter set B)

## FINAL

**Verdict.** The soundness math is right, and set B's literal query counts are not deployable. Every term in `params.py` is a
proven, unique-decoding bound (BCIKS20 Thm 4.1, DG24 Thm 2/3 = AER24). No term leans on the conjectured regime that the 2025
counterexamples broke (Crites–Stewart 2025/2046, BCHKS 2025/2055). `x^6 − 31` is irreducible, and the ternary digit never becomes a fold
variable. No list-decoding factor is needed. My independent recomputation reproduces set B to 3 decimals. **Set B |S| as
parameters: NO-GO.** They are sized for a radix-3 shape nothing ships, with 0.01–0.03 bits of margin, and ZK column padding costs up to 9 bits.
**Formula: GO.** Derive |S| per proof from `params.py` for the shape actually committed, at target 2^-129, with `t_pad` in the rate under ZK.

**Independent soundness, set B as specified (radix-3, no column padding, interactive coins), log2:**

~~~
relation   cells     UNION (params form)  tight     paper/Rust form   margin   bytes
fp8-ada    3*2^28    -128.011             -128.018  -128.008          0.011    622.4 KiB
bf16       3*2^29    -128.026             -128.029  -128.025          0.026    704.0 KiB
fp4        3*2^26    -128.026             -128.032  -128.023          0.026    531.7 KiB
same |S|, ZK t_pad=256:   fp8 -119.34   bf16 -127.20   fp4 -124.86            (F1)
same |S|, pow2 layout:    -99.19 for all three                                  (F2)
Fiat-Shamir, F_p^6, Q=2^64: -96.4 (PCS fold rounds); F_p^8 = F_p[x]/(x^8-11): -158.3   (F4)
~~~

**Corrected |S| (greedy min-bytes on params.py's byte model; + t_pad·24 B/level of `ybar` under ZK), recommended target 2^-129:**

~~~
shape                     fp8 (L=5)                          bf16 (L=4)                   fp4 (L=4)
pow2, no ZK  (ships now)  [314,194,194,195,196]  727.2 KiB   [314,194,194,194] 842.7 KiB  [314,193,194,195] 627.7 KiB
pow2 + ZK t_pad=256       [314,194,194,198,218]  764.7 KiB   [314,194,194,200] 869.9 KiB  [314,193,195,206] 655.8 KiB
radix-3, no ZK            [242,174,175,176,176]  626.8 KiB   [241,175,175,175] 709.0 KiB  [242,174,174,176] 535.4 KiB
radix-3 + ZK (2^-128.1)   [240,173,174,176,194]  659.2 KiB   [240,173,174,178] 731.4 KiB  [240,173,174,183] 559.6 KiB
(at 2^-128: pow2 no ZK fp8 [312,192,192,194,194] 721.8 / bf16 [311,192,193,193] 836.9 / fp4 [312,192,192,193] 623.8 KiB)
~~~

**Findings (F-number, severity, owner, status at 19:54Z):**

~~~
F1  SOUNDNESS-LOSS  ZK per-column RS padding invalidates set-B |S| (fp8 -> 2^-119.3)   pcs-fast/zk/relation  open (zk 318ec9b: union queries_for)
F2  SOUNDNESS-LOSS  set-B |S| on a pow2 shape -> 2^-99.2                              pcs-fast/relation     mitigated: relation dims_for re-derives
F3  BREAK (ZK)      Libra mask leaves the bivariate opening round's cross terms clear  zk/sumcheck/relation  FIXED zk 318ec9b, verified ce370b3; wiring pending
F4  WEAKENING       FS for the sumcheck rounds costs 2^-96.4 at Q=2^64, not 2^-114     coordinator           open (live coins or x^8-11)
F5  WEAKENING       0.01-bit margin; job splits need 2^-(128+log2 N); target enforce   relation/verify-rs    (ii) FIXED verify-rs 0254f65; (i)(iii) open
F6  WEAKENING       ZK mask geometry vs committed index order; k'_1=6 has no room      zk/relation           zk 116f8ac RowMaskLayout, not re-verified
F7  NIT             ybar bytes not in params; queries_for(-130) not a union rule       pcs-fast/zk           queries_for FIXED 318ec9b; bytes open
F8  NIT             challenge bias (2^-32) is multiplicative, not additive             pcs-fast              open (docstring)
F9  NIT             paper (4)/(15)/(17) print the rejection fraction without "1 -"     none                  documented
F10 BREAK (ref)     ref.py/refpcs.rs transcript omits (w, value, dims): z after coins  pcs-fast/verify-rs    open; Rust binary accepts the forgery
F11 BREAK (ref)     ref.py non-canonical words + int64 wrap forge v - 2^64 mod p       pcs-fast/verify-rs    open; Rust rejects; proto NIT (in-memory)
F12 WEAKENING       relation reports 2^-128 for FS / local / cold-live verify-dir      relation              open
~~~

Production chain status: proto `pcs.py` (u32 wire format, `header||z||root||v`) + relation (`lgto/params||stmt||vk||root`, union
gate ≥ 128 bits on the proof's own dims) + Rust `pcs.rs` (canonical-only): no forgery found. The two BREAKs in the reference dialect (F10, F11)
matter because ref.py is the spec that `refpcs.rs` and the `batch *.ref.json` path port. 8c: every live/committed-coin challenge is
verifier-derived. The exceptions are the modes whose coins are prover-known by construction (FS, local seed, cold-live coin files), and F12 asks the relation to stop
attaching a soundness figure to them.

Scripts (`lane/red-team-ligerito` @ c41f23d, all < 10 s, numpy only): `redteam_soundness.py`, `redteam_libra_bivariate.py`,
`redteam_ref_weakfs.py`, `redteam_ref_overflow.py`, `redteam_eqmask_check.py`. Forged fixtures: `fixtures/{weakfs,overflow}.ref.json` here.

Findings are numbered F1.., each with severity (BREAK / SOUNDNESS-LOSS / WEAKENING / NIT), a reproduction or calculation, and
the fix owner. No GPU, no torch; check scripts are small pure-python under `backends/direct/ligerito/redteam_*.py` on
`lane/red-team-ligerito` (9182132): `redteam_soundness.py` (0.08 s) and `redteam_libra_bivariate.py` (0.6 s).

## 0. What the bound rests on (sources checked)

* **Paper (eprint 2025/1187, rendered pages 5 and 14).** (4) prints `((m − n − 1)/(2m))^{|S|} + mk/|F|`, and (17) prints
  `Σ_{i<ℓ} [2k_{i−1}/|F| + (|S_i|+1)/|F| + ((m_i − 2^{k_i} − 1)/(2m_i))^{|S_i|} + m_i k_i/|F|] + 2k_{ℓ−1}/|F| + ((m_ℓ − 2^{k_ℓ} − 1)/(2m_ℓ))^{|S_ℓ|} + m_ℓ k_ℓ/|F|`.
  (18) is the general-code form with `(1 − d/(3m))`. The printed RS base is the *rejection* fraction with the "1 −" missing: read
  literally it would make one query at rate 1/4 worth 1.4 bits. The paper's own §6.4 sizing (`|S| = −λ/log((1+ρ)/2)`, 148 ↔ 2^-100) and
  (18)'s `1 − d/(3m)` confirm the intent. The field-term subscripts (`m_i k_i`, `2k_{i−1}`) are the tall `k`, where the base case (4) and
  §6.1 use the folded `k'`. That is irrelevant: ≥ 27 bits of slack either way.
* **Proximity gaps, proven.** BCIKS20/23 Thm 4.1: RS lines have proximity gaps for every `e ≤ ⌊(d−1)/2⌋` with false witness bound `ε = n`.
  Diamond–Gruen (CiC 1(4) 2024) Thm 2 lifts this to interleaved codes for `e ≤ ⌊(d−1)/2⌋`, and their Thm 3 (= AER24 2024/1399) gives the tensor
  (log-randomness) gap with false witness `ϑ·ε/q` = `k'_i·m_i/|F|` — exactly Ligerito's field term. **Every proximity term in
  params.py is unique-decoding and proven.** The 2025 negative results — Crites–Stewart ePrint 2025/2046 (correlated agreement,
  mutual CA and list-decodability "up to capacity" are false; they fail beyond 1 − H_q(ρ)), Ben-Sasson et al. ePrint 2025/2055 / ECCC
  TR25-169 (n^τ-bounded gaps false; ≥ n^{2−o(1)} exceptions needed at the Johnson radius), and Diamond–Gruen 2025 — all concern the
  regime *beyond* unique decoding (FRI/STIR/WHIR's conjectured parameters). None of them touches `e ≤ ⌊(d−1)/2⌋`. Diamond–Gruen's
  Example 1 shows BCIKS Thm 4.1's ε = n is *sharp*, and params.py uses n.
* **Per-query base.** In the far case the fold is ≥ e+1 from the code, and in the close case `G y' ≠ G X̃ r̄` differs in ≥ d − e positions. So a query
  passes w.p. ≤ `1 − (⌊(m−k)/2⌋ + 1)/m ≤ (m + k − 1)/(2m) < (1 + ρ)/2`. params.py's `(1+ρ)/2` is valid and conservative. The Rust verifier's
  `(m + k + 1)/(2m)` (the "1 −" reading of (17)) is valid and 1/(2m) looser. Set B passes under all three (§2).
* **List decoding.** Not needed. Everything is unique-decoding, so the extracted `X̃_i` is unique and batching the claims costs
  `(#claims)/|F|` with no list factor. **The design's "|S_1| up to 1.5×" risk does not materialise:** 239 stays 239 for the as-specified shape.
* **Ternary digit.** In `ref.py`, digit 0 (least significant) is the ternary one, the rows are the low digits and the k'_i columns are the high *binary*
  digits. So the ternary digit stays in the RS message (tall) dimension at every level (tall_L = 3·2^8). It is never a PCS sumcheck or
  tensor-fold variable, and it enters only the verifier's weights (Lagrange-3 factor of `w`, `(1, ω^s, ω^{2s})` in the generator tensor).
  RS proximity holds for any message length, so the tensor/multilinear argument is intact. In the relation's zero-check it is one degree-6
  round (7 coefficients), booked.
* **Field.** `x^6 − 31` is irreducible over BabyBear: Rabin's test, and the binomial criterion (31 is a non-square and a non-cube; 6 | p − 1 = 2^27·3·5).
  `x^8 − 11` is irreducible (Rabin; the degree-8 FS fix is available, log2|F| = 247.3). `x^7 − a` is never irreducible, since 7 ∤ p − 1 so every a is a 7th power.

## 1. Findings

### F1 — SOUNDNESS-LOSS: ZK per-column RS padding invalidates set B's query counts (fp8 → 2^-119.3)

ligerito-zk (`zk.py`, `T_PAD = 256`) pads every committed column at every level with 256 uniform message coefficients (Ligero-8b
style) and sends `ybar_i = μ^T r̄_i`. This makes level i an RS code of rate `(tall_i + 256)/n_i`. The design and the coordinator's
brief call set B "2^-128 union, ZK counted" and say "ZK adds no soundness term". That assumed masks in pad cells and did not account for
padding the code. With set B's |S| and t_pad = 256 (`redteam_soundness.py` variant b):

~~~
fp8  union 2^-119.34  (L5 768+256 of 4096: rate 3/16 -> 1/4, (5/8)^176)
bf16 union 2^-127.20  (L4 3072+256 of 16384)
fp4  union 2^-124.86  (L4 1536+256 of 8192)
~~~

Corrected |S| (same n_i, greedy min-bytes; bytes = params.py + `ybar` = t_pad·24 B per level, which params does not count):
fp8 `[240,173,174,176,194]` 2^-128.10, 659.2 KiB; bf16 `[240,173,174,178]` 2^-128.20, 731.4 KiB; fp4 `[240,173,174,183]` 2^-128.10,
559.6 KiB. The cheaper alternative lengthens the tiny levels' codes: fp8 rates (1,2,2,3,3) `[239,172,174,158,163]` 651.3 KiB; bf16 (1,2,2,3)
`[239,173,173,154]` 721.4 KiB; fp4 (1,2,2,3) `[239,173,174,155]` 554.5 KiB. **Owner: ligerito-pcs-fast** (add `t_pad` to `LigeritoParams`:
rate and bytes), **ligerito-zk** (its `queries_for(-130)` per level is not a union rule at L = 5, since 5·2^-130 = 2^-127.68; it lands at 2^-128.04
only by ceil rounding), **ligerito-relation** (derive |S| per proof). Handoffs posted 18:50Z.

### F2 — SOUNDNESS-LOSS: set B's |S| on a power-of-two shape → 2^-99.2

Set B is radix-3 (level-1 effective rate 3/8, later 3/16). Nothing downstream implements radix-3: proto/pcs-fast `Dims`, ligerito-sumcheck's
layout (N = 2^30, 16 sub-batches, 13 real) and the Rust verifier's `Params` are all pow2 (only `ref.py` has radix-3). The same
`--rates 1 2 2 2 2 --queries 239 173 174 174 176` on n = 30 has exact rates 1/2 and 1/4, so **union 2^-99.19** (L1 (3/4)^239 = 2^-99.2), for all three
relations. A correct pow2 run needs fp8 `[312,192,192,194,194]` 721.8 KiB, bf16 `[311,192,193,193]` 836.9 KiB, fp4 `[312,192,192,193]`
623.8 KiB. params' own `our_params(..., radix3=False)` agrees: 722.0 / 836.8 / 623.7 KiB. params.py is right; the trap is copying numbers.
**Owner: ligerito-pcs-fast / ligerito-relation**. **Coordinator:** the "implement set B (radix-3) as the default" instruction to pcs-fast has
no consumer — the zero-check, the Rust verifier and proto are pow2. Either commission radix-3 in all three, or re-issue set B as the pow2 line.

### F3 — BREAK (zero knowledge, on integration): the Libra mask does not blind the bivariate opening round

`zk.SumcheckMask` uses `g = a_0 + Σ_i g_i(x_i)`, and `round_values` handles one variable per round. ligerito-sumcheck's zero-check opens with
a round binding (X1, X2) (`round0[3][3]`, 4d68195). By zk.py's own docstring the zero-check's public factors vanish on the mask rows, so
that round is blinded by `ρ·g` alone. `Σ_rest g(X1, X2, rest) = const + 2^{n−2}(g_1(X1) + g_2(X2))` has no `X1^a X2^b` (a, b ≥ 1) term.
`redteam_libra_bivariate.py` (toy zero-check, n = 6, degree 3) shows that all 9 cross coefficients are identical across fresh `(ρ, g)` draws and equal to
the unmasked witness-only ones, and that a second witness for the same statement changes them. That is a distinguisher with advantage ≈ 1. A 3×3 cross block
for the packed pair restores uniformity. Second, the wire forms are incompatible: under ZK every zero-check round must send the full degree-3
`s(X) = eq·q + ρ·G_t`, because Gruen's `(q(0), q(1), q(∞))` cannot express the `ρ·G_t` part. **Owner: ligerito-zk** (cross block, +9 ext
coefficients) **or ligerito-sumcheck** (univariate opening round under ZK), and **ligerito-relation** (glue). Soundness is unaffected.

### F4 — WEAKENING: the design's Fiat-Shamir option (c) costs 2^-96, not 2^-114

Design §3.4(c)/§3.5: "FS for the sumcheck rounds only … `Q·66·3/|F| = 2^-114` at Q = 2^64". The FS'd set includes the PCS
partial-sumcheck rounds (only the "10 query/batching/τ coins" stay live), and **those challenges are the tensor-fold randomness `r̄_i`**. Their
round-by-round error is the interleaved-line gap `m_i/|F|` (BCIKS ε = n, DG Thm 2), not `2/|F|`. So:

~~~
Q = 2^64: relation sumchecks only (RBR, max 6/|F|)      2^-118.9   (design's union form 2^-113.8)
          + PCS partial-sumcheck rounds (Q m_1/|F|)      2^-96.4    [F_p^8 = F_p[x]/(x^8-11): 2^-158.3]
Q = 2^60: 2^-122.9 / 2^-100.4                                        [F_p^8: 2^-162.3]
~~~

No option at degree 6 reaches 2^-128 once any fold round is FS'd. Degree 8 (`x^8 − 11`, verified irreducible) fixes both. The design's
recommendation (a), live coins, is unaffected. **Owner: coordinator** (the design lane is finished), ligerito-pcs-fast for the doc/params.

### F5 — WEAKENING: zero margin, job splits, and a verifier that does not enforce the target

Set B's margin is 0.011 / 0.026 / 0.026 bits. (i) A 4096-VU job is one proof today (`vus = 4096`). If any device splits it into N proofs,
PROTOCOL.md's batch rule (lane b-batch-bound) needs 2^-(128 + log2 N) per proof: N = 2 → fp8 `[242,174,175,176,176]` (626.8 KiB/proof);
N = 4 → `[243,176,176,177,178]`. Ligerito proofs carry no `n_proofs` binding. (ii) The Rust verifier recomputes (17) from the proof's own params
(good: never prover-supplied), but single-proof `verify` only reports `soundness_log2` and does not reject. The target is enforced only in
`batch --target-bits`, which is optional. A proof with |S| = 1 verifies. Pin |S| per relation or make `--target-bits 128` the default.
(iii) Recommend sizing to 2^-129 so a ±1 in the radius convention or a rounding in a sibling lane cannot tip it.
**Owner: ligerito-relation, ligerito-verify-rs.**

### F6 — WEAKENING: ZK mask geometry disagrees with the committed index order; set B's k'_1 = 6 has no room

`ZkParams` assumes layout rows are the HIGH bits, so a round-1 column is whole layout rows. ligerito-sumcheck and proto commit `f[i + R·c] = z[i, c]`
(rows LOW), so a round-1 column is a block of layout columns. Rows-high at k'_1 = 6: 9 mask columns = 9 × 64 = 576 free rows,
against fp8-ada 319 (sumcheck layout 3777/4096), fp8-hopper ≈ 500, and fp4 ≈ 265 of 2048 (needs 288). Rows-low needs free column blocks at both ends,
which set B's radix-3 layout (cols = units × 4096 exactly) does not have. `check_layout` raises, so this is infeasibility, not a silent leak. F9's
size condition itself holds at set B with a large margin (9·3·2^22 mask cells vs ≈ 2·10^3 extension functionals). **Owner: ligerito-zk + ligerito-relation**
(fix the orientation; k'_1 ≥ 7 or a padded layout).

### F7 — NIT: ZK byte model and query sizing

`ybar_i` (t_pad ext per committed level: 30 KiB at L = 5, 24 KiB at L = 4) is not in params' `proof_bytes`. zk.py's `queries_for` default
(−130 per level) should be `−128 − log2 L`. **Owner: ligerito-pcs-fast / ligerito-zk.**

### F8 — NIT: challenge-sampling bias is multiplicative, say so

Extension challenges are `u63 mod p` per coordinate (bias ≤ p/2^63 = 2^-32). Every soundness event is "the challenge lands in a set of size ≤ X", so
the bias multiplies each term by at most `(1 + 2^-32)^6`. It must not be booked as an additive statistical distance, which would be 2^-29 and would kill 2^-128.
Indices are `u64 mod 2^k`, which is exact. **Owner: ligerito-pcs-fast** (transcript docstring).

### F9 — NIT: paper typos

(4)/(15)/(17) print the rejection fraction without "1 −", and the field-term subscripts are `k` for `k'`. All readings are valid and none changes set B
(§0). This closes the design's "someone with a clean copy should confirm (17)". **Owner: none** (documentation).

### F10 — BREAK (reference verifier): `ref.py` does not bind the statement, so z is chosen after the coins

`ref.verify`'s transcript starts at `absorb(root_1)`. `w`, `value` and `dims` are never absorbed. `redteam_ref_weakfs.py` (361a9de) runs level-1
sumcheck messages that sum to a random FALSE value. After the challenges `r` it solves `b(r)·<ra(z), v_1> = final claim`
for the last column coordinate of z (one linear equation), which makes the level-1 claim true of the honest fold. Everything after that is honest.
`ref.verify` accepts at L = 1 and at L = 2 radix-3. The Rust `refpcs.rs` mirrors the transcript: `ligerito-verify ref-fixtures` (0254f65 release
binary) **accepts** both (`fixtures/weakfs.ref.json` in this notes dir). `dims` comes from the proof with no floor (|S| = 1 verifies).
Proto `pcs.py` (`header, z, root, v`), Rust `pcs.rs`, and the relation (`lgto/params || stmt || vk || root`) bind correctly.
**Owner: ligerito-pcs-fast** (ref.py: `ligerito-ref/v2` statement prefix) **+ ligerito-verify-rs** (refpcs.rs, fixtures as must-reject).

### F11 — BREAK (reference verifier): non-canonical words + int64 overflow forge a bound claim

`ref.verify` never range-checks sumcheck coefficients, `final` or ext opened rows. The transcript hashes them mod p, but `escale(c0, 2)`
wraps int64 for `c0 + t·p ∈ [2^62, 2^63 − p)`. The verifier then tests `g(0) + g(1) − K = claim` with `K = 2^64 mod p = 1172168163`, while the update
`eadd(c0, ·)` stays exact. `redteam_ref_overflow.py`: an honest proof of `v` with one lifted word verifies as `v − K·e_0` with `(w, value)` absorbed
before coin 1, through the JSON wire format, at L = 1, 2 (radix-3), 3. Rust rejects (non-canonical). verify-rs had already noticed "`x + p`
verifies like `x`" and filed it as malleability (`/noncanon` expect_ok in ref.py's column). It is a forgery. Proto `claims.verify_column_rounds`
has the same `ext.add(g0, g1)`: an in-memory `Proof` with `g0 + g1 ≥ 2^63` passes for `claim − K` with an identical running claim and identical
transcript bytes. But proto's byte format is u32 and cannot reach the wrap, so it is **NIT** there. **Owner: ligerito-pcs-fast** (reject words ∉ [0, p) in
ref.py `verify`, range-check `g` and `final_y` in proto `_verify`), **ligerito-verify-rs** (flip the `/noncanon` expectation).

### F12 — WEAKENING: the relation verifier reports 2^-128 in modes where it does not hold

(a) `Prover.batch` defaults to `coins_kind="fiat-shamir"` (the gate runs local + FS), and `soundness()` books the interactive union. Under FS
the PCS fold rounds cost `Q·m_1/|F|` (F4): 2^-96.4 at Q = 2^64. (b) `verify-dir` rebuilds `local` coins from the manifest's seed and `live` coins
from `coins_file` in the dump. Both are prover-side artefacts, so a cold accept carries no soundness (8c: the challenges are derivable from prover data),
yet `soundness_log2` is still set. Also: `soundness()`/`dims_for` hard-code `zk=False` and `tall1 = 2^{k_1}`, which F1 needs changed once `t_pad` is
integrated (ZK is a stub there today). F2 does NOT apply to the relation: `dims_for` re-derives |S| for its pow2 N. **Owner: ligerito-relation.**

## 2. Independent numbers (log2, `redteam_soundness.py`)

~~~
                  per-level proximity                               non-prox max   UNION tight / params-form / paper-Rust / params.py
fp8  3*2^28  L1 -129.20 L2 -130.11 L3 -130.86 L4 -130.86 L5 -132.36   -157.9         -128.018 / -128.011 / -128.008 / -128.011   622.4 KiB
bf16 3*2^29  L1 -129.20 L2 -130.11 L3 -130.11 L4 -131.61              -157.6         -128.029 / -128.026 / -128.025 / -128.026   704.0 KiB
fp4  3*2^26  L1 -129.20 L2 -130.11 L3 -130.11 L4 -131.61              -159.9         -128.032 / -128.026 / -128.023 / -128.026   531.7 KiB
relation side (zero-check SZ + sumchecks + constraint batching + claims + Libra + coin hiding): 2^-173.4 / -173.6 / -174.6
zero-check per round: opening (bivariate) 6/|F| = 2^-182.9, univariate 3/|F| = 2^-183.9, ternary round 6/|F|; total ≈ 93/|F| = 2^-178.9
~~~

## 3. Verified OK (explicitly)

* Every params.py term: per-level query `((1+ρ)/2)^{|S|}` with ρ = tall/n (the radix-3 effective rate), tensor `k'n/|F|`, partial sumcheck
  `2k'/|F|`, batching `(|S_{i−1}|+1)/|F|`, and final level = the L-th proximity term plus an exact `⟨w, y_L⟩` check. Correct, proven, conservative.
* 8c: `LiveCoins` and `zk.CommittedCoins`/`challenge_from` derive every challenge from the verifier's coin (+ stmt, C, slot as domain
  separation), with absorbs ignored. τ comes after root_1, Libra ρ after G, α after root_{i+1}, S_i after root_{i+1}. `ref.py`/proto `FSCoins`
  absorb prover messages *by design* (FS reference). They must never be selectable in the interactive ZK mode: bind the mode into the statement as
  PROTOCOL.md 8c does.
* Degree-3 zero-check with Gruen: per-round error includes the eq zeros (`q ≠ q*` but `eq(τ, r) = 0`), so it is 3/|F| univariate and 6/|F| bivariate.

## Log

* 18:22Z start; briefs, design note, red-team-leaf note, zk + sumcheck notes, PROTOCOL.md 8c + batch rule, params/ref/transcript/ext read.
* 18:30Z paper PDF fetched and converted; (17) and the §6.3 induction read.
* 18:40Z pages 5 and 14 rendered: (4)/(17) typo confirmed. DG24 (CiC 1(4)), Crites–Stewart 2025/2046 and BCHKS 2025/2055 read for regimes.
* 18:45Z proto `Dims` (pow2, |S| unchecked), zk.py (T_PAD, SumcheckMask univariate), sumcheck report (bivariate opening, Gruen `q`),
  Rust `params.rs` (recomputes (17), target only in batch) read.
* 18:47Z 9182132: `redteam_soundness.py` + `redteam_libra_bivariate.py`; handoffs posted 18:50Z (pcs-fast, zk, relation, sumcheck).
* 18:52Z a19fb42: `redteam_ref_weakfs.py` (F10), `redteam_ref_overflow.py` (F11). 19:00Z pcs-fast d60b538 `_verify`/`claims`/`from_bytes`,
  relation 0cac5ae `verify`/`soundness`/`verify-dir`, verify-rs 0254f65 `refpcs.rs` read. 19:01Z 361a9de `--dump`; the Rust binary accepts the F10
  pair and rejects the F11 trio. 19:05Z handoffs: verify-rs, pcs-fast, relation.
* 19:10Z ligerito-zk 318ec9b read; ce370b3 `redteam_eqmask_check.py` (F3 fix verified). 19:53Z c41f23d variants (g)/(h). 19:54Z `## FINAL`.
