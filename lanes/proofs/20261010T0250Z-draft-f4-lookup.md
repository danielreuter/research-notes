---
id: proofs/20261010T0250Z-draft-f4-lookup
campaign: flock
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: F4 design agent (lookup), for the proofs coordinator bc-8416bc72
---

# F4 candidate 2: a lookup-based sparse evaluation argument for holographic C-Flock

Front F4, option 5. This is a first full draft, one of three candidate sparse-evaluation arguments, which are chosen by Lean
proof complexity first and cost second. It builds on rec-holo §3.1, §3.3, §3.4, §4, §8 and §9, and it reads the Spark draft
(`note:proofs/20261010T0250Z-draft-f4-spark`) so that the two use the same baselines and prices. Lean paths are as of
`origin/main` `dc67b1542`, where every declaration cited here was checked to exist.
The toys and cost tables behind the C numbers are in the evidence store as `art:a86e936b84c37c04e5822d86e3c46dc04064ff1e8f015b324b46fdd6ba07743f`.

Marks: **M** measured (in the cited run), **C** computed from measured numbers by the formula given, **E** estimated.

## Answer in short

- **Protocol (§1).** The lookup is read-only and one-hot, in the style of Shout ("Twist and Shout", Setty–Thaler), not
  logUp. Each record (one nonzero of a type's matrix) stores its row and column index as registered address chunks of
  width w, each chunk a one-hot vector of 2^w bits (a binary bit when w = 1).
  - The matrix's multilinear extension at the lincheck point is then
    `Σ_k val(k) · ∏_c X_c(k) · ∏_c Y_c(k)`, with `X_c(k) = Σ_a ra_c(k,a)·eq(x_c,a)`: an indexed lookup of chunk c of
    record k's row into the eq table of `x_c`.
  - One degree-D product sumcheck over the K padded records proves it (D = number of chunks, 6 to 38 here). Its factor
    claims reduce to one claim on the registry, a selection sumcheck over the hidden type τ moves that claim to a public
    point, and the registry is opened there at the unique-decoding radius.
  - A new step P0 turns the zerocheck's univariate-skip row point into a multilinear one at a cost of 6/|F| and 128 masked
    values per rep. The eq tables then factor over chunks.
- **Characteristic 2 (§1.2).** Nothing is counted. There are no multiplicities, no timestamps, no fingerprints and no
  grand product, and no vector is committed inside a rep.
  - logUp fails: its identity sees a count only mod 2 (checked, §1.2). GKR-logUp inherits that and adds a GKR.
  - The one-hot identity holds for **any** registered bits: every bit string is some GF(2) matrix (§1.5). So soundness is
    against the registered matrix and needs no well-formedness proof.
- **The bit-committed candidate is the w = 1 case** of the same identity and the same proof. Chunk width is a public
  per-shape knob: w = 3–5 is 2.0–3.2× cheaper than binary at T ≤ 2 types per shape, and w = 1–2 is optimal from T = 16 on
  (C, §5.2).
- **Soundness (§2)** adds only statistical terms: 2^-113 to 2^-110 per rep including the witness list factor (C),
  against today's 2^-97.75. `cr/sha-512` enters only through the fork-finder reduction for the registry root, so **no
  assumption is added**.
- **Zero knowledge (§3).** τ lives only in the witness and in masked values. The registry is opened only at public points,
  every new message carries an M1 pad, and `RegHides(A)` is a theorem from `ZK/Masking`'s lemmas once the level-0 padding
  covers a registration's openings.
- **Lean (§4).** 14 lemma groups: 7 that every holographic candidate needs (the Spark draft's H1–H7) and 7 specific to this
  design, about 1,200–2,200 new lines (E) against Spark's 2,900–5,150.
  - The riskiest lemma is shared by all three candidates: the registry as **one** oracle across sessions. `Game.Lock`'s
    chooser sees each session's continuation, so the natural statement is one game over a registration's lifetime.
  - The riskiest lemma specific to this design is the masked chain of D − 1 products (D up to 38).
- **Cost at 2^20 nonzeros (§5, C).** Per nonzero per rep: 81–242 ns at T = 1, 371–984 ns at T = 16.
  - Per session (two reps): 0.17–0.51 s at T = 1 and 0.78–2.06 s at T = 16, which is 0.06–0.19× and 0.29–0.77× a 2.68 s
    `--zk` session of 2^27 rows (M).
  - It adds 0.8–1.5 MB of proof, two Ligerito openings for the verifier, and about 40 coin rounds per rep.
  - Every holographic candidate pays a **hidden-type tax**, `T × (registered bits per record) × 0.29–0.62 ns`, because the
    opening must cover every type's columns. It dominates at T = 16.
- **Kill (§6).** The wide chunks, the only part that is not candidate 3, are dead if F2's shapes have T ≥ 8 types, or if a
  degree-10 product-sumcheck kernel measures less than about 2× cheaper per record than a degree-30 one.
  - The whole family (this design, candidate 3, and Spark through the same tax) costs more than the session itself at
    K = 2^24 with 16 types unless sessions exceed about 2^31.6 rows (C).

## Where I disagree with rec-holo (and the Spark draft)

1. **A lookup needs no grand product (rec-holo §3.2; Spark draft, "View").** I agree that logUp is unsound in
   characteristic 2. It does not follow that a lookup has to be a grand product with Frobenius multiplicities.
   - With **registered** one-hot addresses, the looked-up value is a public linear function of registered bits:
     `X_c(k) = Σ_a ra_c(k,a)·eq(x_c,a)`.
   - Nothing has to be committed after the lincheck point and nothing has to be counted. The Spark draft's E commitment,
     product GKR, fingerprint and multiplicity bits all disappear, and so does its riskiest lemma, S3.
2. **Price (rec-holo §4.4).** rec-holo's 245–295 ns per nonzero leaves out the registry opening, and the hidden type
   multiplies that opening by T. At T = 16 this tax is 150–800 ns per record per rep here and 150–330 ns in the Spark
   draft (C, §5.2), as much as the sparse argument itself.
3. **The row point (rec-holo §1).** rec-holo keeps the zerocheck's skip weights `L_s(ζ)` on the row side. The Spark draft
   can, because its table `T_x` is arbitrary. An eq-product design cannot: `L_s(ζ) = c·Z_S(ζ)/(ζ+s)` is no product over
   s's bits. P0 (§1.4) fixes this for this design and for candidate 3 alike, at 6/|F| (C).
4. **Decoding radius (rec-holo §9.4).** I agree with the Spark draft's disagreement 3. "Binding" fixes a root, not a
   polynomial: at the Johnson radius up to `listBound = 100·2^logInvRate` messages lie near it. The registry has to be
   opened at the unique-decoding radius (rate 1/4, 160 level-0 queries, (5/8)^160 = 2^-108.5, C).
5. **The hiding budget (rec-holo §3.3)** counts one opening per session. The baseline here opens the registry once per rep,
   so twice per session. Batching both reps' claims into one opening with doubled queries restores one (§5.3).
6. **Timestamps (rec-holo §3.1).** I agree with the Spark draft that read-only memory needs no timestamps. This design does
   not need the read-only memory check at all.

## 1. The protocol, fitted to C-Flock over GF(2^128)

### 1.1 Setting

- **Shape** `(k, K, T, w_r, w_c)`, all public:
  - a block of `2^k` rows;
  - `K = 2^κ` records, K/2 for `A_0` and K/2 for `B_0`, with the side fixed by position;
  - T types padded to `2^lt`;
  - chunk widths `w_r` and `w_c` for the row and column indices.
  - Circuits have 23–47 nonzeros per row (M, arch-recursion), so I take `k = κ − 5` (E).
- **Session.** As in the Spark draft: one C-Flock table `A = I ⊗ A_0`, with `2^m` rows, `n = 2^{m−k}` copies (the batch's
  units) and two reps on one root.
  - `A_0 = A_pub + A_τ` and `B_0 = B_pub + B_τ`. The verifier evaluates the template's public part (slots, pins, I/O) in
    O(nnz_pub).
  - `(A_τ, B_τ)` belongs to the hidden type τ < T.
- **Fields.** Sumchecks run over F = GF(2^128) and Ligerito over K = GF(2^256), as in C-Flock (verifier PROTOCOL.md §9–§15).

### 1.2 Which lookup, and characteristic 2

| form | in characteristic 2 | Lean beyond the common frame |
|---|---|---|
| logUp: `Σ_i 1/(X − f_i) = Σ_a m_a/(X − t_a)` | **unsound**: `m_a` enters mod 2, and `2/(X − t) = 0` | — |
| GKR-logUp (fractional sumcheck) | unsound for the same reason | a GKR as well |
| Lasso / Spark: read-only memory, grand product | sound with Frobenius multiplicities (Spark draft §1.4) or multiplicative timestamps | product GKR, fingerprint, multiset lemma, E inside a rep |
| **Shout-style one-hot, registered addresses** | **sound**: nothing is counted | one degree-D product sumcheck and one identity |

- **Why logUp fails** (toy over GF(2^16), C). Honest counts `[3,3,4,1,6,6,4,3]` satisfy the identity with the counts
  taken mod 2. So does a lookup that reads a value outside the table twice: the identity still holds, so the lookup is
  accepted. Any integer count m enters as m mod 2.
  - The usual repair, counting in a prime field, is not available inside GF(2^128). Moving the counts into the exponent is
    exactly the Spark draft's Frobenius construction, which brings its grand product with it.
- **Why the one-hot form needs no counting.** Each record's address is not a value to be matched against a table. It is a
  set of registered selector bits, and the "lookup" `X_c(k) = Σ_a ra_c(k,a)·eq(x_c,a)` is linear in them.
  - No multiset has to be equal to another, so there is nothing to count. Characteristic 2 enters only as `−1 = 1`
    (`eq(x,a) = ∏_i (1 + x_i + a_i)`) and through duplicate records, which cancel (§1.5).

### 1.3 Registration

There is one hiding Ligerito commitment `Creg` per shape per registration: salted hm96-sha512 leaves, level-0 padding sized
for §3's budget, and **rate 1/4 at level 0**, for the unique-decoding radius. It commits the bits `R_t(k, y)` for every type
t < 2^lt, record k < K and record position y < B_pad.

| record field | bits | content |
|---|---|---|
| row chunk c, c < ⌈k/w_r⌉ | 2^w_r (1 if w_r = 1) | one-hot of row bits `[c·w_r, (c+1)·w_r)` (one bit if w_r = 1) |
| column chunk c, c < ⌈k/w_c⌉ | 2^w_c (1 if w_c = 1) | the same for the column |
| padding to B_pad | — | zero (B_pad is a power of two, or a sum of two) |

- **The side is positional.** Records `k < K/2` are `A_t`'s and the rest `B_t`'s, so `val(k) = α·(1 + k_top) + k_top` is
  public and multilinear.
- **Every bit string is a matrix pair.** Records whose chunks are all zero, used for padding to K, contribute nothing. A
  chunk with several ones contributes every address it selects (§1.5). Registration therefore needs no proof of form.
- **Sizes (C).** B = 80–192 bits per record at T = 1 (w = 3–5) and 30–74 at T = 16 (w = 1–2). The registry is
  `T·K·B_pad` bits: 2^26.6–2^27.6 at K = 2^20, T = 1, and 2^29.0–2^30.0 at T = 16.

### 1.4 One session

The witness `z` holds the type bits τ at public positions. F2's coverage proof binds them to the sampled units' committed
type. Each rep runs:

| step | what | rounds | hidden products (triples) |
|---|---|---|---|
| R1 | zerocheck as today (verifier PROTOCOL.md §9). It ends with claims `v_a`, `v_b` on `(Az)~`, `(Bz)~` in the §11 format: skip weights `w_s = L_s(ζ)` and an eq point `x' ∈ F^{m−6}` | as today | as today |
| R2 = **P0** | the prover sends `a_s = Σ_y eq(x',y)·(Az)[s,y]` and `b_s` for s < 64 (128 masked values). The verifier checks `v_a = Σ_s w_s a_s` and `v_b = Σ_s w_s b_s` (affine), draws `x_0 ∈ F^6`, and takes the new claims `Σ_s eq(x_0, s)·a_s` and `Σ_s eq(x_0, s)·b_s`. The row point `x = (x_0, x')` is now multilinear: local part `x_loc` (k coordinates), slot part `x_slot` | 1 | 0 |
| R3 | **paper-form lincheck** (rec-holo §1): α, then k multilinear rounds over the block's column bits (the slot sum collapses on `I ⊗`). It ends at `r ∈ F^k` with `v_M·ẑ(x_slot, r) = claim`, where `v_M = v_pub + v_hid` and `v_pub = α Â_pub(x_loc,r) + B̂_pub(x_loc,r)` (plus the pin term) is the verifier's | k + 1 | 1 |
| R4 | **sparse sumcheck**: `v_hid = Σ_{k<K} val(k)·∏_c X_c(k)·∏_c Y_c(k)`, with `X_c(k) = Σ_a R_τ(k, pos^r_c(a))·eq(x_c, a)` and `Y_c` the same against `r_c`. κ rounds of degree D (D + 1 in the side round), ending at `r_k ∈ F^κ` | κ | 0 |
| R5 | **factor values**: the prover sends the D values `X̃_c(r_k)` and `Ỹ_c(r_k)`, masked. The verifier checks `val(r_k)·∏ = final` | 1 | D − 1 |
| R6 | **claim reduction**: the prover sends `P[y] = R̂_τ(r_k, y)` for y < B_pad, masked. The verifier checks each factor as `X̃_c(r_k) = Σ_a eq(x_c,a)·P[pos^r_c(a)]` (affine, public coefficients), draws `s`, and takes the claim `R̂_τ(r_k, s) = Σ_y eq(s,y)·P[y]` (one per table if B_pad is a sum of two powers) | 1 | 0 |
| R7 | **selection** (T > 1; the same as the Spark draft's R7): `R̂(τ, r_k, s) = Σ_t eq(τ,t)·Ĝ(t)` with `G(t) = R̂(t, r_k, s)`, over lt rounds of degree 2 (masked). It ends at a public `r_t` with `eq(τ, r_t)·Ĝ(r_t)`. `eq(τ, r_t) = ∏_i (1 + r_{t,i} + τ_i)` is computed from masked `τ_i`, each tied to `ẑ` at τ's public positions by an extra opening claim (PROTOCOL.md §16.2) | lt | lt |
| R8 | **openings**: `ẑ` with its claims, as today; `Creg` at the public point `(r_t, r_k, s)` under the unique-decoding schedule, with the value masked | Ligerito's | — |

- **Rounds per rep (C).** R2–R7 come to `κ + k + lt + 4`: 39 at κ = 20, T = 1 (43 at T = 16), and 31 to 51 across the three
  bounds. R3 replaces today's lincheck rounds, and R8 adds one Ligerito opening. The Spark draft's R4–R7 add 291–627 rounds
  (170–350 in lockstep), and each round waits on the coin server.
- **Prover work per rep beyond R4.**
  - P0 is one pass over the GF(2) vector `Az`, about 2^m × 0.02 ns = 3 ms at m = 27 (E).
  - R6 is `K·B_pad/2` additions in F.
  - R7's G(t) is a pass over all T types' records, `T·K·B_pad·0.003 ns` (E, an 8-bit table fold).
  - The registry opening is priced in §5.

### 1.5 The identity, for any registered bits

For type τ, define the GF(2) matrix pair

`A'_τ = Σ_{k<K/2} (⊗_c ra_c(k)) ⊗ (⊗_c rb_c(k))` and `B'_τ` likewise over `k ≥ K/2`,

where `ra_c(k)` is chunk c's bit vector (length 2^w), so `⊗_c ra_c(k)` is a 0/1 vector over the `2^k` rows. For one-hot
chunks each record is one entry `e_row ⊗ e_col`, and duplicate records cancel mod 2. Then:

`Σ_k val(k)·∏_c X_c(k)·∏_c Y_c(k) = α·Â'_τ(x, r) + B̂'_τ(x, r)`

holds for every bit string, because eq factors over chunks: `eq(x, i) = ∏_c eq(x_c, i_c)`.

- **Checked numerically** (toy over GF(2^16), C). K = 16 records, one of them one-hot in every row chunk and the rest
  arbitrary, D = 5: the identity holds, and `A'` and `B'` come out with 68 and 62 ones.
- **The factor claim is a registry claim** (same toy, C): `X̃_c(r_k) = Σ_a eq(x_c,a)·R̂(r_k, pos_c(a))`, which equals
  `R̂(r_k, x_c)` when chunks are eq-encoded.
- **The product sumcheck** (same toy, C), at κ = 4, D = 5: the honest prover is accepted, and 200 of 200 wrong claims are
  caught (bound κD/|F| = 20/65,536).
- **The binary case.** For w = 1 a chunk is the vector `(1 + b, b)` and `X_c(k) = 1 + x_c + b`, so this is candidate 3's
  identity. Each record is then exactly one entry, so the nonzero bound holds on the registered matrix. For w ≥ 2 a record
  can encode a product set of entries, which matters only for the semantics question in §2.4.

### 1.6 The hidden type index, padding, and a variant I rejected

- **τ** appears only as witness bits, in masked messages (R7's rounds, the masked `τ_i`, `eq(τ, r_t)`) and in masked opened
  values. Every registry opening is at a public point that is independent of τ, and it covers every type's columns.
- **Padding.** Records are padded to K with all-zero chunks, types to 2^lt with all-zero registries, and records to B_pad
  with zero bits. Row and column weights never appear: there are no multiplicities to hide (the Spark draft registers them
  as hidden bits).
- **Rejected: τ in Ligerito's level-0 lanes**, with the basis `b = e_τ ⊗ b'` and the hidden factor `eq(τ, ρ_τ)` in
  Ligerito's final check. It saves R7's lt rounds, but:
  - The final check's `b̂` becomes a masked value, which changes the Ligerito verifier and its refinement.
  - It saves no prover work. With `fast100`'s 2^k0 = 64 lanes the opening's work still scales with all T types' bits.
    With T·64 lanes every opened leaf grows T-fold, about +Q_0·(T − 1) KB per opening (2.4 MB at T = 16, C).

## 2. Soundness

### 2.1 The statement

C-Flock's analysis lives under `Proofs.Flock` until its spec is extracted (AGENTS.md, Lean). So the statement starts as a
sketch in `Proofs/Flock/Soundness/Holo/Statements.lean` and moves to `Specs/Flock/Guarantees` once that spec exists. Names
and types follow `RepSound.lean`.

```lean
/-- **A holographic C-Flock session is sound against its registered matrices.** `Creg` is the registry
committed for shape `sh` before the session. For every prover `σ` (two reps on one root, each with P0,
the paper-form lincheck, the sparse sumcheck, the claim reduction, the selection and the registry
opening), the session accepts while no codeword close to the session's table packs a witness whose
type bits `τ` name a type below `sh.T` and satisfy `I ⊗ (S.pub + regMat Creg τ)` with the statement's
pins and region claims, with probability at most the two reps' errors multiplied, plus the far-registry
term. `regMat Creg τ` is `matOf` (§1.5) of type `τ`'s records in the unique message within the
unique-decoding radius of `Creg`; when there is none, the session rejects except with probability
`εFar`. -/
def HoloSessionSound : Prop :=
  ∀ {F K : Type} [Field F] [Fintype F] [DecidableEq F] [CharP F 2] [Field K] [Fintype K] [DecidableEq K]
    (A : Arith F K) (_hA : A.Correct) (sh : HoloShape) (S : HoloStatement sh) (sch rsch : Schedule)
    (_hsch : fast100 S.m = some sch) (_hr : RegSchedule sh rsch) (Creg : Oracle F)
    (σ : Strategy (holoSession A S sch rsch Creg)),
    prob (fun o => o.accepts ∧ ¬ HoloHolds A S sch Creg o.table) (holoSession A S sch rsch Creg) σ ≤
      ENNReal.ofReal (holoRepError sch rsch S sh ^ 2) + ENNReal.ofReal (εFar rsch)
```

- **The compiled form** has the shape of `RanRegistered` (`Discharge/PrivateCircuit/Statements.lean`, proved as
  `ran_registered`): the same event, bounded by the oracle bound plus `ofReal (q²/2^513)` under `SHA512CRStrict`. It has one
  fork-finder term per root, the table's (as today) and the registry's.
- **Across sessions** the registry is fixed at registration, before every session, by record custody. §4.4 explains why the
  clean form is one game over a registration and its A sessions, with each session's event inside.

### 2.2 Error terms, per rep

L = `listBound` at level 0 = 200, the witness table's list size (Johnson). The registry's list size is 1 (unique decoding).
I multiply every new statistical term by L, as the Spark draft does. That is conservative: the sparse phase's claims do not
depend on the witness message.

Each bound is in units of `L/2^128` unless marked otherwise; the two right-hand columns give the coefficient.

| term | bound (× L/2^128) | K = 2^20, T = 1 (D = 9) | K = 2^20, T = 16 (D = 30) |
|---|---|---|---|
| P0 | 6 | 6 | 6 |
| paper-form lincheck (replaces `εLc`) | 2k + 1 | 31 | 31 |
| sparse sumcheck | κ(D + 1) + 1 | 201 | 621 |
| claim reduction | log B_pad | 7 | 5 |
| selection | 2lt + 1 | 1 | 9 |
| **new terms together** (C) | sum × 200/2^128 | **2^-112.4** | **2^-111.0** |
| triples (M1) | about 2^-128 each, at most 42 | negligible | negligible |
| registry opening, unique decoding | level 0: (5/8)^160 = 2^-108.5 (C); levels ≥ 1 as `fast100` | about 2^-100 (E) | about 2^-100 (E) |
| far registry `εFar` | a far `Creg` is rejected at level 0 except with probability 2^-108.5 per opening | 2^-108.5 (C) | 2^-108.5 (C) |

- The new terms together are 2^-113.1 to 2^-110.4 across all six (K, T) cases (C).
- **Per rep:** the registry's term is about 2^-99 to 2^-100 (E: level 0 at 2^-108.5, levels ≥ 1 as `fast100`'s). A rep is
  then about 2^-97.3 to 2^-97.5, and two reps about 2^-194.6 to 2^-195.0 (E). More queries at the registry's levels ≥ 1,
  whose prover cost is small, restore 2^-195.5 (E).
- **With one registry opening per session** (§5.3), that opening must reach 2^-196 alone. That takes 320 level-0 queries
  ((5/8)^320 = 2^-217, C) and doubled queries at the upper levels.

### 2.3 Assumptions

None is added.
- **Statistical:** Schwartz–Zippel (`Core/Game/Poly`), the witness table's list bound (`ListSize.closeMsgs_card_le`, from
  ArkLib's Johnson bound), and unique decoding for the registry (ArkLib's `relativeUniqueDecodingRadius`, already used in
  `Discharge/ZkSession/Compose.lean`).
- **`cr/sha-512`** enters only through the fork-finder reduction, for the registry root.
- **Record custody** also covers the registry root.
- **The OS's randomness** supplies the registry's salts and pads.
- **The coin server's randomness** supplies `x_0`, α, the sumcheck coins, `s` and the selection coins, each issued after the
  framed bytes it answers.

### 2.4 What "sound" means here: three flags for the coordinator

1. **Against the registered matrix.** The guarantee says the session satisfies `regMat Creg τ`, whatever bits were
   registered. Whether those bits are the intended private circuit is a fact about registration. The same holds for every
   candidate.
2. **The nonzero bound.** At w = 1 the registered matrix has at most K entries. At w ≥ 2 a malicious record encodes a
   product set of entries, so K bounds records, not entries.
   - Soundness does not care. If a guarantee or an accounting claim needs entries ≤ K, use w = 1, or prove one-hotness once
     per registration: about 2^w AND/XOR rows per chunk, roughly 160 rows per record, about 0.4 s at K = 2^20 (E).
3. **Determinism / acyclicity** (rec-holo §9.5) is orthogonal and optional: a per-type comparator at the first draw.

## 3. Zero knowledge

**What the auditor sees.** The padded sizes (k, K, T, w, B_pad, m, the copy count), the roots of the table and of `Creg`,
masked messages, values opened at public points (masked by level-0 pads and mask lanes), and the public outputs. Only the ZK
server sees the matrices, τ, the records and the masks.

- **Every new message is a masked unknown with an M1 pad.** That covers P0's 128 values, R3's and R4's round polynomials,
  R5's D factor values, R6's B_pad record values, and R7's rounds and `τ_i`.
  - Every check is affine in masked unknowns, with coefficients from public coins and public points: `w_s`, `eq(x_0, s)`,
    `eq(x_c, a)`, `eq(s, y)`, `val(r_k)`. None depends on the matrix or on τ.
- **Products of hidden values get sacrificed triples**, as M1's zerocheck already does (`ZerocheckMasked` · `prodL`,
  `Masks`): R3's `v_M·ẑ`, R5's chain of D − 1 products, R7's lt products.
  - That is 6–42 triples per rep (C), at negligible cost (E; rec-holo §3.3 counts about 70).
- **The registry** is opened only at public points, once per rep (or once per session, §5.3).
  - `RegHides(A)` is a theorem, as the Spark draft also argues. It follows from `level0_openings_uniform` (needs
    `#positions ≤ t`), `padded_openings_uniform` and `card_translate_fiber` (`ZK/Masking.lean`), once the level-0 padding
    `t_pad` covers every position opened over the registration's life: `Q_0 × openings` plus re-registration's two
    openings. Its target form is `PrivateCircuit.Hides`.
  - Re-registration is rec-holo §9.4's: the same bits under fresh salts, with equality proved at one random point at the
    unique-decoding radius.
- **The budget (C).** Each session opens 320 level-0 positions (2 × 160, or 1 × 320 batched).
  - A level-0 lane holds `T·K·B_pad/(128·64)` elements: 12,288 at K = 2^20, T = 1, and 65,536 at T = 16.
  - At `t_pad` equal to the lane length (the registry codeword doubles), one registration serves about 38 sessions at
    T = 1 and 205 at T = 16 (low-end widths; twice as many at the high end). Re-committing the doubled registry costs
    0.08–0.12 s and 0.38–0.66 s (§5.6), about 3 ms per session either way.
- **Counts.** The nonzero count is hidden by K, the type count by T, and row and column weights never exist as data.
  Session counts per shape are public, and padding them is F2's job.
- **Trust.** Only the ZK server is trusted for privacy. hm96's hiding gap is proved (`CROnly.hm96Hiding_gap`). The one named
  hiding premise left is `hash-derived-key` (`note:proofs/20261009T1940Z-report-salted-hiding-reduction`), and this design
  adds none.

## 4. Lean proof complexity

### 4.1 What exists

- **Sumcheck rounds.** `Rounds.sumRound_sound`, `lincheckRound_sound` and `residualRound_sound` are for degree ≤ 2 only
  (`hP : P.natDegree ≤ 2`). `Game.prCoin_eval_eq_eval_le` (`Core/Game/Poly`) bounds any degree d.
- **Lincheck.** The chain pattern is `LincheckPhase.value_lincheckRounds_le`. `combSum_eq` and `abEval_eq` handle the comb
  and the evaluation, and `eqAt_split_at` / `OpeningPhase.eqAt_split` split eq.
- **Phases.** `RepSound` has `zerocheck_phase`, `lincheck_phase`, `opening_phase`, `ligerito_phase` and `rep_sound`, chained
  by `Game.value_bind_le`. `OpeningPhase` has `opening_phase_of_card` (n claims, any list size), `prCoin_eqSum_le` and
  `prCoin_batch_le`.
- **Ligerito.** `LigeritoPhase.ligerito_sound` and `finalStage` (any `C : Oracle F`), `LigeritoDecode.card_gt_of_agree`,
  `ListSize.encode_injective` and `closeMsgs_card_le`.
- **Compiled game.** `Core/Game/Lock`: `Lock`, `oracleStrat`, `expect_le_coupled`, `leafE_off_le`. Private-circuit
  statements: `Discharge/PrivateCircuit` (`Hides`, `Commit.Binding`, `RanRegistered`, `ran_registered`).
- **ZK.** `ZK/Masking`: `level0_openings_uniform`, `padded_openings_uniform`, `card_translate_fiber`.
  `Discharge/ZkSession/Table.rep_sound_pad_zk` and `Discharge/ZkReg/Sound.zk_session_soundR`.
- **ArkLib** (`b2e456fc`): `ConstraintSystem/Lookup.lean` and `MemoryChecking.lean` define relations only, with no lemmas.
  Its sumcheck soundness (`execute_soundness`) is proved in its own oracle-reduction framework, not in Verity's `Game`.
  Nothing in either place proves logUp, Lasso, a GKR or a fingerprint, and this design needs none of them.

### 4.2 The common frame (any holographic candidate)

I accept the Spark draft's H1–H7, about 2,150–3,750 lines (E):
- H1, the paper-form lincheck;
- H2, the registry in the doom;
- H3, unique decoding;
- H4, the selection sumcheck;
- H5, the ZK extension and `RegHides(A)`;
- H6, the guarantee and two-rep composition;
- H7, the common `FlockVerify` part and its refinement.

The coordinator should assign them once for whichever candidate wins. §4.4 sharpens H2.

### 4.3 Specific to the chunked eq-lookup

| # | lemma | exists (module · declaration) | new | lines (E) |
|---|---|---|---|---|
| L1 | `prodSumcheck_sound`: the degree-D sumcheck chain over `val · ∏_{c<D} f_c`, each `f_c` multilinear | `Core/Game/Poly` · `prCoin_eval_eq_eval_le`; `LincheckPhase` · `value_lincheckRounds_le` (pattern) | the degree-D round and the chain (candidate 3 needs it too; the Spark draft's S1) | 150–300 |
| L2 | `chunkedEq_identity`: `matOf` (§1.5) and the identity, for any bits | `eqAt_split_at`, `OpeningPhase` · `eqAt_split`; `Model/Basic` · `eqAt` | the definition and the identity | 150–250 (60–100 at w = 1) |
| L3 | factor → record → one registry claim: `X̃_c(r_k)` is linear in `R̂(r_k, ·)`, and the random-s batch | `OpeningPhase` · `prCoin_eqSum_le`, `prCoin_batch_le` | linearity of the MLE in the bits; the batch | 100–180 |
| L4 | `skipPartial_sound` (P0): a wrong `a` survives with probability ≤ 6/2^128 | `prCoin_eqSum_le` (pattern) | the step | 60–100 |
| L5 | `sparse_phase`: doom in, doom out, the error from L1, L3 and L4, chained by `value_bind_le` | `RepSound` · `lincheck_phase`, `opening_phase` (pattern) | the phase lemma | 150–250 |
| L6 | the masked versions: the new pads and the chain of D − 1 triples, into H5 | `Discharge/Composed/Inner/ZerocheckMasked` · `prodL`, `Masks` | the chain of up to 37 triples | 100–200 |
| L7 | `FlockVerify`: the degree-D sumcheck verifier, P0, the factor checks and the claim reduction, each refined and fail-closed | the refinement framework (`Refine/`, `Discharge/Exec`, `Discharge/ZkExec`, `FailClosed`) | the code and its refinement | 500–900 |
| | **specific total** | | | **≈ 1,210–2,180** |

- **The count.** 14 groups: the 7 common and L1–L7. L1, L3, L4 and L6 lean heavily on existing declarations.
- **Against the others (E).** Spark's specific part is 2,900–5,150 lines: product GKR, fingerprint, Frobenius leaves,
  multiset, E inside a rep, and the D̂ evaluator. Candidate 3 is this table with L2 at w = 1, about 1,120–2,030. **The
  general chunk width costs about 100–150 lines** over candidate 3.

### 4.4 The riskiest lemma

**Shared by all three candidates: H2, the registry as one oracle across sessions.**
- `Lock`'s chooser is `Chooser T D β := ℕ → D → (g : Game β) → Strategy g → T`. The table chosen at a slot depends on the cap
  and on the **continuation's game and strategy**.
- Inside one session's game that is fine. If each session is its own game, though, each picks its own table from the same
  root, and two sessions could be judged against different registered matrices. Unique decoding alone does not close the
  gap: two pluralities over different continuations can differ on rarely opened positions.
- **The fix I recommend:** one game per registration, with registration's table node first and its A sessions in the
  continuation. Then `Lock`, `oracleStrat` and `expect_le_coupled` apply unchanged, and `leafE_off_le`'s
  `√(N·Q·Pr[fork conflict])` takes Q summed over the A sessions. The guarantee becomes "every session of this registration
  is sound", with each session's event inside.
- **The risk** is the restatement: `holoSession` becomes a sub-game, and H6 composes A of them. The alternative is a new
  lemma that two pluralities agree wherever either is opened with non-negligible probability, a rewinding argument across
  games, which I would avoid.

**Specific to this design: L6.** `ZerocheckMasked` masks one product per round. L6 needs a chain of up to 37 products of
hidden values checked by triples, with their pads in the session's masked-unknown accounting. It is mechanical but long,
and it touches H5's interface. L1 is the largest new piece of mathematics, but it is self-contained and standard.

## 5. Cost

### 5.1 Model and inputs

Per record per rep:

- **sparse sumcheck** = `D·c_fac + (D²/2 + 2D)·c_mul`
  - `c_fac` is the memory and fold cost per factor-term: 5–19.3 ns. That is the degree-3 kernel's price in the Spark draft's
    §5.1 (15 ns tuned, E; 31–58 ns naive, M, from rec-holo), divided by 3.
  - `c_mul` is one GF(2^128) multiplication at 32 threads: 0.14–0.23 ns (M). D²/2 + 2D is the product tree plus the folds.
- **registry opening** = `T·B_pad·(c_bit + 0.003)`
  - `c_bit` is the `--zk` opening cost per committed bit: 0.29 ns at 2^32 bits (M) to 0.62 ns (C: M0's 0.47 at 2^27 bits
    × 1.32 for `--zk`), the Spark draft's prices.
  - 0.003 ns per bit is R7's pass (E). The opening covers all T types, which is the hidden-type tax.
- The **low** end pairs all low prices and the **high** end all high ones. The chunk widths are chosen per end, per T and
  per K, to minimize the total.
- **Not priced:** small-value first rounds (Bagad–Domb–Thaler, Gruen), in which factor values are drawn from 2^w-entry
  tables before materializing. They would cut the D·c_fac term several-fold for narrow chunks (E).

**Baselines (M, rec-holo §2 and §4.2).** C-Flock's CPU `--zk` session at k_log 24, m 27, 8 copies: 20 ns per row, **2.68
s**, proof **843 KB**, and verification about **1.2 s in Rust and 21 s in Lean**. Upstream M0 at m 27: 88 ms, 374 KB.

### 5.2 Prover: per record per rep (C)

| K | T | end | (w_r, w_c) | D | B_pad | sumcheck ns | opening ns | total ns | binary (w = 1) total |
|---|---|---|---|---|---|---|---|---|---|
| 2^16 | 1 | low | (4, 4) | 6 | 80 | 34 | 23 | **58** | 157 |
| 2^16 | 1 | high | (4, 4) | 6 | 80 | 123 | 50 | **173** | 505 |
| 2^16 | 16 | low | (1, 2) | 17 | 32 | 110 | 150 | **260** | 263 |
| 2^16 | 16 | high | (1, 2) | 17 | 32 | 369 | 319 | **688** | 730 |
| 2^20 | 1 | low | (3, 4) | 9 | 96 | 53 | 28 | **81** | 231 |
| 2^20 | 1 | high | (5, 5) | 6 | 192 | 123 | 120 | **242** | 716 |
| 2^20 | 16 | low | (1, 1) | 30 | 32 | 221 | 150 | **371** | 371 |
| 2^20 | 16 | high | (2, 2) | 16 | 64 | 346 | 638 | **984** | 1,015 |
| 2^24 | 1 | low | (4, 4) | 10 | 144 | 60 | 42 | **102** | 313 |
| 2^24 | 1 | high | (4, 4) | 10 | 144 | 209 | 90 | **299** | 942 |
| 2^24 | 16 | low | (1, 1) | 38 | 40 | 302 | 188 | **489** | 489 |
| 2^24 | 16 | high | (2, 2) | 20 | 80 | 441 | 797 | **1,239** | 1,316 |

**The chunk width against T (C)**, as the gain of the best width over binary:

| T | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| gain at K = 2^20 (low–high) | 2.8–3.0× | 2.3–2.4× | 1.7–1.9× | 1.2–1.4× | 1.00–1.03× | 1.00× |

K = 2^16 and K = 2^24 give the same picture: 2.7–3.2× at T = 1 and 1.00–1.06× at T = 16.

- **The Spark draft at the same prices**, by its own §5.1: 179–475 ns at K = 2^20, T = 1, and 323–782 ns at T = 16.
  - This design is 2.0–2.2× cheaper at T = 1.
  - At T = 16 it costs 1.15–1.26× Spark's (C). That is within either model's spread, and small-value rounds, which are not
    priced here, could reverse it.

### 5.3 Prover: per session, two reps (C)

- **Baseline:** one registry opening per rep.
- **One-open:** both reps' registry claims are batched into one opening with doubled queries, and its prover work is
  about the same as one opening's (E).

| K | T | baseline | one-open | baseline / 2.68 s | rows for ≤ 25% overhead |
|---|---|---|---|---|---|
| 2^16 | 1 | 0.008–0.023 s | 0.006–0.019 s | 0.003–0.008× | 2^20.6–2^22.1 |
| 2^16 | 16 | 0.034–0.090 s | 0.024–0.069 s | 0.013–0.034× | 2^22.7–2^24.1 |
| 2^20 | 1 | **0.17–0.51 s** | 0.14–0.38 s | **0.06–0.19×** | 2^25.0–2^26.6 |
| 2^20 | 16 | **0.78–2.06 s** | 0.62–1.39 s | **0.29–0.77×** | 2^27.2–2^28.6 |
| 2^24 | 1 | 3.4–10.0 s | 2.7–8.5 s | 1.3–3.7× | 2^29.4–2^30.9 |
| 2^24 | 16 | 16.4–41.6 s | 13.3–28.2 s | 6.1–15.5× | 2^31.6–2^33.0 |

- **The last column** is the session size, at 20 ns per row, at which the addition is 25% of the session. The Spark draft's
  are 2^23.6–2^25.2, 2^26.3–2^27.7 and 2^30.2–2^31.5 at T = 1.
- **Small sessions.** A session of at most 2^22 rows takes 84 ms (C). At K = 2^20 the addition is then 3.0–7.0× the session
  at T = 1 and 10–26× at T = 16 (C). Holography pays only where F2 batches many units per session.
- **Memory (C).** The sumcheck's tables are `D·K/2·16` bytes after round 1: 0.08 GB at K = 2^20, D = 9, and 5.1 GB at
  K = 2^24, D = 38 (about 8× less with three small-value rounds, E). P0 and R6 need O(K) more.

### 5.4 Proof size per session (C, from the M fit)

- **Messages besides the registry openings, two reps (C):** κ(D + 2) round coefficients, 128 P0 values, B_pad record
  values, D factor values, R7's rounds, and about 4 values per triple. That is 12–18 KB at K = 2^16, 16–31 KB at 2^20 and
  19–42 KB at 2^24.
- **One registry opening:** the Spark draft's fit to rec-holo §9.4's measured `--zk` openings, 0.42–0.64 MB at 2^27 bits
  plus 0.035 MB per doubling (C). By K and T:

  | K | T = 1 | T = 16 |
  |---|---|---|
  | 2^16 | 0.26–0.48 MB | 0.35–0.57 MB |
  | 2^20 | 0.41–0.66 MB | 0.49–0.74 MB |
  | 2^24 | 0.57–0.79 MB | 0.64–0.90 MB |

  At 160 rather than 218 level-0 queries this should come down by 15–25% (E).

| K | T = 1, two openings | T = 16, two openings | / 843 KB | one-open (≈ 1.4 × one opening, E) |
|---|---|---|---|---|
| 2^16 | +0.53–0.97 MB | +0.72–1.16 MB | 0.6–1.4× | +0.4–0.8 MB |
| 2^20 | **+0.84–1.34 MB** | **+1.01–1.51 MB** | **1.0–1.8×** | +0.6–1.0 MB |
| 2^24 | +1.16–1.60 MB | +1.32–1.84 MB | 1.4–2.2× | +0.8–1.3 MB |

The Spark draft adds 1.7–2.5 MB at K = 2^20 (four openings, two of them its per-rep E).

### 5.5 Verifier per session (E)

- **Added:** two registry openings, about +0.6–1.2 s in Rust and +10–21 s in Lean. That is scaled from the table's 1.2 s /
  21 s, which covers two openings plus the rest (M); the Spark draft's four openings come to +1.2–2.4 s and +20–42 s.
  - Everything else (P0's 128 values, κ rounds of degree ≤ 39, D + B_pad affine checks, lt rounds, and `M̂_pub`) is under
    1 ms in Rust and independent of K except through κ (E).
- **Saved:** the comb over the hidden nonzeros, K × 4.1 ns per rep single-threaded (C from M): 0.3 ms, 4.3 ms and 69 ms at
  the three bounds. The verifier no longer reads the matrix.
- **One-open:** +1 opening with doubled level-0 queries instead of +2 (E).

### 5.6 Registration (C)

- **Commit** `T·K·B_pad` bits at rate 1/4, at 0.18–0.31 ns per bit at rate 1/2 (M, rec-holo §4.1 and §9.4) × 2:

  | K | T = 1 | T = 16 |
  |---|---|---|
  | 2^20 | 0.04–0.12 s | 0.19–0.67 s |
  | 2^24 | 0.87–1.50 s | 3.9–13.3 s |

  Re-registration happens once per 38–205 sessions (§3).
- **The codeword** at rate 1/4 is 4·T·K·B_pad bits: 5.4–10.7 GB at K = 2^24, T = 16 (C).

## 6. What would kill it, and the cheapest experiment

**Kill criteria.**
1. **The wide chunks** (the only part that is not candidate 3) die if either:
   - F2's shapes typically have **T ≥ 8 types**: the gain over binary falls to 1.1–1.4×, and at T ≥ 16 the optimum is
     w = 1–2 (§5.2); or
   - a **degree-10 product-sumcheck kernel is not at least 2× cheaper per record than a degree-30 one**. The model
     assumes per-factor memory costs, so D = 9–10 is about 4× cheaper than D = 30. If the kernel is arithmetic-bound
     instead, the advantage shrinks to about the D² ratio of the tree, which still favors wide chunks. If small-value
     rounds make binary nearly free, it vanishes.

   In either case the design collapses to candidate 3, at no loss: the proof is the same, and w is pinned to 1.
2. **The family** (this design and candidate 3, and Spark too, through the same tax) costs more than the session at
   K = 2^24 with T = 16 unless sessions exceed 2^31.6–2^33 rows (C).
   - If F2's shapes land there, option 5 loses to option 4 or to registering per type (T = 1 per registry, with τ hidden
     some other way).
   - The tax is 3.1–13.4 s per opening at that shape (C).
3. **Lean.** If the guarantee must be stated per session as a standalone game rather than per registration (§4.4), H2 needs
   a cross-game plurality-agreement lemma. That is a risk shared by all candidates, not a kill.
4. **Semantics.** If a guarantee needs the registered matrix to have at most K entries (§2.4), w ≥ 2 needs a one-hotness
   proof at registration (about 0.4 s at 2^20, E) or w = 1. That is a cost, not a kill.

**The cheapest experiments** (none run, per the brief):
- **(a) Local, one core, about 2 hours.** On upstream's GF(2^128) multiplier, time the product-sumcheck kernel at D = 6, 10,
  17 and 30 over 2^16 records, with and without three small-value first rounds.
  - This decides kill 1 and narrows every number in §5.2.
  - It is the same kernel as candidate 3's at D = 2k + 1, so one experiment serves both, and the Spark draft's §6(a)
    proposes it as well.
- **(b) The same kernel, plus one `--zk` opening at 2^28 bits with k0 = 6 and with k0 = 10.** This says whether the
  hidden-type tax can be made per-type: types in extra level-0 lanes, at T-fold larger leaves. It decides how bad kill 2
  is for every candidate.
- **(c) Lean, half a day.** A skeleton of §4.4's registration-lifetime game: the registry slot as `Lock`'s first table node,
  A sessions in its continuation, and `leafE_off_le` instantiated with the lifetime Q. If `rep_sound`'s signature
  survives with the registry as a fixed `Oracle F`, H2 is settled for all three candidates.

## View against the other two candidates

- **Candidate 3 (bit-committed direct sumcheck)** is this design at w = 1. **Merge them** into one chunked eq-lookup:
  - one identity (L2), one degree-D sumcheck (L1), one phase lemma;
  - the chunk width is a public per-shape parameter chosen from T;
  - the generality costs about 100–150 Lean lines (E) and buys 2.0–3.2× at T ≤ 2 (C).
  - P0 (§1.4) is needed by candidate 3 too.
- **Spark-style memory checking** is dominated:
  - **Lean:** its specific part is about 2× larger (2,900–5,150 against 1,210–2,180 lines, E), and its riskiest lemma (E
    committed inside a rep) does not arise here.
  - **Soundness:** its fingerprint gives 2^-77 to 2^-92 per rep before repairs, against 2^-110 to 2^-113 here (C).
  - **Proof:** it adds 1.7–2.5 MB against 0.8–1.5 MB (C).
  - **Rounds:** 291–627 added per rep against 31–51.
  - **Prover:** this design is 2× cheaper at T = 1 and 1.15–1.26× dearer at T = 16, where the hidden-type tax that all
    three pay dominates.
  - Spark's only edge would be very large blocks (k ≥ 20) with T = 16, if no small-value optimization lands.
- **Shared work the coordinator should assign once**, whichever candidate wins:
  - the common frame H1–H7;
  - §4.4's registration-lifetime game;
  - the hidden-type tax experiment (§6b), which decides whether option 5 is viable at K = 2^24 with many types.
