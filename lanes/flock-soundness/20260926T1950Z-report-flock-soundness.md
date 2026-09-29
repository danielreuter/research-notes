---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: report · status: open · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# flock-soundness: Flock interactive soundness in Lean (level 4a)

CHECKPOINT 518934d9 (19:04Z) [open] PUSHED, HELD for train J. η retune folded into #173 (red team granted at af5e9c1b); #173 then took main d69ce770 and the soundness lean-audit.json fix (the deleted FlockSoundnessTest root; 7 pins re-recorded, audit.py --no-replay PASS 4620 decls/84 mods/9 pins), head 518934d9 = merge-tree(d69ce770, af5e9c1b) + lean-audit.json only. #127 ced7b2f3, #163 6146e611, #170 dd0c488a: main merged. #180 (c7580022): ASSUMPTIONS.md split into a 4 KB index, assumptions/*.md, README.md and Audit/README.md. Next: RoPE verified lowering, with W6 on #154/#147.
CHECKPOINT 16785b18 (18:13Z) [open] PUSHED. A2's constant is 2^256 (was 2^256.5, beaten by hashing until the first collision: P = 1 at E[cost] 2^256.33; the scoping lane's finding, coordinator 17:41Z). Fixed where it flows: #127 f1c90b1f, #163 b5009bc9, #170 972d5111, #171 23b2df6e (audit-lean's branch, at the coordinator's request). Record: t·Q_s(8N₀/e)/2^256, audit B t·2^-209.4 (2^-129.4 at t = 2^80), lifetime 2^-128 while N·t ≤ 2^78.4 to 2^90.4; strict-time and ROM rows unchanged. A1 removed on top (#173 16785b18, includes #171). All held for re-audit; the red team reviews A2's changed statement.
CHECKPOINT 5cd69ca3 (16:55Z) [open] PUSHED. #170 (docs only, on #163): the link term of record counts Q_s (Daniel, 16:47Z), t·Q_s(8N₀/e)/2^256.5, audit B t·2^-209.9, lifetime 2^-128 while N·t ≤ 2^79 to 2^91 over A–D. The lifetime doc is restated to match and carries the levers table (§5).
CHECKPOINT 7516258b (16:45Z) [open] PUSHED. #163: the link theorem is proved (flock_batched_linkSoundE; standard axioms). δ_link ≤ Q_s(2(1+k)t'/2^256.5 + 1/(eM) + k/(eRw))/(1 − ρ) under A2 for each commit string's explicit finder and ValueBinding (named, discharged by the hm96 layout); Q_s ≤ N_s. #163 handed to the coordinator for audit. The buy-back list for Daniel is below.
CHECKPOINT 0ab7224d (16:00Z) [open] PUSHED. #163 S3: the batched audit with the expected-time extractor (analysisBE; reruns conditioned on the session accepting, cover ε(1 − N₀/(ek)) ≤ ε_c⁻ + √(k·adv₀) + ε·Pr[link]; flock_batched_countE with δ_link named). Next S4–S6, the link theorem under A2.
CHECKPOINT 4a757268 (15:35Z) [open] PUSHED. Expected-time CR of record (Daniel 14:34Z): #127 ready at f117f52b (A2 named, Assumptions.SHA512ExpectedTimeCR; link term t·N_s(8N₀/e)/2^256.5, B 2^-125.6 at t = 2^80); lifetime doc updated; plan note:20260927T1510Z-draft-expected-time-link-plan; #163 (on #127) S1–S2: accepted-only deviation, the k-accepted extractor, session_knowledge_sound_acc. Next S3 (analysisBE).
CHECKPOINT e56c4b21 (12:15Z) [open] PUSHED. #155 (on #153): one copy of the phases before Ligerito, the _of_card wrappers instances of the list forms at closeMsgs, PiopList.lean removed. flock-zk (12:10Z): zk_veil claims e_i against the running claim's weight, as the model does; they fix PROTOCOL.md's wording, and the model now states it (#153 3f655e25). #153 and #155 merged with main after train D (178/178 standard axioms); #144, #152, #153, #155 all mergeable. Morning summary in lanes/coordinator/20260927T1214Z-summary-from-flock-soundness-morning.md.
CHECKPOINT 27add24d (11:26Z) [open] PUSHED. #153 (on main): the table theorem with M1's padded level 0, for any padding t and extra lanes per rep e (table_sound_pad), and at #123 8d621454's values 2^-196.5 per table at m = 25-27 (table_sound_pad_m1). New pieces: the novel basis's degree structure from xhat_poly, the padded code's list size, MCA and decoding, Ligerito with the padded level 0, the phases before Ligerito over any list. 91/91 standard axioms, no sorry. #152 (on main): the zero-knowledge statement as the M1/M2 red team requires (statistical hm96 hiding in the standard model; Goldreich-Kahan rewinds t/p̃ with t growing, a fresh dummy opening each, p̃ from fresh runs only). audit-lean agreed C and took the decoder patch into #145. Asked flock-zk which weight M1's e_i uses (the model takes it against the full next-stage weight). Next: flock-zk's answer; the canonical HM96 values once M0's SHA-512 leaf layout is final.
CHECKPOINT 084f8478 (10:01Z) [open] PUSHED. Since 04:25Z, as draft PRs: #124 knowledge soundness (table_knowledge_sound_joint; the factor-1 form _tight); #127 DESIGN §3 with both link-term options for Daniel; #136 a table inside a batched session (session_sound_of_table, session_knowledge_sound); #141 several tables per session in #133's shape (sessionB, joint_le_B', one_le_fail_add_B'); #144 (on #141) the compiled lowering over the rows the verifier parses, for every template (lowering_sound, UnitPlace.correct, Prog.isRowsUnit), with L1 named in ASSUMPTIONS §1.5 and test_pinned_rows_read_earlier_columns. No sorry, standard axioms only (159/159 on #144). The M1 level-0 recount went to flock-zk and is in #123 at 8d621454. To audit-lean: C's definition and a tested patch making #133's decoder per drawn unit (`note:20260927T0957Z-handoff-from-flock-soundness-rows-circuit`). Next: audit-lean's answer; M1's padded level 0 once the coordinator confirms it has settled; the canonical HM96 values once M0's SHA-512 leaf layout is final.
CHECKPOINT 736c660a (04:25Z) [open] PUSHED. **#89 is merge-ready.** CI is green; GitHub reports MERGEABLE/CLEAN. A trial merge with main (3040ac1f) is clean, main does not touch the Lean package, and tests/ on the merged tree pass (29 passed, 6 skipped). The compiled theorem is on stacked branch cursor/flock-compiled-8569, draft PR #110 (base: #89's branch). Game.expect (real expectations against a strategy) and Rewinding.expect_bad_le (rewinding for any run distribution) are proved. Next: the compiled model (caps; consistency values from openings sent after every coin, per PROTOCOL.md §13.3/§14/S17), the lockstep coupling with the plurality prover, rewinding at every cap with Jensen over prefixes, then table_sound_compiled.
CHECKPOINT 6dc1cd07 (03:55Z) [open] PUSHED (origin at 6dc1cd07). Lean: **table_sound is proved**. The Ligerito phase is proved in five files: the weights at every stage and a level's fold identity (LigeritoRes), decoding a fold from MCA-good folds (LigeritoDecode), a level's folds (LigeritoPhases), the next level's OOD binding, queries and batching coins (LigeritoMid), and level 0, the last level and the recursion (LigeritoPhase). ligerito_phase closes the last sorry. rep_sound, table_sound, table_sound_fast100 and the new table_sound_fast100_34_35 depend only on propext, Classical.choice and Quot.sound, with BCHKS25 Thm 4.6 as a hypothesis. Arith.Correct: omega_injective is now stated for d ≤ 64 and xhat_poly for L ≤ 40, as flock-verifier proved them. Level.Fits carries the bounds, and every fast100 level fits. Handoff to flock-verifier: `lanes/flock-verifier/20260927T0330Z-handoff-from-flock-soundness-bounds.md` (the bounds suffice). Next: the Arith.Correct instance once both branches are on main, then the compiled theorem.
CHECKPOINT 65520f90 (02:55Z) [open] PUSHED (76777436, 65520f90). Lean: per-level parameter check PROVED (prCoin_level_mca_le: Johnson range, a = mcaA, for every fast100 level); out-of-domain binding PROVED (value_twoOod_collide_le: pairs(L)·(μ/|F|)²); the folds' sumcheck part against a list PROVED (value_foldRounds_sum_le: k·2L/|K|, plus the quadratic-sum invariant). Weight bookkeeping design written into `note:20260927T0205Z-finding-ligerito-proof-plan` §4. Next: the product identity (cff, X̂ MLE), the weights of LigState, the final-check identity.
CHECKPOINT 01bf9d6b (02:40Z) [open] UNPUSHED (token down); bundle `artifacts/flock-soundness-01bf9d6b.bundle` (verified; 1 commit on 9a937b58). Lean: LigeritoMCA.lean PROVED: prCoin_mca_le (BCHKS25Thm46 read as a coin bound over any finite field, via VCVio prEvent_uniformSample), one fold round (rowsAgreeOn_of_fold; pairs·a/|L|), all rounds (foldAllRows_eq_sum matches Model.foldColumn's eq weights; rowsAgreeOn_of_foldAll), and the game lemma value_foldRounds_mca_le ((2^k − 1)·ε over foldRounds, whatever the prover sends). Standard axioms only. Next: level parameters (Johnson range, a = mcaA), out-of-domain binding, then the weight bookkeeping.
CHECKPOINT 9a937b58 (02:25Z) [open] f77c519a (link_sound) and 7f74b6cf PUSHED; 9a937b58 UNPUSHED (token down), bundle `artifacts/flock-soundness-9a937b58.bundle` (verified; 1 commit on 7f74b6cf). Lean: link_sound PROVED (LinkSound.lean: regionPoly nonzero at the Boolean point of the failing region bit, two points squared, union over list and regions); new hypothesis Statement.LinkLayout on link_sound/table_sound; table_sound now waits only on ligerito_phase. Ligerito generic pieces PROVED: card_close_le (list size at any level), drawK uniform (new Arith.Correct.ofLimbs_bijective), rounds over K, α batching, stratified queries (AM-GM). Design answer: the unit draw goes in the clear between registration and the session (`note:20260927T0210Z-finding-unit-draw-placement`). Next: the MCA bridge (VCVio Pr to prCoin) and the per-round fold lemma.
CHECKPOINT daf4b1fd (02:10Z) [open] UNPUSHED (token expired again); bundle `artifacts/flock-soundness-daf4b1fd.bundle` (verified; 2 commits on 1c19d3d7). Lean: zerocheck_phase PROVED (ZerocheckPhase.lean: Z3 eq-reduction via pinned_indep, Z5 skip point via Pcomb vanishing on S, residual rounds with the r_eq = 1 event charged once, the pin via a renamed eq polynomial; sum = εZc exactly), standard axioms only; Arith.Correct's lagS_interp/lagΛ_interp became one `nodes` fact (S, Λ, lagS, lagΛ, combW on the same 128 points). Remaining sorries: ligerito_phase, link_sound. Docs: folded the lifetime-soundness desk study (DESIGN §1.2: serving roots need rewinding; ASSUMPTIONS §7: audits, not tables, and knowledge soundness required, §1.3 marked). Plan for Ligerito: `note:20260927T0205Z-finding-ligerito-proof-plan` (~3–4k lines). Replied to flock-verifier with the Arith.Correct fact order (`note:20260927T0200Z-handoff-from-flock-soundness-arith-facts`). Next: Ligerito generic lemmas.
CHECKPOINT 1c19d3d7 (01:08Z) [open] PUSHED to origin (the VM token works again; no bundle needed, the 4c5b3f41/1c19d3d7 bundles were removed as redundant). Lean: the list-size lemma closeMsgs_card_le PROVED (ListSize.lean: an encoded message read position-first is a codeword of ArkLib's irsCode on the level's points, via Arith.Correct.xhat_poly; Close is relative block Hamming distance; encoding is injective; irs_lambda_le_johnson_mds gives 25·2^r), so opening_phase is axiom-clean. lincheck_phase PROVED (LincheckPhase.lean: per codeword, α and β one coin each, the k_log−6 rounds 2/|F| each via value_lincheckRounds_le, a passing final check forces z_partial off the folded columns, the skip coin r' costs 63/|F| by Lagrange interpolation through the lagS nodes; union over the list). Statement gains hk6 : 6 ≤ kLog (k_skip = 6). Remaining sorries: zerocheck, Ligerito, link_sound. Next: zerocheck.
CHECKPOINT 15bc614e (00:45Z) [open] UNPUSHED; bundle `artifacts/flock-soundness-15bc614e.bundle` (verified; 6 commits on 8ebef00c; supersedes earlier bundles). Batched, serialized sessions are the stated model (ASSUMPTIONS §2; coin commitment = SHA-512 Merkle root over HM96 per (table, rep, round) coin commitments); ZK theorem = single-rewind simulation of one batched session (§6); PRS and a registered key are reserve notes (DESIGN §11.2); options analysis moved to a note. Lean: opening_phase_of_card PROVED (ring-switching identity, 7/|F| per claim, 1/|F| batch, union over list), standard axioms only; opening_phase follows from the shared list-size lemma closeMsgs_card_le (sorry). Remaining sorries: zerocheck, lincheck, Ligerito phases, list size, link_sound. Next: list size (bridge to ArkLib irs_lambda_le_johnson_mds), then lincheck.
CHECKPOINT 50eb5dcd (00:10Z) [open] UNPUSHED; bundle `artifacts/flock-soundness-50eb5dcd.bundle` (verified; 4 commits on 8ebef00c; supersedes 635a3ecc's). DESIGN §11.1: batching inside one serialized session works: single-rewind GK simulator (one step-0 commitment per session), shared coins cost no soundness (per-table bound + union; reps keep independent coins; per-round barrier or per-table streams), latency ≈ 2× session (≈ one table's proving + 220 round trips). PRS fallback costed (~125–210 slots, 0.1–2 GB shares/session, 3–5k Lean lines on top of GK); 'exactly one verifier' doesn't simplify PRS, makes registered keys trivial. Recommendation: batching.
CHECKPOINT 635a3ecc (23:55Z) [open] UNPUSHED (VM token expired); bundle `artifacts/flock-soundness-635a3ecc.bundle` (verified; 3 commits on 8ebef00c). ASSUMPTIONS.md split into the concise list (20.7 KB) + DESIGN.md with derivations (38.9 KB). Lean: Game.Union (LawfulMonad Game, union bounds, mapM loop bounds) and the opening phase's algebra (Schwartz–Zippel for ring switching and batching, honest message, claim value); standard axioms only. ZK (DESIGN §11): malicious concurrent verifier; SHVZK lemma (VEIL's notion) + recommendation: global serialization now (CR only, no setup), PRS preamble if concurrency required; beacon and registered keys as alternatives. Next: finish opening_phase (ring-switch identity, game assembly), list-size lemma.
CHECKPOINT 8ebef00c (23:25Z) [open] UNPUSHED (GitHub auth expired on this VM: git and gh tokens invalid); bundle `artifacts/flock-soundness-8ebef00c.bundle` (verified, on top of bbd552a1). Knowledge soundness added to the theorem list (ASSUMPTIONS §4.4): table_knowledge_sound (rerun from the level-0 commitment, conflicts = collisions, list-decode observed columns) then registered_weights (HM binding vs the registrant's opening); effort ~1,250–2,000 Lean lines (+200–350 for witness-extended emulation), decoding provable via CompPoly's verified GS; first knowledge-error estimate t·2^-227/ε. Next: compiled game + coupling, list-size lemma, phases.
CHECKPOINT bbd552a1 (23:15Z) [open] ASSUMPTIONS §13, one weights root across many proofs: union bound N·2^-195.5 + N·t·2^(17.3−256) (lifetime budget N·t ≤ 2^110.7, set by per-table rewinding, not the root); root binding straight-line, needs the SHA-512 leaf scheme (hm96-sha256/v1 only to t≈2^64.5); hiding fixed by leaf count; ZK sequential only vs malicious verifier; predicate budget; linkability needs knowledge soundness (not planned). Next: compiled game + coupling, list-size lemma, phases.
CHECKPOINT 294723f1 (22:50Z) [open] compiled theorem stated under plain SHA-512 CR for every prover (ASSUMPTIONS §4.3); its cores proved in Lean (Merkle binding, rewinding lemma #bad² ≤ N·Q·#conflict, compilation steps; standard axioms only); ROM a remark; post-quantum section §12: oracle layer PQ-sound as is, compiled layer PQ-sound only asymptotically (CDDGS25, if SHA-512 collapsing), no concrete PQ bound at our parameters. Next: compiled game + coupling, list-size lemma, phases.
CHECKPOINT c91c06da (22:05Z) [open] rep_sound proved from 4 phase lemmas; round lemmas proved (3 encodings); hash width: SHA-512 trees make plain CR clear 2^-128 for every prover up to t≈2^110.7 (SHA-384 ≈2^47, SHA-256 never). Next: list-size lemma, then lincheck phase.
CHECKPOINT 43a4873b (21:40Z) [open] staged along a16z's security stages (ASSUMPTIONS §10–11); Schwartz–Zippel lemmas proved; statement proved from 2 lemmas (rep_sound, link_sound = sorry); numbers proved 2^-195.5 (m≤33) / 2^-195.4 (m=34,35); 1 named assumption. Next: rep_sound phases, round-by-round first.
CHECKPOINT c2d36e79 (21:25Z) [open] statement proved from 2 lemmas; numbers proved; 1 named assumption (BCHKS25 Thm 4.6); CR answer: tight only for provers that know their tables, else ROM.

## Where things are

- Lean package `backends/flock/verifier/lean/soundness/` (PR #89). It is a separate Lake package so that
  `flock-verifier`'s executable doesn't pull in ArkLib.
- Pins: ArkLib `b2e456fc`; through ArkLib's manifest, VCVio `d7089e46`, CompPoly `v4.34.0-patch2` and Mathlib
  `v4.34.0`; Lean 4.34.0.
- Build: `lake exe cache get && lake build` takes about 5 minutes cold on 4 cores. Axiom audit:
  `lake env lean FlockSoundness/Check.lean`.
- `ASSUMPTIONS.md` beside the package, for the reviewer and Table 1.

## Status of the theorem

- **Proved, with only the three standard axioms:**
  - the interaction model;
  - the repetition theorem (`value_interleave_le`): two reps under any adaptive interleaving have value at most the
    product of the two values;
  - additive composition and the union bound;
  - the whole accounting: `tableError` ≤ 2^-195.5 for 22 ≤ m ≤ 33 and ≤ 2^-195.4 for m = 34, 35, over every statement
    shape with at most 2^26 bits per block, 1,024 regions and 64 link-point coordinates. Checked by `decide +kernel`,
    not `native_decide`.
- **Proved (03:55Z), with only the three standard axioms and BCHKS25 Thm 4.6 as a hypothesis:**
  - `table_sound`: for every prover, Pr[both reps accept ∧ ¬CommittedSatisfies] ≤ tableError;
  - `table_sound_fast100` (2^-195.5, m ≤ 33) and `table_sound_fast100_34_35` (2^-195.4);
  - from `rep_sound` (one rep from a doomed start ≤ repError, four phase lemmas) and `link_sound`.
- **Written:** the model of PROTOCOL.md §9–§16 at the oracle layer (`Model/*`).
- **The compiled layer (22:50Z):** the theorem is stated in `ASSUMPTIONS.md` §4.3 (SHA-512 trees, round bytes kept, plain
  collision resistance, every classical prover). Proved: `Merkle.opening_binding`, `Rewinding.bad_sq_le` / `prBad_le`,
  `Compiled.compile_step` / `compile_step_prefix`. To write: the compiled game (Ligerito with caps and the query answers
  deferred to the end of the proof) and the coupling, then `table_sound_compiled`.
- **Not started:** refinement to `Flock.Verify`.

## Axioms

There is one named assumption, **BCHKS25 Thm 4.6**.
- It is stated exactly as ArkLib pins it; a test proves our `Prop` from ArkLib's by `exact`.
- It is a hypothesis, not a Lean `axiom`.

Two items on the original axiom list are not assumptions:
- **Diamond–Posen ring switching.** The spec's per-claim variant (A9) follows from the paper's Appendix B argument plus
  Schwartz–Zippel. ArkLib's version is on its legacy layer with 18 admits, formalizes the other variant, and is not
  usable.
- **Merkle binding.** Proved here for the §14 shape (`Merkle.opening_binding`), as in VCVio. Collision resistance enters
  as an explicit collision-probability term, not a hypothesis.

## Collision resistance vs the random-oracle model (Daniel's question)

The answer, with numbers, is in `ASSUMPTIONS.md` §4.2.

- **Straight-line collision resistance is tight:** 2^-195.5 + Adv_CR(B). It clears 2^-128 up to about 2^64 hash
  evaluations. But it covers only provers that know the tables they commit to.
- **Arbitrary provers under collision resistance need rewinding:** at least t·2^-113.6 at m = 33, with t the adversary's
  hash evaluations. This does not clear 2^-128 for any adversary. The square root sits on the hash term, so the
  67.5-bit statistical margin can't help.
- **The random-oracle model covers arbitrary provers** at 2^-128 up to about 2^63.5 hash evaluations.
- **Round digests** get a tight collision-resistance bound for every prover, since the coin server sees the live bytes.
- **Superseded (22:50Z):** Daniel adopted SHA-512 trees and kept round bytes, so the compiled theorem is under plain
  SHA-512 collision resistance for every prover (`ASSUMPTIONS.md` §4.3), with the random-oracle version only as a
  remark. The SHA-256 comparison moved to `lanes/flock-soundness/20260926T2230Z-finding-sha512-merkle-choice.md`.

## Findings

- **2^-195.5 per table holds for m ≤ 33 only.** m = 34 and 35 have a seventh Ligerito level. Its query term (2^-102.6)
  gives 2^-195.43 per table. PROTOCOL.md §15 and `kb/flock-prover.md` quote 2^-195.5 without the caveat. Both are far
  below 2^-128.
- **The spec's deviations add terms the flock-128 ledger doesn't charge.** Each is below 2^-110, and together they move
  the total by less than 0.001 bit:
  - the `inv(0) = 0` exceptional set (A5);
  - the constant-wire pin (A8);
  - the link points (A14), shared by both reps and so not squared;
  - the L₀ list factor on terms before Ligerito's binding (paper Appendix A);
  - MCA and fold-sumcheck terms summed per round rather than per level.
- **ArkLib's proved Johnson list bound is 1/(2ηρ)**, not 1/(2η√ρ); the bound uses ArkLib's.
- **BCHKS25's printed multiplicity is ⌈√ρ/(1−√ρ−δ)⌉.** The Flock paper uses a tighter one that the proof supports but
  the theorem doesn't state; the bound uses the printed one.

## Zero-knowledge estimate

The estimate follows Daniel's reference-prover plan: a spec-level Lean prover, completeness and simulation theorems, and
byte-for-byte differential tests against the production prover. It waits on M1's masking spec.

| Piece | Agent-days |
|---|---|
| Lean reference prover: a deterministic function of (statement, witness, prover randomness, verifier coins), emitting spec bytes | 10–20 |
| Completeness (the Lean verifier accepts its honest output) | 10–20 |
| Honest-verifier ZK simulator and proof: masked sumchecks; padded Reed–Solomon (opened columns uniform when queries ≤ padding, AHIV22 Lemma 4.15); Halevi–Micali leaf hiding | 15–30 |
| Malicious-verifier ZK with the step-0 coin-seed commitment (simulate for every fixed coin sequence, plus binding) | 5–10 |
| Differential-test harness against the production prover (seed injection exists in PR #83) | 5–10 |
| **Total** | **45–90** |

Expert review of the ZK statements would take a further 2–6 weeks.

What exists to build on:
- **VCVio:** total-variation distance (`tvDist`), a relational program logic with ε-close simulation of handlers
  (`ProgramLogic/Relational/SimulateQ/Epsilon`), and HVZK for three-move Σ-protocols (`SigmaProtocol.HVZK`). These are
  usable for the statistical-distance plumbing.
- **ArkLib:** only a `Simulator` structure on its legacy layer, with the zero-knowledge definition commented out.
- **Nothing** exists for multi-round masking, Reed–Solomon padding or hiding leaves.
- The model is ready for it: the prover's randomness becomes an extra input, masks are extra messages or committed
  columns, and salted leaves change only the Merkle layer.

## What remains

- `Arith.Correct` for GHASH: flock-verifier proved every field in our shapes; the instance is wired in once both
  branches are on `main`.
- The compiled theorem: its cores are proved; the compiled game model (deferred query answers) and the coupling
  remain. Round binding needs nothing now.
- Refinement to `Flock.Verify`, with `flock-verifier`: about 5–10 once their verifier exists.
- ZK: as above.

## a16z staging (Daniel, 21:22Z)

I adopted Thaler's zkVM security stages as the structure (`ASSUMPTIONS.md` §10, and a stage column in §1).

- **Where we are.** This lane is Stage 1a modulo A1 (our level 4a), heading to 1b and to 1c with live coins in place of
  Fiat–Shamir. Level 3 covers Stage 2 plus the lowering theorem of 1d. The reference prover is Stage 3 and 1e (ZK).
- **Deliberate differences:**
  - live coins instead of Fiat–Shamir, so no random oracle for coins;
  - circuits instead of a VM, so 1d is the lowering theorem and "the circuit is the meaning" replaces verified
    bytecode;
  - Stage 2's target is the Lean verifier itself, a Lean-to-Lean refinement with the compiler trusted;
  - Stage 3 proves a reference prover and links the production prover by differential tests;
  - no recursion.
- **Soundness bits.** Stated as a16z suggests: statistical bits per table from proven results only, with no grinding
  credit; the hash term with its model named; each assumption at the stage that uses it.
- **Fiat–Shamir or SNARK variant** (§11). It needs round-by-round soundness per component, a new parameter set
  (state restoration defeats the squaring; flock-128: 2^-75.6), and possibly recursion.
  - I'm proving `rep_sound` round by round first, so those lemmas carry over.
  - The joint two-point out-of-domain term keeps a separate round-by-round lemma (unsquared, about 2^-104.5).

## Tests

- The repository and tree-scanning tests pass: `tests/`, the replica check and the protocol boundaries, 32 passed and
  6 skipped.
- The full suite was run to 83%. Every failure it hit is pre-existing, identical on a clean `main` worktree:
  - `backends/gkr` needs `torch` (a collection error);
  - five `tools/research` pod and pythonpath tests need `~/.research` and pods;
  - one `tools/research` store test, `test_store_honing::test_evict_runs_only_preserved_terminal_quiet_runs_and_leaves_a_restore_record`.

## Hash width (Daniel, 21:30Z)

The details are in `ASSUMPTIONS.md` §4.2a.

- **The rewinding bound for arbitrary provers under plain collision resistance** is `t·√2·S_m/2^{n/2}`. Here
  `S_m = Σ_ℓ √(N_ℓ·Q_ℓ)`, and `log2(√2·S_m)` is 16.3 at m = 33 and 17.3 at m = 35.
- **SHA-512 Merkle trees clear 2^-128 up to t ≈ 2^110.7–2^117.** SHA-384 gets only to about 2^47–2^53, and SHA-256
  never.
- **The tight terms need n ≥ 128 + 2·log2 t:** the round digests, the straight-line reduction and the random-oracle
  bound. So at t ≥ 2^65, SHA-256 misses 2^-128 even in the random-oracle model.
- **The route with neither the random oracle nor a knowledge assumption:**
  - SHA-512 Merkle trees, as A-GKR already uses;
  - the coin server keeps each round's bytes, or the round digests move to SHA-384/512.
- **What doesn't help:**
  - more reps (+0.4 bit each, via the shared level-0 openings);
  - more rewinds (the gain cancels);
  - tight standard-model extraction, which needs SSB or somewhere-extractable hashes from LWE or DDH.
- **Cost of SHA-512 in Flock:**
  - GPU hashing is about 1.5× per byte, a few ms per table and under 2% of a proof;
  - proofs grow about 36%;
  - the Lean verifier is about the same;
  - in-circuit, 57,947 against 22,573 AND gates per compression, with the same Flock rows per input byte.

## Post-quantum (Daniel, 21:53Z)

The section is `ASSUMPTIONS.md` §12; the long form with sources is
`lanes/flock-soundness/20260926T2240Z-finding-post-quantum.md`.

- **The oracle layer is post-quantum as it stands:** statistical soundness with classical messages covers quantum
  provers.
- **The compiled layer is post-quantum only asymptotically.** Chiesa–Dall'Agnol–Di–Guan–Spooner (TCC 2025) prove
  interactive BCS post-quantum sound for semi-adaptive IOPs and collapsing vector commitments. Flock fits: non-adaptive
  queries, Merkle caps, kept round bytes. So, if SHA-512 is collapsing (conjectured; Merkle–Damgård preserves it), the
  error is tableError + negl(λ).
- **The loss leaves no concrete bound:** at least 2^157 rewinds for a 2^-128 target, and a factor Σ L_i(q_i+5) ≈ 2^30 on
  the collapsing advantage, give 2^-11 at best. A number needs the quantum random-oracle model, or better quantum
  rewinding.
- **Margins:** Grover 2^256, BHT 2^170.7 (SHA-256: 2^85.3).
- **Zero knowledge:** HVZK carries over. Malicious quantum verifiers need LMS22-style rewinding, and the coin-seed
  commitment on SHA-384/512.
- **Lean:** only quantum-information libraries (Lean-QIT, QICLean). No proof assistant has quantum rewinding or a
  post-quantum succinct-argument proof. qrhl-tool and EasyPQC handle quantum random-oracle proofs only.
- **Recommendation:** claim no post-quantum number in Table 1.

## Root reuse (Daniel, 22:58Z)

The section is `ASSUMPTIONS.md` §13; the long form is `lanes/flock-soundness/20260926T2310Z-finding-root-reuse.md`.

**Flags:**
- **Decision:** state security per table, or as a lifetime budget. Under plain collision resistance, each table's
  rewinding term adds up, `N·t ≤ 2^110.7`: about 2^30 tables at `t = 2^80`.
- **Design change:** commit the long-lived weights root under the SHA-512 leaf and tree scheme.
- **Design change:** draw the root's Halevi–Micali key at commitment, not the pinned key.
- **Decision:** for concurrent malicious-verifier sessions, serialize, use public-beacon coins, or scope it out.
- **Policy:** a predicate budget.
- **Theorem to add:** knowledge soundness, which linking proofs to the registered weights requires.

## Knowledge soundness (coordinator, 23:14Z)

The section is `ASSUMPTIONS.md` §4.4; the long form, with the effort table, is
`lanes/flock-soundness/20260926T2330Z-finding-knowledge-soundness.md`.

- **Statements.** `table_knowledge_sound`: an extractor reruns the prover from its level-0 commitment. Two runs opening
  one position differently are a SHA-512 collision; otherwise it list-decodes the observed columns and outputs a
  satisfying witness, with `Pr ≥ ε − κ`. Then `registered_weights`: the extracted rows equal the registrant's `W`, or
  Halevi–Micali binding gives a collision.
- **Effort by component:** about 1,250–2,000 Lean lines (K1–K9), roughly half the development so far, plus 200–350 for
  witness-extended emulation if recursion needs it.
  - Decoding (K5) is the largest piece and is provable, since CompPoly's Guruswami–Sudan decoder is verified with no
    `sorry`.
  - The extraction analysis (K4) sets the concrete error. A first estimate is `t·2^-227/ε`.
- **Dependencies:** `table_sound_compiled`; the SHA-512 hm96 layout (commitments lane); M1/M2 for recursion.
- **Risks:** the concrete knowledge error; a thin decoding margin at level 0 (about 99% coverage needed); bridging
  representations.

## Zero knowledge against a malicious, concurrent verifier (Daniel's correction, 23:40Z)

`DESIGN.md` §11; `ASSUMPTIONS.md` §6 now states the target without an honest-verifier fallback.

- **The lemma every option uses** is special honest-verifier ZK: a simulator for any fixed coin sequence. VEIL proves
  it for its compiler (Lemma 4.3, "for any value of verifier randomness", perfect). Masked Flock must keep it on binary
  fields.
- **(a) Global serialization.** Collision resistance only, no setup. About 220 round trips per session: negligible
  with a co-located coin server, 11–33 s across a border. Per-identity serialization is defeated by multiple
  identities, so it must be global.
- **(b) Third-party beacon.** Straight-line simulation, but soundness then trusts the beacon (drand: threshold honesty
  and pairings). A beacon the counterparty controls forces rewinding again.
- **(c) Straight-line extraction.** A trapdoor CRS is trusted setup, so excluded. Registered keys (the bare public-key
  model) need LWE. The observable random oracle is hash-only but heuristic.
- **(d) Prabhakaran–Rosen–Sahai preamble.** Collision resistance only, no setup, real concurrency; a heavy proof.
- **Recommendation:** (a) now, (d) if concurrency is required; (c) with registered keys if one public-key assumption is
  acceptable.

## Buying back lifetime budget on the link term (coordinator for Daniel, Sep 27 16:02Z)

*Adopted 16:47Z: the record counts $Q_s$, as the first row suggests. It is now $t\cdot Q_s(8N_0/e)/2^{256}$ ([PR #170](https://github.com/danielreuter/verity/pull/170), with A2's constant corrected to $2^{256}$ at 17:41Z), and audit B holds $2^{-128}$ while $N\cdot t\le2^{81.4}$. The table below, against that record, is also in the lifetime doc's §5 (`docs/lifetime-soundness.md`) for Daniel.*

Before the restatement the link term of record was $t\cdot N_s(8N_0/e)/2^{256}$ per audit (with the corrected constant). Each bit off it is a bit more lifetime $N\cdot t$; at $2^{-128}$, audit B then held while $N\cdot t\le2^{77.1}$.

| Lever | What changes | Bits gained per audit |
|---|---|---|
| Count only the commit strings the drawn units read ($N_s\to Q_s$) | Analysis only: the link finder draws only unit sets that read its target string. The Lean link theorem (#163, `flock_batched_linkSoundE`) proves this form, and the record follows since $Q_s\le N_s$. | A 3.7, B 4.3, C 10.3, D 13 |
| The first-recovery value layer ($4N_0/e$) | Analysis only: the committed transcript chosen by averaging over auxiliary extractions. Noted for later. | 1 |
| A smaller level-0 codeword $N_0$ | Smaller tables: $N_0=2^{21}$ at m = 33 and $2^{23}$ at m = 35, about a bit per step of m. Costs more tables per session. | about 1 per step of m, 6 from m = 33 to 27 |
| Coarser leaves | Row leaves instead of value leaves: #101's $Q_s$ is $2^{15}$ instead of $2^{24}$. A data-layout change with coarser openings. | 9, with $Q_s$ |
| A wider leaf hash | `hm96` over a 1024-bit digest (SHAKE-256, say). The generic bound becomes $T/2^{512}$. A leaf-format change. | about 256: the term vanishes |
| An extractable or clear value layer | Open the linked values in the clear, or commit extractably. Changes the privacy model. | the term goes |

**Not levers:**
- $c$ is already optimal at 2.
- The verifier's own hashing, about $2^{14}$ SHA-512 calls per table, is negligible next to $t$.
- Fewer drawn units trade against the miss term $e^{-\varepsilon s}$.

**With $Q_s$ alone,** audit B's term is $t\cdot2^{-209.4}$, or $2^{-129.4}$ at $t=2^{80}$. $2^{-128}$ over the lifetime then holds while $N\cdot t\le2^{81.4}$. For A–D the term is $t\cdot2^{-218.4}$, $2^{-209.4}$, $2^{-209.4}$ and $2^{-206.4}$.

## Handoffs

- **Sent to `flock-verifier`:** `lanes/flock-verifier/20260926T2125Z-handoff-from-flock-soundness.md` (layout, shared
  arithmetic, refinement shape, the m = 34/35 and §17.2 corrections), and
  `lanes/flock-verifier/20260926T2250Z-handoff-from-flock-soundness-merkle-binding.md` (their L3-M can instantiate
  `Merkle.opening_binding`), `…/20260927T0200Z-handoff-from-flock-soundness-arith-facts.md` (the `Arith.Correct`
  facts in order), and `…/20260927T0330Z-handoff-from-flock-soundness-bounds.md` (their bounds suffice; `Defs.lean`
  states them).
- **Received:** from `flock-verifier`, `note:20260927T0230Z-handoff-from-flock-verifier` and
  `note:20260927T0310Z-handoff-from-flock-verifier` (every `Arith.Correct` field proved, two with bounds).
- `~/.research` is absent on this VM, so no checkpoint went through the CLI. The notes mirror of `internal/lanes/`
  carries this report.
