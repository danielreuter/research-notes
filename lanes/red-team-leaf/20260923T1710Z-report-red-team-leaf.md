---
lane: red-team-leaf
kind: report
created: 2026-09-23T17:10Z
status: final-provisional
---

CHECKPOINT none (17:55Z) — Targets 2–4 reviewed from landed code / design: share-logup 8cfa7fb/ca3dd7b (F7 SOUNDNESS-LOSS, accounting only,
≈ 14 bits; F8 WEAKENING: `Proof.fp` publishes ≈ 248 bits of linear information per private operand row — a privacy label issue for
*every* leaf under sharing), blake3-leaf e51bcf4 (framing verified, no finding), ligerito-zk design (F9 WEAKENING: missing size condition
on the mask column, fails at toy sizes; F10 NIT FS). ajtai-leaf 3389c39 closes F4, partly F5. **Still no BREAK.** Findings table + `## FINAL`
below; I will re-check share-logup / ligerito-zk / leaf-iface D1–D2 code as they land and append.
CHECKPOINT none (17:45Z) — Target 1 (Ajtai security claim) reviewed; independent estimator written and run
(`backends/direct/ligero/leaf/redteam_ajtai_estimate.py` on `lane/red-team-leaf`, uncommitted yet). No BREAK. Verdict so far: the
n = 64 / 128 parameters are fine (best known attack 2^289 / 2^571 classical), but the design's *justification* for reading M1
instead of M0 (the Buchmann–Lindner "calibration") is wrong and must be rewritten (F1); labelling findings F4–F6. Targets 2–4
waiting on the lanes' notes (share-logup / blake3-leaf / ligerito-zk not yet posted beyond design).
CHECKPOINT none (17:10Z) — started. Worktree `~/projects/verity-main-wt/red-team-leaf` on `lane/red-team-leaf` @ e0cf2cd.

# red-team-leaf — adversarial review of the leaf campaign (Ajtai params, tile sharing, BLAKE3 framing, LeafScheme, Ligerito ZK)

Findings are numbered F1.., each with severity (BREAK / SOUNDNESS-LOSS / WEAKENING / NIT), a reproduction or calculation, and the fix owner.
No GPU; everything below is python on the laptop or a calculation. Attack/estimate scripts live under
`backends/direct/ligero/leaf/redteam_*.py` on `lane/red-team-leaf`. Sources read: ajtai-design FINAL (2a61a1f, `ajtai_params.py`),
ajtai-leaf (ede23de → a9eaaa4: `leaf/ajtai.py`, `hashchain._compose_leaf`, `hashauth.LeafParams`, Rust `auth.rs::Leaf`), leaf-iface
0d7d716, blake3-leaf note (census + framing), share-logup note §0–§1, `PROTOCOL.md`, `merkle.py`, `rowleaf.py`, Buchmann–Lindner
2008/493 (full text), SWIFFT FSE'08.

## 1. Target 1 — the Ring-SIS leaf (`ajtai-n64` / `ajtai-n128`)

### 1.1 The instance, as implemented (a9eaaa4), and what was verified OK

`h = Σ_{j<steps} X^(steps−1−j)·B·s_j` in `F_p[X]/(X^n+1)`, `p = 2^31−2^27+1`, `s_j ∈ {0,1}^256` = the column's committed operand bits,
`B` = 256 seeded ring elements. Collision ⇒ `γ = s − s' ∈ {−1,0,1}^m \ {0}`, `m = 256·steps` (12288 fp8 / 24576 bf16 / 6912 fp4),
`A·γ = 0 mod p` with `A` the `n × m` unrolled negacyclic matrix. Checked in code, each an obligation of design §6:

* bits: every `hash.{a,b}[i].b<j>` row gets `ctx.boolean` (`hashchain.compose` step 1); the gadget refuses anything but single committed rows
  with coefficient 1 as `bits` — so `γ` is exactly ternary, no relaxation factor. ✔
* chain start = 0: the `n` `acc_in` rows go into `sys.chain["c"]` (`_compose_leaf`), i.e. the `c_in = 0 at every chain start and pad`
  rule of `PROTOCOL.md` (cross-column constraints) applies; `acc_out` into `sys.chain["y"]`. ✔ (Poseidon2's `cap − IV` mechanism.)
* `steps ≤ n` asserted in `_compose_leaf` (fp8 48 ≤ 64, bf16 96 ≤ 128); `n` a power of two in both shipped sets. ✔
* digest tie: `is_end` is a `ctx.pin` (public vector, `Linear pin:… = pub`), `hash.d[x]` pins public, `is_end·(acc_out − d) = 0`. ✔
* digest values canonical (`< p`): Python `hash_public_vectors`, Rust `format.rs` "non-canonical field element". ✔
* Merkle leaf framing: `leaf = SHA256(frame ‖ len‖"leaf" ‖ len‖domain_id ‖ len‖rank ‖ len‖rank ‖ len‖schema ‖ len‖value)` — schema
  string and value length are in the preimage, so an Ajtai leaf (`ajtai-babybear-n64-b1/row/v1`, 256 B LE) and a Poseidon2 leaf
  (`poseidon2-babybear-w24/row/v2h`, 32 B BE) can never collide as tree leaves without a SHA-256 collision; the relation string (which fixes
  the scheme) is in the statement digest and the auth block's `schema`/`params_sha256` must match it (`_hash_auth_block_r`, Rust
  `Leaf::of_relation`). ✔ — answers target 3's "same digest bytes across schemes" for the Ajtai/Poseidon2 pair.
* rejection sampling `derive_row`/`derive_ring_element`: mask to 31 bits, accept `< p` ⇒ uniform on `[0, p)`, acceptance 15/16, SHAKE-256
  prefix property used correctly. ✔
* chain accumulation and β = 1: the recurrence is an exact `mod p` identity; nothing about the 48/96 chained steps changes the norm — the
  extracted `γ` is `s − s'` bit-by-bit regardless of how the sum was accumulated. The only norm-relevant hazard is `steps > n` (free
  collision `X^a(1 + X^n) = 0`), asserted away. ✔

### 1.2 Independent security estimate (`redteam_ajtai_estimate.py`, ~20 s, no imports from the design lane)

Re-derived from scratch: `δ_b` (Chen), M0 (LaBRADOR `sis_secure` rule: ℓ2 target `√m` in the best dimension), M1 (design's rule: target `√d`
in dimension `d`), then the checks the design did not make. Core-SVP `2^(0.292 b)` / `2^(0.265 b)` throughout.

| | n = 64 (fp8/fp4) | n = 128 (bf16) |
|---|---|---|
| M0 (LaBRADOR proof-norm rule), fp8 `m` | BKZ-391 → **114 / 104** (design: 114/104 ✔) | BKZ-839 → 245 / 222 ✔ |
| M1 (design's primary) | BKZ-970 in `d* = 916` → **283 / 257** (design: 976 → 285/259; agrees to 2 bits) | BKZ-1906 → 557 / 505 ✔ |
| **`d_min`: smallest `d` with any ternary kernel vector (`3^d ≥ p^n`)** | **1249** | **2497** |
| pure-lattice attack that can *output a collision* (`d ≥ d_min`, target = norm of the sparsest ternary kernel vector actually expected in `d` coords) | BKZ-1197 in `d = 1257` → **350 / 317** (typical-ternary target: BKZ-1169 → 341/310) | BKZ-2392 → 698 / 634 |
| M2 (Dilithium ℓ∞ model, design's numbers, not re-derived) | 357 / 324 | 676 / 613 |
| **Wagner k-tree (best known attack)** | fp8 `k = 6`: **2^289** (time and memory); fp4 `k = 5`: 2^335 | bf16 `k = 6`: 2^571; fp8@n128: 2^795 |
| CRT / ideal sub-instance (§1.4) | no gain (2^289 → 2^330 → 2^641 for `s = 0, 1, 2` zeroed slots) | same |

**Independent bottom line.** Best known attack on `ajtai-n64` = generalised birthday at **2^289 classical** (Wagner needs 2^283 memory
too; a quantum k-list algorithm à la Grassi–Naya-Plasencia–Schrottenloher improves the exponent to roughly `n log p/(k+2)` ≈ 2^250);
every lattice attack that can actually emit a ternary vector needs BKZ ≥ 1169 (**≥ 2^341 classical / 2^310 quantum**); the M1 rule is a
valid *lower bound* on the lattice attack (2^283 / 2^257) because its optimum lies in a dimension (916) where no ternary kernel vector
exists at all. `ajtai-n128`: ≥ 2^557 lattice floor, 2^571 birthday. Both sets are far above 128 bits with margin ≥ 2× in block size and
≥ 2^150 in birthday cost. **Parameters: no finding.**

### 1.3 F1 — WEAKENING (of the argument, not the parameters): the "M1 reproduces Buchmann–Lindner" calibration is false; §2.4 / §7.3 / §8 must be rewritten

Design §2.4 justifies reading M1 (285) instead of M0 (114) by "M1 lands within 3–9 bits of the only published cryptanalysis of a binary
Ring-SIS hash (Buchmann–Lindner: 68 bits for SWIFFT, 127 for (96,18,389))". Read BL 2008/493 §4.2 and §6 (fetched, full text):

* BL's object is the **pseudo-collision**: "a vector in this lattice with Euclidean norm less than `√(nm)`, i.e. all vectors in the
  smallest ball containing all collisions" — that is `√m` in our notation, **M0's target**, not a ternary vector.
* BL's method: "`len(d) = p^(n/d) δ^d` … takes its minimal value for `d_min = √(n log p / log δ)` … we need a δ s.t. `len(d_min) = √(nm)`"
  (their Table 1: SWIFFT `δ = 1.0084`, `d = 206`; recommended set `δ = 1.0061`, `d = 308`). **That is exactly M0 with the optimal sublattice
  dimension** — the LaBRADOR rule the design calls "the number not to read".
* BL's 68 / 127 bits are **Lenstra–Verheul extrapolations of 2009 NTL-BKZ and RSR running times** (their Fig. 1), not Core-SVP. Under
  Core-SVP the same target costs ~35 bits (BKZ-119) for SWIFFT and ~62 for their recommended set (my script, §F): BL's cost model is ≈ 30–65
  bits above Core-SVP at those block sizes, which is the whole "agreement".
* So M1 = 71 vs BL = 68 is two unrelated models (different target norm, different cost model) landing near each other by accident. It is
  not evidence for M1, and a reviewer who knows BL will notice that BL's own rule is M0.

**What the argument should say instead** (all of it is already true of the implementation, §1.1): (i) extraction is straight-line and yields
`γ = s − s'` with `s, s'` bit-constrained, so the attacker's problem is `SIS_∞` with `β_∞ = 1`, **not** `SIS_2` with `β_2 = √m`; M0 is the
right rule when the extracted witness is only ℓ2-bounded (LaBRADOR/Greyhound relaxed openings with slack), which is not our situation; (ii)
the standard, NIST-vetted estimate for `SIS_∞` is the Dilithium ℓ∞ model (design's M2, 357/324); (iii) the counting bound `3^d ≥ p^n`
shows no ternary kernel vector exists below `d = 1249`, so any lattice attack works in `d ≥ 1249` and needs BKZ ≥ 1169 (≥ 2^341); (iv) the
best known attack is the k-tree at 2^289. Quote M0 as "the reduction-norm rule, 114/104; not applicable to straight-line ternary
extraction", not as a "conservative floor" for the hash. **Fix owner: ajtai-design** (note §2.4, §7.3, §8 bullet 2 and the
`ajtai_params_test.py` cross-check that asserts M1 ≈ BL); coordinator for the Table 1 assumption line
(suggest: "Ring-SIS_∞ collision resistance over F_p[X]/(X^n+1), β_∞ = 1; best known attack 2^289 (k-tree), lattice ≥ 2^283").

**Conventions checked against the sources (web, 17:45Z).** (a) lattice-dogs `labrador.c`: `sis_secure(rank, norm)` accepts iff
`log2(norm) < min(LOGQ, 2·√(LOGQ·LOGDELTA·N)·√rank)`, `LOGDELTA = log2(1.00444)`, `N = 64`, `LOGQ = 32` (`data.h`) — with `rank = 1` this is
M0 verbatim, and every call site feeds it an **extracted-witness norm with slack** (`6·T·SLACK·…·√normsq`, `2·SLACK·√normsq`; LaBRADOR
Thm 5.1: "norm slack √(128/30) ≈ 2 … only guaranteed to output a witness with norm at most √(128/30)·β"). That is precisely the situation
(relaxed ℓ2 openings) in which M0 is the right rule and our leaf is not in it. (b) `lattice-estimator` `SIS.lattice` (docs
`algorithms/sis-lattice`): Euclidean bound → "root-Hermite factor required for BKZ to produce the required output" (= M0/M1 shape with the
given `β_2`); infinity bound → "we use the worst case euclidean norm bound [`√d·β_∞`] as a lower bound on the hardness, then analyse the
probability of obtaining a short vector where every coordinate meets the infinity-norm constraint" per MATZOV22 p.18 / Dilithium21 p.35
with `ζ` ignored coordinates (zero-forcing) — i.e. M1 is the estimator's own *lower bound* and M2 its estimate for `SIS_∞`. Design §2.2's
labels are therefore right; only the BL justification is wrong.

### 1.4 The CRT question (X^n+1 splits completely mod p) — evaluated, no attack

`p ≡ 1 mod 2^27`, so `X^64+1` and `X^128+1` split into linear factors mod p (roots = the 128th / 256th roots of unity), `R_p ≅ F_p^n`
by evaluation, exactly SWIFFT's `Z_257[X]/(X^64+1)` situation (257 ≡ 1 mod 128). The classic fully-splitting warnings are about (a)
Ring-LWE *decision* with non-spherical error (Peikert 2016; Elias–Lauter–Ozman–Stange) and (b) short elements not being invertible, which
breaks relaxed-opening / challenge-difference arguments in lattice ZK (Lyubashevsky–Seiler 2018). Neither is a collision-resistance
property; the worst-case reductions (Lyubashevsky–Micciancio 2006, Peikert–Rosen 2006) need `X^n+1` irreducible over **Z**, which it is.
Concretely for this instance:

* *Subring / ideal trick.* Force every `γ_i` into `I_S = {f : f(ζ_k) = 0 ∀k ∈ S}` so the `|S| = s` CRT constraints vanish for free. Ternary
  polynomials of degree `< 48` in `I_S` number `3^48 / p^s` (evaluation at `s ≤ 48` points is onto `F_p^s`): 76 → 45 → 14 bits of input
  entropy per polynomial for `s = 0, 1, 2`, against `(64 − s)·30.9` bits of remaining constraint. The k-tree over the 256 lists then costs
  2^289 → 2^330 → 2^641 (script §E): monotone worse. In the lattice view the kernel sublattice on any `d` coordinates spanning `F_p^n`
  has volume `p^n` regardless of the CRT structure (two bit positions' 96 rotations already have rank 64), so BKZ sees the same lattice.
* *Two-position NTRU-like shortcut* (`γ_i / γ_i' = −b_i'/b_i`): the rank-2 module lattice has dimension 128 and volume `p^64`;
  Gaussian-heuristic shortest vector `2^16.9` ≫ `√96` — no unusually short vector, no shortcut. Ring automorphisms `X ↦ X^t` map
  collisions of `B` to collisions of `σ_t(B)`, not of `B`.
* Zero divisors: short zero-divisors exist plentifully (`I_k` has index `p` in `Z^n`, `λ_1 ≈ 2.7`), which is why the *hiding* variant must
  never rely on invertibility — irrelevant to binding.

Conclusion: the design's §6.6 sentence ("the CRT splitting does not give an attack: a collision must vanish in all n components") is
correct; the concrete trade-off above is what to cite. **No finding.**

### 1.5 F2 — NIT: M1's headline dimension is infeasible; relabel M1 as a lower bound

`m1_blocksize` picks `d* = 916` (n = 64) / `1680` (n = 128), below `d_min = 1249 / 2497`. M1 "succeeds" by finding a vector of norm `√d` in a
sublattice that contains no ternary vector, i.e. it is not describing an attack; the design's own text ("given the benefit of the doubt
that any such vector is ternary") half-says this. Relabel: "M1 = attacker-favourable floor of the lattice attack; the attack itself needs
`d ≥ d_min` and costs ≥ 2^341". Also `m1_blocksize` scans only `d0 ± 64`, which is why the design gets 976 and I get 970 — cosmetic.
**Fix owner: ajtai-design** (`ajtai_params.py` docstring + §2.2 M1 bullet).

### 1.6 F3 — the M0-vs-M1 ruling (coordinator's question), and the recommendation on `n`

**Ruling:** for the collision resistance of a bit-input Ring-SIS hash whose openings are checked bit-exactly by the circuit, M0 is not the
attack cost and not the right number for Table 1; the right statement is "best known attack" (k-tree 2^289 at n = 64, 2^571 at n = 128)
with the lattice floor (M1 2^283 / real ≥ 2^341). M0 (114/104 at n = 64) becomes the relevant number only if the leaf is ever reused as a
commitment with *relaxed* (ℓ2-slack) openings — e.g. inside a lattice-based proof of knowledge with rewinding/slack — which this design
does not do and should say so explicitly (pitfall for future reuse). **Recommendation: ship `ajtai-n64` for fp8/fp4 and `ajtai-n128` for
bf16-hopper as designed**, with the assumption line rewritten per F1. `n = 128` everywhere is not needed for security; it is only the answer
if the coordinator wants the LaBRADOR rule satisfied for optics (769 rows/unit, 13.6× chain-test growth — ajtai-leaf measures).

### 1.7 F4 — NIT: two `derive_B`s, two tags, transposed layouts

Design (`ajtai_params.derive_ring_element`): stream `SHAKE-256("verity/ajtai-babybear/B/v1" ‖ LE32(i))`, `i` = bit position, `k`-th accepted
word = coefficient `k` of `b_i`. Leaf (`ajtai.derive_row`): stream `SHAKE-256("verity/ajtai-babybear/A/v1" ‖ LE32(x))`, `x` = coefficient
index, `i`-th accepted word = `B[x][i]`. Different tag, transposed indexing ⇒ different matrices; the design's regression vector in
`ajtai_params_test.py` does not describe the shipped leaf. Both are uniform on `[0, p)`, both prefix-consistent, so security is identical —
but the brief and design §7.9 say one function, four call sites. Also: design note §1.3 states `B` "must be regenerated by the verifier";
the Rust verifier does not regenerate anything (see F6). **Fix owner: ajtai-leaf** (adopt one; the shipped `A/v1` layout is fine — then
ajtai-design updates its test vector, or deletes `derive_*` from `ajtai_params.py` and imports the leaf's).
**Status 17:50Z: resolved at ajtai-leaf 3389c39** — the leaf adopted the design's `B/v1` per-bit-index `derive_ring_element` (regression
vector in its tests), refuses non-power-of-two `n`, and the schema carries `r0`. Closed.

### 1.8 F5 — WEAKENING (labelling / fingerprint): "hiding only up to preimage search" is false for a linear leaf

`leaf/ajtai.py` docstring: "Unsalted and deterministic: hiding only up to preimage search on a row (same caveat as Poseidon2 today)".
`relchain.ZK_HASHED_NOTE` (both `lane/ajtai-leaf` and `lane/leaf-iface`): "…their Poseidon2-BabyBear row digests (deterministic, unsalted:
hiding only up to preimage search on a row)" — hard-coded Poseidon2 wording that now goes into the fingerprint/`zk_statement` of an
`fp8-ada+ajtai-n64` run. For `h = A·s` there is no preimage search involved: (1) `h(s) − h(s') = A(s − s')` — two committed rows that differ
in one byte are told apart *and the byte located and recovered* by testing 1536 × 255 candidates against `Δh` (µs); differences of a few
dozen bits by MITM; (2) any row whose conditional entropy given public structure is `< n log2 p ≈ 1978` bits is determined by its digest
and recoverable by knapsack/lattice methods; (3) `h` is additively malleable (`h(s) + h(s')` is a valid linear image of `s + s'`). Design
§3.1 says all this correctly; the code and the fingerprint contradict it. Required: `assumption`/docstring say "binding-only; linear
digest leaks equality, sparse differences and low-entropy rows — not hiding"; `ZK_HASHED_NOTE` parametrised by the leaf (`leaf.privacy_note`
on the `LeafScheme`), relation/`hash_name` carries `r0` (unsalted) as design §8 asks (`ajtai-babybear-n64-b1/v1` currently does not).
**Fix owner: ajtai-leaf** (docstring, `hash_name`), **leaf-iface** (`LeafScheme.privacy_note` + `ZK_HASHED_NOTE` by leaf), coordinator
(Table 1 wording; same for the BLAKE3 leaf: "unsalted, hiding up to preimage search" *is* the right caveat there and for Poseidon2).
**Status 17:50Z: partly addressed at 3389c39** — `hash_name`/schema carry `r0`, `__init__` comments "binding only, NOT hiding (digest
linear in the row's bits)"; still open: the module docstring line 13 still says "hiding only up to preimage search on a row (same caveat as
Poseidon2 today)", `assumption` says nothing about hiding, and `ZK_HASHED_NOTE` is still the Poseidon2 sentence (leaf-iface D2).

### 1.9 F6 — NIT (trust model): the Rust verifier never regenerates `B`; `B` is bound only by the pinned system digests

`auth.rs`: "The in-circuit side needs nothing here: the system file carries the constraints." `B` lives in the 128 `Linear` rows of the
system file; the verifier accepts the file iff `(sys_id, table_digest)` equal the pinned pair for `fp8-ada+ajtai-n64`, else refuses —
**unless `--allow-any-system`**, which verifies against any system file and only flags `system_pinned = false`. For every other relation an
un-pinned system is "a different relation"; for Ajtai it is "the same relation with a different (possibly trapdoored or all-zero) key" —
`B = 0` makes every row digest 0 and every proof trivially consistent with any tree built the same way. The pin makes this a non-issue in
the default mode (the pin is the regeneration, baked into the binary), but design §1.3/§6.7 claim regeneration, and `Leaf::ajtai(n)`
accepts any `n ≤ 1024` with no pin for `n ≠ 64`. Ask: (a) `--allow-any-system` refuses hashed (v5) statements whose leaf carries key
material, or (b) Rust derives `B` from the tag and checks the 2n `Linear` rows' coefficients (cheap: 256·n SHAKE words). Document either
way. **Fix owner: ajtai-leaf / ligero-verify.**

## 2. Target 2 — tile-64 row sharing (`share-logup` @ 8cfa7fb / ca3dd7b: `chain.py`, `protocol.py`, `hashchain.compose_shared` / `row_hash_system`, `relchain.SharedHashedRunner`)

### 2.1 What was verified OK (read the code, not only the note)

* **Coin order / 8c.** `ρ_0..ρ_{C−1}` are the tail of challenge 1 (`_challenge1(..., n_fp)`, coordinate 0), i.e. `SHAKE(H(stmt, c1c2, r1))`
  interactive (coins alone; `r1` is opened after G's root, its commitment `c1` made before) / `SHAKE(H(stmt, root, r1))` Fiat–Shamir. G's
  lane rows are in G's root, so `ρ` is post-commitment for G without any new slot. ✔ `F` (`Proof.fp`) is a prover message after coin 1,
  absorbed into `seed2_preimage` (`|fp=`) before the column challenge in FS. ✔ H's statement digest binds `ρ` and `F_H` (`|fp_rho=`, F). ✔
* **Per-VU independent coefficients.** The fingerprint constraints ride the chain test as extras `e = 2·n_extra_links + o·C + x` at the end
  column of VU `v` with coefficient `extra_coef(rc, e)[:, col] = u_{e mod 6}·u_6^(e div 6 + 1)` where `rc` is `(D, 7, l)` — per column
  uniform. So VU `v` and VU `v'` get independent coefficients (different columns) and the 16 constraints of one column get distinct
  monomials (degree ≤ 1 + ⌈16/6⌉ = 4). I specifically looked for a cross-VU cancellation (`lanes_v1 = R_1 + Δ`, `lanes_v2 = R_2 − Δ`,
  which would pass a shared coefficient *without knowing ρ*); it is excluded by the per-column `rc`. ✔
* **What binds H's lanes to the row.** H's lanes are committed knowing `ρ` and `F_H`; the fingerprint alone is then *not* binding on H's
  side (an 8-equation knapsack in 768 16-bit unknowns is LLL-trivial). H is bound by its Poseidon2 digest pinned at the unit's end and
  opened as the leaf at rank `r` under the x/W root (`verify_vus` step 4, `verify_hash_auth` on the per-VU expansion), with the role a
  public pin (`IV(role) = IV_x + role·(IV_w − IV_x)`, roles checked against `shared_units(auth)`). Chain of custody: tree leaf ⇒ (Poseidon2
  CR) H's lanes = `R` ⇒ `F_H = fp_ρ(R)` ⇒ (VUs of one unit agree on `F`, `F_H := F_G`) G's lanes `= R` except w.p. `(767/p)^C` (G's lanes
  pre-`ρ`). The note's soundness sentence ("no witness other than a Poseidon2 preimage of the leaf digest") is the right one. ✔
* **Same bit rows.** `compose_shared`: `lane[j] = Σ_q 2^(nb·q)·word[per·j + q]` with `word = Σ 2^i bit_i` of step 1's bit rows
  (`_lanes_of` / `_lane_rows`, `ctx.eq`, `ctx.learn(r, 0, 2^16)` — a theorem of the equality). The fingerprint is over the bits the GEMM
  decodes, not a copy. ✔ Same lanes are what H's sponge absorbs (`row_hash_system` `state = lanes + caps`). ✔
* **"Can a VU share a different row than the committed one?"** No: `x_index[v]`/`w_index[v]` are in the auth block (statement digest),
  the unit list is derived by the verifier from it, `F_G[v]` must equal `F_H[unit(x_index[v])]`, and that unit's digest is opened at rank
  `x_index[v]`. A VU pointing at rank `r` while using row `R' ≠ R_r` needs `fp_ρ(R') = fp_ρ(R_r)`. ✔

### 2.2 F7 — SOUNDNESS-LOSS (accounting only, ≈ 14 bits; label unaffected): `fingerprint_collision` is booked per proof, not per fingerprint, and ignores the challenge-expansion bias

`protocol.soundness(..., fp=)` adds `fingerprint_collision(C, steps) = ((16·steps − 1)/p)^C` **once per proof**. The event is "some VU's
committed operand row differs from the shared row it is matched to yet has equal fingerprints"; a sub-batch has `2·n_vus` (fp8-ada at
`l = 16384`: 682) distinct nonzero difference polynomials, all evaluated at the same `ρ`, so the bound is the union `2·n_vus·(767/p)^C`
(+9.4 bits). Also `_expand` draws challenge elements as `u32 mod p` (no rejection; the masks in `_uniform_symbols` *do* reject): `2^32/p =
2.13`, so residues below `2^32 − 2p` have 3 preimages and the rest 2 — a residue's probability is at most `3/2^32 ≈ 1.41/p`, and
Schwartz–Zippel per coordinate is `≤ 1.41·767/p` (+0.49 bits per coordinate, +3.9 / +4.9 bits for C = 8 / 10). Corrected: interactive
`2^−170.6 → 2^−157.3`; FS `(767/p)^10·2^60 = 2^−153.7 → 2^−139.4`. Both still far under the `2^−128` target, so the accepted batch bound
(`2^−128.08`) does not move at 2 decimals — but the term as written is wrong and the docstring ("booked per proof — the event that *a* VU's
operand row differs") states the single-VU event. **Fix owner: share-logup**: multiply by `2·n_vus` (pass `n_vus` to `soundness`) and either
rejection-sample `_expand` or carry the 1.41 factor (the latter also applies to every `r`/`rho_lin`/`rho_quad`/`rc` SZ term booked today —
pre-existing, coordinator's call whether to touch `protocol.py` for it).

### 2.3 F8 — WEAKENING (privacy / ZK label): `F` is an unmasked linear function of the private operand rows

`Proof.fp` = `F[v][o][x] = Σ_{s,i} ρ_x^(16s+i)·lane_o[i][48v+s]`: `C = 8` (10 in FS) field elements per operand per VU = **≈ 248 (310) bits
of linear information about each private operand row, with verifier-known coefficients, sent in the clear.** This is the same class as
red-team-zk F1 (the unmasked `q|_H`), smaller in volume but not maskable inside the current design: a mask row `m` added to both G's and
H's constraints is prover-controlled on both sides (`lanes_G ≠ lanes_H` compensated by `m_G ≠ m_H`), so it would destroy soundness; the
cross-proof equality `F_G = F_H` is exactly what forces `F` into the clear. Consequences under `included-hash-shared` for **every** leaf,
including Poseidon2: (1) equality of two rows is visible (already visible from the digests); (2) two rows differing in a few bytes have
`F − F' = Σ ρ^j Δ_j` with sparse `Δ` — recoverable by MITM over positions/values for `≲ 6–8` differing bytes (`1536^t·255^t` candidates,
halved) — this is the Ajtai F5 linear-leak caveat, now attached to the shared Poseidon2/BLAKE3 columns too, at 248 instead of 1978 bits;
(3) any row with `< 248` bits of conditional entropy given public structure is determined by `F`. For the *current* labels this is a
labelling matter (operands are already "hiding only up to preimage search"; the zk_statement of an `included-hash-shared` run must add
"fingerprints `F` (C×31 bits of linear information per operand row) are public"); for the campaign's private-operand ZK target it is a
real HVZK leak. Structural fix (v2): fold the row units into the *same* Ligero proof as the VUs (H's units as extra columns of G, the
equality `F_G = F_H` becomes an in-proof linear constraint and `F` never leaves the prover) — share-logup's own "tile-wide session"
alternative points there. **Fix owner: share-logup** (zk_statement wording now; design note for v2), coordinator (Table 2 footnote for
the tile64 headline: "sharing publishes a 248-bit linear fingerprint of every operand row").

### 2.4 NIT (pre-existing, share-logup inherits it): the hashed chain-start column's SZ term is not "below the field term"

`chain.py` module comment: 32 extras at a hashed chain-start column give degree 7, `(7/p)^6 = 2^−169`, "below the field term `(n+3)/p^D`
the accounting already books". At `l = 16384`, `n = 4l`: `(n+3)/p^6 = 2^−169.4` — equal, not below; and the chain test's own SZ term is
not itemised in `soundness()` at all (it hides under the field term). Harmless at 2^−128 (`2^−168.6 + 2^−169.4 ≈ 2^−168`), but the
accounting should book `max_degree^D/p^D` explicitly once fingerprints add degree-4 columns at every VU end. Owner: share-logup / hash-relation.

## 3. Target 3 — BLAKE3 framing / LeafScheme (`blake3-leaf` @ e51bcf4 `leaf/blake3.py`; `leaf-iface` @ d35a52f)

Verified in code (`leaf/blake3.py`): keyed mode with `KEYED_HASH` on every chunk block and parent (`key_for(word_bits)` = `verity/blake3-leaf/v1/w8|w16`
zero-padded, replaces IV as the first CV of every chunk *and* of the parents); in-circuit only chunk compressions with `flags = [cs, ce, 0, 0,
KEYED]`, `block_len = 64` constant (rows are multiples of 64 B), `counter = pos >> (4 − lg)`; `cs`/`ce`/hold indicators derived from the bit
decomposition of a **carried** position row `pos` (`pos_in = 0` at the chain start by the `c` family, `pos_out = pos_in + 1` linked; `_bits_raw`
is an integer identity since `pos < 2^npb ≪ p`) — a sound private counter, no public layout pins needed; chunk CVs parked in hold slots by
`[pos == end of chunk c]` products; digest `[n_chunks | CV_0 | CV_1 | CV_2]` as 16-bit limbs pinned at the end; `leaf_bytes` rejects
malformed limbs/`n_chunks` and computes the standard left-heavy keyed parent fold with `ROOT` on top ⇒ the SHA-256 tree leaf value is exactly
`blake3(row_bytes, key=key_for(word_bits))`. A prover publishing CVs that are not a row's CVs but fold to the leaf needs a keyed-BLAKE3
parent collision/preimage. Rows of one chunk are refused (the chunk's last block would need `ROOT`). ✔ No finding on framing.

* NIT (metadata, not security): role is not in the key, so an x row and a W column with identical bytes have identical BLAKE3 digests and
  identical Ajtai digests (Poseidon2 separates them by IV); the *statement's* digest table therefore reveals x/W byte-equality for those two
  leaves. Domain separation of the trees is intact (different `domain_id`). Owner: blake3-leaf/ajtai-leaf docstrings.
* Cross-scheme leaf bytes: settled by the SHA-256 leaf framing (schema + lengths), §1.1 ✔; statement ↔ auth-block ↔ relation-string
  consistency checked by both readers ✔. `ZK_HASHED_NOTE`: F5 (the BLAKE3 wording "unsalted, hiding up to preimage search" is correct).
* Length: encoded by `n_chunks` in the digest + `CHUNK_END` on each chunk's last block, fixed per relation; a shorter row cannot pose as a
  longer one. Word bits: in the key (`/w8` vs `/w16`), so the same bytes read as u8 vs u16 rows have different digests ✔.
* leaf-iface (D0 landed; D1/D2 pending at 17:50Z): `LeafScheme` contract + registry + Poseidon2 plugin verified against the `main` behaviour
  by their own byte-identity tests (statement bytes / leaf bytes unchanged). The `ZK_HASHED_NOTE` is still the hard-coded Poseidon2 sentence
  in every branch I looked at (`lane/ajtai-leaf` 3389c39 `relchain.py:994`) — with `+ajtai-n64` in the relation the zk_statement literally
  says "Poseidon2-BabyBear row digests". Tracked under F5 (owner leaf-iface: `LeafScheme.privacy_note`, D2).

## 4. Target 4 — Ligerito ZK (`ligerito-zk` design note 17:00Z, read at 17:50Z; no code yet)

### 4.1 The leak model and the mask — checked, no BREAK

The catalogue L1–L6 is complete for the paper's protocol (I looked for a seventh: the Merkle *roots* of rounds ≥ 2 are commitments to folds
of `y_1`, covered by the same argument as L4/L6; the coin openings carry nothing). The central claim — every message of every round after
round 1 is a functional of `y_1 = M̃_1 r̄_1 = payload + r̄_1[C_1−1]·m` with `m` the uniform top column — is right: `r̄_1[C_1−1] = Π_j r_j`
(all column bits 1) is nonzero except w.p. `k'_1/p^6`, `y_1` is then uniform in `F^{2^{k_1}}` **conditioned on the payload**, and the
verifier sees `≈ 2^{k_{ℓ−1}} + Σ_i |S_i| + Σ_i (2k'_i+1) + E ≈ 2^11` functionals of it (N = 2^29: `2^{k_1} = 2^22`). The joint view is
uniform iff those functionals are linearly independent *as functionals of `m` alone* — generic, and they say they test rank at toy size. The
A-cells fix the one thing the top column does not reach (round 1's `u^{(1)}[c]`, `c < C_1−1`) ✔. Libra §4.1 for L1 with `3n+1` coefficients
matching the `3n+1` independent linear constraints (`nd+1`) ✔; the `+ρ_zk g` combination costs `1/p^6` in soundness ✔; `v_g` verified as
a committed inner-product claim (not taken on faith) ✔. Consistency of masking the zero-check's *input*: the sumcheck runs on `f^` and
the final check evaluates `C` on `f^(z_i)`, which is the honest value of the masked instance — sound iff `C ≡ 0` at mask cells and no
constraint at a real cell *reads* a mask cell (their §3 requirement; the shift-coupled constraint at column `C_1−2` reads column `C_1−1`,
they name it). ✔ Per-column RS padding + public `ȳ_i = μ^T r̄_i`: the L5 argument is Ligero 8b's, exact for `|S_i| ≤ t_pad` ✔; soundness
= the paper's row check for the message `(y_i ‖ ȳ_i)` at the padded rate, `|S_i|` re-sized ✔ (`ȳ_i` fixed before `S_i`) ✔. Coins: `K`
slots at step 0, `chal_k` a function of `r_k` and the statement only ✔ 8c.

### 4.2 F9 — WEAKENING (parameter condition missing): the mask column must be larger than the number of revealed functionals

The uniformity of the view needs `rank(leak functionals restricted to the mask cells) = #functionals`, hence `2^{k_1} + 127 ≥ 2^{k_{ℓ−1}}
+ Σ|S_i| + Σ(2k'_i+1) + E + (3n+1)·6`. At N = 2^29 it is `2^22 ≫ 2^11`. At the toy sizes of §5 (N = 2^12–2^16) with the paper's shapes
(`k_1 ≈ 8–10`, final vector `2^{k_{ℓ−1}}` possibly equal to `2^{k_1}` for a 2-round recursion, `|S| = 192`) the inequality can **fail** —
the final vector alone has as many entries as the mask column, and the L6 entries plus the L4 openings then *determine* `m` and expose
`payload` folds. The design nowhere states the condition; `ZkParams` should assert it (and the toy test should pick `k_1` so that it holds
with margin, or the "exact rank" test will pass or fail by dimension rather than by design). Also: the G-block (`6(3n+1)` cells) sits inside
the mask column and is *not* free given the transcript (the Libra messages pin `3n+1` combinations of it) — exclude it from the rank count
(hence the `−(3n+1)·6` above). **Fix owner: ligerito-zk** (a one-line assertion + a sentence in §1.1).

### 4.3 F10 — NIT: Fiat–Shamir reading not addressed

The design is the interactive committed-coin protocol (`K ≈ 60` slots). The b-zk-fix F3 lesson (labels differ between interactive and FS;
FS soundness gets the `q·ε` grinding factor, and the *simulator* argument does not carry over — FS-ZK needs the programmable RO) is not
mentioned. Say explicitly that `ligerito-zk` is interactive-only until an FS note exists, and that the `zk_statement` labels follow
PROTOCOL.md 8c. **Fix owner: ligerito-zk** (`omitted()` text).

### 4.4 NITs for the layout contract (owner: ligerito-zk / ligerito-sumcheck)

* `check_layout` must take *referenced* cells (read by a constraint located elsewhere: shifts, wide groups, lookup selectors, chain-start
  pins), not only cells with a constraint located at them — the note says "constrained-or-referenced", make `referenced_cells()` the API.
* A-cell row `q` must be a padding row in **every** round-1 column, including the columns that hold the last real VU (fp8-ada: 3724 real
  rows of 4096 — fine; a relation with 4096 real rows has no `q`). State the requirement `rows_real < 2^{k_1 rows}`.
* Statement-adaptive `V*` (red-team-zk A5) is covered for `|S_i| ≤ t_pad = 256` — the honest `|S_4| = 214` after the padded-rate resize is
  within 256 but the margin is 42; if round 4's rate is not lowered (doubled codeword), note that `t_pad` must be ≥ the *largest* `|S_i|`.
* Merkle leaf salting is listed in `omitted` ✔ (same G3 item as Ligero).

## Findings table (running)

| # | severity | target | one line | owner |
|---|---|---|---|---|
| F1 | WEAKENING (argument) | ajtai-design §2.4/§7.3/§8 | BL09's method *is* M0 (pseudo-collisions, `√(nm)`, LV cost); "M1 reproduces BL" is a coincidence; rewrite the justification as straight-line ternary extraction + Dilithium ℓ∞ + `d_min` counting + k-tree 2^289 | ajtai-design, coordinator (Table 1) |
| F2 | NIT | ajtai-design §2.2 | M1's optimum `d* = 916 < d_min = 1249`: label M1 a lower bound; real lattice attack ≥ 2^341 | ajtai-design |
| F3 | ruling | coordinator | read M1/k-tree, not M0, for a bit-exact hash; M0 only if the leaf is reused with relaxed openings; ship n = 64 (fp8/fp4), n = 128 (bf16) | coordinator |
| F4 | NIT — **closed** (3389c39) | ajtai-leaf / ajtai-design | two `derive_B`s (`A/v1` per row vs `B/v1` per bit position, transposed); leaf adopted `B/v1` | ajtai-leaf |
| F5 | WEAKENING (labelling) — partly (`r0` in schema) | ajtai-leaf, leaf-iface | "hiding only up to preimage search" is false for a linear digest (docstring still says it); fingerprint `ZK_HASHED_NOTE` hard-codes Poseidon2 for every leaf | ajtai-leaf, leaf-iface (D2) |
| F6 | NIT (trust) | ajtai-leaf / ligero-verify | Rust never regenerates `B`; `--allow-any-system` accepts any key; no pin for `n ≠ 64` | ajtai-leaf |
| F7 | SOUNDNESS-LOSS (accounting, ≈ 14 bits, label unchanged) | share-logup `protocol.py` | `fingerprint_collision` booked once per proof instead of `×2·n_vus` (+9.4 b); `_expand` is `u32 mod p` without rejection (+0.49 b/coord); corrected FS bound `2^−139`, still ≪ `2^−128` | share-logup |
| F8 | WEAKENING (privacy / ZK label) | share-logup, coordinator Table 2 | `Proof.fp` publishes `C·31 ≈ 248 (310 FS)` bits of verifier-known linear functionals of every private operand row — for every leaf, incl. Poseidon2; sparse row differences recoverable; not maskable in the two-proof design; v2: fold H's units into G's proof | share-logup (zk_statement now; v2 design), coordinator |
| F9 | WEAKENING (missing parameter condition) | ligerito-zk §1.1 | mask-column uniformity needs `2^{k_1} ≫ #revealed functionals (≈ 2^{k_{ℓ−1}} + Σ|S_i| + …)`; fails at the §5 toy sizes; G-block cells are not free given the transcript | ligerito-zk |
| F10 | NIT | ligerito-zk | interactive-only; FS reading / `q·ε` and the non-transfer of the simulator not stated | ligerito-zk |
| — | NIT | share-logup / hash-relation | hashed chain-start SZ term `(7/p)^6 = 2^−169` equals, not undercuts, the field term; book `max_degree^D/p^D` explicitly | share-logup |
| — | NIT | blake3-leaf / ajtai-leaf | role not in the key: identical x-row / W-column bytes ⇒ identical digests (Poseidon2 separates by IV) | blake3-leaf, ajtai-leaf |
| — | NIT | ligerito-zk / ligerito-sumcheck | `check_layout` must cover *referenced* cells (shift, wide, lookup); A-cell row `q` needs `rows_real < 2^{k_1,rows}`; `t_pad ≥ max |S_i|` | ligerito-zk |

**No BREAK found in any target as of 17:50Z; no handoff files posted.**

## FINAL (posted 17:55Z; will be amended in place if share-logup / leaf-iface D1–D2 / ligerito-zk code changes the picture before 23:30Z)

**Coordinator summary.**

1. **Independent estimate for the Ring-SIS leaf** (method: own script `redteam_ajtai_estimate.py` @ 7e595ed on `lane/red-team-leaf` — Chen
   `δ_b`, Core-SVP `2^{0.292b}` / `2^{0.265b}`; M0 = LaBRADOR `sis_secure` rule, M1 = design's rule, both reproduced to ≤ 2 bits; then two
   checks the design did not make: the counting bound `d_min = ⌈n log_3 p⌉` on the smallest dimension where a ternary kernel vector exists,
   and the Wagner k-tree cost with the fp8 / fp4 / bf16 list sizes; CRT/ideal sub-instance trade-off computed for 0/1/2 zeroed slots):

   | | ajtai-n64 | ajtai-n128 |
   |---|---|---|
   | best known attack (classical) | **k-tree 2^289** (2^283 memory) | k-tree 2^571 |
   | lattice floor (M1, a lower bound: its optimum `d* = 916 < d_min = 1249`) | 2^283 / 2^257 q | 2^557 / 2^505 q |
   | lattice attack that can emit a collision (`d ≥ d_min`) | BKZ ≥ 1169 → ≥ 2^341 / 2^310 q | BKZ ≥ 2392 → ≥ 2^698 |
   | M0 (LaBRADOR proof-norm rule) | 114 / 104 — **not the collision cost** for a bit-exact hash; relevant only if the leaf is reused with relaxed (ℓ2-slack) openings | 245 / 222 |
   | CRT (X^n+1 splits into linear factors) | no gain: zeroing `s` slots costs `2^{~31s·(k−1)}` in list size, ideal sub-instances keep `p^{n−s}` volume; the ring is only a compact matrix here | same |

   **Ruling M0 vs M1:** read the k-tree / M1-lower-bound numbers, not M0. The design's *justification* ("M1 reproduces Buchmann–Lindner") is
   wrong (F1: BL09 targets pseudo-collisions of ℓ2 norm `√(nm)` with the M0 method and LV extrapolation; their 68/127 bits are not Core-SVP)
   — the parameters survive, the argument must be rewritten as: straight-line ternary extraction + `d_min` counting + Dilithium ℓ∞ + k-tree.

2. **Recommendation: ship `ajtai-n64` for fp8-ada / fp4, `ajtai-n128` for bf16-hopper**, as designed, *binding-only* — with the assumption
   line rewritten (F1), the docstring/fingerprint stopping to call it "hiding up to preimage search" (F5: a linear digest reveals equality,
   locates and recovers sparse byte differences in µs, and determines any row with < 1978 bits of conditional entropy), and the Rust
   verifier's `--allow-any-system` refusing hashed statements whose leaf carries key material or re-deriving `B` (F6).

3. **Findings** (table above; none BREAK, no handoffs posted): F1 WEAKENING (argument), F2 NIT, F3 ruling, F4 NIT closed, F5 WEAKENING
   (labelling), F6 NIT (trust), **F7 SOUNDNESS-LOSS** (share-logup accounting, ≈ 14 bits of slack in the fingerprint term, corrected FS
   bound `2^−139` still ≪ `2^−128`; the accepted headline does not move), **F8 WEAKENING** (share-logup publishes `Proof.fp` = 248 / 310
   bits of verifier-known linear functionals of every private operand row, for every leaf — the tile64 headline needs the footnote and the
   zk_statement the sentence; v2 fix = fold H's units into G's proof), **F9 WEAKENING** (ligerito-zk: mask column must exceed the number of
   revealed functionals — `2^{k_1} ≫ 2^{k_{ℓ−1}} + Σ|S_i| + …`; unstated, fails at the toy sizes of its own §5), F10 NIT (ligerito-zk FS
   reading), plus three unnumbered NITs (chain-start SZ term; role not in BLAKE3/Ajtai key; `check_layout` scope).

4. **Verified OK, explicitly:** share-logup coin order (ρ = tail of challenge 1, post-commitment for G, no new slot needed; F is absorbed
   before the column challenge), per-VU independent coefficients (no cross-VU cancellation), "a VU cannot share a different row than the
   committed one" (auth block ⇒ unit ⇒ digest ⇒ Poseidon2 preimage ⇒ `fp_ρ` equality w.p. `(767/p)^C`), same bit rows fingerprinted as
   decoded; BLAKE3 keyed framing (carried position row, flags, counter, `n_chunks`, native parent fold) and the SHA-256 leaf framing across
   schemes (schema + lengths, cross-scheme collision impossible without a SHA-256 collision); Ajtai chain accumulation keeps β = 1 exactly
   (a `Linear` row per digest coordinate, no carries, `acc_in = 0` pinned by the `c` family); `derive_B` rejection sampling uniform and
   prefix-consistent; Ligerito-ZK leak catalogue L1–L6 complete and the mask-column argument correct given F9's condition.

## Log

* 17:10Z start; briefs, design note, ajtai-leaf note + code, leaf-iface / blake3 / share-logup notes read.
* 17:40Z `redteam_ajtai_estimate.py` written and run; BL 2008/493 full text read (§4.2 pseudo-collision definition, §6 method).
* 17:45Z CHECKPOINT (Target 1 done).
* 17:50Z share-logup code (8cfa7fb/ca3dd7b) read: `chain.py` extras, `protocol.py` fingerprint term, `hashchain.compose_shared`,
  `relchain.SharedHashedRunner`, `_challenge1`/`_expand`; F7, F8 written. blake3-leaf e51bcf4 `leaf/blake3.py` read: no framing finding.
  ligerito-zk design note read: F9, F10. ajtai-leaf 3389c39 closes F4, partly F5.
