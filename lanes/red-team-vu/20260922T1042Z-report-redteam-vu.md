---
id: r20-proof/red-team-vu/20260922T1042Z-report-redteam-vu
campaign: r20-proof
lane: red-team-vu
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/redteam_vu.md
---

# Red team: the two full-VU provers, the ZK construction, the leaf/v2 binding

Lane `red-team-vu`, branch `lane/red-team-vu`. Every row below is a *concrete* input run through the real prover
and verifier on `vy-cpu3` (run `r20260922-070024-e7d1`, rustc 1.98.1, `fixtures/redteam/vu-battery/v1/`), or an
argument that says exactly why no such input exists. Machine-readable twin: `notes-asset:campaigns/r20-proof/assets/red-team-vu/reports/redteam_vu.json`. Tools (all under
`redteam/` and `fixtures/`, no other lane's code touched):

- `verity_numerical.redteam.vu_forge_a` -- adversarial `run-vu` directories for Candidate A (real K=1536 VUs, one
  edit, every unit row still satisfies the unit circuit, the forger claims the word the edited chain leads to);
- `backends/redteam/vu-battery-b` (`redteam-vu-b battery|challenger`) -- adversarial `ChainAir` traces for
  Candidate B built with the lane's own witness generator plus imposed hints (`IntCtx::overrides`), run through
  the lane's constraint evaluator and the real Plonky3 prove + verify over Goldilocks and BabyBear, and a 10^5-sample
  audit of both challengers;
- `verity_numerical.redteam.leaf_v2_exhaustion` -- the leaf/v2 hiding break and the randomizer-exhaustion table;
- `backends/redteam/run_vu_battery.sh` / `fixtures/redteam/vu-battery/v1/run_battery.sh` -- reproduce all of it.

## 1. Findings

Status: **forged** = the real verifier accepted an input it must reject (or a privacy claim is concretely false);
**UNSAT** = the real verifier rejected the adversarial input and the evaluator names the constraint that fired;
**argued** = no input exists, with the reason; **open** = not settled tonight.

| # | target | attack | status | evidence / fixture |
|---|--------|--------|--------|--------------------|
| F1 | **B** `verity-direct` ChainAir, both fields | **statement binding: the verifier is handed no public values.** Two zero VUs (`a = b = 0`, `y16 = 0`) proved and verified "as" the two real VUs: accepted. Any satisfying trace is a proof of every statement (any `x`, `w`, claimed words, batch). | **forged** | `b_zero_batch_as_any_statement`, Goldilocks + BabyBear, `vu_battery_b_r20260922-070024-e7d1.json`. Fix owner: lane `direct` (B). PROTOCOL B 12.4 already says "not bound to an external statement" -- this is the accepted forgery that sentence describes. |
| F2 | **B** both fields | **batch size / degree unbound.** A proof of a 256-row (2-VU) trace is accepted by the verifier configured for `log_n = 19` (B = 4096): uni-stark 0.4.3 reads `degree_bits` from the *proof*; `log_n` only sizes the PCS. Combined with F1 a 2-VU proof passes as a 4096-VU proof. | **forged** | `b_degree_bits_unbound`, both fields, same run. Fix owner: lane `direct` (absorb `degree_bits`, AIR id, public words, `B`, `K` before `alpha`). |
| F3 | **leaf/v2** (`reference/leaf_v2.py`, note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2 5/6) | **hiding is false at t = 1.** The RS code is *systematic on the evaluation domain* (note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2 line 52: `codeword[(n/k) j] = message[j]`), so an opened column `c = (n/k) j` with `j < l` **is payload word j in the clear**, randomizers or not. Lemma 4.15 needs the message positions disjoint from the opened positions. At `n=16384, k=4096, l=3840, t=191`: 23.4 % of columns are systematic payload positions; **44.8 payload words per row, 2 865 per 64-row chunk, in the clear per proof**; `P(no clear word in a proof) = 7e-23`. Demonstrated at the reference's reduced code (`n=1024,k=256,l=192,t=48 <= 64 randomizers`): 11 payload words of one row read off the first session's openings and checked equal to the plaintext. | **forged** (privacy) | `python -m verity_numerical.redteam.leaf_v2_exhaustion` (1.3 s, laptop), `notes-asset:campaigns/r20-proof/assets/red-team-vu/reports/redteam_vu.json: leaf_v2.systematic_leak`. Fix owner: auth lane (encode on a coset disjoint from the message domain, or put the payload on the non-systematic positions / interpolate at ζ ∉ D as in Ligero). |
| F4 | **leaf/v2** | **randomizer exhaustion, quantified.** Beyond F3: the union `u` of opened columns leaves `u - rank(randomizer block)` linear relations on the payload. Reduced code: session 2 (`u = 90 > 64`) gives 26 relations: the true payload row is consistent, a payload with one word one bit off is not -- a payload-equality oracle after two sessions (false positive `p^-26`). Campaign code, m sessions: expected union `16384(1-(1-191/16384)^m)`; m=2: 124 relations (3.8 kbit of 61.4 kbit per row, 6.2 %), m=6: 43 %, full message determined at m ≈ 25 (`u >= k`); words are 16-bit so lattice/ILP recovery starts much earlier than the field-linear count. | **argued** + demo | same module, `campaign_projection` table |
| F5 | **A** `verity-gkr run-vu`, splice | VU 1 unit 40 takes `x.c` from VU 0's `y_39` (valid unit), units 40..95 re-chained honestly, claimed word = spliced chain's cast. PCS: `ligero: linear functional value mismatch`; `--clear`: `chain: VU 1 unit 40 incoming word differs`. | UNSAT | `fixtures/redteam/vu-battery/v1/a/a_splice` |
| F6 | **A**, `c_0 != 0` | VU 1 unit 0 chained from VU 0's `y32` (valid unit), rest honest, claimed word of that chain. Rejected in both modes. | UNSAT | `a/a_c0_nonzero` |
| F7 | **A**, epilogue `y32` | VU 0's epilogue row generated from an FP32 word whose cast is `word+1` (row self-consistent), public word `word+1`. `X_epi[0,y32] - X[(0,95),y] = 0` fires (PCS: linear functional mismatch). | UNSAT | `a/a_epilogue_y32` |
| F8 | **A**, epilogue claim | honest hints, `y16` column and public word `word+1`. Rejected by the *epilogue circuit* (`assertions: phase-1 round 0 sum mismatch`), not by the linkage. | UNSAT | `a/a_epilogue_claim` |
| F9 | **A**, public word / swapped words | honest witness, public word `word ^ 1`; two VUs' public words exchanged (each a real word). Both rejected (`X_epi[v,y16] = word_v`). **Answer to 1(iv): a prover cannot open a different word than the public input.** | UNSAT | `a/a_public_word`, `a/a_swap_words` |
| F10 | **A**, ρ ordering | `add_chain` is called after the Ligero commitment; `rho_geo` is squeezed from the transcript *after* `root`, circuit hashes, unit counts and public words are absorbed (`start_transcript` -> `commit` -> `add_chain`). The prover cannot know ρ before committing; a wrong linkage makes the batched functional a nonzero polynomial in ρ of degree < 401 408 -> field term `401 407 / 2^192 = 2^-173.4`. | argued | `backends/gkr/src/main.rs` `prove`/`verify` order; `PROTOCOL.md 12.2` |
| F11 | **A** statement binding | `start_transcript` absorbs the unit circuit hash, the epilogue circuit hash, unit counts (B, 96), the Ligero root and every public word before any challenge; `LIGERO` params are compile-time constants; K is fixed by the circuit hash. A proof for another circuit, another B or another word set changes every challenge. | argued | `main.rs::start_transcript` |
| F12 | **A/B** `+p` accumulator shadow (BabyBear battery `chain` class) | **B/BabyBear**: `x.c` limbs := limbs of `c_1 + p` (all downstream hints honest for those limbs): `vu.link[0]`, `vu.link[1]` (limb-wise), `x.c_hi.limbs`, `acc.s` fire; `c_0 := p` as limbs: `vu.first_c[0..1]` fire -- rejected. **B/Goldilocks and A**: `c + p` is not a distinct field element (`p > 2^32`, `c`,`y` single columns); the nearest witness `x.c = c + 2^32` is rejected (`x.c` range, `vu.link`). No shadow exists. | UNSAT / argued | `b_shadow_plus_p`, `b_c0_shadow_p`, `b_nonword_c`, `b_c0_nonword`; A: `a/manifest.json: not_representable` |
| F13 | **B** 95-row VU | row 95 dropped (`vu.next_first`); 95 rows with `last := 1` on step 94 and honest `inv` (`vu.last_key`, `vu.last_def`) | UNSAT | `b_vu95_drop`, `b_vu95_lastflag` |
| F14 | **B** 97-row VU | last row duplicated; a `step = 96` row appended (row-local constraints hold) -- `vu.next_first` fires in both | UNSAT | `b_vu97_dup`, `b_vu97_step96` |
| F15 | **B** step counter | skip (`step 5 -> 6`), restart mid-VU (`first=1, step=0, c=0` at row 48, rows 49.. honest for the restarted chain); a *wrapped* counter `95 + p` is the field element 95 -- not a distinct trace | UNSAT / argued | `b_step_skip`, `b_restart_mid_vu` |
| F16 | **B** flag flips | `first := 1` mid-VU (`vu.first_step`, `vu.first_c`, `vu.next_first`); `last := 1` mid-VU (`vu.last_key`); `last := 0` on step 95 (`vu.last_def`) | UNSAT | `b_first_flip`, `b_last_flip`, `b_last_zero` |
| F17 | **B** shared `last` row | VU 1 = its rows 0..94 + VU 0's last row (`vu.link`) | UNSAT | `b_shared_last` |
| F18 | **B** claim column | `claim ^ 1` on the last row (`vu.out`); arbitrary claim on non-last rows accepted **by design** (PROTOCOL B 12.4: read on `last` rows only) -- harmless only once F1 is fixed by binding the *last-row* claims | UNSAT / accept_by_design | `b_claim_last`, `b_claim_free_nonlast` |
| F19 | **B** Plonky3 0.4.3 weak Fiat-Shamir | the batch-combination `alpha` (two_adic_pcs.rs:330) and the FRI query indices are sampled **without absorbing the claimed openings at `zeta`** (`trace_local/next`, quotient chunks) or `degree_bits`; the verifier also never absorbs `public_values` even when given. Exploitability: the reduced openings depend on the claimed values only through two scalars (`sum_i alpha^i y_i` per opening point `zeta`, `zeta·g`), so matching a committed fold at 100 query points is 100 equations in 2 unknowns -- not forgeable at Q = 100 by this route; it is a checklist violation and the upstream fix (observe openings before `alpha`) should be taken when B binds its statement. | argued | source: `p3-uni-stark-0.4.3-succinct/src/verifier.rs:57-61`, `p3-fri-0.4.3-succinct/src/two_adic_pcs.rs:330`, `verifier.rs:27-60` |

Control cases: `a_honest` accepted in both modes; `b_honest` accepted over both fields; all evaluator-failing
counts are 0 exactly on the accepted cases and >= 1 on every UNSAT case (the evaluator and the verifier agree on all
36 B cases and 14 A runs).

The two B forgeries are **not** chain-linkage failures: every linkage / counter / flag attack is caught
(`OodEvaluationMismatch`). They are the missing statement: B's verifier proves "there exists a satisfying
ChainAir trace of some height" and nothing about *which* VUs. The fixture `run_battery.sh` exits 1 until the
`direct` lane absorbs `(degree_bits, AIR/circuit id, B, K, x, w, claimed words or their hash)` into the
challenger before `alpha` and checks the last-row claims against those public values (boundary constraints or a
public-value column).

## 2. Challenger / transcript audit (`TRANSCRIPT_CHECKLIST.md`)

### Candidate A (`backends/gkr/src/transcript.rs`, `main.rs`, `ligero.rs`)

- Absorbed before the first challenge: domain tag, unit circuit hash, epilogue circuit hash, `B`, 96, Ligero
  root, all `B` public words (`start_transcript`). Batch size, K (via the circuit hash) and the circuit identity
  are pinned. The Ligero `Params` are compile-time constants (not absorbed -- acceptable only because the binary
  *is* the verifier; a serialized verifier would have to absorb `k, n, t`).
- Challenge derivation: SHA-256 chain, `squeeze_fp` rejection-samples 64-bit words below `p`; extension elements
  are three independent squeezes. No challenge is reused: each sumcheck round squeezes after absorbing that
  round's polynomial; the layer-merge coefficients, `rho_geo` (chain), the Ligero row coefficient `r` and the
  opening set are separate squeezes in fixed order.
- **Ligero parameters from the code**: `k = 4096, n = 16384` (rate 1/4), `t = 192`, no randomizers (`l = k`,
  non-ZK), challenge field Goldilocks^3 (`|F| = 2^192`, `Ext([Fp;3])`). Recomputed terms (accountant
  `appendix_c`, `e = floor((n-k)/2) = 6144`): IRS query `(1 - 6144/16384)^192 = 2^-130.2`; linear query
  `((k+l)/n)^t = (1/2)^192 = 2^-192`; IRS field `(n+1)/2^192 = 2^-178`; linear field with the geometric ρ over
  401 408 constraints `2^-173.4`. **Total 2^-130.2**, meets 2^-128; the query term dominates and is what `t=192`
  buys. If the ZK payload `l = 3840` is adopted the linear query term is `(7936/16384)^192 = 2^-200.7`; unchanged.
- **Mismatch (documentation, not soundness)**: `ligero::row_coeffs` combines the IRS rows with *powers of one*
  challenge `1, r, r^2, ...`, while `security.accounting.ligero_error` states "the IRS test keeps uniform row
  coefficients in both modes (no geometric-sequence proximity statement is relied on)". The code relies on the
  parametrised-curve proximity gap (BCIKS20 Thm 1.5, degree `rows - 1`); at `B = 4096` (`rows ≈ 6.2e4`) the
  induced field term is `rows·(n+1)/2^192 ≈ 2^-162` -- immaterial at 2^192, but the accountant's row for A must
  say `combination = powers` for the IRS test too, or the code must draw `rows` independent coefficients.
- `open_set`: `challenge().0[0] mod n`; `p ≡ 1 (mod 2^14)` so the bias is `1/p`; duplicates re-drawn.

### Candidate B (`backends/direct/src/challenger.rs`, `stark.rs`, Plonky3 0.4.3-succinct)

- **The fork is right.** `FixedSerializingChallenger64::sample`: `log_size = 64` for Goldilocks; upstream computes
  `(1u64 << 64) - 1`, which wraps to `0` in release (debug: overflow panic), so every sample masked to 0 -- the
  audit reproduces it: 1000/1000 zeros from the unmodified `SerializingChallenger64`. The fork masks with
  `u64::MAX` when `log_size >= 64` and rejection-samples below `p`. 10^5 samples: 0 zeros, 0 out of range,
  chi² low byte 252.5 (256 bins, 99.9 % quantile 330.5), chi² 16 buckets of `[0,p)` 10.7 (quantile 37.7);
  Goldilocks² coordinates independent (0 equal pairs in 5·10^4).
- **BabyBear path**: unmodified `SerializingChallenger32` (`log_size = 31`, mask `2^31 - 1`, rejection below `p`):
  10^5 samples, 0 zeros, chi² 231.4 / 18.0 -- sound.
- **Transcript bytes (B-AIR, FS)**: `HashChallenger<u8, Keccak256, 32>`: `observe` appends raw bytes (no tag, no
  length prefix); `sample` flushes when the output buffer is empty: `out = Keccak(input_buffer)`, `input_buffer :=
  out` (32-byte chaining). Order: `trace_commit` (32 B) → `alpha` (ext) → `quotient_commit` (32 B) → `zeta` →
  PCS `alpha` → per fold: commit (32 B) → `beta`; `final_poly` (ext, 8 B per coordinate LE) → PoW: `observe(witness)`
  and `sample_bits(16) == 0` → 100 × `sample_bits(log_max_height)`. **Never absorbed**: `degree_bits`, AIR identity
  / width, FRI parameters, public values (`prove_with`/`verify_with` pass `vec![]`), the opened values at `zeta`.
  The first two are F1/F2; the last is F19.

## 3. ZK open items (note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction 7-8)

1. **Conditioned pole-redraw under HM96 coins (rule as specified, 3.4 / PROTOCOL A 5.1).** Step 0 commits
   `S = 2` slots `z_T^(1), z_T^(2)` per table with every other coin; the prover opens/uses the first slot with
   `z_T^(i) ∉ Img_T = {T(β_T)}` over the *public* table; if both lie in `Img_T` the prover aborts (public event).
   Soundness bound: the prover learns nothing about a committed slot (statistical hiding 2^-160), so the used
   `z_T` is uniform over `F_c \ Img_T` and the pole term is `|T| / (|F_c| - |T|)` per table -- identical to the
   unconditioned bound up to a factor `1/(1 - |T|/|F_c|)`; with `|T| ≤ 2^18` and `|F_c| = 2^192 (A) / 2^128 (B)`
   the completeness loss is `P(both slots in Img_T) = (|T|/|F_c|)^2 ≤ 2^-220`. **Grinding is not available to
   either party**: the prover cannot bias coins it cannot see; a malicious *verifier* pre-committing `z = T(β)`
   for a guessed witness value hits `Img_T` by construction (honest witness ⇒ `w ∈ T`) and is redrawn -- the probe
   returns the public answer "in the image" for every honest witness, i.e. nothing. **argued: bound given, no
   attack.** Residual: the rule must be evaluated on the *opened* slot values only after the HM96 opening checks
   (item 7.2 of the checklist); a prover implementation that peeks at slot 2 before slot 1 is opened is not a leak
   but breaks the transcript's determinism.
2. **Abort leakage across sessions.** Prover aborts are functions of `(verifier messages, public data)` only
   (three cases, 3.2) -- trivially simulatable. Verifier-chosen aborts at round `i`: everything `V*` has seen is
   `com_1` (Merkle root over statistically hiding leaves, `n·2^-160` union) and padded/blinded messages that are
   uniform given the committed coins (HVZK simulator of section 2); the abort decision is therefore a function of
   a simulatable view, and the transcript prefix is output verbatim. Across sessions on the same witness the views
   are independent **iff** all randomness (pads, randomizers, blinding rows, HM96 strings, salts) is fresh and the
   Ligero budget is per *session* (`t ≤ k - l` with fresh randomizers per session) -- then the union of `m`
   session views is the union of `m` independent simulatable views. **The only leak is randomizer reuse**, which is
   exactly F3/F4 in leaf/v2 (there the commitment is *long-lived* by design, so "fresh randomizers per session" is
   impossible and the budget is per commitment lifetime -- and the systematic positions leak even inside the
   budget). For the VU protocols: argued, no leak, conditional on the per-session re-randomisation item 7.4.
   Simulator caveat (item 7.10): Goldreich-Kahan rewinding needs the estimate-`p_abort` step when `V*` aborts with
   probability close to 1; the sketch in 3.2 omits it -- **open** (proof gap, not a leak).
3. **PRG seed handling.** ZK_CONSTRUCTION 7.5 requires a per-session seed never derived from the witness; the
   *reference* `leaf_v2.py` derives randomizers as `SHA-256(seed | canonical_id | row)` with a caller-supplied seed
   and rejection-sampling below `p` (no modulo bias) -- correct, but the seed is a *per-commitment* secret (the
   opening key), so any two proofs reuse the same randomizers by construction (F4). The ZK reference
   (`security/zk_reference.py`) draws pads with `secrets`/`random` per session -- fine at the reference level; no
   GPU PRG exists yet to audit. **open** (nothing to test).
4. **B-AIR Fiat-Shamir domain separation: which bytes.** Listed in section 2 above. Missing versus checklist 7.7:
   no length prefixes or tags on absorbed messages (safe only because every absorbed object has a fixed byte length
   for a fixed AIR and `degree_bits` -- which are themselves not absorbed: F2); `(K, B, C, profile, code
   parameters)` not absorbed; the grinding witness *is* absorbed (`check_witness` observes it before `sample_bits`);
   query-index derivation is separated from challenge derivation only by order in the same chain.

## 4. leaf/v2 algebraic binding (note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2, `reference/leaf_v2.py`)

- **Digest binding.** The digest is `H(canonical_id | dtype | shape | code.text | chunk roots)`; a chunk root is a
  Merkle root over `H(chunk, column, column bytes)` leaves. Two tensors with the same digest need equal chunk roots
  ⇒ equal column leaves (CRH) ⇒ equal tableau columns *as committed*. The IRS test (`t = 191`, rate 1/4, unique
  decoding `e = 6144`) guarantees each row is within `e` of a unique codeword with error `(1 - e/n)^t = 2^-129.5`
  per proof (plus `(n+1)/|F_c|`): a dishonest committer can commit a row that is *not* a codeword, and the word it
  "binds" is the unique nearest codeword's payload -- so binding holds for the decoded payload, not for the
  committed bytes. Two *different* tensors: their nearest codewords differ in ≥ `d = n - k + 1 = 12 289` positions,
  the committed rows differ in ≥ `d - 2e = 1` position ⇒ different leaves ⇒ different roots. **argued**.
- **Malleability (add a codeword to the leaf).** The tableau is Merkle-committed column-wise with `(chunk, column)`
  in the leaf preimage; adding a codeword to a row changes every column's leaf and the root, so the digest changes:
  the *commitment* is not malleable. The *linear test* is: it proves `U_V[row][j] - U_P[rho][j'] = 0` under a
  verifier challenge, and a prover holding both tensors can satisfy it for any pair of rows differing by a codeword
  that is zero on the payload positions -- which is exactly the randomizer freedom, not an attack. **argued**.
- **Cross-tensor confusion.** `canonical_id`, `dtype`, `shape`, `code.text` are in the digest preimage; the
  randomizer PRG is keyed by `canonical_id | row`. Two tensors with equal chunk roots but different ids have
  different digests. The *proof*, however, refers to a tensor only by digest: check (not done here) that the
  statement the VU proof binds (F1 for B) carries the digest, otherwise the algebraic equality `x = W row` is to an
  unnamed tableau. **argued**, conditional on the statement binding of the host proof.
- **Randomizer exhaustion.** F3 (hiding false at any `t` because of systematic positions) and F4 (quantified
  linear leak beyond the budget: 26 relations at the reduced code after two sessions; 6.2 % of every row's bits
  after two campaign-size sessions; whole message at ≈ 25). **forged (privacy)**.
- **"The verifier needs no byte-hash equality."** True as stated: the linear test replaces `SHA-256(x) == leaf`
  with an algebraic equality against the committed tableau; what the verifier *does* need is that the tableau it
  opened columns of is the one named by the digest in the statement -- i.e. the chunk roots must be absorbed into
  the host proof's transcript and the digest must appear in the host statement. In B today (F1) nothing is, so
  leaf/v2 riding B's opening binds to nothing. **argued**.

## 5. Ledger

Component entries `red-team-vu` (track `shared`, scope `component`): F1+F2 `--breakthrough` ("B accepts any
satisfying trace as any statement; direct lane must fix"), F3 `--breakthrough` ("leaf/v2 systematic encoding leaks
payload words in the clear; auth lane must fix"), one UNSAT entry per prover for the chain-linkage battery, one
for the challenger audit. Plots regenerated (`notes-asset:campaigns/r20-proof/assets/synthesis/reports/plots/overhead_red-team-vu.png`).

## 6. Not done / open

- The A battery ran at `B = 4` (the negatives tier has the operands for `B ≤ 52`); the linkage constraints scale
  linearly and nothing in `add_chain` depends on `B` beyond the loop -- but a `B = 16` run is cheap and should be
  added to the fixture when `vu-k1536` positives are exported on the pod.
- No `--check-witness` was added to A (`lane/a-babybear` not on main at 3e959ae); the Goldilocks argument (F12)
  makes the BabyBear `chain` shadow class moot for A as it exists. A BabyBear port of A must re-run F12 limb-wise.
- Malicious-verifier simulator gap (3.2 / item 7.10): open, proof-level.

## 7. Fixes (lane `soundness-fixes`, 2026-09-22; branch `lane/soundness-fixes`)

Gate run `r20260922-073904-7a6c` on vy-cpu3 (AMD EPYC 7713 slice, 16 threads): unit negatives (23) + `chain.rs`
(6, incl. `statement_suite`, `operand_binding_goldilocks`) + `statement.rs` (4) pass in release; `vu-neg` 52/52
rejected over both fields; `vu-bench` 64 VUs bound over both fields (+ BabyBear with `--bind-operands`);
**`fixtures/redteam/vu-battery/v1/run_battery.sh` exits 0: 36 B cases, 0 FORGED**, A 14/14 as before.

| finding | status | commit | what changed | check that fires / pinning test |
|---|---|---|---|---|
| F1 statement unbound (B, both fields) | **fixed** | `3fe85aa` | `direct/src/statement.rs` + `stark.rs::{prove_bound, verify_bound, verify_bound_bytes}`: the statement (every claimed `y16`, optionally `x`,`w`) is the verifier's input. Header absorbed into the challenger **before any challenge**: domain tag `verity-direct/stmt/v1`, AIR id (SHA-256 of field, layout, constraint names), field prime, width, challenge-extension degree, `B`, `K`, `STEPS`, rows, `degree_bits`, FRI `log_blowup/num_queries/pow_bits`, every claimed word, `sha256(x)`, `sha256(w)`. The claim column `vu.y16` is a **public column**: the verifier evaluates its own copy of the column polynomial `W` (barycentric on the trace domain, `statement::eval_pair`) and requires `opened.trace_local[col] == W(ζ)` and `trace_next[col] == W(ζ·g)`. Soundness: the opened row is bound to the committed trace by the PCS; a committed column `C != W` with `C(ζ) = W(ζ)` needs ζ a root of a nonzero degree-`< n` polynomial: `+ n / |F_c|` per public column (`2^19 / 2^124 = 2^-105` BabyBear^4 at `B = 4096`, added to the accounting; `2^-173` Goldilocks^3). Not `AirBuilderWithPublicValues`: 4096 raw public values would enter every constraint evaluation; the column check costs the verifier one barycentric evaluation per public column. | `BoundError::StatementColumn{vu.y16}` / battery `StatementColumnMismatch(vu.y16 = column 2843|2899 at zeta)` on `b_zero_batch_as_any_statement` (both fields). Pins: `direct/tests/chain.rs::statement_suite` F1a (zero batch as real statement), F1b (one word changed / two words swapped), F1c (other FRI params); `operand_binding_goldilocks` (operand flip rejected with `--bind-operands`). Side effect: `b_claim_free_nonlast` (F18) is now **rejected** too: the column is bound at every row, not only `last` rows. |
| F2 `degree_bits` from the proof (B, both fields) | **fixed** | `3fe85aa` | `verify_bound_bytes` computes `degree_bits` from `Statement::rows()` = `next_pow2(max(B·96, MIN_ROWS))` and rejects a proof carrying anything else *before* anything is absorbed or verified; the value is also in the absorbed header. `log_n` is no longer a verifier argument. | `BoundError::DegreeBits{expected: 19, got: 8}` / battery `DegreeBitsMismatch(expected 19, proof says 8)` on `b_degree_bits_unbound`. Pin: `statement_suite` F2. |
| F19 FS absorption gaps (B checklist) | **partially fixed** | `3fe85aa` | Public values, `degree_bits`, AIR id, field, FRI parameters, `B`, `K` absorbed before the first challenge (header above) -- done. **Residual, documented in `PROTOCOL.md` 12.5:** the openings at ζ are still not absorbed before `alpha` and the FRI query indices: that sampling is inside `p3-fri 0.4.3::verify_shape_and_sample_challenges`, reached through `Pcs::verify`; changing it means patching `p3-fri` (the fork pins `-succinct` crates), which this lane did not do. The red team's argument stands: 100 (now 166) query equations in 2 unknowns, not forgeable by this route; it remains a checklist violation to close at the Plonky3 bump. Domain tags: the header's tag is the only domain separation; raw Keccak chaining otherwise unchanged. | `statement.rs` unit tests (`header` pins the field order and the words); `TRANSCRIPT_CHECKLIST.md` wave-3 items. |
| F3 leaf/v2 systematic RS leaks payload (privacy) | **fixed** | `7232e27` (+ docs `354b3ba`) | Codeword domain moved to the coset `31·H_n` (BabyBear's generator, `∉ H_n ⊇ H_k`): disjoint from the message domain, so no codeword symbol is a message symbol. `code_text` gains `/coset=31`; `encode_row` = coset NTT, `decode_row` = coset INTT, prover/verifier evaluate `v`, `q`, `r_i` at `η_c = 31·g_n^c`. The committer's "free systematic quarter" is gone (all `n` symbols computed); the b-encode lane's cosets-only kernel is 31.6 vs 32.2 ms, so no `explore.tensor` / `zk_cost` number moves. `note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2` 2/4/5/6, `note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 2.1, `note:r20-proof/auth-integration/20260922T0737Z-report-auth-integration` privacy column + item 7 updated. | `tests/reference/test_leaf_v2.py::test_no_opened_column_is_a_payload_word` (opens every column of every chunk; the old encoding is shown to expose every word, so the test is not vacuous); `redteam.leaf_v2_exhaustion` now reports `payload_words_in_clear = 0` in every session (`leaf_v2_exhaustion.json` regenerated; `campaign_clear_words` 0.0/row, the pre-fix row kept as `campaign_clear_words_before_fix`). |
| F4 randomizer exhaustion (leaf/v2) | **stays true, stated** | `354b3ba` | Not a bug the coset fixes: `oracle = True` from session 2 at the reduced code, row determined at ~25 campaign sessions, unchanged. `note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2` 6 now says so and names the only fix -- re-randomisation per session -- as a protocol-owner decision (0.6 s per weight re-commitment vs one private proof per commitment). | `leaf_v2_exhaustion.json` `oracle`, `campaign_projection` |

### 7.1 Carried to the LogUp realisation and the F19 residual closed (lane `b-bind`, 2026-09-22; branch `lane/b-bind`)

`lane/soundness-fixes` was merged onto `main` (b-lookup's LogUp realisation, the latency lane's `--rtt-ms` hooks)
by this lane; the LogUp prover/verifier (`lookup_stark.rs`, a fork of uni-stark with two extra rounds) had shipped
with the pre-fix behaviour -- no statement, `degree_bits` from the proof -- which red-team-3's `redteam-logup-b`
battery exercises as `zero_batch_as_any_statement` and `degree_bits_from_proof` against `verify_lookup`. Gate run
`r20260922-091130-525e` (vy-cpu3, 12 threads): 42 tests incl. `tests/lookup_statement.rs` (5, 2^17 rows) green,
`vu-neg` 52/52 in limb and `--lookup` mode over both fields, 64-VU bound proofs in every mode, `run_battery.sh` exit
0 (36 B cases 0 FORGED), babybear-rules battery `--lookup` 83/83 + 87/87 controls + 6/6 extras. PROTOCOL.md 14.7-14.8.

| attack (LogUp path, `vu-bench --lookup`) | before (`verify_lookup`, b-lookup as merged) | after (`verify_lookup_bound_bytes`) | pin |
|---|---|---|---|
| F1a zero batch (two zero VUs) offered as the proof of two real words | **ACCEPTED** (no statement; the words are witness cells) | `StatementColumnMismatch(vu.y16 at zeta)`: the round-1 main column is checked at ζ, ζ·g against the verifier's word polynomial | `lookup_statement.rs` F1a, BabyBear^4 / ^5 / Goldilocks |
| F1b honest proof, one word changed / two words swapped in the statement | ACCEPTED (same) | `StatementColumnMismatch` | F1b |
| F1c other FRI parameters at the verifier | ACCEPTED if the proof shape matches (parameters not in the transcript) | header differs -> every challenge differs -> `InvalidOpeningArgument` | F1c |
| F2 2-VU (2^17-row) proof for the 4096-VU verifier | **ACCEPTED** (`degree_bits` and the table height taken from the proof; red-team-3 `degree_bits_from_proof`) | `DegreeBitsMismatch(expected 19, proof says 17)` before anything is absorbed | F2 |
| F2' the same words at the limb realisation's height (8 bits) | n/a | `DegreeBitsMismatch(expected 8, proof says 17)`: the height is the tables', `Statement::min_rows` | F2' |
| table substitution: verifier holds a table set with one entry changed | rejected only through the recomputed preprocessed commitment (the verifier's challenges did not depend on its tables) | header carries `sha256(table set)` -> challenges differ; the commitment check stays | `lookup_statement.rs`, `vu-bench --lookup` inline |
| table substitution: prover commits its own `P` (honest trace) against the honest verifier | `InvalidOpeningArgument` (commitment compare) | the same, plus the header digest | same |
| operand flip with `--bind-operands` | n/a (no operands in the statement) | `StatementColumnMismatch(x.a[7])` | `lookup_operand_binding_babybear` |
| F19 residual: ζ-openings not absorbed before α / the query indices (both realisations) | checklist violation (`p3-fri 0.4.3::TwoAdicFriPcs::{open, verify}` sample α first) | **closed**: vendored `p3-fri` (`backends/direct/vendor/p3-fri`, `[patch.crates-io]`), openings absorbed before α in `open` and `verify`; **transcript changed**; `rounds.sequential_depth` +1 | gate + timing run `r20260922-094310-af1a` (42 tests, vu-neg 4x52/52, both batteries green on the patched transcript; `sequential_depth` 16 -> 17 limb, 21 -> 22 LogUp) |

Statuses: F1 **fixed in both realisations**; F2 **fixed in both realisations**; F19 **fixed** (header 3fe85aa, openings-before-α
this lane); F3/F4 leaf/v2 unchanged from above. The `verify_lookup` entry point remains for the diagnostic tests and
the `--unbound` timing baseline and labels its results `statement_binding.bound = false`.

**B + LogUp at 2^-128 (BabyBear, 4096 VUs, 166 queries, PoW 16), bound vs unbound, same box, back to back, twice:**
Cost of the binding (run `r20260922-094310-af1a`, vy-cpu3, 12 threads, LogUp realisation, 4096 VUs, 2^19 rows,
bound and unbound back to back, twice): BabyBear^4 prove 199.4 / 182.8 s bound vs 197.6 / 201.8 s unbound;
BabyBear^5 213.3 / 217.5 s bound vs 225.4 / 218.1 s unbound. The difference is inside the box's own repeat-to-repeat
swing (~10%); the binding adds a header absorption and one barycentric public-column evaluation. Same box caveat as
before: vy-cpu3 is ~3.2x slower than the vy-cpu2 that recorded the unbound 60.1 s / 70.4 s (PROTOCOL.md 14.5).

**Re-timed B at 2^-128 (BabyBear, 4096 VUs, 166 queries, PoW 16), statement-bound:** `t.total` 544.8 s = witness
42.0 s + prove 502.9 s (run `r20260922-080527-f30c`; 553.1 s in the gate run), verifier 0.61 s, proof 3.45 MB, peak
RSS 30.6 GB, `overhead.vs_native_peak` 1.35e10 -- on vy-cpu3, a shared-host EPYC 7713 slice ~3x slower than the
b-chain lane's vy-cpu2 (168 s). **Cost of the fix:** the pre-fix `--unbound` path on the same box measured 426.4 s
and 485.4 s total in two runs (prove 384.0 / 437.8 s); six alternating 512-VU runs (`r20260922-082522-3e97`) gave
prove bound 45.4 / 46.2 / 64.8 s vs unbound 37.4 / 68.2 / 61.5 s: the box swings 40 % within minutes and the sign of
the difference flips, so no fix cost is resolvable above the machine noise. Algorithmically the prover adds one
SHA-256 over the 4096 words, ~20 challenger observes and one O(n) column compare; the verifier adds one O(n)
barycentric evaluation per public column (+0.05-0.1 s measured: 0.55-0.66 s vs 0.53-0.55 s). Result files:
`notes-asset:campaigns/r20-proof/assets/b-air/results/vu_babybear_q166_bound_r20260922-080527-f30c.json` and
`..._UNBOUND_BASELINE_...json` (the latter is a timing baseline, not a proof number).

Ledger: `soundness-fixes.jsonl` -- `vu` entry "B full VU, statement-bound (SOUNDNESS FIX F1-F3)" (`--breakthrough`,
run `r20260922-073904-7a6c`, timing pair `r20260922-080527-f30c`) and `component` entry "leaf/v2 non-systematic RS on
coset 31*H_n (PRIVACY FIX F4)" (`--breakthrough`). Statuses in `notes-asset:campaigns/r20-proof/assets/red-team-vu/reports/redteam_vu.json` flipped to `fixed` with the commits.
