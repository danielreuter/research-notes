---
id: r20-proof/zk-construction/20260922T0737Z-report-zk-construction
campaign: r20-proof
lane: zk-construction
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/ZK_CONSTRUCTION.md
---

# The zero-knowledge construction for Candidates A and B (zk-construction lane, 2026-09-22)

Status: **design + cost model + toy reference; nothing implemented in a prover, nothing measured.** This document
is the privacy component shared by tracks A and B: what the non-ZK protocols leak, the honest-verifier layer that
hides it, the malicious-verifier mechanism, its price per VU, its soundness terms, a reference of the masking
pieces, and the red-team checklist. It consolidates and extends `backends/gkr/PROTOCOL.md` sections 3, 5, 8 and
`backends/direct/PROTOCOL.md` sections 3, 5, 8 (both already carry the padded-transcript / blinding-row layer and
the step-0 proposal); the new parts are the leakage inventory (section 1), the FRI variant of B (2.4), the
Fiat-Shamir comparison (3.3), the priced deltas (section 4, `verity_numerical.security.zk_cost`,
`notes-asset:campaigns/r20-proof/assets/zk-construction/reports/zk_cost.json`), the accountant terms (section 5) and the reference (`security.zk_reference`, section 6).

Tags as in the protocol documents: **[source]** read in a cited document, **[derivation]** a shown calculation,
**[proposal]** this lane's choice, **[assumption]** an unfixed parameter. Labels: an implementation of section 2
alone is `COMPLETE_HVZK_BACKEND`; with section 3's step 0 implemented, written down and red-team reviewed it is
`COMPLETE_ZK_BACKEND` (`backends/AGENTS.md`).

## 0. What is private in the Verity setting

The VU is `GemmCoordinate<K>`: `x[0:K]`, `W[0:K]` (BF16 words), the chain of `K/16` accumulators from `c_0 = 0`,
and the output word `y`. The outer protocol (`verity.verification.target`, "Statement and binding") publishes only
Merkle roots `h_O`, `h_L` over packed words and the verdict; the input/output *bitstrings* themselves are never
public values -- they are authenticated against the roots. The user's direction: "the completed backend must
protect private operands and outputs against a malicious verifier."

~~~text
private   x, W (the 32 operand words per unit), every accumulator word c_s, the output word y,
          every hint (decode digits, flags, quotients, remainders, leading-bit positions), every checker wire,
          the lookup multiplicities m_T (counts of witness values), the logUp helpers
public    profile, K, B (padded batch and real count), the checker C, the tables T_1..T_5, code parameters,
          the hash family, the roots h_O, h_L, the verdict, every message SHAPE (a function of (K, B, C) only)
~~~

Consequence for every design: **nothing the numerical backend commits is public**, so every opening and every
prover message must be simulatable. The binding of the committed `x, W, y` to the outer roots is a separate
obligation (PROTOCOL A/B section 10 item 5) and is out of scope here.

## 1. What the non-ZK protocols leak

Concrete list, per candidate, for the non-ZK diagnostics that exist or are modelled tonight
(`NON_ZK_PROOF_DIAGNOSTIC` / `ARITHMETIC_DIAGNOSTIC` numbers on the ledger).

| channel | A (GKR + logUp-GKR + Ligero, `zk="none"`) | B-Ligero (`zk="none"`) | B-AIR (Plonky3 uni-stark, FRI + Keccak) |
|---|---|---|---|
| opened commitment columns | `t = 192` columns of a 45 809-row tableau: 192 x 45 809 = **8.8M witness symbols per batch** in the clear (payload `k` per row, no randomizers): operands, hints, query wires, multiplicities of 192 of 4 096 payload positions of every row | 192 x 291 186 rows = **55.9M symbols per batch**: every checker value, every helper `1/(z - w_j)` at those positions | `s = 189` FRI queries x 2 points x 2 794 columns = **1.06M LDE evaluations per batch** of the column polynomials, plus the DEEP evaluations `T_i(zeta), T_i(g zeta)` of all 2 794 columns |
| interleaved (IRS) test response `v = r^T U` | one random `F_c`-linear combination of **all** rows: a linear function of the whole witness (`n` = 16 384 symbols) | same | FRI folding layers: `19` oracles whose openings are linear functions of the trace at the query positions |
| linear / quadratic test responses `q_add`, `p_0` | polynomials of degree `< k + l - 1`, `< 2k - 1` whose coefficients are linear/quadratic functions of the witness | same; with 335M linear and 261M quadratic constraints the leaked functions are dense in the witness | the quotient polynomial (committed, opened at `s` points): a public polynomial in the trace values |
| sumcheck round polynomials `s_j(X)` | 1 569 rounds x 3 values: each `s_j(0), s_j(2), s_j(3)` is a linear function of the layer's wires (checker GKR) or of `prod (z - w_j)` products (fractional GKR); the final `v_l, v_r` are evaluations of the wire MLE at a random point | -- (helper-column mode has no sumcheck) | -- |
| logUp fractions | `q_root = prod_j (z_T - w_j(beta))` reveals the multiset's characteristic polynomial at `z_T`; the per-layer `p_k, q_k` claims reveal partial products; multiplicities `m_T` are committed but their opened positions leak counts (exact usage histogram of table rows) | helpers `h_j` in the clear at opened columns; `sum h_j` reveals the multiset's rational function at `z_T` | one-hot selectors and 2-bit limbs at the query positions (no lookup argument) |
| Merkle leaves | `H(column)` unsalted: a dictionary attack on low-entropy columns (a column of 45 809 symbols is not low-entropy, but hiding is then an assumption on `H`) | same | `H(row)` unsalted: the same |
| verifier-adaptive coins | all challenges are the verifier's: an adaptive verifier picks `Q` after seeing `com_1`, picks `r` to project onto a target row, picks `z_T` at a chosen witness value (pole probing: `q_root = 0` iff `z_T` equals some `w_j`) | same (`z_T`, `r`, `Q`) | Fiat-Shamir: no verifier coins (the hash is the verifier) |
| abort / timing | none today (fixed shapes) | none | none |

**Pole probing under a malicious verifier (new item).** Without step 0 a verifier who suspects a witness value
`w*` sets `z_T := w*(beta_T)`; then `q_root = 0` exactly when `w*` occurs among the queries. This is a
one-bit witness oracle per session even when every message is padded (the *event* `q_root = 0` is visible through
the deferred constraint being satisfiable only with `<q_root> = pad`). The public redraw rule does not stop it: it
redraws only when `z_T` lies in the *table image*, and an honest witness's queries always lie in the table, so a
malicious `z_T` in the image is redrawn -- i.e. the redraw rule closes exactly this probe **for honest witnesses**
(section 3.4). Step 0 closes it for any witness because `z_T` is fixed before `com_1`.

## 2. Honest-verifier construction (HVZK) per component

### 2.1 Ligero-committed witnesses (A, B-Ligero) **[source AHIV22 4.6, Lemma 4.15; libzk 4.2-4.3]**

Parameters (the protocols' reference set): RS `[n = 16 384, k = 4 096]` over `F_t`, payload `l = 3 840`, opened
`t = 192` (`191` minimum), `k - l = 256 >= t + 1`.

~~~text
per committed row       k - l = 256 uniformly random symbols at the randomizer positions zeta_{l+1..k} of H_k
                        -> any t <= 256 opened columns of the row are uniform (the randomizer-to-opened-symbols
                           map is a t x 256 Cauchy-type matrix of full rank: zk_reference.opened_columns_rank)
                           IF AND ONLY IF the codeword domain is disjoint from the interpolation domain H_k.
                        FIX 2026-09-22 (red team F4, lane soundness-fixes): with the codeword evaluated on H_n
                        itself (systematic RS, as the first leaf/v2 reference and the direct/encode "systematic
                        quarter" do) the opened column (n/k) j IS message symbol j -- payload in the clear for
                        every j < l hit by Q, randomizers irrelevant; the Cauchy row for that column is zero.
                        B-Ligero's committed tableau and leaf/v2 MUST encode on a coset s H_n with s notin H_n
                        (leaf/v2: s = 31, `code_text .../coset=31`; all n symbols computed, the free systematic
                        quarter is gone, encoder cost unchanged within noise: cosets-only 31.6 ms vs 32.2 ms,
                        direct/encode/README). Pin: tests/reference/test_leaf_v2.py::test_no_opened_column_is_a_payload_word.
per tableau             3 blinding rows: u_0 (uniform codeword, degree < k), u_add (uniform degree < k+l-1,
                        payload sum 0), u_q (uniform degree < 2k-1, vanishing on the payload points)
                        -> v = r^T U + u_0, q_add + u_add, p_0 + u_q are uniform on their affine spaces
per leaf                HM96 O(k)-bit commitment to the column, k = 160: leaf = (h_j, H(x_j)), |x_j| = 964 bits
                        -> statistical hiding n 2^-160 = 2^-146 per tableau (accountant `zk` term)
~~~

Exact extra material per batch (`K = 1536, B = 4096`): the payload loss `k/l - 1 = 6.67%` more rows
(A/BabyBear: 45 809 -> 48 873 rows; B/BabyBear: 291 186 -> 310 602), `+3` blinding rows per tableau, `n` HM96
strings per tableau. Per VU (A/BabyBear): +49.0 kB encoded, +49.6 kB hashed, +12.7 kB PRG output, `+6.8`
committed elements (the pads of 2.2); B/BabyBear: +311 kB encoded, +312 kB hashed, +78.6 kB PRG. Nothing else
changes: the tests, the query set and the soundness terms are those of the non-ZK Ligero (section 5).

### 2.2 GKR / sumcheck rounds (A) **[source FS24 2.3, libzk 6.5; alternative Libra 4.1 / CFS17]**

**Default [proposal, PROTOCOL A 5.2]: padded transcript.** Every transcript element `e` (each `s_j(0), s_j(2),
s_j(3)`, each `v_l, v_r`, each `p_k, q_k` claim, `q_root`) is sent as `<e> = e + pad_e` with `pad_e` a fresh `F_c`
element committed in `W_1` (as `deg(F_c/F_t)` trace coordinates) before any challenge. The verifier's checks
(`s_j(0) + s_j(1) = s_{j-1}(r_{j-1})`, the final-round identities) become linear (and, per product, one quadratic)
constraints on the pads with public coefficients (Lagrange weights at the challenges), evaluated inside the Ligero
tests. Simulation: every `<e>` is uniform; the simulator picks the `<e>` uniformly and solves for pads that satisfy
the deferred constraints (they are underdetermined: one pad per element, one constraint per round).

~~~text
pads per batch (accountant pad_elements, K=1536, B=4096)          4 674 F_c elements
  checker GKR: 6 layers x (sum of round degrees + 3)                                       712
  fractional GKR: sum_T [3 n_T(n_T-1)/2 + 4 n_T]  (n_T = 27, 23, 20, 20, 20)             3 962
committed trace coordinates                                        4 674 x d = 28 044 (BabyBear^6) = 6.8 / VU
extra rounds / depth                                               0 (the checks are already deferred to Ligero)
extra prover field ops                                             4 674 additions; PRG 28 kB per batch
~~~

**Alternative [derivation]: Libra masking (`CandidateA.sumcheck_masking = "libra"`).** Per sumcheck instance the
prover commits to `g(x) = a_0 + sum_i g_i(x_i)` (`g_i` of the round degree), publishes `H_g = 2^n a_0 + 2^{n-1}
sum_i (g_i(0) + g_i(1))`, receives `rho`, runs the sumcheck on `f + rho g` for `H + rho H_g`; the final `g(r)` is
opened from the commitment (one Ligero linear constraint). Committed elements: `(d+1) x rounds + 1` per instance
(vs `d x rounds` pads) -- 111 instances at `B = 4096` (6 checker layers + 105 fractional-GKR layers), 6 249
masking elements instead of 4 674 pads (+1 575); soundness `+1/|F_c|` per instance (`zk_sumcheck_masking_error`,
2^-178.6 at BabyBear^6, section 5); the final evaluations `v_l, v_r` must
still be padded (Libra hides them with a second masking layer inside GKR; we keep the pads). Extra depth: `rho`
travels with the existing challenge message (0). The padded transcript is kept as the default because it is
uniform across the checker GKR, the fractional GKRs and the leaf claims, and adds no soundness term; the Libra
variant is priced for the case where deferral is replaced by in-the-clear verification (a GPU verifier that does
not want 1 569 deferred linear constraints).

### 2.3 LogUp accumulators (A: fractional GKR; B: helper columns) **[source Hab22, PH23]**

- A: `q_root` is padded (`<q_root>`), `p_root = 0` is asserted (nothing sent), every `p_k(rho, 0/1), q_k(rho, 0/1)`
  claim is padded, the `m_T` leaf claim `m~_T(rho_T)` is a deferred linear constraint on the committed
  multiplicities (padded value). Multiplicities live in `W_1` with Ligero randomizers: opened columns reveal
  nothing about the usage histogram. The tree itself is never sent.
- B (helper columns): the helpers `h_j = 1/(z_T - w_j)` and `h_v = m_T(v)/(z_T - t_v)` are a second randomized
  tableau (`com_2`) with its own randomizers, blinding rows and HM96 leaves; the constraints `h_j (z_T - w_j) = 1`,
  `h_v (z_T - t_v) = m_T(v)`, `sum h_j = sum h_v` are Ligero constraints; no fraction is ever sent. Extra cost is
  the 6.67% row loss of 2.1 on 361M helper coordinates (already inside B's +7.0%).
- Pole probing: section 1 (honest witness: the public redraw rule; any witness: step 0).

### 2.4 AIR/FRI (B-AIR, the current Plonky3 implementation's shape) **[source ethSTARK 5.5; derivation]**

Trace: one row per unit, `U = 393 216` real rows in a `2^19` domain (131 072 padding rows), LDE at rate `1/4`
(`n = 2^21`), `s = 189` FRI queries at `2^-128` in the proven unique-decoding regime (`explore.pcs.fri_queries`;
21 field-term applications). Randomised-trace ZK:

~~~text
random rows        every column is uniform on `revealed = 2 + 2 s = 380` designated padding rows (DEEP zeta, g zeta,
                   and 2 LDE points per query are all outside the trace domain and distinct); the evaluation map
                   from 380 random rows to 380 revealed points has full rank -> the revealed values are uniform
                   (`accounting.fri_zk_requirements`: padding_covers = True at B = 4096; below ~1 000 units the
                   trace domain would have to double)
selector column    `is_real` (public, 1 column): every constraint is multiplied by it, so random rows satisfy
                   nothing; degree 5 -> 6, quotient chunks 4 -> 8 (`+4 d` base columns)
blinding codeword  one random polynomial R of degree < 2^19 (d base columns) committed with the trace; FRI runs
                   on P + R where P is the DEEP/quotient combination: the fold oracles and the final polynomial
                   are uniform
salted leaves      32 B salt per Merkle leaf (LDE row) of both trees, or HM96 leaves as in 2.1
~~~

Extra per VU (census layout, BabyBear^6): +31 base columns of 2 924 (+1.06% committed and encoded), +1.6% hashing
(salts), 37 kB PRG. Goldilocks^3: +16 columns (+0.8%), +1.2% hashing. The Plonky3-layout (2 794 columns) rows are
within 0.1% of these. **Caveats:** (i) the FRI query positions must not be reused across the trace and quotient
trees beyond the counted `2 s` points -- Plonky3 opens the same positions in every tree, which is what the count
assumes; (ii) the DEEP quotients `(T_i(x) - T_i(zeta))/(x - zeta)` are functions of revealed values only; (iii)
the FRI *final* polynomial is sent in the clear and is hidden by `R`; (iv) grinding / proof-of-work bits (Plonky3
`pow_bits = 16`) are irrelevant to privacy; (v) the non-interactive Plonky3 prover has **no verifier coins**, so
its honest-verifier ZK is ZK against any verifier in the random-oracle model (3.3) -- at depth 1.

## 3. Malicious-verifier zero knowledge

### 3.1 Why the honest-verifier layer is not enough

Sections 2.1-2.4 assume the verifier's coins are uniform and independent of the prover's messages. A verifier
who chooses `Q` after `com_1`, `r` after the rows are fixed, or `z_T` at a guessed witness value (section 1, pole
probing) breaks the simulation: the simulator cannot choose the opened columns before it knows `Q`, and the
Ligero randomizers hide only `t` *uniformly chosen* columns of each row (any `t` fixed columns are still uniform --
Lemma 4.15 is for arbitrary `Q` -- but a verifier who *adapts* `Q` to `com_1` can, e.g., open the same `t` columns
of a row across sessions while the prover re-randomises; the HM96 hiding of the other leaves is what stops a
dictionary attack; the formal issue is that no simulator exists for an adaptive `Q` without rewinding).

### 3.2 The mechanism chosen [proposal, PROTOCOL A 5.5 / B 5.3]: verifier-coin commitment (step 0, HM96)

Before the first prover message the verifier samples **every** coin of the session and sends one statistically
hiding, computationally binding commitment per challenge slot (HM96 first scheme, `k_V = 160`, from the same
collision-resistant `H` as the Merkle tree; `O(k)` variant for the long coins `r` and `Q`). Each challenge message
of the honest-verifier protocol becomes the *opening* of its slot; the prover verifies the opening before sending
the message that depends on it.

~~~text
transcript order (A; B-Ligero identical with R = 7 slots; B-AIR interactive with R = 27)
 0   V -> P   c_1 .. c_R                         HM96 commitments to all coins, R = rounds.protocol
 1   P -> V   com_1                              the randomized tableau (2.1, pads of 2.2 inside)
 i   V -> P   x_i                                opening of slot i in the order of PROTOCOL 5.1; P checks
                                                 H(x_i) = y_i, coin_i := h_i(x_i); malformed -> P aborts
     P -> V   the padded / blinded message that depends on coin_i    (never before the opening verified)
 ... parallel slots (all z_T, beta_T, z_0; the five tables' round-j coins) open in one message
 5d  P -> V   opened columns                      after the opening of Q verified
what V commits to     every z_T^(1), z_T^(2), beta_T; z_0; every mu_k, lambda_k; every r_j; every alpha_i, beta_i,
                      merge coefficient; gamma; the Ligero vector r (H(r) committed, r sent with x); rho_add, rho_q; Q
binding requirement   computational: two openings of c_i are an H-collision (HM96 3.2). If binding fails the
                      verifier adapts a coin -> privacy fails (not soundness); this is the only new use of H
hiding requirement    statistical 2^-160 per slot, R 2^-160 = 2^-149.4 total for A: what the PROVER may learn
                      about future coins -> a SOUNDNESS term (accountant `commitment_hash / verifier coin
                      commitments`), below every other term (section 5)
message timing        +1 verifier message before com_1; every other opening rides on the message it replaces:
                      depth 381 -> 382 (A), 3 -> 4 (B-Ligero), 22 -> 23 (B-AIR interactive)
abort / restart       P aborts iff an opening fails, a coin is out of domain, or all S redraw slots of a table
                      lie in Img_T -- all public data. P never aborts on witness data and never restarts within
                      a session; a new session recommits everything with fresh randomness (pads, randomizers,
                      blinding rows, HM96 strings) and the verifier recommits fresh coins. V aborts on any
                      failed check. The verifier's abort decision may depend on com_1: com_1 is a Merkle root
                      over statistically hiding leaves, so the decision is (2^-146-close to) independent of the
                      witness -- the abort itself leaks nothing (Goldreich-Kahan).
privacy argument      any V*: (1) run V* to get c_1..c_R; (2) send a simulated com_1 (random tableau); (3) take
                      the openings; if V* aborts output the prefix; (4) rewind to after step 0 with all coins
                      known, run the HVZK simulator of section 2 on those coins, replay; V* must open the same
                      coins (binding) or abort; (5) on abort-in-replay-only, repeat (4) (expected repetitions
                      bounded because the abort probability differs by <= 2^-146 between the runs). Result:
                      computational ZK under collision resistance of H with statistical loss n 2^-160 per tableau.
~~~

Cost of step 0 alone (on top of HVZK), `K = 1536, B = 4096`: A: `R = 1 589` slots, +0.39 MB communication per
batch (+94.7 B/VU on 19.3 kB/VU), 1 589 HM96 opening checks (hashes of `<= 121` B strings: +95 B/VU of hashing,
+0.002% time), +1 depth; B-Ligero: `R = 7`, +1.7 kB per batch, +1 depth; B-AIR interactive: `R = 27`, +6.6 kB,
+1 depth. **Every design's malicious-verifier increment over HVZK is below 0.01% of prover time**; the depth is
the only visible cost (section 4).

### 3.3 The alternative not chosen: Fiat-Shamir

Making the protocol non-interactive removes the verifier's coins altogether: honest-verifier ZK of a public-coin
protocol is ZK against every verifier in the random-oracle model, at **depth 1**. It was not chosen:

1. **Assumption.** The random-oracle model is an idealisation of `H` beyond collision resistance; the campaign's
   rule is "hash-based preferred" with additional assumptions as *labelled alternatives*. Step 0 uses CRH only.
2. **Soundness re-parameterisation.** Under the generic state-restoration bound `eps_FS <= q x eps_round`
   (BCS16; Block et al. 2024/1161 for FRI) with `q = 2^60` hash queries, every per-round term must fall to
   `2^-188` (`zk_cost.fiat_shamir_reparameterisation`): the Ligero query term needs `t = 279` opened columns
   (1.46x; **it no longer fits `k - l = 256`**, so the ZK payload must shrink to `l <= 3 816`), and A's logUp identity
   term needs Goldilocks^4 / BabyBear^7 (challenge x challenge 1.78x / 1.36x more limb MACs -- on the bucket that
   is 40% of A's time). Grinding recovers some bits at extra prover work. The interactive protocol charges none of
   this.
3. **Transferability is not required** (user decision, `backends/AGENTS.md`), so FS buys nothing we need besides
   depth. Depth is the measured question for A (381 vs 3); if the RTT sweep makes A's depth binding, FS is the
   labelled alternative to price against the `c`-variables-per-round and table-sharding reductions of PROTOCOL A 5.4
   (depth 110-158 at ~2x sumcheck-round work) -- under "random-oracle" in the assumption list, never as the
   default.

B-AIR as it exists (Plonky3, FS) is the one design where FS is already the mechanism; its label path is
`NON_ZK_PROOF_DIAGNOSTIC -> COMPLETE_ZK_BACKEND (random-oracle)` in one step once 2.4 is implemented -- with the
assumption label -- or `-> COMPLETE_HVZK_BACKEND (interactive) -> COMPLETE_ZK_BACKEND` via step 0 at depth 23.

### 3.4 The pole redraw under step 0

The redraw slots `z_T^(1), z_T^(2)` are committed in step 0 like every other coin; the rule "use the first slot
not in `Img_T`" is evaluated on the opened values and public data; the transcript records the slot used. The
verifier can no longer place `z_T` adaptively; it can still *pre-commit* to `z_T = w*(beta_T)` for a guessed
`w*` -- but for an honest witness `w* in T`, so `z_T in Img_T` and the slot is redrawn (public, witness-independent).
A dishonest witness with `w_j notin T` has no privacy claim. The conditioned soundness bound (`z_T` uniform over
`F_c \ Img_T`) is unchanged: the prover learns nothing about the committed slots (hiding), so the bound over the
verifier's *honest* coins is the one that matters for soundness, and privacy needs no distributional assumption on
the coins at all.

## 4. Cost table per VU (`security.zk_cost`, `notes-asset:campaigns/r20-proof/assets/zk-construction/reports/zk_cost.json`; every figure a cost-model estimate)

`K = 1536, B = 4096, 2^-128`, H100, Blake3 at 50 GB/s, PRG at 100 GB/s; utilisation 0.172 (note:r20-proof/tensor-cost/20260922T0450Z-report-tensor's TensorZKP
calibration) and, for A, 0.0143 (`tc_sumcheck_4090` model-equivalent tensor-bucket utilisation). `none` is the
non-ZK diagnostic a kernel measurement corresponds to; `hvzk` is the protocol documents' layer **and what
note:r20-proof/tensor-cost/20260922T0450Z-report-tensor already priced** (the accountant's rows and pads contain it: the finding of this lane is that note:r20-proof/tensor-cost/20260922T0450Z-report-tensor's
A/B rows are HVZK numbers, not non-ZK numbers); `malicious` adds step 0.

| design (field, d) | extra committed el./VU | extra encoded B/VU | extra hashed B/VU | extra field ops (limb MACs/VU) | PRG B/VU | extra comm. B/VU | depth | overhead none -> hvzk -> malicious @0.172 | delta hvzk | delta malicious over hvzk |
|---|---|---|---|---|---|---|---|---|---|---|
| A (BabyBear^6) | +6.8 (pads) | +49 024 | +49 600 (+95 step 0) | +5.8e7 (+0.8%) | 12 740 | +0 / +94.7 | 381 -> 381 -> 382 | 1.055e7 -> 1.070e7 -> 1.070e7 | **+1.43%** (+0.89% @0.0143) | +0.002% |
| A (Goldilocks^3) | +3.4 | +94 656 | +95 232 (+95) | +2.2e8 (+2.2%) | 24 150 | +0 / +94.7 | 381 -> 382 | 1.216e7 -> 1.251e7 -> 1.251e7 | **+2.91%** (+2.31%) | +0.002% |
| A-hintfree depth 630 (BabyBear^6) | +6.8 | +34 480 | +35 056 (+95) | +4.1e7 | 9 110 | +0 / +94.7 | 630 -> 631 | 9.945e6 -> 1.005e7 -> 1.005e7 | **+1.07%** (+0.65%) | +0.002% |
| B-Ligero (BabyBear^6) | 0 | +310 656 | +311 808 (+0.4) | +3.7e8 (+6.7%) | 78 640 | +0 / +0.4 | 3 -> 3 -> 4 | 1.348e7 -> 1.442e7 -> 1.442e7 | **+7.02%** (+6.76%) | < +0.001% |
| B-Ligero (Goldilocks^3) | 0 | +406 144 | +407 296 (+0.4) | +9.5e8 (+6.7%) | 102 530 | +0 / +0.4 | 3 -> 4 | 2.160e7 -> 2.312e7 -> 2.312e7 | **+7.02%** (+6.73%) | < +0.001% |
| B-AIR (census layout, BabyBear^6; relative only, no absolute row in note:r20-proof/tensor-cost/20260922T0450Z-report-tensor) | +31 columns x 2^19 / 4096 = +3 968 (+1.06%) | +63.5 kB (+1.06%) | +96 kB (+1.58%) | +1.06% of the LDE work | 36 900 | +1.6 (step 0) | FS 1; interactive 22 -> 23 | -- | **~+1.1-1.6% per bucket** | +0.00% |
| B-AIR (Goldilocks^3) | +16 columns (+0.80%) | +65.5 kB (+0.80%) | +98 kB (+1.19%) | +0.80% | 37 300 | +1.6 | 1 / 22 -> 23 | -- | **~+0.8-1.2%** | +0.00% |
| C QuickSilver (comparison, `explore.vole`) | 0 | 0 | 0 | 0 | 0 | 0 (667 kB/VU P->V is native) | 2 | 3.05e6 (designated-verifier, `zk_mode` caveat) | native | native (malicious-verifier in the F_sVOLE-hybrid, QuickSilver Thm 2) |

Reading the table:

- **The privacy layer is 1-3% for A and 7% for B-Ligero; the malicious-verifier step is free in prover time and
  costs one round trip.** Every non-ZK number on tonight's ledger has a complete-ZK counterpart within these
  factors -- below the 10% threshold of the lane brief in every cell, so the non-ZK numbers are essentially the
  complete numbers (ledger `--breakthrough` entry).
- The A/B ranking does not move: A/BabyBear 1.07e7 vs B/BabyBear 1.44e7 at 0.172 (1.35x, was 1.34x non-ZK);
  at the `tc_sumcheck_4090` utilisation A 6.02e7 vs B 5.30e7 (B ahead by 1.14x, was 1.20x).
- B-Ligero pays the full `k/l - 1 = 6.7%` on every bucket because encoding, hashing and the row combination all
  scale with rows; A pays it on the Ligero buckets only (its sumcheck buckets are unchanged), so its relative cost
  falls as the sumcheck share rises (0.89% at the measured 4090 utilisation).
- B-AIR's random rows are free at `B = 4096` (the `2^19` domain has 131 072 padding rows for 380 needed); the
  visible costs are the selector's quotient doubling and the leaf salts.
- On top of the `tc_sumcheck_4090` re-pricing of A (6.0e7 at 0.0143 model-equivalent, H100 peak-ratio scaled --
  labelled, not measured there): HVZK +0.89% -> 6.02e7; malicious the same.

## 5. Soundness impact (`security.accounting`; `zk_cost.soundness_with_zk`)

| addition | term | value (`K = 1536, B = 4096`, Goldilocks^3 / BabyBear^6, `t = 191`) | in the accountant |
|---|---|---|---|
| Ligero randomizers (`l = 3 840` instead of `k`) | linear query term `((k + l)/n)^t` shrinks (7 936 vs 8 192 over 16 384); IRS and quadratic terms unchanged; `k > l + t` enforced by `LigeroParams.validate(zk=True)` | `2^-200.6` vs `2^-192` (helps) | `ligero_error` |
| blinding rows | none (the blinding rows are of the tested codes; the tests' soundness statements are for affine codes, AHIV22 App. B) | 0 | -- |
| HM96 leaves | none for soundness (binding = CRH, already the `commitment_hash` term); hiding `n 2^-160` | zk term `2^-146` (A), `2^-145` (B, two tableaux) | `zk` kind, not summed |
| padded transcript (A default) | none: checks become Ligero linear constraints, `combination="uniform"` for A | 0 | -- |
| Libra masking (A alternative) | `instances / |F_c|`, 111 instances | `2^-185` (GL^3), `2^-178.6` (BB^6) | `zk_sumcheck_masking_error`, `batching` |
| step 0 coin commitments | hiding `R 2^-160` (what the prover learns) | `2^-149.4` (A, R = 1 589); `2^-157.2` (B, R = 7); `2^-155` (B-AIR, R = 27) | `commitment_hash`, statistical |
| FRI randomised trace | none for the trace / blinding polynomial (same degree bound); selector: DEEP/quotient degree `5N -> 6N` | `2^-170.7 -> 2^-170.4` (GL^3) | `fri_zk_requirements` |
| **totals** | A hvzk / malicious / malicious+libra; B hvzk / malicious | **all `2^-129.5`**, `meets(-128)` True at Goldilocks^3 and BabyBear^6 (`test_soundness_terms_leave_the_operating_point`) | |

Nothing changes at the stated extension degrees: the operating point is set by the Ligero IRS query term
`(5/8)^t` and the logUp identity term, neither of which the ZK layer touches. The Fiat-Shamir alternative is the
only privacy route that moves parameters (3.3).

## 6. Reference implementation (`verity_numerical.security.zk_reference`, tests < 1 s)

- `LigeroToy(p=97, n=32, k=12, l=4, t=6)`: row encoding with randomizers, the three blinding rows, prover
  responses `v, q_add, p_0`, the verifier's checks; `prove` / `simulate_view`. Tests: honest views verify, a wrong
  product or a wrong linear relation is rejected; the **simulated view verifies without the witness**;
  `opened_columns_rank` = `t` for 20 random query sets (exact uniformity of opened symbols); chi-square of every
  projected view coordinate against uniform on `F_97` is below the 99.9% quantile for two different witnesses and
  for the simulator, and 10x above it for the opened symbols without randomizers (`view_statistics`).
- `masked_sumcheck` (degree-3 product, `n <= 6`, Libra mask): complete, rejects a wrong sum; `transcript_map_rank`
  shows the affine map mask -> transcript has rank `3n + 1` = the dimension of the consistent-transcript space, so
  the transcript is uniform there and independent of `f`; chi-square of every round-polynomial coefficient under
  fixed challenges and `rho` for two different `f` is uniform; without a mask the transcript is deterministic.
- `padded_sumcheck`: the protocols' variant; deferred linear constraints hold for the honest prover and fail for
  a wrong claim; padded messages uniform.

## 7. Red-team review items (checklist for the red-team lane)

1. **Coin-commitment binding.** HM96 first scheme: two openings `x != x'` of `(h, H(x))` with `h(x) = h(x')` are an
   `H`-collision; check the universal-hash family is fixed per slot *by the verifier* and that the prover checks
   `h_i(x_i) in domain(coin_i)`; check the `O(k)` variant for `r`, `Q` binds the whole vector (commit to `H(r)`,
   compare after receipt). A malleable or length-ambiguous encoding of `x_i` breaks binding without a collision.
2. **Slot list is public and complete.** `R = rounds.protocol` must be a function of `(K, B, C)`; every `C` line of
   PROTOCOL 5.1 -- including the `S = 2` redraw slots per table, `beta_T` only for multi-column tables, and the `c`-tuple
   when `variables_per_round > 1` -- has a slot; no coin may be drawn outside step 0 (a late coin re-opens the
   adaptive attack).
3. **Pole redraw under ZK.** The redraw decision reads only `z_T^(i)`, `beta_T`, the table; the transcript records the
   slot deterministically; a prover implementation must not branch on a zero denominator anywhere else
   (PROTOCOL A 4.4 / B 4.4); confirm the fractional GKR / batch inversion has no data-dependent early exit.
4. **Abort / restart leakage.** The prover's only aborts are the three public ones; a *new session* must
   re-randomise everything (pads, randomizers, blinding rows, HM96 `x_j`, salts) -- reusing `W_1`'s randomness across
   sessions with a different `Q` opens `2t` columns of the same row (Lemma 4.15 needs `k - l >= t` per session).
   Check that the verifier's abort after `com_1` cannot be correlated with the witness beyond the HM96 hiding
   bound (it must not see anything else before deciding).
5. **Masking randomness source.** Pads, randomizers, blinding rows, HM96 strings and salts come from a PRG seeded
   per session (GPU-side AES-CTR or hash-based); the ZK claim is at the ideal level (uniform); the PRG assumption is
   recorded separately (PROTOCOL 7). Check seed handling (never reused, never derived from the witness), and that
   the PRG output is not truncated modulo `p` with bias (rejection sampling or 64 extra bits per element).
6. **Pad reuse.** One pad per transcript element indexed by `(step, table/layer, round, evaluation point)`; a pad
   shared by two elements leaks their difference. The index map is public; check it is injective in an
   implementation with `c` variables per round (`(d+1)^c - 1` values per message).
7. **Fiat-Shamir domain separation** (only if 3.3 is ever taken, or for B-AIR as it exists): every absorbed
   message is length-prefixed and tagged (tree roots, round polynomials, openings); the query-index derivation
   is separated from the challenge derivation; the `pow_bits` grinding witness is absorbed; the transcript includes
   `(K, B, C, profile, code parameters)`. The Plonky3 0.4.3 challenger mask bug (`backends/direct/README.md`) is the
   kind of failure this item covers.
8. **Column-opening consistency across trees** (B-Ligero two tableaux; B-AIR trace + quotient + folds): the same
   `Q` must be opened in every tree; a verifier who accepts different index sets per tree opens more than `t`
   positions of the vertically juxtaposed matrix.
9. **HM96 leaves vs unsalted leaves.** If an implementation ships `H(column)` leaves, hiding is an assumption on `H`
   beyond CRH and must be labelled; the accountant's `zk` term becomes "not quantified".
10. **Malicious-verifier simulator.** The Goldreich-Kahan expected-time argument is cited, not read, in the
    protocol documents; the sketch in 3.2 should be checked for the case where `V*`'s abort probability after
    `com_1` is close to 1 (the simulator's expected repetitions are bounded by the closeness of the two abort
    probabilities, which needs the HM96 hiding bound to be applied to the *whole* `com_1`, i.e. union over `n`
    leaves).

## 8. What remains unresolved

- Proofs: honest-verifier ZK of the composition (padded GKR + fractional GKR + Ligero) is inherited from FS24
  Theorem 6 / AHIV22 Lemma 4.15 by analogy, not proved for this composition; the malicious-verifier simulator is
  a sketch (item 10). These are PROTOCOL A/B section 10 items 1-2, unchanged.
- The B-AIR HVZK layer is priced relative to a trace whose absolute cost note:r20-proof/tensor-cost/20260922T0450Z-report-tensor never modelled; the interactive
  FRI depth (22) assumes one beta per fold and no batching of the fold challenges.
- The PRG rate (100 GB/s) and the HM96 universal-hash evaluation cost are assumptions; both are < 0.7% of time.
- Communication figures use the accountant's 8-byte-element estimate for all fields.
- Whether A's depth (382 with step 0) is acceptable is the RTT question of PROTOCOL A 5.4, not a privacy question;
  if it is not, the labelled Fiat-Shamir alternative (3.3) is the only privacy-preserving depth-1 route and costs
  `t = 279` / one more extension degree.
