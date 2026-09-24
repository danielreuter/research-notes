---
lane: ajtai-design
kind: report
created: 2026-09-23T16:30Z
status: done
---

CHECKPOINT none (16:50Z) — PROVISIONAL parameter set posted (unstructured `h = A·s`, n = 64, β = 1, SHAKE-256 seed). Superseded by the
17:10Z checkpoint below after reading ajtai-leaf's §1: the per-column identical constraint system forces the Ring-SIS form.

CHECKPOINT none (17:10Z) — **PROVISIONAL parameter set for `ajtai-leaf` (revised, Ring-SIS form, agrees with ajtai-leaf §1 except for n):**
`h = Σ_j X^(steps−1−j) · B·s_j` in `R_p = F_p[X]/(X^n+1)`, `p = 2^31 − 2^27 + 1`, `s_j` = the 256 committed operand **bits** of column `j`
(β = 1; nibbles/bytes are worse everywhere, §2.5), `B` = 256 seeded ring elements (SHAKE-256, §1.3). **`n = 64` for the FP8 and FP4 relations
(48 steps ≤ 64), `n = 128` for bf16-hopper (96 steps ≤ 128); `n` must be a power of two and ≥ `steps` (hard requirement, §6.1).** Not `n = 256`
(6n+1 = 1537 rows/unit ≈ Poseidon2's 1737 — the whole point is lost) and not `n = 96` (`X^96+1` is reducible over Z, §7). Digest per operand =
`n` BabyBear words = **256 B (n = 64) / 512 B (n = 128)**, `<u4` LE. Security at n = 64, β = 1 (Core-SVP classical / quantum bits): calibrated
attack model M1 **285 / 259**, ℓ∞ model M2 357 / 324, generalised birthday 289, proof-norm rule M0 114 / 104 (§2.3 explains why M0 is not the
number to read); at n = 128: M1 563 / 511, M0 245 / 223. Rows/unit: 704 private-operand bit rows (every private-operand leaf pays these) +
6n + 1 = **385 (n = 64) / 769 (n = 128)** = 10.3 % / 20.6 % of fp8-ada's 3724 leaf-only; **1089 = 29.2 %** all-in (Poseidon2: 1737 / 2441 =
46.6 % / 65.5 %). Unsalted in v1; the leak is quantified in §3 and is worse than Poseidon2's. Full note below.

# Ajtai (Ring-SIS) operand-commitment leaf over BabyBear — design note

Lane `ajtai-design` (design only, no pod). Brief: `coordinator/20260923T1630Z-brief-leaf-campaign.md` §3.3. Companion code lane: `ajtai-leaf`
(`leaf/ajtai.py`, its §1 is the gadget this note parametrises). Reference implementation of every estimate in this note: `/tmp/ajtai/ajtai_params.py`
(also proposed for `backends/direct/ligero/leaf/ajtai_params.py`, §8); every number below is reproducible from it in ~45 s.

**Bottom line.** Build it, as `ajtai-n64` (FP8/FP4) and `ajtai-n128` (bf16). It cuts the leaf's own in-circuit cost from 1737 to 385 rows/unit
(4.5×) with a 285-bit classical / 259-bit quantum collision-resistance estimate under the estimator that reproduces the published SWIFFT
cryptanalysis, at the price of a 8–16× larger digest (256–512 B per operand vs 32 B), a 6.9× larger chain test, and a leaf that is **not**
hiding without ~2.2 kbit of salt. It does not remove the 704 private-operand bit rows: all-in the hashed fp8-ada relation goes from +65.5 % to
+29.2 %; only the tile/LogUp restructuring (§4.4, lane share-logup) gets to single digits.

## 0. Setting and what is committed

* Field `F_p`, `p = 2^31 − 2^27 + 1 = 15·2^27 + 1 = 2013265921` (`log2 p = 30.907`). `2^27 | p − 1`, so `X^n + 1` splits completely over `F_p` for
  every power of two `n ≤ 2^26` (NTT-friendly; the same situation as SWIFFT's `Z_257[X]/(X^64+1)`).
* Ligero (`PROTOCOL.md`): one constraint system, applied at every column (unit) of a VU; rows are committed vectors of length `l` (one entry per
  unit); `Linear` constraints (`Σ coef·W + c = pub` or `= 0`) are checked by the linear test, `Quadratic` by the product test, and carried state by
  the chain test on linked rows (`sys.chain[...]`, random post-commitment coefficients, `chain_coefs` materialises one `(D, l)` tensor per link
  term). Rows cost NTTs; the row count per unit is the cost metric.
* Operand commitment today (`hashchain.compose`, hash-relation report §2): step 1 turns the public operand pins into **private operand bit rows**
  `hash.a[i].b<j>`, `hash.b[i].b<j>` — 704 rows/unit for fp8 (2 operands × 32 E4M3 bytes × 11 rows: 8 bits + decode), 2 × 256 bits are the
  operand bits per unit; every column of a VU covers 32 words of each operand row; a VU is 48 columns (FP8, K = 1536) or 96 (bf16-hopper).
  These bit rows are what the leaf hashes (`s_j ∈ {0,1}^256` per operand per column). Poseidon2 adds 1720 rows (two sponges) + 17 digest pins.
* Uniform system ⇒ the leaf gadget is the same `Linear`/`Quadratic` set at every column with carried state. This is what rules out the naive
  `acc += A_blk·s_j` (same `A_blk` at every column ⇒ `h = A_blk·Σ_j s_j` ⇒ swapping columns collides; ajtai-leaf §1) and forces a public linear
  state transition `acc_out = M·acc_in + B·s_j`.

## 1. Hash definition (item 1)

### 1.1 Definition

Let `R_p = F_p[X]/(X^n + 1)`, `n` a power of two, `w = 256` bits per column per operand, `steps ≤ n` columns per VU. For one operand of one VU
with bit columns `s_0, …, s_{steps−1} ∈ {0,1}^w`:

~~~
h = Σ_{j<steps} X^(steps−1−j) · (Σ_{i<w} b_i · s_{j,i})   ∈ R_p          (B = (b_0, …, b_{w−1}) ∈ R_p^w public, seeded)
  = Σ_{i<w} b_i(X) · g_i(X),      g_i(X) = Σ_j X^(steps−1−j) s_{j,i}     (0/1 coefficients, degree < steps ≤ n)
~~~

computed by the per-column recurrence `acc_0 = 0`, `acc_{j+1} = X·acc_j + B·s_j`, `h = acc_steps` (multiplication by `X` in `R_p` is the
negacyclic shift `(a_0..a_{n−1}) ↦ (−a_{n−1}, a_0, …, a_{n−2})`). Digest = the `n` coefficients of `h`, each in `[0, p)`.

This is Ring-SIS in the SWIFFT shape (Lyubashevsky–Micciancio–Peikert–Rosen, FSE 2008, doi:10.1007/978-3-540-71039-4_4,
https://www.alonrosen.net/PAPERS/lattices/swifft.pdf: `h = Σ a_i x_i` over `Z_q[X]/(X^n+1)` with binary `x_i`), with `(n, m_ring, q) = (64, 256, p)`
instead of `(64, 16, 257)`, and the inputs `x_i = g_i` restricted to degree `< steps`. Unrolled, `h = A·s mod p` for the `n × (w·steps)` matrix
`A = [X^(steps−1)B | … | X·B | B]` (each block the `n × w` matrix whose column `i` is the coefficient vector of `X^k b_i`), i.e. an SIS matrix with
`m = w·steps` columns: `m = 12288` (FP8, 48 steps), `24576` (bf16, 96 steps), `≈ 6912` (FP4: 1536 × 4 + 96 × 8 scale bits, if the FP4 relation
packs them into 48 columns of 144 bits — `w` changes, nothing else does).

Both operands of a unit (x row and W column) are hashed by the same recurrence with the same `B` into two separate digests (the tree framing
separates roles, as today). A joint digest of both would halve the rows (§4.1) but is incompatible with per-operand leaves.

### 1.2 Why bits (β = 1) and not nibbles/bytes

Committing the operand as `w'` words in `[0, β]` with `β = 15` (nibbles) or `255` (bytes) shrinks `m` by 4–8× but the collision vector's ℓ∞ bound
grows to `β`, and lattice attacks only see the ratio `β / q^(n/d)`. §2.5: at `β = 255` even `n = 256` (1 KB digest, 1537+ rows) is at 126
classical bits under M1; at `β = 15`, `n = 128` gives 145. Bits are also what the relation already commits (the 704 bit rows exist for the
decode anyway), so the leaf gets them for free. **β = 1.**

### 1.3 Deriving `B` from a seed

`b_i` (coefficient `k`) := the `k`-th accepted value of the stream `SHAKE-256(b"verity/ajtai-babybear/B/v1" || LE32(i))`, read as LE32 words
`u`, `v = u & 0x7FFF_FFFF`, **accept iff `v < p`** (acceptance 15/16; no modular reduction — `u mod p` would bias by up to 2^−4 per word, harmless
for security but avoidable). Properties: (a) prefix-consistent in `n` (`b_i` for `n = 64` is the first 64 coefficients of `b_i` for `n = 128`) and
in `w` (more bits per column = more `b_i`), so `ajtai-n64` and `ajtai-n128` are the same family and any `(n, w)` pair is fixed by the seed string
alone; (b) no role, format or relation in the seed — role/format separation is the tree's job (leaf prefix / separate roots), exactly as for
Poseidon2 today; (c) nothing-up-my-sleeve: the seed is a fixed ASCII string; a trapdoored `B` (one with a known short kernel vector) would have to
be planted by whoever writes the code, and is detectable only by regenerating from the seed — the verifier MUST regenerate `B` from the seed, never
accept it from the statement or the prover. `derive_ring_element` / `derive_B` in `ajtai_params.py` are the reference (ajtai-leaf's
`verity/ajtai-leaf/v1|p|n|m|f` seed is equivalent in every respect but the prefix-consistency; pick one, the string is a v1 constant).

Digest encoding: `n` × LE u32 (`<u4` lanes), `4n` bytes: **256 B (n = 64), 512 B (n = 128)**; the tree/leaf framing hashes `leaf_bytes` natively.
A 31-bit packing (248 / 496 B) is not worth the code.

## 2. Parameters and security (item 2)

### 2.1 Collision ⇒ short kernel vector

Two distinct inputs `s ≠ s'` (same `steps`) with `h(s) = h(s')` give `γ = s − s' ∈ {−1, 0, 1}^m \ {0}` with `A·γ = 0 mod p`, i.e. `γ_i(X) = g_i − g_i'`
ternary of degree `< steps ≤ n` with `Σ_i b_i γ_i = 0` in `R_p`. Because `deg γ_i < n`, `γ_i ≠ 0` as a polynomial iff `γ_i ≠ 0` in `R_p`
(coefficient representation is unique below degree `n`) — so `γ ≠ 0`. Norms: `‖γ‖_∞ ≤ 1`, `‖γ‖_2 ≤ √m` (`= 111` for FP8, `157` for bf16), and
`‖γ‖_2 ≤ √d` on any `d` coordinates. This is an `SIS_{n, m, p, β}` solution (ℓ∞ β = 1; ℓ2 β = √m) for the structured (negacyclic) matrix `A`;
as in Dilithium/LaBRADOR/SWIFFT we assume the negacyclic structure does not help the attacker (no known attack exploits it for power-of-two
`X^n+1`, prime `p`, and the standard remark that lattice reduction ignores the algebraic structure — SWIFFT §5, "Lattice attacks").

### 2.2 The estimators (formulae)

All are Core-SVP: cost of BKZ with block size `b` is `2^(c·b)` with `c = 0.292` classical (Becker–Ducas–Gama–Laarhoven 2016), `0.265` quantum
(Laarhoven 2015), `0.2075` "plausible" floor (Dilithium spec §6.1 / Kyber spec). Root-Hermite factor of BKZ-`b`
(Chen 2013; `model_BKZ.delta_BKZ` in pq-crystals/security-estimates):

~~~
δ_b = ( (π b)^(1/b) · b / (2 π e) )^(1 / (2(b − 1)))         δ_341 = 1.00444, δ_438 = 1.00374, δ_484 = 1.00348, δ_976 = 1.00208
~~~

The attacker works in the kernel lattice `Λ = {x ∈ Z^m : A x = 0 mod p}` restricted to `d ≤ m` coordinates (zeroing the others; Micciancio–Regev
2009 §3.5: "the problem cannot become harder by increasing `m`"), a lattice of dimension `d` and volume `p^n` (for `d > n`). BKZ-`b` finds a vector
of ℓ2 norm `≈ δ_b^d · p^(n/d)`, minimised at `d* = √(n log2 p / log2 δ_b)` where it equals `2^(2 √(n · log2 p · log2 δ_b))`.

* **M0 — proof-norm rule.** Attack succeeds at `b` iff `2 √(n log2 p log2 δ_b) ≤ log2 √m`. This is exactly `sis_secure(rank, norm)` in the
  lattice-dogs LaBRADOR/Greyhound code (`labrador.c`, `LOGDELTA = log2 1.00444`, i.e. BKZ-≈340): the rule LaBRADOR uses for its *proof* norm
  bound. It asks for a vector of ℓ2 norm `√m` in the full dimension, which is what the reduction needs, but a random such vector is not a ternary
  vector — no attack corresponds to it. Reported as the conservative floor.
* **M1 — attack-dimension ℓ2 rule (primary).** Attack succeeds at `b` iff `∃ d ≤ m: δ_b^d p^(n/d) ≤ √d` — the attacker needs, in dimension `d`, a
  vector no longer than the longest ternary vector supported there, and is given the benefit of the doubt that any such vector is ternary.
  Reported as the number to read: it reproduces the published cryptanalysis of SWIFFT (§2.4).
* **M2 — Dilithium ℓ∞ model.** `SIS_linf_cost` of pq-crystals/security-estimates (`MSIS_security.py`, Ducas et al., Dilithium spec App. C.3),
  ported verbatim: randomised BKZ-`b` basis shape, the `d` coordinates of the found vector are Gaussian with `σ = ℓ/√d`, success probability
  `erf(1/(σ√2))^d`, repeated `R = 2^(−log2 P − 0.2075 b)` times (each sieve call yields `2^(0.2075 b)` vectors): `cost = 2^(c b) · R`. The most
  attack-faithful of the three for an ℓ∞ target, but it assumes the Gaussian-coordinate heuristic; reported as the upper estimate.
* **Wagner — generalised birthday** (Wagner 2002; the SWIFFT paper's own estimate, §5 "Generalized Birthday Attack"): split the `m` columns into
  `2^k` blocks, build `2^k` lists of `3^(m/2^k)` ternary combinations, merge pairwise zeroing `n log2 p / (k+1)` bits per level:
  `cost ≈ 2^(k + n log2 p / (k+1))` subject to `(m / 2^k) log2 3 ≥ n log2 p / (k+1)`. Not a lattice attack; depends on `m` (more columns help the
  attacker slightly) and dominates at small `n`.

### 2.3 Results, β = 1

Per-`n` numbers (cls / qnt / pls = classical / quantum / plausible Core-SVP bits). M1 and M2 do **not** depend on `m` (the attack lives in
`d* < m` coordinates), so one line covers FP8, bf16 and FP4; M0 and Wagner do (FP8 `m = 12288`, bf16 `24576`, FP4 `6912`).

| n | digest | M1 b (d*) | **M1 cls / qnt / pls** | M2 b | M2 cls / qnt / pls | Wagner FP8 / bf16 / FP4 | M0 FP8 cls / qnt | M0 bf16 cls / qnt | M0 FP4 cls / qnt |
|---|---|---|---|---|---|---|---|---|---|
| 32 | 128 B | 485 (501) | **142 / 129 / 101** | 643 | 188 / 171 / 133 | 131 / 118 / 147 | 38 / 34 | 29 / 26 | 47 / 43 |
| 48 | 192 B | 732 (692) | **214 / 194 / 152** | 936 | 274 / 248 / 194 | 218 / 192 / 252 | 74 / 67 | 59 / 54 | 90 / 82 |
| **64** | **256 B** | 976 (872) | **285 / 259 / 203** | 1220 | 357 / 324 / 253 | 289 / 254 / 335 | **114 / 104** | 93 / 84 | 137 / 124 |
| 96 | 384 B | 1455 (1219) | **426 / 386 / 302** | 1774 | 519 / 471 / 368 | 500 / 430 / 597 | 202 / 183 | 166 / 150 | 239 / 217 |
| **128** | **512 B** | 1925 (1555) | **563 / 511 / 399** | 2312 | 676 / 613 / 480 | 795 / 571 / 992 | 297 / 269 | **245 / 223** | 350 / 317 |

Reading: the smallest `n` with 128/128 under M1 is `n = 32` (142/129), with **no margin** — and Wagner is at 131/118 there too. `n = 64` is the
smallest power of two above it and has a ≥ 2× block-size margin under every attack model (BKZ-976 vs BKZ-438 for 128 classical bits); `n = 128`
is required anyway for bf16 (§6.1) and additionally satisfies the proof-norm rule M0 at 128 quantum bits for every `m` here.
What `n = 64` does **not** satisfy is M0 (114 cls / 104 qnt for FP8): a reviewer applying the LaBRADOR-implementation rule literally will say
"< 128". §2.4 is the reason I recommend reading M1 instead; if the coordinator wants M0 satisfied, the answer is `n = 128` everywhere (769 rows,
20.6 %), not `n = 96` (§7).

### 2.4 Cross-checks against published parameters

* **SWIFFT (n = 64, m = 1024, q = 257, β = 1).** The paper's own estimate: generalised birthday with 16 lists of 3^64 ≈ 2^102, **2^106**, and
  "the dimension 1024 of our lattice is too large for the current state-of-the-art reduction algorithms". Our estimators: Wagner `k = 3`, 131 bits
  (the paper's `k = 4` run uses lists 2 bits short of the requirement, "conservative in the algorithm's favour"; my rule requires full lists, hence
  131 vs 106 — Wagner numbers in this note are therefore optimistic by up to ~25 bits at small `n`, irrelevant at `n ≥ 64`); **M1: BKZ-242 in
  `d* = 294`, 71 classical bits; M2: 102 bits.**
  Buchmann–Lindner, "Secure Parameters for SWIFFT" (INDOCRYPT 2009, https://eprint.iacr.org/2008/493): lattice reduction finds SWIFFT
  pseudo-collisions (ℓ2 norm ≤ √1024) in sublattices of dimension 205–251, costing about a **68-bit** symmetric cipher (Lenstra–Verheul heuristic);
  they recommend `(n, m_ring, p) = (96, 18, 389)` for **127 bits**. M1 on their recommended set: BKZ-402 in `d* = 444`, **118 classical Core-SVP
  bits**. So M1 lands within 3–9 bits of the only published cryptanalysis of a binary Ring-SIS hash at this shape, in both instances, and M2 is
  ~30 bits above it. This is why M1 is "the number to read" and why the recommended margin is stated in M1 terms.
* **LaBRADOR (Beullens–Seiler 2023, https://eprint.iacr.org/2022/1341) / Greyhound implementation (lattice-dogs).** `q ≈ 2^32` (LOGQ 32 in
  `data.h`), ring `Z_q[X]/(X^64+1)`, Ajtai commitments with the rule `log2 ‖·‖_2 < min(log2 q, 2√(log2 q · log2 δ · n))`, `δ = 1.00444` — this is
  M0 (`δ = 1.00444` ⇔ BKZ-341 ⇒ their "128-bit" convention is Core-SVP-classical ≈ 100). Their parameters sit exactly where M0 says; ours sit
  1.15× further in block size under the same rule at `n = 64` (M0 b = 391, FP8) and 2.5–3× at `n = 128` (839 bf16 / 1014 FP8) — and the ternary
  target, which M0 ignores, is worth another 2.5× (M1 b = 976 at n = 64).
* **Dilithium (Ducas et al., 2021 spec, App. C.3).** MSIS with ℓ∞ bound; parameter selection uses `SIS_linf_cost` = M2 exactly, and reports
  Core-SVP with `c = 0.292 / 0.265 / 0.2075`. Our M2 numbers are computed with their code path (ported), with `q = p` and `B = 1`.
* **Micciancio–Regev 2009** ("Lattice-based cryptography", §3.5 and the "Hermite factor" discussion): the `2^(2√(n log q log δ))` formula and the
  `d* = √(n log q / log δ)` optimum used by M0/M1; Gama–Nguyen 2008 for `δ ≈ 1.01` = "reachable", `1.005` = "hard".

Uncertainty, honestly: (i) Core-SVP is a lower bound on BKZ cost (it ignores the ~polynomial number of SVP calls and memory), so all bit counts
are conservative in the defender's favour by 10–30 bits; (ii) M1's "any vector of that ℓ2 norm is ternary" is conservative in the attacker's
favour by 0–30 bits (M2 − M1); (iii) the calibration against Buchmann–Lindner is on `q ∈ {257, 389}`, `n ∈ {64, 96}` — extrapolating to `q ≈ 2^31`
is where the formula is least tested (their instances have `n log q ≈ 512–830`, ours `1978–3956`; larger `n log q` makes the kernel lattice
sparser and the estimate *more* standard, not less); (iv) structured-lattice speedups for power-of-two negacyclic SIS are unknown at present but
are the standing assumption behind every module-lattice standard. **Margin recommended: ≥ 2× in BKZ block size under M1 for 128 classical bits
(i.e. M1 ≥ 256 cls), which `n = 64` meets (976 vs 438) and `n = 32` does not (485).**

### 2.5 Nibbles and bytes (for the record)

FP8 row, `m = 3072` nibbles (β = 15) / `1536` bytes (β = 255), M1 classical bits: β = 15: `n = 64` → 60, `128` → 145, `192` → 233; β = 255:
`n = 128` → 49, `256` → 126, `320` → 167 (M0 is lower still). Wagner does not depend on β here (lists are built from the values). Bits win by a
factor of 2–5 in `n` for the same security; §1.2.

## 3. Hiding variant (item 3)

### 3.1 What leaks without salt

`h = A·s` is a public deterministic **linear** function of the operand bits. With the digest public (it is a tree leaf):

1. **Equality** of two committed operand rows (same digest) — Poseidon2 leaks this too.
2. **Differences.** For two committed rows `s, s'` with digests `h, h'`: `h − h' = A(s − s')`, an SIS instance whose *solution* is the sparse
   ternary difference. If the rows differ in `t` positions, the difference is recoverable by meet-in-the-middle/ISD in `≈ 2^(t/2)`-ish work (for
   `t ≲ 60`, minutes) and by lattice reduction when `t log2 3 ≲ n log2 p` minus a margin — i.e. whenever the two rows are close (fine-tuning
   deltas, quantised near-duplicates), the attacker learns *exactly where and how* they differ. Poseidon2 leaks nothing of the kind.
3. **Low-entropy rows.** The digest is `n log2 p ≈ 1978` (n = 64) / `3956` (n = 128) bits of linear information about `m = 12288` bits. When the
   row's conditional entropy given public structure is below that (sparse/zero-heavy quantised weights, rows known up to a few hundred bits,
   repeated patterns), the row is determined by the digest and recoverable by the same knapsack/lattice machinery (generic preimage search on a
   full-entropy row is `2^(n(log2 p − 1))` — SWIFFT's inversion argument — and is irrelevant; structure is the threat).

So an unsalted Ajtai leaf is a *binding-only* commitment. If the reason the hashed relation makes operands private is ZK w.r.t. operand values,
Ajtai unsalted is not acceptable for that use; if it is only to commit (operands are public elsewhere, as in the bare relation), it is fine.

### 3.2 The hiding variant

`h = A·s + A_r·r`, `r ∈ {0,1}^(m_r)` fresh uniform per operand row, `A_r` = further seeded ring elements (same stream, indices `w..w+m_r/steps`),
`r` spread over the columns like `s` (`m_r/steps` extra bits per column, each an extra committed bit row + one `Quadratic` `r(r−1) = 0`).
**Statistical hiding by the leftover hash lemma**: `Δ((A_r, A_r r), (A_r, uniform)) ≤ 2^−λ` needs `m_r ≥ n log2 p + 2λ`:

| n | `m_r` (λ = 128) | extra bit rows per FP8 column (48) | per bf16 column (96) |
|---|---|---|---|
| 64 | 2235 bits | 47 | — |
| 128 | 4213 bits | — | 44 |

i.e. +47 rows (+47 quadratics) per unit at `n = 64`: leaf cost 385 → 432 (11.6 % of 3724). Binding is unchanged: a collision gives
`[A | A_r]·(s − s', r − r') = 0` with a ternary vector, the same SIS with `m + m_r` columns (M1/M2 unchanged; M0/Wagner move by < 1 bit).
Computational hiding with fewer random bits (e.g. `m_r = 256`, relying on a decisional binary-knapsack assumption) is folklore, not a standard
assumption; I do not recommend it. **Recommendation:** ship `ajtai-n64` unsalted as v1 (cost measurement, binding-only); make `salt_bits` a leaf
parameter with default `0` and document in the relation string (`+ajtai-n64-r2235`) so a hiding deployment is a parameter, not a redesign.
The witness generator must draw `r` from a CSPRNG per row and never reuse it across rows (reuse turns the hiding back into §3.1 item 2).

## 4. In-circuit design and cost (item 4)

### 4.1 The gadget (as ajtai-leaf §1, per unit, per operand)

* Inputs: the operand bit rows already committed by `hashchain.compose` step 1 (`hash.a[i].b<j>` / `hash.b[i].b<j>`), 256 per operand; no
  re-decomposition.
* State: `n` linked hint rows `acc_in[0..n)` (chain start = 0, no IV) and `n` hint rows `acc_out[0..n)` with the `Linear` constraint

  ~~~
  acc_out[x] − acc_in[x−1] − Σ_{i<256} B[x][i]·s_i = 0        (x ≥ 1;  for x = 0:  acc_out[0] + acc_in[n−1] − Σ_i B[0][i]·s_i = 0)
  ~~~

  where `B[x][i]` is coefficient `x` of `b_i`. This is a field identity by construction (values `mod p`), so append it directly to `sys.linear`
  (as the sponge's quadratics are) — `ctx.eq`'s integer audit would refuse a 258-term sum with 31-bit coefficients. 258 terms/row × 2n rows.
* Chain: `sys.chain["acc"] += acc_in[j+1] = acc_out[j]` (n links per operand); the chain test checks them with random post-commitment
  coefficients; Schwartz–Zippel degree is unchanged from Poseidon2's usage.
* Output: `n` digest pins `hash.d[...]` (`ctx.pin(_, 0, p)`, public per-column vectors — `Linear.pub` — zero except at the VU's end column),
  tied by `is_end · (acc_out[x] − d[x]) = 0` (Poseidon2's structure, `is_end` is the existing end-of-VU indicator row).
* Chain start: `PROTOCOL.md` ("cross-column constraints": `c_in = 0` at every chain start and pad) — the chain test itself forces every linked
  `_in` row to 0 at a chain start, which is why Poseidon2 stores `cap − IV`. So `acc_in[0..n) = 0` at the first column is enforced for free
  **provided the `acc_in` rows are registered as chain-linked rows** (`sys.chain[...]`), not merely constrained by a `Linear`; §6 step 3.

Rows/unit: `2 × (n + n) + 2n pins + 1 = 6n + 1`; links `3 + 2n`.

| n | leaf rows/unit | % of 3724 | all-in with the 704 operand rows | % | Poseidon2 |
|---|---|---|---|---|---|
| 64 (FP8/FP4) | **385** | **10.3 %** | 1089 | 29.2 % | 1737 / 2441 (46.6 % / 65.5 %) |
| 128 (bf16) | **769** | **20.6 %** | 1473 | 39.6 % | same |
| 256 (ajtai-leaf provisional) | 1537 | 41.3 % | 2241 | 60.2 % | — no gain — |

Why not fewer rows: (a) folding `acc_out` into the link expression (`Y = acc_in shifted + B·s`, a 257-term expression per link) is one NTT per
involved row either way and `chain_coefs` materialises one `(D, l)` tensor per link *term* (2n × 257 terms ≈ 100 GB) — explicit `acc_out` rows
are the right call (ajtai-leaf §1); (b) making the `acc_out` rows *be* the digest pins (public partial digests at every column) saves 2n rows
but publishes ≈ 1978 bits of linear information per column about that column's 512 operand bits — total loss of operand privacy; no;
(c) a joint digest of x and W (one accumulator over 512 bits/column, 3n+1 rows) is incompatible with per-operand leaves.

Costs that are not rows: chain test `3 + 2n` links vs 19 today (n = 64: 131, **6.9×** the chain-test coefficient encodes and NTTs per
sub-batch; the Rust verifier's `chain` does one NTT per involved row — this is the verifier's main growth); statement `2n` public words per
column (pins are `(len(pins), l)` — 2n × l × 4 B per VU = 24.6 KB/VU at n = 64, 48 columns, unless the serialiser sparsifies zero columns; §7).

### 4.2 Random-projection alternative (needs a post-commitment coin)

Ligero's linear test *is* a random projection of all linear constraints, so the expensive part is not checking `A·s = h` but committing the
carried state. With a coin `ω` available **after** the operand bits are committed and **before** the carried rows are, carry a scalar instead of
a vector: `t_0 = 0`, `t_{j+1} = ω·t_j + Σ_i b_i(ω)·s_{j,i}` (one hint row + one `Linear` per operand per coin), where `b_i(ω)` is the evaluation of
`b_i` at `ω ∈ F_p` **without** reducing mod `X^n + 1`. Then `t_steps = H(ω)` for `H(X) = Σ_i b_i(X) g_i(X) ∈ F_p[X]`, `deg H ≤ n + steps − 2`, and the
digest must be `H` itself (`n + steps − 1` coefficients, 444 B for FP8 at n = 64 — plain SIS binding, no ring reduction, same estimates). The
verifier evaluates the claimed `H` at `ω` and pins `t_steps = H(ω)`. Soundness per coin: Schwartz–Zippel `(n + steps − 2)/p ≈ 2^−23.9` ⇒ **6 coins
for 128 bits**: `2 operands × 6 × (1 carry + 1 out + 1 pin) + 1 ≈ 37 rows/unit (1.0 %)`, 12 + 3 links. The catch: it needs a two-round commitment
(commit bits → coin → commit carried scalars), which the current protocol does not have ("no live verifier today; local coins" — Fiat–Shamir
would do, but the prover's row commitment is single-round today). Recommend as v2 if the chain-test growth of §4.1 bites; it is a protocol change.
(Evaluating at a root `ω_k` of `X^n + 1` instead — a CRT component of the ring digest — avoids the digest-size change but checking `t` random
components out of `n` only catches a cheating prover with probability `t/n`; not useful.)

### 4.3 Tile alternative: only the 128 row units of a shared 64×64 tile carry digests

In a 64 × 64 tile of VUs every x row is shared by 64 VUs and every W column by 64. Hash each operand **once** in a dedicated "row unit" (a
48-column chain over that row's 1536 words: `n` acc_in + `n` acc_out + `n` pins + 1 = `3n + 1` rows/unit, 193 at n = 64) — 128 row units per
tile — and let the 4096 VUs prove their operand words are *the row unit's words* by the LogUp multiset argument (lane share-logup: ~1 lookup row
per operand word + the amortised table). Leaf cost per VU: `(3n+1) × 128 / 4096 = 6.0` rows (n = 64) / 12.0 (n = 128) — **0.16 % / 0.32 %** —
plus share-logup's lookup rows, which are the same for any leaf; and the 704 private-operand bit rows also move to the row units (they are the
words the table is built from). The leaf's own cost stops mattering in this regime; what remains is digest size (256 B vs 32 B per operand row —
`128 × 256 B = 32 KB` per tile vs 4 KB) and verifier chain-test width. Ajtai stays the cheapest to *prove*, Poseidon2/BLAKE3 the cheapest to
*store*; if share-logup lands, the leaf choice is decided by digest bytes and the verifier, not by rows.

### 4.4 Cost summary per parameter set (rows/unit, leaf only / all-in, % of 3724)

| set | relation | n | steps | digest | leaf rows | leaf % | all-in rows | all-in % | links |
|---|---|---|---|---|---|---|---|---|---|
| `ajtai-n64` | fp8-hopper, fp8-ada, fp4 | 64 | 48 | 256 B | 385 | 10.3 % | 1089 | 29.2 % | 131 |
| `ajtai-n64-r2235` (hiding) | same | 64 | 48 | 256 B | 432 (+47 quad) | 11.6 % | 1136 | 30.5 % | 131 |
| `ajtai-n128` | bf16-hopper (and conservative FP8) | 128 | 96 / 48 | 512 B | 769 | 20.6 % | 1473 | 39.6 % | 259 |
| §4.2 projection (v2, protocol change) | any | 64 | 48 | 444 B | ≈ 37 | 1.0 % | ≈ 741 | 19.9 % | 15 |
| §4.3 tile + LogUp | any | 64 | 48 | 256 B/row | 6 amortised | 0.16 % | share-logup's | — | — |

## 5. Statement, verifier, prover (item 5)

* **Statement.** Unchanged public statement + the digest pins: per VU, `2n` BabyBear words (`hash.d[0..2n)`, x then W, coefficient order) as
  public per-column vectors, nonzero only at the VU's end column. `leaf_bytes` = `n` × LE u32 per operand (`LeafScheme.leaf_bytes`), consumed by
  the tree framing exactly like Poseidon2's 32 B. The relation string carries the leaf and its parameters (`fp8-ada+ajtai-n64`), which fixes `B`
  through the seed; the verifier regenerates `B`.
* **Verifier.** Linear test: the 2n digest constraints are ordinary `Linear` rows — the verifier folds them with the rest (`rᵀ·A_blk` once per
  batch: the folded coefficient of each operand bit row is `Σ_x r_x B[x][i]`, `n × 256` MACs per operand per batch — negligible); the pins enter
  as public constants. Chain test: `3 + 2n` links instead of 19 (one NTT per involved row per sub-batch, `D × (2n + 3)` coefficient encodes): this is
  the real verifier growth, **6.9× the chain-test share at n = 64, 13.6× at n = 128**; ajtai-leaf measures it (Rust `verify.rs::chain`).
  Recomputing `B` from the seed: `256 × n` SHAKE words (1.5 MB of XOF at n = 128), once per process.
* **Prover, native.** Per operand row: `h = Σ_i b_i g_i` in `R_p` — `256` negacyclic products of length `n` (NTT: `256 × n log2 n ≈ 100k` mults at
  n = 64) or the unrolled `A·s`: `n × m = 64 × 12288 = 0.79 M` MACs, exact in float64 (`A < 2^31`, ≤ 24576 terms ⇒ partial sums `< 2^46 < 2^53`,
  one `mod p` at the end — the `(A_f64 @ s_f64) mod p` idiom, one matmul per committed set, ~100 M MACs per 128-row tile; microseconds on any GPU).
  In-circuit witness: the `acc` rows are the recurrence, `2n × 258` MACs per unit (n = 64: 33k), i.e. ≈ 2 % of the 1704 S-box rows' cost —
  Poseidon2's witness generation (`poseidon2_rows`) disappears. Row count is the only cost that matters for the prover and it is 385 vs 1737.

## 6. Binding argument, written for the red team (item 6)

**Claim.** If the hashed relation with leaf `ajtai-n<n>` accepts two VUs whose committed operand bit rows differ but whose digest pins agree
(or one VU whose digest equals a leaf that was computed from different bits), then one can extract `γ ∈ {−1,0,1}^m \ {0}` with `A·γ = 0 mod p`,
i.e. solve Ring-SIS_{n, 256, p, β∞=1} for the seeded `B`, which costs ≥ 2^259 quantum / 2^285 classical Core-SVP under M1 at n = 64 (§2.3).

**Proof obligations, each of which a red team should try to break:**

1. *The `s_{j,i}` are bits.* They are the private operand bit rows with `b(b−1) = 0` product constraints and the decode constraints of
   `hashchain.compose` step 1. Attack surface: any row that feeds the digest but is **not** bit-constrained (e.g. if the leaf is pointed at
   decoded word rows or hint rows). Check: every `s_i` in the `acc_out` constraint is a row with a product constraint `s(s−1) = 0` in `sys.quadratic`.
2. *The recurrence is enforced exactly.* `acc_out − shift(acc_in) − B·s = 0` is a field identity, no integer audit needed (values are residues,
   the digest is defined mod p). Attack surface: a wrong `B` (prover-supplied, not regenerated), or the coefficient orientation (`B[x][i]` vs
   `B[i][x]`) differing between the native `leaf_bytes` computation and the constraint — that gives an *availability* failure, not a break, but
   check that `verify` recomputes the digest from the seed independently of the prover's code path.
3. *Chain start is 0 and chain links hold.* The chain test binds `acc_in[j+1] = acc_out[j]` with post-commitment random coefficients; the
   soundness error is the existing chain-test bound (Poseidon2 uses the same mechanism). The chain **start** must be forced to zero at each VU's
   first column; if it is not, the prover picks `acc_in[0]` freely and every digest is reachable (total break). The chain test does this for every
   linked `_in` row (`PROTOCOL.md`, cross-column constraints: `c_in = 0` at every chain start and pad) — check that all `2n` `acc_in` rows are in
   `sys.chain`, and that none of them is a plain hint row that only a `Linear` ties to the previous column.
4. *`steps ≤ n` and `n` a power of two.* With `steps > n`, `X^n = −1` makes column `j` and column `j + n` contribute with opposite sign at the same
   coefficient: bit `(j, i) = 1` and bit `(j+n, i) = 0` collides with `(0, 1)` — `γ_i = X^a(1 + X^n) = 0` in `R_p` — a **trivial collision**,
   independent of `B`. `X^n + 1` reducible over `Z` (n not a power of two) reduces the effective `n` to the largest cyclotomic factor (SWIFFT §5.3;
   §7). Check: the leaf asserts `steps ≤ n` and `n ∈ {64, 128, 256}` at construction.
5. *Extraction.* From two accepting bit assignments with equal digests, `γ = s − s'` is ternary, nonzero (some bit differs), degree `< steps ≤ n`
   per `γ_i`, and `Σ b_i γ_i = 0` in `R_p` because both accumulations equal the same public `h`. Norms: `‖γ‖_∞ = 1`, `‖γ‖_2 ≤ √m`. No rewinding,
   no coin: the extraction is straight-line from the two witnesses.
6. *Hardness.* Ring-SIS over `F_p[X]/(X^n+1)`, `p` prime with `X^n + 1` splitting completely, `m_ring = 256` ring elements, ternary solution. Known
   attacks: BKZ on the kernel lattice (M1: BKZ-976 in dimension 872 at n = 64), the ℓ∞-aware variant (M2: BKZ-1220), generalised birthday (2^289),
   and nothing structure-specific for power-of-two negacyclic SIS. The CRT splitting does **not** give an attack: a collision must vanish in all
   `n` CRT components simultaneously (the SWIFFT setting has the same property and it is what makes it fast). Cross-relation collisions (an FP8
   digest equal to a bf16 digest under the same `B`) are still SIS solutions; the tree framing domain-separates anyway.
7. *`B` is honest.* Derived from a fixed ASCII seed by SHAKE-256 with rejection sampling (§1.3). A trapdoor requires controlling the seed string
   in the shipped code; the verifier regenerates `B` and refuses any other. Check: no code path lets the statement, the proof or a config file
   supply `B` or the seed.

What the argument does **not** give: hiding (§3.1); security of a nibble/byte-committed variant (§2.5); anything if the bit rows are shared
between the operand decode and another gadget that constrains them differently (they are the same rows; that is fine as long as both constraint
sets hold — but a gadget that *replaces* the bit constraints with range constraints would break obligation 1).

## 7. Pitfalls (item 7)

1. **`steps > n` is a free collision** (§6.4). The FP8 relations have 48 steps (`n ≥ 64`), bf16-hopper 96 (`n ≥ 128`). Any future relation with more
   columns per VU must raise `n` or restart the chain. Assert it.
2. **`n` must be a power of two.** `X^96 + 1 = (X^32 + 1)(X^64 − X^32 + 1)` over `Z`; `γ_i` in the ideal generated by `X^32 + 1` collides in a
   64-dimensional sub-instance with slightly larger coefficients. Do not offer `n = 96` as the "conservative middle".
3. **Do not read the proof-norm rule M0 as the attack cost** — and do not ignore it either: state both (n = 64: 114/104 M0 vs 285/259 M1). A
   reviewer with the LaBRADOR rule in hand will flag n = 64; the reply is §2.4 (Buchmann–Lindner). If that argument is not acceptable to the
   coordinator, `n = 128` everywhere costs 769 rows.
4. **Naive `acc += A_blk·s_j` collides** (column swap); per-column public scalars do not fix it (48-term knapsack); the state transition must be
   the negacyclic shift (ajtai-leaf §1). Anyone "simplifying" the gadget re-introduces this.
5. **`ctx.eq` integer audit.** The `acc_out` constraint is a mod-p identity with 31-bit coefficients; `ctx.eq` will refuse it. Append it to
   `sys.linear` directly (documented, like the sponge quadratics) — do not "fix" it by shrinking coefficients (that is a different, weaker `B`).
6. **`chain_coefs` per link term.** A dense link expression is 100 GB; the state must be explicit rows. Also the chain test grows to `3 + 2n`
   links — measure the Rust verifier before declaring victory; at n = 128 it is 13.6× today's chain-test share.
7. **Statement/pins.** `2n` public per-column vectors, nonzero only at end columns: `2n × l × 4 B` per VU in the statement as serialised today
   (24.6 KB/VU at n = 64) unless the serialiser sparsifies; the tree leaf itself is only `4n` B. Check `serialize.py`.
8. **Unsalted = linear leakage** (§3.1): equality, sparse differences, low-entropy rows. Do not describe the unsalted leaf as hiding. Salt is a
   parameter (`r2235` at n = 64); the salt must be fresh per row.
9. **Seed derivation.** Rejection-sample `v < p` (not `mod p`); little-endian words; mask to 31 bits first; the same stream must be used by the
   witness generator, the gadget, the native `leaf_bytes` and the verifier's regeneration — one function (`derive_B`), four call sites. Prefix
   consistency in `n` lets `ajtai-n64` and `ajtai-n128` share test vectors.
10. **Nibbles/bytes.** Committing words rather than bits is a 2–5× loss in `n` for the same security (§2.5) — never "optimise" the 704 bit rows
    away by hashing decoded words.
11. **Digest is 8–16× larger than Poseidon2's** (256/512 B vs 32 B): Merkle leaf hashing (native) and leaf storage scale accordingly; for the
    tile regime (§4.3) that is 32 KB per tile.
12. **Core-SVP is a lower bound on attack cost and BKZ simulators disagree by ±10 bits at these block sizes**; the recommended margin (≥ 2× block
    size under M1) absorbs that. Anything at `n = 32` (142/129/Wagner 131) has no margin and is rejected.

## 8. Recommendation and hand-offs

* **Build `ajtai-n64` (FP8/FP4) and `ajtai-n128` (bf16-hopper)**, β = 1, `B` from `SHAKE-256("verity/ajtai-babybear/B/v1" || LE32(i))` with rejection
  sampling, unsalted v1 with `salt_bits` as a parameter. Digest 256 B / 512 B per operand. Leaf cost 385 / 769 rows/unit = 10.3 % / 20.6 % of 3724
  (1089 / 1473 = 29.2 % / 39.6 % all-in with the 704 operand rows Poseidon2 also pays; Poseidon2: 1737 / 2441 = 46.6 % / 65.5 %).
* Security (Core-SVP cls/qnt): n = 64 — M1 285/259, M2 357/324, Wagner 289, M0 114/104; n = 128 — M1 563/511, M0 245/223. Recommended margin
  met (≥ 2× block size under the estimator that reproduces Buchmann–Lindner's SWIFFT cryptanalysis).
* Top three risks: (1) verifier chain-test growth (131/259 links vs 19) — the one cost that could erase the win; measure first (ajtai-leaf);
  (2) a reviewer applying the proof-norm rule rejects n = 64 — fall back to n = 128 (769 rows) if the §2.4 argument is not accepted;
  (3) the unsalted leaf's linear leakage being mistaken for hiding — the relation string must say `r0`.
* To `ajtai-leaf`: switch the provisional `n = 256` to `n = 64` (fp8/fp4) / `128` (bf16); assert `steps ≤ n`; confirm the chain-start-zero
  enforcement (§6.3); adopt `derive_B` (or keep your seed string — but one function, four call sites); expose `salt_bits`.
* To `share-logup`: with the tile restructuring the leaf's rows stop mattering (6 rows/VU amortised); the decision variable becomes digest bytes
  and chain width.
* Script: committed as `backends/direct/ligero/leaf/ajtai_params.py` + `ajtai_params_test.py` (10 tests, 0.6 s: field constants, δ anchors,
  seed derivation regression vector and prefix consistency, M0 < M1 ordering, the recommended set's margins, the SWIFFT / Buchmann–Lindner
  cross-checks) on `lane/ajtai-design` @ `2a61a1f` (worktree `~/projects/verity-main-wt/ajtai-design`, from e0cf2cd). No `leaf/__init__.py`
  on the branch on purpose (leaf-iface owns the package; the test imports by path, so it runs before and after the merge). `python
  ajtai_params.py` prints every table in this note (~45 s). Copy at `/tmp/ajtai/ajtai_params.py`.

## 9. Log

* 16:30Z start; brief §0–3.3, §9; PROTOCOL.md, compile.py, hashchain.py, hash-relation and lattice-scout reports read.
* 16:50Z CHECKPOINT: provisional unstructured set (n = 64). 17:10Z CHECKPOINT: revised to the Ring-SIS form after ajtai-leaf §1; n = 64 / 128.
* 17:05Z estimator cross-checked against SWIFFT (paper §5) and Buchmann–Lindner 2009 (M1 within 3–9 bits of both instances); Wagner list-size bug
  (2 vs 3 values per coordinate) found and fixed — the earlier Wagner numbers were ~40 bits too high at small n, unchanged conclusions.
* 17:07Z script + tests committed on `lane/ajtai-design` @ 2a61a1f. Note complete.

## 10. Sources

* Lyubashevsky, Micciancio, Peikert, Rosen. *SWIFFT: A Modest Proposal for FFT Hashing.* FSE 2008. §2.2 parameters `(64, 16, 257)`, §5 generalised
  birthday 2^106 and lattice-attack discussion, §5.3 reducible polynomials.
* Buchmann, Lindner. *Secure Parameters for SWIFFT.* INDOCRYPT 2009, https://eprint.iacr.org/2008/493 — pseudo-collisions in dimension 205–251,
  68-bit; recommended `(96, 18, 389)`, 127-bit.
* Micciancio, Regev. *Lattice-based Cryptography* (2009), §3.5 (SIS parameter selection, the `2^(2√(n log q log δ))` rule); Gama, Nguyen,
  *Predicting Lattice Reduction*, EUROCRYPT 2008 (δ regimes).
* Ducas, Kiltz, Lepoint, Lyubashevsky, Schwabe, Seiler, Stehlé. *CRYSTALS-Dilithium* spec v3.1 (2021), §6.1 Core-SVP, App. C.3 MSIS ℓ∞ estimate;
  code https://github.com/pq-crystals/security-estimates (`MSIS_security.py`, `model_BKZ.py`) — ported as M2.
* Becker, Ducas, Gama, Laarhoven. *New directions in nearest neighbor searching…* SODA 2016 (0.292); Laarhoven, PhD thesis 2015 (0.265).
* Chen, Y. *Réduction de réseau et sécurité concrète du chiffrement complètement homomorphe*, PhD 2013 (the `δ_b` formula).
* Beullens, Seiler. *LaBRADOR*, CRYPTO 2023, https://eprint.iacr.org/2022/1341; implementation https://github.com/lattice-dogs/labrador
  (`labrador.c: sis_secure`, `data.h: LOGQ 32, LOGDELTA`) — the M0 rule.
* Wagner. *A Generalized Birthday Problem.* CRYPTO 2002.
* Verity: `backends/direct/ligero/PROTOCOL.md`, `compile.py` (`Linear.pub`, `pin`, integer audit), `hashchain.py` (`compose`, step 1 bit rows),
  `ligero-verify/src/verify.rs::chain`; lane notes `hash-relation/20260923T0840Z`, `lattice-scout/20260922T0541Z`, `ajtai-leaf/20260923T1630Z`.
