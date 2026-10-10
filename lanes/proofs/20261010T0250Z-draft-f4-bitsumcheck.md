---
id: proofs/20261010T0250Z-draft-f4-bitsumcheck
campaign: flock
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: F4 design agent (bit-committed sumcheck), for the proofs coordinator bc-8416bc72
---

# F4 candidate 3: the direct sparse sumcheck, indices committed bit by bit

Front F4 of Daniel's reset (9 Oct, 7 PM PT) is option 5, holographic C-Flock. This note designs candidate 3: commit each
nonzero's row and column index as bits, plus its value bits, and prove
`M̂(x, y) = Σ_k val_k · eq(x, row_k) · eq(y, col_k)` by one sumcheck over the nonzeros `k`. Paths and declarations are
on `origin/main` at `dc67b1542`. Every cost number is marked M (measured), C (computed) or E (estimated). The local
computations behind the C numbers (a GF(2^16) toy of the whole phase, a multiplication counter, the cost and error
tables) are in the evidence store as `art:dc659142f1e5fc6ad5866fc36e2123997ae41178b701f35363c4f2ef077a2fa9`.

## Answer in short

- **The protocol.** Registration commits, per unit type, the hidden template as a binary table of `P = 2ℓ+2` bit planes
  over `n = 2^ν` slots (ℓ row bits, ℓ column bits, the A-side bit and the B-side bit, in the template's `2^ℓ`-slot
  coordinates). It uses C-Flock's own binary Ligerito commitment at rate 1/8, salted hm96-sha512 leaves.
  - Per rep, the lincheck keeps its shape. The prover sends the 64 folded hidden comb values `h` beside `z_partial`.
  - A 28-round sparse phase at ν = 20 (`ν + 8` in general) checks `h`: an eq check (6 coordinates), a 6-round row
    pre-sumcheck that absorbs the univariate skip's Lagrange weights, then one sumcheck of degree `d = 2ℓ+1` over the
    slots, then a plane batch.
  - It ends in one claim on the registered table. Both reps' claims are opened once per session, at the
    unique-decoding radius.
  - Booleanity is free (the PCS commits bits), padding is `a = b = 0`, and duplicates cancel exactly as in `Hidden.tmpl`.
- **Where it runs.** Primary deployment (B): inside the recursion, as the inner protocol that V* verifies, which is the
  reset's end goal. The type index is a V* witness that selects `root_τ` from the registration, so a session opens one
  type's table only. The native form (A, no V*) is the fallback; it needs masks, a re-registration budget and an
  `O(T)` opening for the hidden type.
- **Soundness.** It is statistical, and adds no premise.
  - The sparse phase adds `(6 + 12 + ν·d + log P')/|F|` per rep: `2^-118.7` at ν = 20, and `2^-111.0` if charged
    with C-Flock's list factor `L₀ = 200`. That moves the rep error by under 0.08 bit even with the list factor (C).
  - The registered opening is sized for `2^-205` by itself (251 level-0 queries at rate 1/8, C).
  - The guarantee is one new statement, `Flock.Guarantees.HoloInnerSound`: `InnerSound` of the holographic inner
    protocol. It plugs unchanged into the existing `Flock.Guarantees.RecursiveSound`.
- **Zero knowledge (B).** The registered root sits behind a firewall commitment, and every new message is a firewall-
  committed inner message. So `RecursiveZK` covers it with only its message count changed: no RegHides, no
  re-registration.
- **Lean.** 21 new lemma groups.
  - About 1,750–1,900 lines for `InnerSound`, of which about 850 are specific to this candidate.
  - Plus 800–1,500 lines of V* bridge work, shared by every option-5 candidate (F5's building blocks).
  - Riskiest specific lemma: D1, the lincheck hybrid (`comb'` correct or caught). Second: R2, the registered opening at
    the unique-decoding radius.
- **Cost at 2^20 nonzeros (C from M rates).**
  - Inner prover: +30–94 ms per session for both reps and the registered opening (29–90 ns per slot). That is 3–10×
    below Spark's measured-rate cost (0.26–0.31 s), and +34–107% of B_rep's 88 ms or +1–3.5% of the `--zk` prover's
    2.68 s.
  - Inner proof: +23 KiB plus one registered opening.
  - V*: +1.0–1.7e9 rows per session, against option 4's 2.4–3.4e10 (14–33×, C/E). Option 5 overtakes option 4 above
    about 2^15–2^16 nonzeros per session.
- **Kill criterion.** K1: the degree-d product kernel runs near the naive kernel's 2–3.4 ns per multiplication, which
  puts the slot sumcheck above 150 ns per slot per rep at ν = 20. Test it with a single-file micro-kernel over
  `opcount.py`'s matrix, without a pod. Run since: it does not fire (278 ns per slot per rep on one local thread, 75 on
  four, M; about 10–16 on the pod's 32, E; "K1 result").
- **Recommendation.** Candidate 3. Spark is dominated on Lean, prover, proof size and rounds (it has 291–627 live coin
  rounds per rep against 24–32). The lookup candidate collapses to Spark in characteristic 2. Fall back to Spark only
  if K1 fires.

## Where I disagree

- **rec-holo §4.4, the variant without `E`.** rec-holo prices the version without committed `E` vectors at 760–1,000 ns
  per nonzero, assuming eq is computed by a product tree (2ℓ GKR cells per nonzero).
  - The direct sumcheck doesn't build that tree. Its per-round cost is the square of the number of factors that vary
    across a pair of slots, and in a sorted table most don't.
  - Counted on a synthetic template (`opcount.py`, C): 74–163 multiplications per slot per rep at ν = 20, and 21–75 ns
    per slot for two reps.
- **The Spark draft's price for this candidate** (`note:proofs/20261010T0250Z-draft-f4-spark` §6). It prices it at
  `2·(2k+1)²` multiplications per nonzero per rep (1,058 / 1,922 / 3,042). The count above is 11–24× lower at ν = 20
  (79–173 per real nonzero at fill 0.94), so its "within 1.5× of Spark" turns into "3–10× below Spark".
- **rec-holo §9.4, "same circuit" from binding.** Binding fixes the committed word, not one polynomial.
  - At C-Flock's Johnson radius, a word can lie within the radius of two codewords whose distance is at most
    `2(1 − √ρ − η)` (0.58 at rate 1/2), and the minimum distance (0.5) allows that. Each opening then certifies a claim
    about *some* list member, possibly a different one per opening.
  - Nothing in the soundness proof rules out a registrant whose sessions use two different matrices, with no SHA-512
    collision.
  - The registered table's opening (and route P's `com_σ` and its re-registration check) must run at the
    unique-decoding radius `(1 − ρ)/2`, where the list has one member (R1, a triangle-inequality lemma). That costs
    queries only: at rate 1/8, 251 level-0 queries reach `2^-205`, against 218 at rate 1/2 for C-Flock's `2^-107` (C).
- **rec-holo §3.3, RegHides.** In deployment B the registered openings appear only in V*'s witness, which only the
  trusted ZK server sees. The hiding of the registered commitment is then just the root's hiding: one more firewall
  leaf under `RecursiveZK`, or statistically by `note:proofs/20261009T1940Z-report-salted-hiding-reduction`. No
  opening budget, no re-registration. RegHides stays needed in deployment A.
- **rec-holo §5, "V* is gone".** That holds for the native holographic deployment, which here is the fallback. The
  reset's end goal is sampled proofs *through recursion*, with V* built per shape by `VStar.statements`. In that setting
  option 5 keeps V*, `InnerSound` and VBridge, and removes what grows with the template: `HiddenComb` and the in-circuit
  reads of the template's rows.
- **The brief's "booleanity enforced".** Nothing to enforce: C-Flock's PCS commits GF(2) tables, so every committed value
  is a bit by construction. What would need care, a value field wider than one bit, doesn't occur: values are bits
  (`HEntry.val : ZMod 2`).
- **Agreements.** I agree with rec-holo §3.4 and §4.5(a) that route P stays cheaper for a circuit with no repetition.
  - At 32–66 nonzeros per AND, this candidate costs 0.9–5.9 µs per AND (C), against route P's 335–388 ns.
  - It narrows Spark's 400–1,000× over B_free to about 30–740×, which isn't enough.
  - Candidate 3 is for the end goal's repeated templates, where its cost is per template, not per copy.

## 1. The protocol, fitted to C-Flock over GF(2^128)

### 1.1 Setting

- C-Flock proves `A·z ∘ B·z = z` over GF(2), with `A = I ⊗ A₀` (copies) and `F = GF(2^128)`, `K = GF(2^256)` (folds).
  - The zerocheck's univariate skip on the low 6 bits gives the row weights `e[s + 64u] = L_s(z)·eq(ρ_in, u)`.
  - The lincheck (`Model/Piop.lean`, `lincheck`, L1–L5) has α, β, then `k_log − 6` rounds over the top column bits
    with challenges `t`. The verifier itself computes `folded = foldAll t (comb A S z α β ρ_in)`, 64 values, and checks
    `Σ_s folded[s]·z_partial[s] = claim`.
  - `comb[c] = Σ_i e[i]·(αA₀[i,c] + B₀[i,c]) + β·[c = pin]` is the only place the matrix enters.
- The hidden statement is already modeled on main (`Proofs/Flock/Recursive/Target.lean`).
  - `HClass` publishes `m`, `k_log`, the pin, the public part of `A₀` and `B₀`, the template's slot size `2^slotLog`, the
    unit slots it fills, and `nnz`.
  - `Hidden cls = Fin nnz → HEntry` lists entries `(side, row, col, val)` in slot coordinates. `Hidden.side` adds the
    template to the public part on every unit slot, and `Hidden.tmpl` sums the values at `(i, c)` in `ZMod 2`.
  - `flockInner` is the inner protocol over this class: statement `Hidden cls`, the verifier `Model.table` reading `M`
    whole. `flock_inner_sound` proves `InnerSound` at `tableError` (≤ 2^-205 for 22 ≤ m ≤ 33).
- Notation here: `ℓ = slotLog` (≥ 6, refused otherwise), `n = 2^ν ≥ nnz` slots, `d = 2ℓ + 1`, `P = 2ℓ + 2` planes, and
  `P' = 2^⌈log₂ P⌉`. In the counts `ℓ = ν − 5` (about 30 nonzeros per template row): ν 16/20/24 gives ℓ 11/15/19,
  d 23/31/39, and P' 32/32/64.

### 1.2 Registration (once per type)

- **The table.** The registrant writes type t's template as `R_t ∈ GF(2)^{P' × n}`. Slot `k` holds `row_k` (ℓ bits),
  `col_k` (ℓ bits), `a_k = [side = A]·val`, `b_k = [side = B]·val`, and zero pad planes.
  - Unused slots are `a = b = 0`.
  - The slot order is free (soundness never reads it). Sorted Morton order makes the prover cheapest (§5.1).
- **The matrices it defines.** `tmpl_A(R)[i, c] = Σ_{k: row_k = i, col_k = c} a_k` in GF(2), likewise B.
  - Every bit table defines a matrix, so there is nothing to validate.
  - Duplicates cancel and padding vanishes, exactly as `Hidden.tmpl` does.
- **The commitment.** C-Flock's binary table commitment (ring switching over the low 7 bits, Ligerito), with slot bits
  low so that a registered claim has C-Flock's `(value, skip ∈ F^64, x)` format.
  - Rate `ρ_reg = 1/8`: registration is paid once, and a low rate buys a large unique-decoding radius (§1.4).
  - Salted hm96-sha512 leaves; the root is `root_t`.
- **Several types.** With `T` types (T padded to a power of two, all of one shape `(ℓ, ν)`), the registration digest is
  the Merkle root over `root_0 … root_{T−1}`. In deployment B, the registration `R` of `recGame` carries this digest
  behind a firewall commitment.

### 1.3 One rep (after the zerocheck, unchanged)

| step | prover sends | verifier draws / checks | error |
|---|---|---|---|
| L1–L3 | as today | α, β, the `k_log − 6` column rounds `t` | as today |
| L4′ | `z_partial ∈ F^64` and `h ∈ F^64`, the hidden part of `comb` folded at `t` | computes `folded = fold_t(comb_pub) + h + β·fold_t([·= pin])`, checks `Σ_s folded[s]·z_partial[s] = claim` | as today |
| L5 | | `r'`, the `ab` claim, as today | as today |
| H1 | | `ζ_c ∈ F^6`; target `Σ_s eq(ζ_c, s)·h[s]`, which must equal `Σ_i e[i]·M̂_hid(i, y)` at `y = (ζ_c, t)` | 6/\|F\| |
| H2 | 6 degree-2 round polynomials, then `v₂` | rounds over the 6 low row bits of `Σ_s ŵ(s)·V(s)`, with `ŵ` the multilinear extension of `s ↦ L_s(z)` and `V(s) = Σ_u eq(ρ_in, u)·M̂_hid((s, u), y)`; ends at `ζ_r` with the check `claim = ŵ(ζ_r)·v₂` (`ŵ(ζ_r) = Σ_s eq(ζ_r, s)·L_s(z)`: 64 eq values, 64 products) | 12/\|F\| |
| H3 | per round `c₀, c₂, …, c_d` (`c₁ = claim + Σ_{i≥2} c_i`, characteristic 2) | ν rounds of `Σ_{k ∈ {0,1}^ν} U·Φ(R̂_τ(·, k)) = v₂`, where `x = (ζ_r, ρ_in)`, `U = Σ_{u ∈ units} eq(x_hi, u)·eq(y_hi, u)` (public) and `Φ(u) = (α·u_a + u_b) · ∏_{j<ℓ} (1 + x_j + u_{r,j}) · ∏_{j<ℓ} (1 + y_j + u_{c,j})` | ν·d/\|F\| |
| H4 | `u ∈ F^{P'}`, `u_p = R̂_τ(p, r_k)` | checks `U·Φ(u) = claim`; draws `ζ_p ∈ F^{log P'}`; the registered claim is `Σ_p eq(ζ_p, p)·u_p = R̂_τ(ζ_p, r_k)` | log P'/\|F\| |

Why it is complete, in four identities, each a lemma of §4:
- In characteristic 2, `eq(x, b) = ∏_j (1 + x_j + b_j)` on bits (A1, `eqAt_bool`'s neighbour).
- `M̂_hid(x, y) = U(x_hi, y_hi) · Σ_k (α a_k + b_k) · eq(x_lo, row_k) · eq(y_lo, col_k)` (A2).
- A multilinear `R̂` agrees with `R` on the Boolean cube, so the cube sum of `Φ(R̂(·, k))` is the slot sum (A3).
- `Σ_s eq(ζ_c, s)·fold_t(comb_hid)[s] = Σ_i e[i]·M̂_hid(i, (ζ_c, t))` (A4).

The toy (`toy.py`, GF(2^16), ℓ = 8, ν = 11, 4 types) checks the identity and accepts every honest session of every type,
with the degree bound asserted each round (M, toy).

Per rep this adds `ν + 8` coin rounds (24 / 28 / 32), and these messages: 64 + 13 + ν·d + P' field elements.

### 1.4 Once per session: the registered opening

- **What is opened.** Both reps' registered claims are on the same table `R_τ`. The existing opening phase
  (`opening_phase_of_card`, which batches several claims at several points) opens them together, once per session.
- **Unique decoding.** Level 0 is the registered word, at the unique-decoding radius `δ = (1 − ρ_reg)/2 − η` with list
  bound 1. Later levels are fresh per-session commitments at C-Flock's Johnson radius, as today.
- **Sizing.** The opening is not repeated per rep, so its query terms must reach the session target alone: 251 level-0
  queries at rate 1/8, and the later levels' query counts doubled (C, `extra.py`). The same number of hashed queries
  would come from one opening per rep at per-rep sizing.
- **Batching across sessions.** In B, all of an outer proof's sessions of type τ can batch into one registered
  opening, with more claims per opening. That makes it T openings per outer proof instead of one per session (E: same
  lemma, bigger `nClaims`).

### 1.5 The hidden type index

- **Deployment B.** `τ` is part of the hidden statement. F2's coverage proof binds each session's slot to its committed
  type.
  - V* reads `root_τ` with a Merkle read over the T sub-roots (`log T` levels, about 1e6 rows at T = 128, E) and checks
    the registered opening against it. The position read stays in V*'s witness.
  - A session opens `P'·n` bits of one type, never every type, which is the reset's "evaluates one matrix padded to its
    shape's nonzero bound".
- **Deployment A.** The verifier can't select a root it may not see.
  - The session table carries τ's `log T` bits (one more claim).
  - A t-sumcheck `Σ_t eq(τ, t)·R̂(ζ_p, r_k, t)` (log T rounds, degree 2) ends at `eq(τ, r_t)·w_R`, with `w_R` one claim
    on the stacked registration of all T tables.
  - The opening then costs `O(T·P'·n)`, masked (§3).

### 1.6 Variants

- **Fixed-width rows.** Give each template row `W = 64` slots, so the row is the slot's high bits and is not committed.
  - That leaves `ℓ + 2` planes, and degree `ℓ + 2` ("about log n" exactly), which halves the sumcheck's proof and error.
  - Fill is about 0.47, so per real nonzero it costs the same: 101 vs 104 multiplications at ℓ = 11 uniform, 58 vs 53
    wide (C, `opcount_rows.py`).
  - It needs `W` as a public shape parameter, and the compiler must split rows of more than W nonzeros. Worth keeping as
    the second shape if the proof-size or round-degree budget binds.
- **B′: open the registered table natively in the outer session.** Registering `R_τ` as an outer-session registered
  table would save V* the registered opening's hashing. But it brings back deployment A's hidden-type problem and
  RegHides, so not recommended.

## 2. Soundness

### 2.1 The statement

C-Flock's spec still lives in the proofs package, so its guarantees are stated in `Proofs/Flock/Recursive/Statements.lean`
(trusted) and proved in `Proofs/Flock/Recursive/Guarantees.lean`, not under `Models/` (whose `Models/Flock/Guarantees`
holds only the audit law today). The new statement sits beside `RecursiveSound`, in its form:

```lean
namespace Flock.Guarantees

/-- **The holographic inner protocol is sound over the class.** Its statement is a registered word `w` (level 0 of the
registered schedule `rsch`, at the unique-decoding radius) of a template's bit table (`RegTable cls`: row bits, column
bits, the A and B bits, in slot coordinates). It holds when `w` decodes within that radius to a table whose block
statement (`RegTable.toStatement`: the class's public part plus the table's matrices on the unit slots, the class's
`m`, `k_log`, pin and regions) has a satisfying witness. On the schedule `(T, CT)` with live coins, every prover makes
the inner verifier accept a statement that does not hold with probability at most `holoError`. Statistical: no
assumption. -/
def HoloInnerSound : Prop :=
  ∀ {F K : Type} [Field F] [Fintype F] [DecidableEq F] [CharP F 2] [Field K] [Fintype K] [DecidableEq K]
    {nT r : ℕ} (T : Fin nT → Type) (CT : Fin r → Type) [∀ k, Fintype (CT k)] [∀ k, Nonempty (CT k)]
    (A : Arith F K) (_hA : A.Correct) (cls : HoloClass) (regs : List (Region cls.kLog (cls.m - cls.kLog)))
    (sch : Schedule) (_hsch : fast100 cls.m = some sch) (rsch : RegSchedule cls) (_hud : rsch.UniqueDecoding)
    (_hlay : ∀ R : RegTable cls, (R.toStatement regs).LinkLayout cls.ptLocal cls.mPts),
    InnerSound (holoInner T CT A cls regs sch rsch) (ENNReal.ofReal (holoError sch rsch cls regs))

/-- **The registered word names one template**: within the unique-decoding radius, two tables that `w` decodes to are
equal. With `HoloInnerSound`, every session and every audit on one registration proves the same circuit. -/
def RegDecodesUnique : Prop :=
  ∀ (cls : HoloClass) (rsch : RegSchedule cls), rsch.UniqueDecoding →
    ∀ w (R R' : RegTable cls), rsch.Close w R → rsch.Close w R' → R = R'

end Flock.Guarantees
```

- **The auditor's statement.** It needs no new form. It is `RecursiveSound` at `I := holoInner …` and
  `εin := holoError …`, with `x R ω` the registered word that the registration's (firewall-committed) root opens to,
  and `hin := SecurityProofs.HoloInnerSound …`.
- **What a statement holds of.** `holds w` is about the decoded template, a function of the registration alone. So the
  circuit that every session proves is fixed when `R` is, and `RegDecodesUnique` says that phrase is well defined.
- **`HoloClass`.** It is `HClass` with `6 ≤ slotLog`, `ν` (`nnz = 2^ν`) and `T`. The verifier refuses any other form.

### 2.2 Error terms (C)

Per rep, added to `piopError` (`Accounting/Bound.lean`):

| term | coin | count | ν 16 | ν 20 | ν 24 |
|---|---|---|---|---|---|
| H1 eq validation | `ζ_c` | 6 (`prCoin_eqSum_le`) | 6 | 6 | 6 |
| H2 row pre-sumcheck | `ζ_r` | 6 rounds × 2 | 12 | 12 | 12 |
| H3 slot sumcheck | `r_k` | ν rounds × d | 368 | 620 | 936 |
| H4 plane batch | `ζ_p` | log P' | 5 | 5 | 6 |
| **sum, /\|F\|** | | | **391 = 2^-119.4** | **643 = 2^-118.7** | **960 = 2^-118.1** |
| charged like `piopError`, × L₀ = 200 | | | 2^-111.7 | 2^-111.0 | 2^-110.4 |

- **The case split.** The sparse phase's bad event (`h` wrong yet every check passes) doesn't depend on the session's
  list element, so D1 can charge it once. If the hybrid is easier inside the list union, the `× L₀` row is the price.
  - The rep error is today at most `2^-102.5` (its square is `tableError ≤ 2^-205`), and at least level 0's own query
    term, `2^-106.8` at 218 queries.
  - So the sparse term moves it by under 0.001 bit charged once, and by under 0.08 bit charged with `L₀` (C).
- **The session error.**
  `ε_session ≤ linkError + (repError + ε_sparse)² + regError`.
  - `regError` is the registered opening's: list bound 1 at level 0; MCA and fold terms over GF(2^256) far below
    2^-205; the query terms sized to `2^-205` (§1.4).
  - That gives about `2^-204` per session (C), against today's `2^-205`.
- **The bound is tight.** In the toy's rate test (GF(2^10), ν = 11, d = 17), a liar who plants roots in every round
  passed 65 of 400 times (0.163, M toy). The prediction `1 − (1 − d/|F|)^ν` is 0.168, and the union bound 0.183.
  Against the full chain, the adaptive liar (wrong `h`, every later check kept passing by solving for the next
  message) got 0 of 60 accepted, all rejected at the registered opening (M, toy).

### 2.3 Premises

- **None new.**
  - `HoloInnerSound` is statistical, like `flock_inner_sound`.
  - Unique decoding is a parameter (rate, queries) plus R1, an elementary distance lemma. The Johnson-range MCA
    theorem `prCoin_mca_le` (`LigeritoMCA.lean`) already covers every radius below Johnson's, so δ_UD is in range.
- **B's composition.** It takes exactly `RecursiveSound`'s hypotheses:
  - the VBridge obligation, discharged by F5's `VStar.statements` (the holographic sub-verifier is new V* code, §4);
  - `cr/sha-512` for the fork finders;
  - A3 (`uniform/os-random`) for V*'s laws;
  - the `live-verifier` record custody;
  - the coin server's randomness for the live inner coins.
- **A.** It adds `cr/sha-512` for the registered tree across sessions (two sessions' openings of one root either agree
  or give a collision: `Registered/Binding.lean`, `TwoOpenings.collides`) and record custody of the registration.
- **Semantics flag (rec-holo §5, §9.5).** The guarantee says the outputs satisfy the registered constraint system. Under-
  determined templates are possible, as with every option, and per-unit acyclicity stays a separate check.

## 3. Zero knowledge

- **Deployment B (primary).** The auditor sees only these:
  - the padded shape `(ℓ, ν, P', T, rsch)`, which fixes V*;
  - session counts per shape;
  - the firewall's commitments to the registration digest and to every inner message (their number and sizes are
    functions of the shape);
  - the outer V* session;
  - the public outputs.

  The matrix, the type index and the nonzero count appear only in V*'s witness, behind the trusted ZK server.
  - `Flock.Guarantees.RecursiveZK` is already generic in the inner messages (`msgs`, `nh`), so it applies with `nh`
    increased by the sparse phase's messages and the registered root. Its bound `ε_o + n_h·2^-193` grows by about 70
    terms of `2^-193`.
  - Circuit privacy follows because the simulator reads public inputs only, and the registered word is not one of them.
  - If the registered root is shown in the clear rather than behind a firewall leaf, its hiding is the salted leaves'
    statistical hiding (`CROnly/Hiding.lean`, `hm96Hiding_gap`;
    `note:proofs/20261009T1940Z-report-salted-hiding-reduction`).
  - No RegHides and no opening budget: no auditor ever sees a registered column.
- **Deployment A (fallback).** Every new message becomes a masked unknown with an OS-drawn pad, as in M1.
  - New hidden products: 2ℓ triples for Φ's product, 64 for `Σ folded·z_partial` once `h` is masked, and `log T` plus
    one cross-table triple `eq(τ, r_t)·w_R` for the hidden type.
  - The cross-table triple breaks `session_shvzk`'s product decomposition (`ZK/Session.lean`), which simulates per
    table.
  - The registered opening reveals level-0 columns every session, so it needs padding for A audits (the
    `padded_openings_uniform` pattern, `ZK/Masking.lean`), RegHides(A) and re-registration with an equality check at
    the unique-decoding radius (§ "Where I disagree", on §9.4).

## 4. Lean proof complexity

All new modules sit under `Proofs/Flock/` (C-Flock's analysis is all there for now), with the trusted statements beside
`Recursive/Statements.lean`. Line counts are E, calibrated on the modules they copy: `RepSound.lean` is 231 lines,
`LincheckPhase.lean` 599, `Model/Piop.lean` 162, `Recursive/Target.lean` 264, `Accounting/Padded.lean` and
`PaddedNumbers.lean` are the precedent for a level 0 with its own radius.

| id | new | builds on (module · declaration) | lines |
|---|---|---|---|
| S1 | `HoloClass`, `RegTable` (planes), `RegTable.tmpl`/`side`/`toStatement`, `RegSchedule` with `Close` and `UniqueDecoding`, `holoInner` | `Recursive/Target.lean` · `HClass`, `Hidden.tmpl`, `Hidden.side`, `toStatement`, `flockInner`; `Recursive/Schedule.lean` · `schedInner` | 90 |
| S2 | `HoloInnerSound`, `RegDecodesUnique`, their lean-audit entries | `Recursive/Statements.lean` · `RecursiveSound`'s form | 40 |
| M1 | the model: `holoLincheck` (L4′), `sparsePhase` (H1–H4), `holoTable` (two reps, then the registered opening) | `Model/Piop.lean` · `lincheck`, `comb`, `foldAll`; `Model/Session.lean` · `table`; `Model/Ligerito.lean` | 180 |
| A1 | `eqAt_bits`: `eq(x, b) = ∏ (1 + x_j + b_j)` on a bit vector | `OpeningPhase.lean` · `eqAt_bool`; `Level3/Fold.lean` · `eqAt_split` | 25 |
| A2 | `side_mle`: `M̂_hid = U · Σ_k val_k eq eq` | `ZerocheckPhase.lean` · `sum_eqAt`; `LincheckPhase.lean` · `eqAt_split_at`, `val_cast_eq` | 70 |
| A3 | `phi_cube_sum`: the cube sum of `Φ(R̂(·, k))` is the slot sum | `LigeritoMCA.lean` · `foldAllRows_eq_sum` | 40 |
| A4 | `comb_split`: `fold_t(comb) = fold_t(comb_pub) + fold_t(comb_hid) + β·pin`, and H1's identity | `LincheckPhase.lean` · `combSum_eq`, `foldAll_eq_sum`, `claim_eval_split`; `Composed/Inner/Lincheck.lean` · `foldAll_concat` | 70 |
| — | H1 and H4's coins | `OpeningPhase.lean` · `prCoin_eqSum_le` (existing) | 0 |
| C1 | `prodRoundPoly`: degree ≤ D, evaluation, sum rule in characteristic 2 | `LincheckPhase.lean` · `roundPoly`, `roundPoly_natDegree_le`, `roundPoly_eval`, `roundPoly_sum` | 100 |
| C2 | `degRound_sound` at degree D | `Rounds.lean` · `sumRound_sound`; `Core/Game/Poly.lean` · `prCoin_eval_eq_eval_le` (any degree) | 30 |
| C3 | `value_degRounds_le`: ν rounds of degree D | `LincheckPhase.lean` · `value_lincheckRounds_le`, `lincheckRounds_succ` | 110 |
| C4 | H2, the row pre-sumcheck | `LincheckPhase.lean` · `value_lincheckRounds_le` (degree 2) | 20 |
| C5 | H4's final product and the plane batch | `OpeningPhase.lean` · `prCoin_eqSum_le`, `eqAt_split` | 50 |
| D1 | `lincheck_phase_holo`: `h` correct (then today's lincheck) or wrong (then the sparse phase catches it) | `LincheckPhase.lean` · `lincheck_phase_of_card`, `abEval_eq`, `value_lincheck_le` | 220 |
| D2 | `sparse_phase`: H1 to H4 to the registered claim, errors summed | C1–C5, A1–A4 | 120 |
| D3 | `rep_sound_holo` | `RepSound.lean` · `rep_sound`, `opening_phase`, `ligerito_phase` | 150 |
| D4 | `table_value_sound_holo`: link, two reps, the registered opening | `Soundness.lean` · `table_value_sound`; `SessionBatch.lean` · `sessionB` | 120 |
| R1 | `closeMsgs_card_le_one` below `(1 − ρ)/2` | `ListSize.lean` · `closeMsgs_card_le`; `Defs.lean` · `closeMsgs` | 80 |
| R2 | the registered opening at the unique-decoding radius: level 0 with list bound 1, its accounting | `OpeningPhase.lean` · `opening_phase_of_card`; `LigeritoMCA.lean` · `prCoin_mca_le`; `Accounting/Padded.lean` · `padRadius`, `padQueryError`; `Discharge/ZkSession/Table.lean` · `rep_sound_pad_zk` | 150–300 |
| R4 | `holo_inner_sound` (and `_fast100` with the numbers) | `Recursive/Schedule.lean` · `sched_sound`; `Recursive/Target.lean` · `flock_inner_sound` | 40 |
| N | `holoError` and its numbers | `Accounting/Bound.lean` · `piopError`, `tableError`; `Accounting/Fast100.lean` | 60 |
| V | V*'s holographic sub-verifier and its bridge | F5's blocks (field multiplies, degree-d sumcheck rounds, Merkle paths, hm96 rows); `Assumptions/Recursive.lean` · `VBridge` | 800–1,500 |

- **Totals.** 21 new groups (S1–S2, M1, A1–A4, C1–C5, D1–D4, R1, R2, R4, N, V).
  - `InnerSound`'s part is about 1,750–1,900 lines (2,550–3,400 with V).
  - The part specific to this candidate (A1–A4, C1–C5, D1–D2) is about 850.
  - V is shared with any option-5 candidate and is mostly F5's work.
- **What B doesn't need.** No cross-session extraction lemma: the registered word is part of `x R ω`, so every session
  of an audit reads the same word by construction. Its binding inside V* is the registered-reads machinery that already
  serves the hidden rows (`Recursive/Flock.lean`, `ZkOuter.rd`; `qR²/2^513`).
- **The riskiest specific lemma is D1.** The mathematics is a two-case split. The risk is plumbing: `lincheck_phase_of_card`
  and `RepDoomed` are stated for a verifier that computes `comb` itself, and the hybrid must thread the prover's `h`
  through the `Game` without changing the downstream phase signatures.
  - The cheapest test: a sorry-skeleton of `holoLincheck` and D1's statement. If `opening_phase` and `ligerito_phase`
    take its output claim unchanged, D1 is 200 lines; if `RepDoomed` must change, add about 300.
- **Second risk: R2.** `Level.radius` reads the global `eta` and the Johnson form. `Accounting/Padded.lean` shows a
  level 0 with its own radius, list bound and query term, and `rep_sound_pad_zk` shows a rep proved over it. R2 follows
  that route, and the risk is how many `.radius` sites (12 files) the proof touches.
- **Deployment A adds about 1,100–1,500 lines:**
  - R3 `reg_extract_consistent` (sessions' extracted registered words agree, or a collision, lifting `TwoOpenings.collides`),
    about 300. It would be the riskiest lemma overall, and it is shared by all three candidates in A.
  - the t-sumcheck and τ's claim, about 160;
  - the masking extension and the cross-table triple in `session_shvzk`, RegHides(A), 400–600;
  - the native verifier's refinement in place of V.

## 5. Cost

Inputs (M, rec-holo §4.1, vy-nebius-2, 32 threads):
- GF(2^128) multiply: 0.14–0.23 ns;
- opening: 0.26–0.47 ns per committed bit;
- commit: 0.31 ns per bit;
- B_rep: 0.66 ns per row (88 ms at m 27);
- the CPU `--zk` prover: 20 ns per row (2.68 s at the same shape).

The multiplication counts are C from `opcount.py`: a template of `2^(ν−5)` rows with 20–40 nonzeros each, padded to
`2^ν` slots. A round costs, per pair of slots, `c² + (P − c) + c`, where `c` is the number of factors whose bits differ
across the pair's block. The count omits the constant's scaling (≤ +10%).

### 5.1 Prover, per session

| | ν 16 | ν 20 | ν 24 |
|---|---|---|---|
| multiplications per slot per rep, wide-Morton / uniform columns (C) | 50 / 98 | 74 / 163 | 102 / 245 |
| mean varying factors `c` in rounds 1–3, uniform (C) | 4.7, 8.8, 11.0 | 6.5, 12.0, 14.6 | 8.4, 15.3, 18.4 |
| slot sumcheck, two reps (C) | 0.9–2.9 ms | 22–79 ms | 0.48–1.89 s |
| registered opening, `P'·n` bits once (C) | 2 Mbit: 0.5–1.0 ms | 32 Mbit: 8.7–16 ms | 1,024 Mbit: 0.28–0.50 s |
| **total added** (C) | **1–4 ms** (20–60 ns/slot) | **30–94 ms** (29–90 ns/slot) | **0.65–2.4 s** (39–143 ns/slot) |
| Spark at rec-holo §4.4's 245–295 ns/nonzero (C) | 16–19 ms | 257–309 ms | 4.1–4.9 s |
| Spark draft's own price (its §5.2) | | +0.42–1.12 s | |
| registration commit per type, rate 1/8 (C/E) | ~3 ms | ~40 ms | ~1.3 s |
| prover memory after round 1 / after round 3 with small values (C/E) | 12 MB / 3 MB | 0.25 / 0.06 GiB | 5.0 / 1.25 GiB |

- **Against C-Flock's own session.** At 2^20 the addition is +34–107% of B_rep's 88 ms, or +1–3.5% of the `--zk`
  prover's 2.68 s (C).
- **Against rec-holo's Spark formula.** That is `2 × (300 ns·nnz + 30 ms)`: 0.10 / 0.69 / 10.1 s (C).
- **Uniform columns are the worst case.** A real template's columns are local (copies between neighbouring rows),
  which `opcount.py`'s `local` and `wide` models put at 0.5–0.75× the uniform count.

### 5.2 Proof size

- **Inner proof, per session (C).** Sumcheck 11.5 / 19.4 / 29.2 KiB, plus the other messages (`h`, H2, `u`) at
  3.4 / 3.4 / 4.4 KiB, plus one registered opening. That opening is 0.4–1.2 MB (E), sized like a table opening with
  doubled later-level queries.
- **Deployment B.** The inner proof is V*'s witness; the auditor sees the outer proof. That grows polylogarithmically
  with V*'s rows, by at most about one table proof (0.4–1 MB, E).
- **Deployment A.** The auditor's proof grows by the inner figures plus masking pads (E).
- **Against Spark.** Its draft adds the openings of two `E` vectors, timestamps and four GKRs: +1.7–2.5 MB at 2^20.

### 5.3 Verifier

- **The sparse phase's algebra (C).** 1,202 / 1,722 / 2,498 GF(2^128) multiplications per session (two reps), plus the
  registered opening.
  - Natively (A) that is 5–10 µs at 4 ns per multiplication (single thread, M rate).
  - The opening is 7.8 ms upstream (M, rec-holo §4.1) to about 1 s under `--zk` (E, rec-holo §4.6).
- **In V* (B), rows per session (E/C):**
  - registered opening's hashing: about 1.0–1.7e9 (E). Level 0's 251 queries plus the later levels' queries doubled
    make about 0.6–1.0× the hashed queries of the inner table's two reps, priced at rec-holo §5's 1.7e9 rows per session
    for those.
  - algebra: 1,722 × 2,187 ANDs (Karatsuba 3^7) = 3.8e6 (C);
  - firewall commitments to about 70 more inner messages: 1e7 (C, at 142,282 rows per hm96 leaf);
  - root_τ read: about 1e6 (E).
- **Total and its proving cost.** About 1.0–1.7e9 V* rows, independent of the template's size. That is +0.7 s at
  B_rep's rate to +34 s at the `--zk` rate of outer proving per session (E).
  - Against V*'s existing 2.7–3.2e9 rows per inner table (rec-v0 §S5, via rec-holo §4.5), it is +31–63%.
  - Batching a type's sessions into one registered opening per outer proof (§1.4) amortizes it.
- **Rounds.** 24 / 28 / 32 live coin rounds per rep (C), run in lockstep across the reps, plus the opening's. Spark's
  draft has 291 / 443 / 627.

### 5.4 Against option 4 (F3: V* reads the template as data)

| nonzeros per session | 2^16 | 2^20 | 2^24 |
|---|---|---|---|
| option 4, 23K ANDs per nonzero (the RoPE fold alone, reset), 1.0–1.4 rows per AND (C) | 1.5–2.1e9 | 2.4–3.4e10 | 3.9–5.4e11 |
| option 5, this design (E) | 1.0–1.7e9 | 1.0–1.7e9 | 1.0–1.7e9 |
| ratio (C/E) | 0.9–2.1× | 14–33× | 225–530× |

- **Where option 5 starts winning.** Break-even is about 2^15–2^16 nonzeros per session (C/E). Option 4's in-circuit
  row reads (1.6M ANDs per hm96 row, reset) only lower it.
- **Small shapes.** A shape menu that is mostly below 2^16 nonzeros would favour option 4 there.

## 6. What would kill it, and the cheapest experiment

- **K1, specific to this candidate: the product kernel.**
  - The C numbers assume the round kernel runs near the multiplier's 0.14–0.23 ns throughput (M). rec-holo's naive
    degree-3 sumcheck kernel ran at 31–58 ns per term (M), about 2–3.4 ns per multiplication in this model.
  - At that efficiency the slot sumcheck is 0.33–1.1 µs per slot for two reps at ν = 20, which is worse than Spark.
  - **Kill line:** above 150 ns per slot per rep at ν = 20, or two reps at ν = 24 at or above Spark's 4.1 s.
  - **Cheapest experiment** (local, one file, no pod; run since, see "K1 result"): a Rust or C kernel of the
    per-pair coefficient-form product (c varying affine factors times a constant product), on upstream's GF(2^128)
    multiplier, over `opcount.py`'s uniform template at ν = 20, at 1 and 32 threads. Then compare ns per slot with the
    C column of §5.1. A 2× margin either way is decisive.
- **K2, for all of option 5: small shapes.** If F6's shape menu puts most sessions below about 2^16 nonzeros, the extra
  registered opening in V* costs as much as option 4 (§5.4).
  - **Experiment:** count V*'s rows for one registered opening at the menu's shapes with `VStar.statements`' existing
    Ligerito-verifier builder, against `23K × nnz`. It is a row count, not a run.
- **K3, Lean: D1's signature change.** If the hybrid forces `RepDoomed` and the four phase lemmas' signatures to change,
  candidate 3's specific part roughly doubles (+300 lines). It would still be below Spark, whose S3 (an oracle in the
  middle of a rep) has the same problem and more.
  - **Experiment:** the D1 sorry-skeleton (§4), half a day.
- **Not a killer: unique decoding.** It is needed by every option-5 candidate (Spark's draft reaches the same conclusion
  for `E` and `com_s`), and costs queries only.

## K1 result

Run on the proofs coordinator's VM, no pod. The kernel, its driver and its output are
`art:1f10f57cfc19a1f2248f0c931a56d3d5a377c6fa2e1e132446e85c98aa8fabcd`.

- **Verdict: K1 does not fire.** At ν = 20 (ℓ = 15, d = 31, uniform columns) the slot sumcheck takes 278 ns per slot per
  rep on one thread here and 75 on four (M), and about 10–16 ns on the pod's 32 threads (E), against the 150 ns line.
  One thread here is above the line and two are at it (147, M); the line prices the deployed prover. At ν = 24 two reps
  take about 0.29–0.77 s on the pod (E; up to 2.0 s in the pessimistic case below), against Spark's 4.1 s.
- **The kernel** (`k1.c`, C, gcc 13.3 `-O3 -march=native`, OpenMP):
  - Multiplier: PCLMULQDQ on 128-bit registers, mod `x^128 + x^7 + x^2 + x + 1`. Karatsuba takes 3 carry-less
    multiplies and the reduction 2, and `a·p + b·q` shares one reduction. Not upstream's multiplier. VPCLMULQDQ (4
    multiplies per instruction) is available here and unused.
  - Per pair: the factors whose values differ across the pair are multiplied out in coefficient form; the rest go into
    one constant, which is folded into the first varying factor. Pairs whose value factor is 0 on both sides (padding)
    are skipped.
  - Rounds 1–4 run from the bit planes. After s rounds, a factor's value is `cst_j + β_s[the block's 2^s bits]`, with
    one table shared by every eq factor, so binding costs nothing there. Round 4 writes the factor records (62 MiB at
    ν = 20, 1.2 GiB at ν = 24), and every later round binds and evaluates in one pass.
  - Each round's `g(0) + g(1)` is checked against the claim, and Φ of the final record against `g_ν(r_ν)`; all 68 timed
    reps pass. The multiplier agrees with a bitwise reference.

ns per slot per rep, best of 5 reps (ν = 24: of 2), uniform / wide-Morton:

| ν (ℓ, d) | multiplications per slot, kernel (M) vs `opcount.py` (C) | 1 thread (M) | 4 threads (M) | pod, 32 threads (E) |
|---|---|---|---|---|
| 16 (11, 23) | 81 / 44 vs 98 / 50 | 186 / 132 | 50 / 36 | 6.5–10.7 / 4.6–7.6 |
| 20 (15, 31) | 132 / 64 vs 163 / 74 | 278 / 183 | 75 / 49 | 9.7–16.0 / 6.4–10.5 |
| 24 (19, 39) | 196 / 87 vs 245 / 102 | 397 / 250 | 124 / 70 | 13.9–22.8 / 8.8–14.4 |

- **Rates here (M).**
  - The raw multiply is 1.51 ns per thread (8 independent chains; 4.64 ns latency).
  - The kernel runs at 2.0–3.0 ns per multiplication per thread, 51–75% of that throughput.
  - Four threads are 3.2–3.8× faster than one. The kernel is compute-bound: its 264 B of memory traffic per slot per
    rep (C) would need only 1.8 GB/s at the kill line.
- **The CPUs.**
  - This VM: `lscpu` names it "Intel(R) Xeon(R) Processor" under KVM. It is family 6, model 207 (5th-generation Xeon
    Scalable, Emerald Rapids), with 4 vCPUs, one thread per core, 2 MiB L2 per core and 320 MiB L3.
  - Other work held the VM's load at 1.1–1.8 during the runs, so 4-thread reps vary by up to 2×; the best is taken.
  - The note's M rates came from a different machine: vy-nebius-2's Xeon 6776P (Xeon 6, Granite Rapids, one core
    generation later), at 32 threads, with upstream b684b12's multiplier (rec-holo §4.1). That multiplier runs at 4.0 ns
    on one thread there, against this kernel's 1.51 here.
- **The pod estimate (E).**
  - It is the 1-thread time here, divided by upstream's multiplier's 32-thread speedup on the pod: 4.0 / 0.23 to
    4.0 / 0.14 = 17–29× (C from M). It takes a pod thread to be as fast as a thread here.
  - If a pod thread were instead as much slower as upstream's multiply is slower than this one (2.64×), ν = 20 would be
    26–42 ns: still 3.5–6× under the line.
- **Against §5.1 (C).** The slot sumcheck for two reps comes to 0.6–1.4 ms, 13–34 ms and 0.29–0.77 s at ν 16, 20 and
  24 (E). That is at or under §5.1's 0.9–2.9 ms, 22–79 ms and 0.48–1.89 s, so §5.1 stands as a conservative price.
  - The kernel does 80–89% of `opcount.py`'s multiplications. It counts a factor as varying only when its values differ
    across the pair, and it skips padding pairs.
  - On this VM's 4 threads, two reps at ν = 24 take 4.16 s (C from M). That compares 4 vCPUs with Spark's 32-thread
    price.
- **Not measured.** The pod itself (no pod run), upstream's multiplier and field representation, and real templates
  (uniform columns are the worst case, §5.1). Untried speedups: VPCLMULQDQ, chunked eq tables for the constant product,
  and records from a later round.

## View against the other two candidates

- **Spark-style memory checking** (`note:proofs/20261010T0250Z-draft-f4-spark`). It is dominated:
  - Lean: 5,000–8,900 lines in that draft's estimate, with a new protocol-level oracle in the middle of a rep (its S3),
    multiset and grand-product reasoning, and the Frobenius-multiplicity argument. Against this note's 2,550–3,400,
    the shared V included. The draft itself put candidate 3 at 2,900–4,900.
  - Prover: 3–10× slower at 2^20 at the same measured rates (§5.1).
  - Proof: +1.7–2.5 MB against +0.02 MB plus the registered opening that both need.
  - Rounds: 443 live coin rounds per rep at 2^20 against 28, each waiting on the coin server.
  - Soundness: its fingerprint terms are 2^-77 to 2^-92 per rep, against 2^-111 to 2^-119 here.
  - Its one structural advantage, cost linear rather than quadratic in the varying factors, matters only beyond about
    ℓ = 20–22, outside F6's likely shapes. That draft reaches the same recommendation.
- **The lookup-based argument.** Over GF(2^128), logup's sums count multiplicities mod 2, which breaks soundness. A
  sound lookup is a grand product with multiplicities as Frobenius exponents, which is Spark's memory check.
  - Its looked-up values (`E`) must still be committed after the lincheck point. So it inherits Spark's extra oracle and
    proof size.
  - Lasso-style table decomposition gains nothing, since `eq(x, ·)` is verifier-evaluable already.
  - I expect it to converge on Spark, and so to lose to candidate 3 for the same reasons.
- **Recommendation:** candidate 3, in deployment B, with fixed-width rows as a second shape if the round degree or proof
  size binds. Fall back to Spark only if K1 fires.

## Reproduce

Local, no pod. The scripts are `art:dc659142f1e5fc6ad5866fc36e2123997ae41178b701f35363c4f2ef077a2fa9`. Python 3
with numpy:
- `python3 toy.py`: the GF(2^16) toy; the identity, honest sessions, the adaptive liar and the rate test, about 20 s.
- `python3 opcount.py 16 20 24`: multiplication counts; ν = 24 takes 74 s and 1.3 GB.
- `python3 opcount_rows.py 11 15`: the fixed-width-row variant.
- `python3 costs.py`: §5.1's prover, proof and verifier columns and the per-rep error.
- `python3 extra.py`: unique-decoding queries per rate, the `L₀`-weighted term, memory, and V* rows against option 4.

Lean citations: `git show origin/main:Security/Proofs/Flock/…` at `dc67b1542`.
