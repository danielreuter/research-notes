---
id: r20-proof/red-team-3/20260922T0921Z-report-redteam-3
campaign: r20-proof
lane: red-team-3
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/redteam_3.md
---

# red-team-3: forgeries against the wave-3 cryptographic machinery

Lane `red-team-3` (`lane/red-team-3`, rebased on main 147a6f8 -- the b-ligero2 statement-binding merge is in; the
`lane/soundness-fixes` lane is **not** merged as of this run, so T4 is a read-only review).  Machine-readable
twin: `notes-asset:campaigns/r20-proof/assets/red-team-3/reports/redteam_3.json`.  Fixtures: `fixtures/redteam-3/` (`manifest.json` + the two battery outputs), loader
test `backends/numerical/tests/redteam/test_redteam_3_fixtures.py`.  Accepted forgeries are also in
`note:r20-proof/red-team-3/20260922T0904Z-finding-redteam-3-urgent` and on the ledger (`ledger/red-team-3.jsonl`, `component` scope).

Harnesses (committed, not merged into any prover):

* T1 `backends/redteam/logup-b` -- a Rust binary linked against `verity-direct` that builds adversarial
  `(main, aux, preprocessed)` triples for `LookupChainAir` and drives `prove_lookup`/`verify_lookup` with a
  prover configuration and a *separately chosen* verifier configuration (`redteam-logup-b battery --root
  fixtures/bench-instances/v1 --out DIR --queries 8`).  Before proving, every forged triple is run through the
  constraint evaluator (`LookupEvaluator`) so the report says *which* constraint rejects.  Run
  r20260922-085839-3976 on vy-cpu3, BabyBear^4, 2 real VUs of `vu-k1536-neg`, 2^17 rows, 391 queries/row.
* T2 `verity_numerical/redteam/gpu_a_forge.py` -- builds forged `prover.Instance`s (re-chained units, forged
  epilogues, out-of-table queries, a substituted table) and mutated `prover.Proof`s and runs them through the
  Python `gpu.prover.verify` with the verifier's own instance (`--vus 2 --device cpu`, on vy-sp1; the CPU path
  is the same code with `device="cpu"`).  `k=4096, n=16384, t=192`.

## 1. Attack table

| # | Target | Class | Case | Construction | Result | Severity | Fix / owner |
|---|--------|-------|------|--------------|--------|----------|-------------|
| 1 | T1 LogUp | control | `honest` | 2 real VUs, prover = verifier config | ACCEPTED (expected) | -- | -- |
| 2 | T1 LogUp | statement binding (F1) | `zero_batch_as_any_statement` | prover proves two all-zero VUs; verifier "checks" the statement of the two real VUs (words 48849, 16299) | **ACCEPTED -- FORGERY** | critical | bind the statement in `prove_lookup`/`verify_lookup` exactly as `stark.rs::verify_bound_bytes` does for the limbs path; **soundness-fixes / b-lookup** |
| 3 | T1 LogUp | degree from proof (F2) | `degree_bits_from_proof` | verifier configured for log_n = 19 (4096 VUs) builds the table at `1 << proof.degree_bits` (what `main.rs` does via `pre.clone()`); 2^17-row proof | **ACCEPTED -- FORGERY** | high | `verify_lookup` takes `log_n` from the verifier config and rejects `proof.degree_bits != log_n`; `main.rs` builds `pre_for_verify` from `tables.preprocessed(1 << cfg_log_n)`; **soundness-fixes / b-lookup** |
| 4 | T1 LogUp | degree from proof (F2) | `degree_bits_pinned_by_pre_height` | same, verifier hands over its own 2^19-row table | REJECTED `InvalidProofShape` | -- | (shows the one-line fix suffices) |
| 5 | T1 LogUp | multiplicity / out-of-table | `oot_query_adversarial_helper` | `x.c_lo := 70000` (outside T16) on row 2; the helper of its group holds exactly `1/(z - q*)` so `lookup.helper` passes; `g`, `S` re-accumulated | REJECTED (`lookup.sum_last` fires; FRI `OodEvaluationMismatch`) | -- | -- |
| 6 | T1 LogUp | multiplicity credited | `oot_query_mult_credited` | as 5, plus `m[65535] += 1` (histogram total preserved) | REJECTED (`sum_last`) | -- | -- |
| 7 | T1 LogUp | multiplicity negative/wrapped | `oot_query_mult_negative` | as 5, `m[65535] -= 1` (a `p-1` wrap where it was 0) | REJECTED (`sum_last`) | -- | -- |
| 8 | T1 LogUp | padding-row multiplicity | `padding_row_multiplicity` | `m := 1` on the first padding row of P (all-zero tuple, tag 0), `g := 1/z` there, `S` re-accumulated | REJECTED (`sum_last` only -- clean isolation of the identity) | -- | -- |
| 9 | T1 LogUp | table binding | `table_row_substitution` | prover commits a table matrix whose T16 has a 65537th row (65536) and queries it | REJECTED `InvalidOpeningArgument` (verifier recomputes P from the public table set, compares `pre_commit`) | -- | -- |
| 10 | T2 GPU A | control | `honest` | 2 real VUs | ACCEPTED (expected) | -- | -- |
| 11 | T2 GPU A | chain linkage | `splice` | VU 1 re-chained from step 40 with VU 0's word 39 | REJECTED (`ligero: linear functional value mismatch`) | -- | -- |
| 12 | T2 GPU A | chain linkage | `c0_nonzero` | VU 1 starts from VU 0's y32 instead of 0 | REJECTED | -- | -- |
| 13 | T2 GPU A | epilogue | `epilogue_y32` | epilogue row for a different y32 that casts to y16+1; public word y16+1 | REJECTED | -- | -- |
| 14 | T2 GPU A | epilogue | `epilogue_claim` | epilogue's y16 cell != public word | REJECTED (`phase-1 round 0 sum mismatch`) | -- | -- |
| 15 | T2 GPU A | statement | `public_word` | honest witness, verifier's public word +1 | REJECTED | -- | -- |
| 16 | T2 GPU A | statement | `swap_words` | verifier's two words swapped | REJECTED | -- | -- |
| 17 | T2 GPU A | LogUp multiplicity | `logup_oot_mult` | out-of-table query with a compensating multiplicity on a real row (prover's `multiplicities` monkeypatched) | REJECTED (`LogUp level 0: final check`) | -- | -- |
| 18 | T2 GPU A | LogUp table binding | `logup_table_subst` | prover's R16 table has a 65537th row (65536) and queries it; verifier uses its own table | REJECTED (`phase-1 round 0 sum mismatch`) | -- | -- |
| 19 | T2 GPU A | proof malleation | `proof_noncanonical_msg` | `msgs[5][0] += p` (non-canonical, same residue) | REJECTED (`LogUp level 1: final check` -- see observation O5) | -- | -- |
| 20 | T2 GPU A | Merkle | `opening_column_swap` | two opened columns' (values, paths) exchanged | REJECTED (`merkle path`) | -- | -- |
| 21 | T2 GPU A | Merkle | `opening_path_truncated` | one path shortened by a node | REJECTED (`opening shape`) | -- | -- |
| 22 | T2 GPU A | proof malleation | `opening_column_value_plus_p` | one opened column entry `+ p` | REJECTED (`non-canonical column value`) | -- | -- |
| 23 | T2 GPU A | shape from proof (F2 class) | `opening_fewer_columns` | opening with t-1 columns | REJECTED (`malformed opening`) | -- | -- |

**Accepted forgeries: 2 (both T1, both inherited wave-2 classes that the LogUp realisation never received).**
**T2: 0 of 13.  T3/T4: review only (below), no forgery constructed.**

Must-reject cases added to the 83-case BabyBear battery: **none** -- every case above attacks the verifier
contract or the commitment/transcript layer, not a witness of the WP2 relation, so none generalises to the
witness-level battery (count unchanged).

## 2. T1 -- B-AIR LogUp realisation: what the code does (answers to the brief)

*Who commits the table, and when.* `prove_lookup` commits the padded preprocessed matrix `P` (116,722 table rows
in 6 columns, zero-padded to `2^log_n`) and observes `pre_commit` **first**, then `main_commit`, then samples
`z, beta`; the aux round follows and `alpha` is sampled after `aux_commit` (`lookup_stark.rs` prove and verify are
symmetric).  The verifier **recomputes** `P` from the public `TableSet` and compares commitments (case 9).  So
(a) table binding holds -- *provided the verifier builds `P` from its own configuration*: `main.rs`'s
`vu_bench_lookup` passes `pre.clone()`, the prover's matrix, which is what makes case 3 accept.

*Multiplicities / out-of-table (b).* Multiplicities live in the main trace committed before `z`; helpers
`h_j = 1/(z - Σ beta^c q_c)` are constrained by `h*(z - q) = 1` on **every** row including padding
(`eval_lookup` has no row selector on `lookup.helper[*]`; the padding rows of `zero_vu()` carry valid zero
queries and get helper values).  A zero denominator would need `z = comb(q)` for a base-field tuple against an
extension-field `z`: probability `(N_q)/|F|`, inside the identity term.  The identity is a rational-function
identity in `z`; cases 5-8 confirm the only constraint that fires when the helpers are made locally consistent
is `lookup.sum_last`, i.e. the sum check is doing the work and it cannot be balanced by an integer or wrapped
multiplicity because the adversarial term `1/(z - q*)` is not in the span of table terms.

*Running sum (c).* Per row `row_sum = Σ_j h_j - g` where `h_j = Σ_{i in group j} 1/(z - q_i)` is one *batched*
helper per group (`h_j * Π(z - v_i) - Σ_i Π_{k != i}(z - v_k) = 0`) and `g (z - t) - m = 0` is the table side;
`sum_first: (S - row_sum) * first = 0`, `sum_step: (S' - S - row_sum') * transition = 0`,
`sum_last: S * last = 0`.  Padding rows carry `g` from their all-zero preprocessed tuple and zero multiplicity
(so `g = 0` is forced) and helpers from the zero VU's valid queries, so the wrap across padded rows is just more
terms of one sum (case 8 forges exactly one such term and is caught by `sum_last` alone).  A zero denominator in
a batched helper makes `Π = 0` and the constraint collapses to `Σ_i Π_{k != i}(z - v_k) = 0`, which is nonzero
for a single vanishing factor: unsatisfiable, not exploitable.

*Challenge order (e).* Nothing is sampled before what it must depend on **inside the argument**; the failure is
that nothing *outside* the trace is absorbed at all (case 2) and the degree is prover-chosen (case 3).

*`check-rows` battery path (f).* `air::lookup_failing_rows` evaluates program + helper constraints per row with
fixed `z, beta`, **skips** the four global constraints (`lookup.table`, `lookup.sum_first/step/last`), uses zero
multiplicities and a zero `P`, and substitutes "query in table?" (the `INVALID` sentinel from the Rust query
mapper) for the identity.  So the battery exercises the *row-local* LogUp constraints and table membership by
construction, **not** the sum check or table binding; the coverage record in the fixture (`coverage`) shows that
for case 5 the check-rows path reports `lookup.helper[0]` + `lookup:x.c_lo` (the honest prover's helper) while
the constraint that rejects the proof is `sum_last`, which check-rows never evaluates.  Not a soundness bug (the
battery is a checker for witnesses, the full prover is gated separately) but the README should not describe the
`--lookup` battery as covering the LogUp argument.

## 3. Soundness-bound recomputations vs claims

| Term | Claim | Recomputed from code | Verdict |
|------|-------|----------------------|---------|
| T1 LogUp identity, BabyBear^4, B=4096 (2^19 rows, 391 q/row, 116,722 table rows, `N_COLS=6`) | 2^-93.8 (PROTOCOL.md 14.4 / README) | `lookup_soundness_bits(2^19, 391, 116722, ext_bits)` = **93.80**; structurally `(N_q+N_t) + N_COLS*N_q` over |F_ext| -- the two-variable Schwartz-Zippel in (z, beta) gives `N_COLS*(N_q+N_t)`, +0.0006 bits; padding rows *are* in N_q (they carry queries), the formula already counts 2^19 rows | **matches** |
| T1 LogUp identity, BabyBear^5 | 2^-124.8 | same formula at 5x30.9 bits: 124.7-124.8 | matches |
| T1 FRI term | 2^-128.6 | not re-derived (Plonky3 diagnostic PCS, out of scope for this lane) | -- |
| T2 Ligero `k=4096, n=16384, t=192`, BabyBear^6 (186 bits) | 2^-127.7 "dominated by SHA-256 collision" | appendix-C: proximity `(1-e/n)^t` with `e = (n-k)/2 - 1 = 6143`: `0.625^192 = 2^-130.2`; linear `((k+l)/n)^t <= 2^-192`; field terms `(n+1)/2^186 = 2^-172`; hash 2^-128 -> total `2^-128 + 2^-130.2 = 2^-127.7` | **matches**, with observation O1 |
| T3 per-proof target for N sub-batches | `per_proof_target(-128, N) = -128 - log2 N`; union `= N x per-proof` | `accounting.per_proof_target` / `union_over_proofs` do exactly this; b-ligero2 `bench_vu --total-vus` derives `t` from the per-proof target and reports `union_over_proofs(..., n_proofs)` | correct |

## 4. Observations (no forgery, should be recorded)

* **O1 (T2, accounting assumption vs code).** `gpu/ligero.py::row_coeffs` combines the committed rows for the
  *proximity* test with **geometric powers of one challenge** (`1, r, r^2, ...`), but `accounting.ligero_error`
  states "the IRS test keeps uniform row coefficients in both modes (no geometric-sequence proximity statement is
  relied on)".  The GPU A prover *does* rely on a correlated-agreement statement for geometric sequences
  (BCIKS20 Thm 1.6 style); numerically it costs `(rows-1)` in the field term, invisible at 2^-186 -- but the
  written assumption is wrong for this backend.  Owner: security-accounting / a-gpu (a PROTOCOL.md sentence).
* **O2 (T2).** Query indices are `challenge()[0] % n` with a BabyBear element; `p mod 2^14 = 1`, so the bias is
  `1/122881` on one residue -- negligible.  `open_set` rejection-samples distinct indices, so duplicate-index
  openings cannot be constructed (the verifier recomputes the same set).
* **O3 (T2).** Merkle leaves and internal nodes share one SHA-256 domain; the path-length check (`opening shape`,
  case 21) is what prevents a leaf/node confusion.  Cheap to add a leaf/node prefix byte; not exploitable as is.
* **O4 (T2).** The verifier derives every shape (segment sizes, layer count, `t`, path length) from its own
  instance and `Params`; nothing size-like is read from the proof (case 23).  `msgs` are not canonicality-checked
  (case 19 rejects only because the transcript absorbs the raw value and the challenges diverge) -- a
  `verify` that reduced before absorbing would accept a non-canonical proof with the same challenges, which is a
  malleability, not a forgery.  Suggest an explicit `0 <= v < p` check on `msgs`.
* **O5 (T3).** `bench.contract.fingerprint` writes `N_subbatches` and `validate` checks it, but `N_subbatches`
  is **not** in `contract.IDENTITY_FIELDS` and the ledger schema has no such field: an N=25 sub-batched
  B=4096 result and a single-proof B=4096 result compare as identical identities.  Soundness-wise both are
  union-2^-128 so the comparison is legitimate, but the judge should carry the field (and the ledger `note` is
  currently the only place it survives).  Owner: judge / b-ligero2.
* **O6 (T3).** Sub-batch transcripts are seeded with `H(tag || statement || root)` where the root is per
  sub-batch, so no coin is shared across sub-batches.  `_BIND_STATEMENT` is a module-level toggle in
  `ligero/protocol.py` used to build the pre-fix red-team fixture; it should not be reachable from a bench entry
  point (grep shows it is only flipped in the fixture builder -- fine today, a footgun tomorrow).
* **O7 (T3).** `_expand` reduces `uint32` words mod `p` with "bias 2^-31" in the comment; the actual
  distribution gives residues below `2^32 - 2p` three preimages and the rest two (max point mass `3/2^32`
  vs `1/p`), a factor 1.4 on every Schwartz-Zippel term -- < 0.5 bits, immaterial, but the comment is wrong.
* **O8 (T4, read-only).** `lane/soundness-fixes` adds `statement.rs` and `verify_bound_bytes` to the **limbs
  path only** (`stark.rs`, `main.rs`); `lookup_stark.rs` is untouched.  When it merges, F1/F2 stay open on the
  LogUp path (cases 2-3 above are exactly that residual).  Nothing to re-attack yet; the U1/U2 fixes should
  land in the same lane.
* **O9 (T1 harness note).** main at 1bd19ab did not compile `verity-direct` (`ChallengerBb::from_hasher` on
  `RttChallenger`, fixed in 147a6f8); the battery was run after rebasing.

## 5. Open items

1. U1/U2 fixes for `verify_lookup` (statement digest absorbed before `pre_commit`; `log_n` from config) -- then
   re-run `redteam-logup-b battery`: cases 2-3 must flip to REJECTED, 1 stays ACCEPTED.
2. The GPU-scale run (4096 VUs on vy-sp1) of `gpu_a_forge.py` was not done -- the classes are size-independent
   and 2 VUs exercise every constraint family; the malleation cases would be identical.
3. A 3-variable LLL / adaptive-claim attack on the GPU A transcript (the b-ligero2 pre-fix class) was not
   attempted: the SHA-256 transcript absorbs the public words in `start_transcript` before any challenge, which
   closes that class by construction; worth one fixture when the a-gpu lane freezes its transcript layout.
4. O1 wording in PROTOCOL.md / `accounting.py`; O5 `N_subbatches` in `IDENTITY_FIELDS` and the ledger.
