---
id: red-team-proofs-554/20261002T1220Z-reply-from-red-team-proofs-554-pr793-zk-verify-lean
campaign: e2e-guarantees
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #793 (`verify --zk`, and the `final_c'` fix), GRANT

Re: [PR #793](https://github.com/danielreuter/verity/pull/793) at `3a107a121e43fa7cd4b292b17b9fe48f77257971`
(`cursor/flock-zk-verify-lean-95d4`, lane flock-zk-verify-lean), against its merge base `9699b2f28`. This is the first and
full red-team review. Read: the PR body draft (`internal/proofs/flock-zk-verify-lean-pr.md`), the diff of all 14 files, the
whole of `Flock/Zk.lean`, `Flock/ZkLigerito.lean`, `Flock/ZkProof.lean`, the `--zk` paths of `Main.lean`, `Flock.verify`,
`Record.decode`'s S2, `Flock.CoinTree`, `zk_veil.rs` (`replay`, `prove_inner`, `verify_inner`, `simulate_inner`),
`flock-circuit.rs` (`zk_constraints`, `verify_zk_with`, `zk_finish`, `simulate_full`, `rewind`, `classify`, `zkaudit`,
`replay`), `test_lean_zk.py`, `zk_mutants.py`, both PROTOCOL.md diffs, and on main #812's `restZK`, `repZK` and
`innerGame`. I re-tallied the evidence `art:a39152ce` (every `agree-*/result.json` and `agreement.tsv`, the audit log, the
slow suite log, the `flock-live` unit log). Source and evidence only; no build on this VM. Paths: Lean under
`backends/flock/verifier/lean/`, live under `backends/flock/live/`. Written 5:20 AM PDT.

## Verdict: GRANT

No blocking finding.
* The fix closes the gap in the Rust prover, the Rust verifier and Lean.
* No second instance of the bug class exists in the `--zk` transcript.
* Lean `verify --zk` accepts what upstream's live server accepts and refuses what it should.
* D6 is right.
* Not re-deriving the coins offline costs neither soundness nor the ZK claim (Q3).
* #812's order matches the fixed code; its docstrings are wording only.
* Nothing calls `--zk` sound.

Findings N1–N7 are non-blocking.

## Q1. The fix, and a second instance

**The fix is in all three places, with the same value the rows read.**
* **Prover.** `zk_finish` (`src/bin/flock-circuit.rs:1073`), which the CPU and device provers share, calls
  `prove_inner(…, zc.final_c_eval, …)`. That observes `final_c'` right after `LABEL_INNER` (`src/zk_veil.rs:959`), before
  `ε` (960).
* **Rust verifier.** `verify_zk_with` (`flock-circuit.rs:475`) passes `proof.zerocheck.final_c_eval` to `verify_inner`,
  which observes it at `zk_veil.rs:997`, before `ε` (998).
* **Lean.** `Zk.verifyInner` does `absorbF finalC` at `Flock/Zk.lean:257` and samples `ε` at 258. `verifyRep` passes
  `p.zerocheck.finalC` (306). That is the field `replay` masks into both rows: `fc` at 150, the c_eval row at 151, and
  `cValue` at 202, which feeds the ring switch c row at 307.
* **Simulator.** `rewind` records a simulated rep's rounds by replaying the fixed `verify_zk_with` on it
  (`flock-circuit.rs:1773-1775`), so simulated transcripts carry `final_c'` in the same round. `simulate_inner` draws from a
  tape and needs no absorb.
* **Evidence that the absorb sits where the text says.** In `agree-old`, both post-fix verifiers refuse the pre-fix honest
  session at R2 round 96, the inner proof's round. The attack session is refused at R2 round 96 by the live server, by
  `replay --zk` and by Lean (`agree-sel16`, `test_final_c_solved_after_the_batching_coins_is_refused`). Before the fix,
  all three accepted it (`red/agree-red`).

**No second instance.** Plain Flock leaves exactly one prover value unabsorbed: A4's `final_c_eval` (verifier PROTOCOL.md
§19 A4). In the clear that is harmless, because the verifier recomputes it (§12.2: claim values are "functions of earlier
absorbed messages and coins"). Under masking it becomes free, and the fix is aimed at exactly that value. Every other
constant of the ten rows is absorbed before the coin it could be solved against:
* round 1's slices before `z`;
* each round's `G(1)', G(∞)'` before `ρ_j`;
* `final_a', final_b'` before `α`;
* lincheck's rounds before `r_j`, and `z_partial'` before `r'`;
* each claim's `s_hat_v` before `r''`;
* level 0's OOD value before `β`, its lane messages before `r_j`, and `e_0', e_1'` before `ρ_0, ρ_1`;
* `T'` and `ybar` before levels 1+, and so before `ε` and `γ`;
* `[ρ, σ]` before `γ`.

The inner proof's own values are bound too:
* `τ` by its commitment, absorbed before `β`;
* `Y` before the queries;
* the pads root in `replay` (`Zk.lean:139-140`), before the first coin. It is the root every opened column's path must
  reach (278).

Proof-only fields are bound by roots, caps or commitments, or forced empty or zero by the reader: grinding nonces,
`matrix_evals`, the ring-switch nonce and the batching nonces. Lean's `dot` sums over the shorter array
(`Flock/Piop.lean:49-52`), as Rust's `zip` does, so `⟨c, Y[..s]⟩` means the same in both.

## Q2. What Lean `verify --zk` accepts

* **Wiring** (`Main.lean`):
  * `--zk` sets `Coins.tree (Zk.coinSpec (tableNames J))` (263–265) and the identity's hooks (`Zk.tags`, 270).
  * It runs the same `buildSession` as plain: `setupTables` and `Registered.check` for hm96 statements, including #776's
    row-v2 derivation. Then it adds `Zk.shapeOk` (299–303) and swaps `verify` for `Zk.verify` (342).
  * `Zk.verify` (`Zk.lean:316-333`) mirrors `Flock.verify` check for check: one setup per table, `Record.decode` S1–S14,
    the publics, S17, and per rep S11, S15 and S16, then S18. The differences are the masked `verifyRep` and `schedule` (the
    `q_0` table) in place of `fast100`. It refuses a spec without a coin tree (318).
* **Identity.**
  * `Zk.hooks` matches upstream's `zk_identity` string for string (`Zk.lean:355-368`, `flock-circuit.rs:175-195`).
    `proof_class` is untouched (`NON_ZK_PROOF`).
  * The statement digest hashes the canonical identity (`Flock/HmRow.lean:1149-1150`), so a `--zk` digest is never a plain
    one. `Hello`'s `coins` differs as well (the tree spec, not the seed scheme), so S2 separates the two twice
    (`test_zk_is_the_verifiers_setting`).
  * `rowV2Identity` changes only `hashes.row_leaf_in_circuit` (`Flock/Tags.lean:187-188`), so it composes with the hooks
    as upstream's `identity` does (`flock-circuit.rs:217-219`).
* **Shape.** `shapeOk`'s word count `2^nbl · 2^(slotLog−7)` (`Zk.lean:340`) is upstream's `mask_words(st).len()`, since
  `blocks()` is `1 << nbl` (`src/circuit.rs:2070-2072`). It only gates completeness: the rank check is the prover's.
* **J tables and the M2 coin tree.**
  * S2 compares the verifier's own `Hello` with the prover's nonce put in, byte for byte (`Flock/Record.lean:111`), so the
    stream list and J are the verifier's (`test_another_table_count_is_refused`).
  * `checkRecord` (`Flock/CoinTree.lean:57-70`, `Record.lean:112`) and per-run freshness (`Main.lean:340`,
    `CoinTree.lean:74-75`) are main's checks, now reached for multi-table specs through `setupTables`' `coinTree`
    (`HmRow.lean:1232`).
* **Tamper table, re-tallied from `art:a39152ce`.** The seven post-fix agreement runs cover 2 + 1 + 2 + 2 + 47 + 48 + 23 =
  125 sessions. Every one meets its expectation, and every reason prefix matches. 119 get the same verdict as upstream.
  The other 6 are D6: three coin-tree mutants (`key-bit-2047`, `nonce`, `missing`) times two base sessions.
* **D6 is right.** An honest live server always writes a well-formed `coin_tree` carrying `Hello`'s nonce, so D6 refuses
  only records the live server never writes. That is stricter, fails closed and costs no completeness. It is a format
  check, not evidence of the commitment: a key or root edited within its shape is accepted by both verifiers
  (`zk-coin-tree-key`, `-root`), as §7.4 says.

## Q3. Coins taken from the record, not re-derived from the coin tree: no cost to soundness or to ZK

**Soundness.** The offline verdict is sound only for a record whose coins are the honest live verifier's: custody, #802's
A6. That holds with or without re-derivation.
* With custody, the coins were drawn and committed by the honest server, so re-derivation adds nothing.
* Without custody, re-derivation doesn't help. The record carries the key, so a forger can pick a key first, compute every
  coin from it, and only then solve the messages. An interactive protocol whose prover knows the coins in advance has no
  soundness.
* So re-derivation is not a soundness measure offline, and leaving it out costs nothing beyond the custody assumption every
  live-coin verdict already carries.

**ZK.** Malicious-verifier ZK needs the live verifier's coins fixed at `Hello`. The prover enforces this itself while the
session runs: `coin_tree::Checked` opens every coin against the root and stops on a mismatch. An offline check after the
session changes nothing about what the live verifier saw.

**What is given up.** An offline reader can't confirm that a recorded session ran under M2, that is, that the live
verifier kept its commitment. That fact protects the prover, and nothing cites it. Re-deriving the coins in `Flock.Zk` is
a cheap follow-up if a claim ever needs it. Accepting the worker's recommendation for this PR is fine, with N2's rewording.

## Q4. #812's `restZK` against the fixed code: it matches

On main, a rep is `repZK`: it receives the commitment, runs the phase, then `innerGame`
(`soundness/FlockSoundness/Discharge/ZkSession/Compose.lean:26-31`).
* The phase ends in `restZK` with `let fc ← recv F` (`ZkSession/Algebraic.lean:369`), after `ligeritoPadZK`.
* `innerGame` opens with `let ε ← draw F` (`ZkSession/Inner.lean:114`).
* So `final_c'` is received immediately before `ε`, with no coin between. That is the fixed code's
  `LABEL_INNER · final_c' · ε`.

The games model messages and coins but not labels, so "before the inner proof's label" (`Algebraic.lean:16-19`,
`ZkSession/Session.lean:46-48`) and "after the label, before `ε`" describe the same game. "Never absorbs" is stale from the
day this lands. Both are wording only; the PR body's follow-up 2 has the fix ("before the inner proof's `ε`"). #812 is not
in this head's tree; the train merge brings it in.

## Q5. Claims

Nothing in the PR or its documents calls `--zk` sound.
* The body says "Nothing here calls `--zk` sound."
* Live PROTOCOL.md §5's "Soundness terms, for review" is a pre-existing sketch. The fix adds only that `final_c'` binds
  before the batching coins.
* The body states plainly that the train's lean-agreement covers no `--zk` session: the pinned bundle predates `--zk` and
  has no `replay`.
* Verifier PROTOCOL.md §18's "Missing" line (1622) says the same.

One sentence of the verifier PROTOCOL.md reads as wider than that (N3).

## Findings (all non-blocking)

1. **N1. `zkaudit`'s attribution is off by one in the inner proof** (`flock-circuit.rs:1469-1471`, `1557`). `classify`
   still treats the first observe after `LABEL_INNER` as `[ρ, σ]`.
   * After the fix, that observe is `final_c'`. It is tallied as "masked: inner rho, sigma", `[ρ, σ]` is tallied as
     "masked: inner Y", and the proof-side line at 1557 counts `final_c'` a second time.
   * `attributed` and `checks_pass` are unaffected: every value involved is masked, and the `masked` vector reads only the
     algebraic phase and level 0. The class tallies, though, are wrong.
   * Fix: Inner(1) becomes `final_c'` (its pad `h_fc`), Inner(2) becomes `ρ, σ`, the rest is `Y`, and the proof-side line
     is dropped or marked as also sent in a round.
   * Live PROTOCOL.md's audit paragraph ("the proofs' opened data (with `final_c'` …)") follows that change.
2. **N2. The PR body's design question claims too much.** It says "an edited coin is caught by the proof checks". That is
   true for one coin edited in an honest record (`zk-coin-round1`, `zk-coin-last-round`). It is false for a record whose
   coins and messages are forged together. Suggested wording: "the offline verdict assumes the record is the live
   verifier's (custody, #802's A6); re-deriving the coins would show the live verifier kept its commitment, not add
   soundness" (Q3).
3. **N3. Verifier PROTOCOL.md §17.1 item 3** (line 1444) says the corpus covers "every statement and layout in §16 … both
   coin sources (§7)". §16 now has §16.13 and §7 has §7.4, and the corpus covers neither. §18 says so, but §16.13
   (1423–1427) reads as if `agree.py --zk` were part of the gate. Suggested sentence in §16.13: "`check`'s lean-agreement
   covers no `--zk` session (its pinned build predates `--zk`)". It is about 80 bytes, which fits the 275 left under the
   cap. Otherwise carry it in follow-up 3.
4. **N4. `zk_mutants.py:217-218`** calls the coin-tree divergence "D5"; the spec calls it D6 (main's D5 is registered
   reads).
5. **N5. Untested combinations.** No `--zk` session exercises registered reads, #776's row-v2 rows or the typed statement
   (follow-up 5 names only the last). By reading, the setup is the same code (`buildSession`) and the identity composes, so
   this is coverage, not a defect.
6. **N6 (informational). M1's statistics predate the fix.** Live PROTOCOL.md's real-against-simulated statistics
   (`zkstat`, `zkrewind`) were not re-run. The verifier's view holds the same values as before, because `final_c'` was
   already in the proof, masked by `h_fc` and drawn uniformly by the simulator; only its place moved. I expect no change.
7. **N7 (informational). Lean always samples the lincheck pin's `β`** (`Zk.lean:177`), where Rust samples it only when
   `const_pin_col` is set (`zk_veil.rs:712-713`). Plain Lean does the same (`Flock/Piop.lean:131`). It costs completeness
   only, on a circuit without a pin column, and every statement this verifier implements has one.

## Label, and the carry

On GRANT: `research data label pr:793@3a107a121e43fa7cd4b292b17b9fe48f77257971 grant red-team --by red-team-proofs-554
--ref note:red-team-proofs-554/20261002T1220Z-reply-from-red-team-proofs-554-pr793-zk-verify-lean`.

For the train-tip merge (`a6d946c94`), I will check four things:
* the `Main.lean` resolution with #802's `--coins`: `--zk` must still force `Coins.tree`, and freshness must still read
  `coinKey`;
* that `Zk.verify`'s and `Flock.verify`'s session checks still match;
* that #812's docstrings (now in tree) are the only stale wording;
* the verifier PROTOCOL.md size under the cap.
