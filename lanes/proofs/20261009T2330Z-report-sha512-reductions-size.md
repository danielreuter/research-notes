---
id: proofs/20261009T2330Z-report-sha512-reductions-size
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-5737a706-931b-5555-a15d-9206d236e0b9
---

# SHA-512 as reductions: sizing the restatement (for top, Slack 1791585044.741179)

**Summary (paste-ready)**

1. **Statements that change: 8 guarantees on main, plus 1 on a branch.** On main: `Flock.SecurityProofs.EndToEnd`, `EndToEndDrawn`, `EndToEndHidden`, `EndToEndHiddenDrawn`, `EndToEndRegistered`, `EndToEndRegisteredDrawn`, `RecursiveSound` and `FlockSoundness.Discharge.FailClosed.flock_verify_sound`. These are exactly the lock's `frozen (hash, …)` entries that take `TableCRZ`/`LinkCRZC`/`Finder.CR`. On `cursor/rec-audit-land-95d4`: `RecursiveAudit`, whose fork disjuncts become terms. Two other `hash`-frozen guarantees, `RecursiveZK` and `ZeroKnowledgeHidden`, rest on `hash-derived-key` (hiding), not on collision resistance, so they are out of scope. PoUW (`Hidden.lean`, `FlockTile/Statement.lean`) is not forced to change if the old forms stay as corollaries.
2. **Size: about 0.9k–1.6k Lean lines, almost all interface changes.**
   - The six end-to-end statements plus `flock_verify_sound`: 400–700 lines.
   - `RecursiveSound`: 150–300 lines.
   - `RecursiveAudit` in probability form: 300–600 lines, of which about 150–300 are the one new piece of math (see item 5).
   - **The proofs already compute every finder and its bound as a term.** The conjecture enters only in the last step: `Finder.CR.le`, `adv*_le_strict`, `stage_bind`'s `(hinv pos).trans (hCR pos).le`, and `link_mass_le`'s `h3`.
   - The knowledge and fork finders need no internal change. Instantiate the existing theorems at the budget `q := √(2^513·ε)`, with ε the finders' largest success (a definable sup over draws, tables and levels). The CR hypothesis then holds by definition, and `q²/2^513` reads `ε`.
   - The link finders do need restating through the link chain (12–15 theorems, about 40 `2^256` sites). The expected-time form can't be met by choosing `t'` without losing a factor `2(1+k)` ≈ 2^23.6.
3. **The fork disjunct as a probability term is a square root with no 1/q loss.** `fork_ref` (`Recursive/Fork.lean:253`) already proves `Pr[off at pos]² ≤ ε_fork(pos)`. So the round-fork term is `Σ_{i<r} Σ_pos κ_i(pos)·√ε_fork,i(pos)`, which is `RecursiveSound`'s existing `(Σκ)·√(q²/2^513)` with the conjecture taken out.
   - **8090-class values used:** r = 257, ρ = 1/2, `--draw subset:n` (so κ = 1/(1−ρ) = 2). I assumed K = Σ_pos κ_i, the number of commit strings carrying a round message, of 2^16 (plausible) or 2^36 (the loose Q_s ≤ 2^35 cap). K is not in the Lean or the notes.
   - **Under `cr/sha-512`** the term is 257·K·q·2^-256.5. At q = 2^64 that is **2^-148.5 (K = 2^36) or 2^-168.5 (K = 2^16)**, against the proved statistical 2^-191.9. The total stays under the 2^-128 target for q ≤ 2^84.5 (K = 2^36) or q ≤ 2^104.5 (K = 2^16).
   - Without the root, the term would be 2^-341 at q = 2^64 and invisible. The root costs half the collision exponent: 192.5 of 385 bits at q = 2^64.
   - The session knowledge terms (√(N·Q·ε) per table) and the inner table's terms are already roots today. I estimate about 2^-163 for the sessions and 2^-170 for the inner table at q = 2^64. The link term is linear, with no root.
4. **Alternatives if the root is too costly.**
   - (a) Shrink K, a layout lever: have V* carry each round's message through few commit strings, for example the message's digest. At K = 2^4 per round the term is about 2^-180 at q = 2^64.
   - (b) Replace rewinding at the round commitments with straight-line extraction in the random-oracle model, where the extractor reads the commitment's hash query. That gives a linear term, about q²/2^512, but it changes the assumption from `cr/sha-512` to the ROM (`rom-cr`), so it is Daniel's call.
   - Merging the forks into one finder by Cauchy–Schwarz gains nothing under a uniform budget.
5. **What makes it larger, though nothing makes it impossible.**
   - (i) The link chain needs a real restatement (item 2).
   - (ii) The sessions' `boundIf` is `if ZkOuter.CR … then bound else 1` at budgets fixed across the strategies τ. A per-τ ε needs the budgets generalized to functions of τ through `zk_sessions_recursive_full/upto` and `outerV_stage_le`, or a sup over every reachable τ.
   - (iii) **New math:** `InnerForkRec` in probability form needs the inner compiled table's fork finders under `refStrat` to be dominated by σ's own fork finders. That means a relabelling of two-run finders; today `leafAvg_relabel` covers one run. This sits in the part of `RecursiveAudit`'s proof that is open anyway.
   - (iv) Every changed guarantee record moves in the lock, so Daniel gets 8 diffs (9 once `RecursiveAudit` lands). The definitions the statements read barely grow, because `TableCRZ`/`LinkCRZC` already read the finder definitions.

Everything below was read on origin/main at fetch time and on `origin/cursor/rec-audit-land-95d4`. Nothing was built.

## 1. Where the hypotheses are used (file:line, origin/main)

- **The definitions:**
  - `Security/Proofs/Flock/Soundness/Assumptions.lean:52`: `SHA512CRStrict`, which says `(∀ b, cost b ≤ q) → Pr[coll] ≤ q²/2^513`.
  - `Assumptions.lean:77`: `SHA512CRExpected`, which says `Pr[coll] ≤ E[cost]/2^256`.
  - `ASSUMPTIONS.md:31-32` and `:169-174` give the table of which term each one bounds.
- **The per-finder wrapper:** `StrictCR.lean:86`, `Finder.CR H q := SHA512CRStrict H g s id (fun _ => q) q`. Its `.le` (`:89`) is the only place a `q²/2^513` is produced.
  - Users: `adv₀_le_strict:299`, `advR_le_strict:306`, `self_le_strict:318`, `table_sound_compiled_strict:329`, `advRS/adv₀S/selfS/epsS_le_strict:405-438`, `ksBoundAccB_le_strict:470`, `ksAvgBE_le_strict:495`, `TreeRewind.le:228`.
- **The link (A2):**
  - `Audit/FlockLink.lean:487` (`trial_mass_le`, `hCR`), `:522` (`ideal_mass_le`) and `:651-656` (`LinkCR`).
  - `LinkFinder.lean:308` (`link_mass_le`: the only consumer of the A2 inequality, at `h3`).
  - It reaches the guarantees through `ZkLink/Link.lean`, `ZkLink/CompiledLink.lean`, `Discharge/Exec/FlockLinkL.lean` and `Audit/FlockLinked.lean`.
- **The Z-layer packaging:**
  - `Discharge/ZkLink/StrictZ.lean` (`TableCRZ`, `ksAvgStrictZ`; 17 `2^513` sites).
  - `LinkCRZC` (ZkLink).
  - `Discharge/Exec/StrictCRL.lean` (`TableCRL`, `LinkCRL`; 11 sites).
- **The recursion:**
  - `Recursive/Fork.lean:309` (`stage_bind`, `hCR` used once at `:328`).
  - `Recursive/Sound.lean:65-129`, `Recursive/Flock.lean:501` (and `ZkOuter.CR`/`boundIf` on the branch, `Flock.lean:~170`).
  - `Recursive/Stage.lean:550`.
  - `Recursive/ZkReg/Off.lean:60` (`qR²/2^513`, `δ_reg`) and `Recursive/ZkReg/RegLink.lean:152` (`Finder.CR` for the registered-value finders).
  - `Recursive/Target.lean:184-186`.
- **The end-to-end statements:** `EndToEnd/Statement.lean:95-107`, `EndToEndDrawn/Statement.lean:78-88`, `EndToEndHidden/Statement.lean:94-106,158-168` and `EndToEndRegistered/Statement.lean:94-106,166-177`.
  - All six defs have one shape: binders `(qF qS : ℝ)` and `t'`, then the hypothesis `∀ ω j, TableCRZ … qF qS`, then `LinkCRZC … t'`. The bound is `ksAvgStrictZ … qF qS + ofReal(Σ_p w_p·(2t'(1+k)/2^256 + 1/(eM) + k/(eRw))/(1−ρ))`.
- **`RecursiveSound`:** `Recursive/Statements.lean:54`, with `_hCR : ∀ i < I.r, ∀ ω pos, (forkAt … i ω pos).CR H512 (q i)` and the bound term `(Σ_pos weightS i pos)·√(q_i²/2^513)`. Its sessions use `boundCR`/`slackCR` at `qF qS qW qR`.
- **`flock_verify_sound`:** its conjunct defs in `Discharge/FailClosed/*` take `TableCRZ` and bound the link as `if LinkCRZC then bound else ⊤`. Lock note: `lean-audit.json:3207`.
- **PoUW (not in scope):**
  - `Definitions/Pouw/PearlC/Hidden.lean:30-34`: its `Bounded` class is the provers whose finders meet `cr`/`ecr` at q.
  - `Proofs/Pouw/PearlC/FlockTile/Statement.lean:33`: `F.Cls` is `TableCRZ` and `LinkCRZC`.
  - It keeps working if the old Flock forms stay as corollaries.
- **Other non-guarantee consumers:** `CROnly/*`, `Binding/E2E.lean`, `Registered/*`, `ZK/GK/{Extract,Link,Theorem}.lean`, `Headline.lean`, `Teeth.lean` and `Discharge/Exec/*L.lean`. All stay on the old forms via corollaries.
- **The lock's own reasons:** `Security/lean-audit.json:3149-3157` (`frozen`), e.g. "takes the table and link finders' collision bounds (TableCRZ, LinkCRZC) as hypotheses instead of a collision disjunct tied to the run".

## 2. The fork disjuncts (branch `cursor/rec-audit-land-95d4`)

- `Recursive/Defs.lean:60`: `FindsColl H g s out := ∃ b, Outcome g s b ∧ IsColl H (out b)`. This is existential over reached outcomes, with no probability.
- `Recursive/Stage.lean:589` `RoundFork := ∃ i < r, ∃ ω pos, (forkAt … i ω pos).Finds H512`; `:598` `SessionFork := ExAt σ … ∃ j, ZkOuter.Fork …`. `Flock.lean:177` `ZkOuter.Fork` is "some knowledge, registered-value, row-read or link finder finds a collision".
- `Compile.lean:161` `InnerForkRec`: a `forkG` of σ's continuations after round i whose decoded inner transcripts `pick` reads as a collision. Its proof (`zk_sessions_recursive_fork_inner`) is marked open.
- `Property.lean:148` `RecursiveAudit` (i) (`:201`): `RoundFork ∨ SessionFork ∨ InnerForkRec ∨ (∃ o, reached ∧ VerifiesV ∧ ∃ i, reads ∧ row ≠ p i ∧ Collides) ∨ Pr ≤ bound`.
- **How the fork form is made today** (`Stage.lean:~610-660`, `zk_sessions_recursive_fork`): it runs the probability form `zk_sessions_recursive_full` at budgets 0. With no fork, `Finder.cr_of_not_finds` gives CR at budget 0, so the √ term is √0. So the probability form exists already for the round and session forks; the fork form throws it away.

## 3. Per-guarantee notes

| guarantee | what changes in the statement | proof |
|---|---|---|
| `EndToEnd`, `…Drawn`, `…Hidden`, `…HiddenDrawn`, `…Registered`, `…RegisteredDrawn` | Drop the binders `qF qS t'` and the two hypotheses. Replace `ksAvgStrictZ … qF qS` with the same closed form at `εF(σ), εS(σ)` (the largest success of the rewinding and self-clash finders over ω, j, (r, ℓ) and level 0). Replace `2t'(1+k)/2^256` with `εL(σ, p)`, link finder p's success. About 8–12 statement lines each, plus docstrings. | The knowledge part is unchanged inside: instantiate at `qF := √(2^513 εF)` and prove `Finder.CR` by definition (about 30 lines once, shared). The link part goes through the restated link chain. The wrapper proofs are about 10–20 lines each. |
| `flock_verify_sound` | Seven conjunct defs (`SoundZ`, `SoundZJ`, `SoundZH`, `SoundZHJ`, `SoundZHJR`, `SoundExec`, `SoundExecH`) change the same way. `if LinkCRZC then … else ⊤` becomes the ε form. | Same as the row above; about 100–200 lines. |
| `RecursiveSound` | `_hCR` and `q` go away, and `√(q_i²/2^513)` becomes `√εfork_i(σ)`. The sessions' `boundCR … qF qS qW qR τ` becomes a bound at τ's own ε. | `stage_bind` is unchanged (instantiate q). Per-τ budgets need the constants generalized to functions of τ through `zk_sessions_recursive_full/upto`, `outerV_stage_le` and `ZkOuter.bound/slackIf`: mechanical, 150–300 lines. |
| `RecursiveAudit` (branch) | The four existential disjuncts become terms. Round forks: `Σ_i Σ_pos κ√ε`. Session forks: the sessions' bound at their ε. Inner fork: the compiled table's `√(2^logN·Q·ε)` terms at σ's inner fork finders. The registered-row collision: one run's success, linear. | The round and session parts reuse `zk_sessions_recursive_full`. The inner part needs the two-run relabelling (new, 150–300 lines) inside an already-open proof. Total 300–600 lines. |

**Per-finder or max.** Using one sup per finder kind (εF, εS, εfork_i) keeps today's closed forms character for character. It is exact against today's number once the conjecture is applied, because every finder gets the same budget. A per-finder term, a separate ε for each (r, ℓ) and each pos, means restating `ksStrict`, `epsS` and `ksAvgStrict(Z)` over a family of ε. That adds about 150 lines and still changes no proof internals.

## 4. Arithmetic at the 8090 class (`UniversalUnit_v1{G=8090,N_IN=64,N_OUT=32}`)

**Inputs, with sources:**
- Proved statistical total 2^-191.92 (`internal/proofs/rate-soundness-number.md`, line 30).
- r = 257 rounds: 2 reps × 128 coin rounds + 1 (same file, line 260).
- 8 stages (sessions).
- `--draw subset:n`, so `candWeightK` is `1/(1−ρ)` on `Sk` (`Stage.lean:104`).
- ρ = 1/2.
- k = 6,171,993 (≈ 2^22.56).
- Level-0 table length 2^logLen₀ ≈ 2^21, from rateZ = 0.125 = 2^logLen₀/(e·k).

**Assumed:**
- Every finder's budget q = 2^64 SHA-512 evaluations.
- Queries per level of about 2^8 (so 2Q₀ ≈ 2^9).
- K = Σ_pos κ_i per round across the sessions, at 2^16 or 2^36. K is not pinned in the Lean or the notes.

**Round forks.** The term is `Σ_{i<257} K·√ε_i`, and under `cr` ε_i ≤ q²/2^513, so √ε_i ≤ q·2^-256.5. That gives 257·K·q·2^-256.5 = 2^(8.006 + log K + log q − 256.5).

| K | q = 2^64 | q = 2^80 | largest q for 2^-128 |
|---|---|---|---|
| 2^36 | 2^-148.5 | 2^-132.5 | 2^84.5 |
| 2^16 | 2^-168.5 | 2^-152.5 | 2^104.5 |
| 2^4 (layout lever a) | 2^-180.5 | 2^-164.5 | 2^116.5 |

The same term without the root would be 257·K·q²/2^513, which is 2^-341 at K = 2^36 and q = 2^64.

**Session knowledge terms.** These are already roots today and in `RecursiveSound`. Per table, `√(2^21·2^9·q²/2^513) = q·2^-241.5`, which is 2^-177.5 at q = 2^64. About 13 such terms per table (level 0 plus 2 reps × about 6 levels) give about 2^-173.8. Multiplying by (1 + 257) × 8 stages, if the slack carries them as it carries `tableErrZ`, gives about **2^-162.8**.

**Inner table terms.** The same shape, counted once: about **2^-170**.

**Link term.** It is linear (`link_mass_le`: mass ≤ Pr[finder succeeds] + 1/(eM)). With A2 applied afterwards it is today's `Q_s·t'·2^-231.44` per stage (rate report, line 334).

**The registered-row collision.** It is one run, linear: `qR²/2^513`, negligible.

**Total at q = 2^64.** The statistical part (2^-191.9) is dominated by the cryptographic terms: about 2^-148.5 at K = 2^36, or about 2^-162 at K = 2^16, where the session roots dominate. Either way it clears DESIGN §7's 2^-128.

## 5. Why the knowledge finders need no internal change

`Finder.CR H q` is `(∀ b, q ≤ q) → ev ≤ q²/2^513`. At `q := √(2^513·ε)` with `ev ≤ ε`, this is `ev ≤ ε`, true by definition. So `∀ ω j, TableCRZ … (√(2^513 εF)) (√(2^513 εS))` holds for every prover when εF and εS are the sups of its own finders' success. The existing theorems then give the probability form directly.

The same trick does not work for `SHA512CRExpected`. Its right side is `E[finderCost(t')]/2^256`, and setting `t' := 2^256·εL` gives a bound of `2(1+k)·εL`. Once A2 is applied, that is a factor 2(1+k) ≈ 2^23.6 worse than today. So the link chain gets its real restatement: replace `link_mass_le`'s `h3`/`h5` step with `Pr[coll]` and thread `εL c` up through about 12–15 theorems.
