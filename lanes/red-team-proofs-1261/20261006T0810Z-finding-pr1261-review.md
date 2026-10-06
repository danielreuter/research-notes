---
id: red-team-proofs-1261/20261006T0810Z-finding-pr1261-review
campaign: flock
lane: red-team-proofs-1261
kind: finding
status: final
repo: verity
origin: pr:1261@b4784eb8e0167d59e96b738058209edd8ca2567a
---
# Red team, PR #1261 (the recursive audit's two guarantees): BLOCK, then GRANT at the same head

**Status update, 1:23 AM PDT, 6 Oct: GRANT.** The proofs coordinator fixed the PR body at the same head `b4784eb8e` (no
new commits). I read the posted body (`gh pr view 1261 --json body`) against the one I reviewed.

- B2 is fixed: gap 3's last sentence, the Piece G line, the `rd` fields bullet, the first Limits bullet and the
  Statement review now say `coef` and `dirs` (every public input), with why an untied `dirs` matters.
- B1 is fixed: a new paragraph, "What `VBridge` needs of V\*, beyond gap 3", is the wording below, plus one accurate
  sentence on why `Good` then doesn't tie the sums. The Piece G line and a new Limits bullet point to it.
- Non-blocking note 1 (`miss 1`) is now a Limits bullet.

Label `grant=red-team` on `pr:1261@b4784eb8e0167d59e96b738058209edd8ca2567a`, by red-team-proofs-1261, ref this note,
written 2026-10-06T08:23:37Z. `research data labels … --key grant --remote` shows it "on both", local and remote.

Two remaining nits in the text, both non-blocking: gap 3's heading ("V\* registers `coef` itself") and its first
bullet ("the draw, the rounds' coins and the comb `coef`") still name only `coef`, though the gap's closing sentence
covers `dirs`. And the "Red team" paragraph's "the Lean holds" means my probes and axiom prints passed; the kernel replay
is still `check`'s.

The original review follows.

Reviewed 1:10 AM PDT, 6 Oct, by red-team-proofs-1261 for the proofs coordinator. The review is of head
`b4784eb8e0167d59e96b738058209edd8ca2567a` of `cursor/rec-thm-95d4`, base `main` (`origin/main` `c305471c5`, merge base
`7b410fbf6`), read in a separate worktree (`/tmp/rt1261`). File references are relative to
`verity/Security/Proofs/Flock/Recursive/` unless they start with `verity/`, `backends/` or `tools/`.

**Verdict: BLOCK, on the PR's text, not its Lean.** The Lean is sound as far as I can check it: both guarantees and every
lemma I probed print only `propext`, `Classical.choice` and `Quot.sound` (17 `#print axioms` lines at the head, no `sorryAx`, no
errors, on a build of the head that rebuilt every lane module). The three gap fixes are real
fixes, `boundCR` and `slackCR` are the old premise form where `cr/sha-512` holds, `hown` is something the verifier's own
check establishes, `TagsOk` forces one table, and the lock is the audit's byte for byte.

What blocks is the claim about which V\* the statements cover. The PR says `VBridge` "is provable only once V\*'s staging
registers `coef`", that "Piece G proves them at the V\* that registers `coef`", and its Limits name `coef` as the one gap
between the model and V\* as staged. V\* as staged (`cursor/rec-step3-95d4` at `273017068`, `rec_outer.py` and
`rec_vstage.py`) has two more things the model can't hold:

1. **A registered value the prover chooses after the history, shared by every session.** The running sums `rec-acc` are
   read by every level's statement and by the algebra, and the verifier's reads file takes their root from the prover's
   registration. With `link_rows`, so are `rec-rows-L<level>`. `ZkOuter`'s `own` and `rd` are functions of the history
   `(R, ω, t)` alone, so the model's acceptance event is not the real verifier's.
2. **A second public input, `dirs`.** Every `RecOpen` instance reads `coef` and `dirs` from `public-inputs.bin`.
   `ZkOuter` is the no-public-input path, so `dirs` has to be verifier-registered as well.

Both fixes are text in the PR body, at the same head. Details and the exact wording I'd accept are under "Blocking
findings". I would grant this head once the body says them.

## What I ran

Two runs, on vy-nebius-2, in my own tree (`/workspace/research/scratch/rt1261-c492/tree`). Its three `.lake` directories
are copies, made under the cache locks, of the check cache's kept trees for the head's keys (`lean-deps/50ebab66…`,
`lean-builds/66fdc22f…`, `7df98e67…`, `aaede730…`), never links. The Lean steps ran under an `audit` Lean slot. Both
runs' custody is preserved, and every `out/` file is in the record.

- **r20261006-052640-f0c4** (run record art:c1bf1803e086f586836c966050d39ddc90e192c9e94554c16b78605dd727feb8), at source
  `b4784eb8e`. Its question is in `out/question.txt`. It ran a targeted `lake build Proofs.Flock.Recursive` of the head
  (`build-head.log`: 480 modules rebuilt, including all 16 of the lane's `Proofs.Flock.Recursive*` modules and both
  `Specs.Flock.*.Recursive` modules; "Build completed successfully (4604 jobs)"). Then it ran the probe
  `Probe1261.lean` (`probe-head.log`) and `ProbeZK.lean` at the head (`zk-head.log`), checked out `e7bf84caf`'s Lean
  sources (11 modules rebuilt, 4602 jobs), reran `ProbeZK.lean` (`zk-e7bf.log`), diffed (`zk.diff`), and restored
  the head's sources. `rc.txt`: every step returned 0, and `ZK_DIFF_RC=1` (the outputs differ, see check 5).
- **r20261006-075859-40dc** (run record art:fc10cdade07d67847a369369f92d85479b3d7e982f7eb499b71ffb728add45a6), at
  source `b4784eb8e`. It rebuilt the head in the same tree (4604 jobs) and ran `Probe1261b.lean` (`probe-b.log`), which
  investigated the first run's probe bug (see "Probe bugs").

The first run took 2 h 26 min (05:27–07:53Z). Node 2's Quiet guard paused its Lean for unbooked timed windows (PoUS
`p2_v1` sweep cells) and one booked served window, about 05:31–05:49Z, 05:49–06:15Z, 06:20–06:44Z and 07:05–07:45Z. The
run waited them out (note:red-team-proofs-1261/20261006T0632Z-friction-node2-quiet-pauses-lean).

I did not replay the kernel and did not rerun the PR's audit; `check` does both. The PR's audit is run
`r20261006-032546-c760`, record art:10380efa5e40fb18d9a357eee9e68ec3f3752eeed0c6ed39c441c60a86b9328a, which I fetched and
read (check 6).

## Blocking findings

### B1. `rec-acc` (and `rec-rows-L<level>`) are outside the model, and the PR doesn't say so

**What V\* as staged does.** `rec_outer.py`'s docstring: the openings of both reps are positions `0 .. N - 1` of one chain,
and "the prover registers its `N + 1` rows as the value `rec-acc` … under the V\* session's program string
(`session_program`, which every statement reading the value shares)". Each level's instance reads `acc` at row `p` and
`acc_out` at row `p + 1`, and "V\*'s algebra (`verity_flock.rec_residuals`) reads a rep's first and last rows"
(`rec_vstage.py` line 333: `reads["acc0"], reads["acc1"] = (chain.reg, …)`). In `stage`, the verifier's own reads file
is `own = {"ports": {"out": read(tops.own, …), "acc": read(chain.reg.entry(), at), "acc_out": read(chain.reg.entry(), …)}}`
(lines 227–228). `tops.own` is the verifier's own entry, rebuilt from the recorded `b || c`; `chain.reg.entry()` is the
prover's registration. Under `link_rows` the `row` port reads `rec-rows-L<level>`, also the prover's (lines 234–236).

**What the model can hold.** `ZkOuter.own` (`Flock.lean:51`) and `ZkOuter.rd` (`Flock.lean:62`) are fields of
`zs R ω t j`, so they are fixed by the history before any session starts. Within a session, the prover's registration
`R'` comes after them (`baseGame`: `.send Reg' fun _ => …`), and `hown` quantifies over every `R'` at the fixed `own`.
`rd.committed` needs a registrant's opening of each read's root. The roots the model can hold are the ones fixed by the
history: the hidden circuit's rows (`R`), the verifier's own values (draw, coins, `coef`), and the gateway's commitments
(`rec-c<i>`, tops), which the verifier rebuilds from `t`. The running sums are none of these. They are computed after
the last inner coin from the inner proof's rows and the coefficients. Even with `Cm` carrying openings, their root also
depends on the prover's salts.

**Why it matters.** `RecursiveSound` bounds
`Accepts (zs R ω t) …`, which is `LiveAcceptsZKR I (zs … j).own` at every session: the verifier checks the session's reads
against the model's `own`. The staged verifier checks them against the prover's `rec-acc` root, so it accepts in runs where the
model's verifier rejects, e.g. any registration of a different chain. With `own` set to any history-determined root the
theorem bounds a smaller event than the real one. If `rd` and `own` leave the `acc` reads out, `Good` no longer ties the
levels' sums to one another or to the algebra's reads, and `VBridge` fails the way the plan's gap 2 counterexample does:
a forged sum passes. So `VBridge` can't be proved for V\* as staged even after `coef` (and `dirs`) are registered, and
the vbridge plan saw the need: "The outer hypothesis covers several statements: one per level plus the algebra parts,
sharing `rec-acc` and `rec-c<i>`" (note:proofs/20261005T2345Z-draft-vbridge-plan, line 112). The PR's gap 1 fix shares the
history (so `rec-c<i>` and the tops) but not a value the prover registers once for all sessions.

**Smallest fix (text, no Lean).** In the gap 3 paragraph, in "Every named hypothesis" (the "Piece G proves them" line)
and in Limits, say what `VBridge` needs of V\*. For example:

> `VBridge` is provable only for a V\* whose registered reads all have roots fixed by the history: the hidden circuit's
> rows, the gateway's commitments (`rec-c<i>`, the tops), and the values the verifier registers itself (the draw, the
> coins, `coef`, `dirs`). `ZkOuter`'s `own` and `rd` are functions of `(R, ω, t)`, and each session's `R'` is its own.
> V\* as staged also reads `rec-acc`, the prover's running sums, which it registers once after the last inner coin and
> every level's session and the algebra read, and, with `link_rows`, `rec-rows-L<level>`. The model holds neither, so
> covering them needs a prover registration between the last round and the sessions in `recGame`, with its binding priced,
> or a V\* that doesn't need them (for example, the chain committed through the gateway before a coin).

Either alternative is future work. Neither is needed to merge this PR as a statement about the model.

### B2. `dirs` is a second public input, and Limits names only `coef`

`rec_outer.stage` composes each level's circuit with `public_inputs={"coef": COEF_PUBLIC, "dirs": DIRS_PUBLIC}` and writes
`public = {"coef": coef, "dirs": dirs}` to `public-inputs.bin` (`dirs` is `R.dirs_words(q.pos, H)`, the position's low
bits, which pick the climb's direction at each level). `ZkOuter` is the setup path with no public inputs: `Exec.Inputs`
(`verity/Security/Proofs/Flock/Soundness/Discharge/Exec/Event.lean:36`) has no public-inputs field, `ht` pins
`I.tags.typed = false`, and `FlockVerify.buildStmt` refuses `--public-inputs` for a statement without hidden outputs
(`backends/flock/verifier/lean/FlockVerify.lean:129`). Untied `dirs` would let an instance climb by a direction other
than the one its position names, opening another leaf under the same top. So `dirs` must be verifier-registered (or
computed in-circuit from registered coins) just as `coef` must. The gap 3 heading, "No public inputs", already implies
it, but its last sentence and Limits name `coef` only.

**Smallest fix (text).** Replace "registers `coef`" with "registers `coef` and `dirs` (every public input)" in gap 3's
last sentence, the "Piece G" line and the first Limits bullet.

## Check 1: the three gap fixes are real fixes. Yes, with B1 as their limit

**(a) A family of sessions (`737eac265`, `c5a34134d`). Yes.** V\* at a history is `zs R ω t : (j : Fin S) → (Vs j).Outer
Reg'`, played in a row by `sessions` (`Multi.seqC`, `Multi.lean:150`). `ZkOuter.ofBase_surj` (`Flock.lean:93`) shows
every session strategy has a name, so no prover is lost. `sessions_le` (`Flock.lean:351`) is `accepts_le` at each session
summed by `Multi.prob_seqC_exists_le` (`Multi.lean:191`). The bound is the expected sum of each session's bound at the
strategy named there (`sumS`, `Flock.lean:344`). A later session's name reads the earlier sessions' outcomes, which
is the prover's adaptivity, not a weakening. The family shares the history only (B1).

**(b) `RegAgree` at every unit, a disagreeing read counted bad (`417622a44`, `c5a34134d`). Yes.** `Good`
(`Flock.lean:161`) is no wrong unit and `RegAgree` at every unit, drawn or not. `badUnits` (`Flock.lean:171`) is the
wrong units, `regWrongZ` at the registrant's leaf and `offUnits`, all fixed by `τ`. `badUnits_nonempty` shows a
non-`Good` layer has one, so `miss 1` covers them (`accepts_le`, `Flock.lean:233`). A drawn bad unit is caught by
`zk_session_regDrawnR` (`ZkReg/Vals.lean:153`) or by `off_le` (`Flock.lean:203`), which goes through `hown` and
`checked_of_accepts` to `Reads.prob_offOn_le` (`ZkReg/Off.lean:62`) at `qR²/2^513`. The plan's gap 2 counterexample (an
undrawn `RecOpen` reading another node row) is now a bad unit. This is a proof, not a premise moved elsewhere.

**(c) `coef` verifier-registered (`c5a34134d`). Yes in the model; disclosed for staging; incomplete for staging
(B2).** `ZkOuter.rd`'s docstring now records the verifier's own values, and gap 2's fix makes `Good` tie every unit's
`coef` wires to them. No new field or premise was added for it. The PR says staging still carries `coef` as a public
input; it doesn't say the same of `dirs`.

## Check 2: `boundCR` and `slackCR` are no weaker than the old `hCRo`. Yes

- `RT1261.boundCR_of_CR` and `RT1261.slackCR_of_TabCR` (the probe) prove `boundCR = bound` where `CR` holds and
  `slackCR = stageSlack` where `TabCR` holds, each by `if_pos`. Elsewhere they are `1`, which is ≥ any probability. So
  at a σ whose reached strategies all satisfy `cr/sha-512`, the new right-hand side equals the premise form's, and
  elsewhere the theorem still holds where the old one had nothing to say. Nothing is weaker.
- The one thing `CR` asks beyond the first draft's `hCRo` is the third finder at the new budget `qR`. That isn't a
  weakening: gap 2's fix added the off-leaf term it prices (`off_le`), and the PR body lists it.
- `CR` (`Flock.lean:131`) is `TabCR ∧ RegCRZC … qW ∧ (oneRun … pick).CR H512 qR`. `TabCR` (`Flock.lean:124`) is
  `TableCRZ` at every `ω, j`, the form `zk_session_soundR`'s `hCR` takes. `RegCRZC` is `zk_session_regValsR`'s `hW`.
  The `qR` finder is `StrictCR.oneRun` of the session, outputting `Reads.pick`, the extractor's pair at `offAt`, which is
  the pair `prob_offOn_le` needs. All are the soundness package's existing open `Finder.CR` form (`SHA512CRStrict`).
  The probe's axiom prints show none of them is a hidden axiom.

## Check 3: `hown` is what the verifier's check gives, not an assumption that the attack is absent. Yes

`hown` (`Flock.lean:64`): at an accepted outcome, `OwnReads own c pub t (rd.restrict (rowIn draw)).isRead rd.port
rd.readAt`. `OwnReads` (`verity/Security/Proofs/Flock/Soundness/Discharge/ZkReg/Defs.lean:59`) says each of `rd`'s reads
at a drawn row is a row of a port in `own`, at the position the verifier's program reads there (`unitIndices` of the
drawn statement). It is a static alignment between `rd` and the verifier's reads file plus facts `AcceptsZKR` itself
establishes (`recordDraw`, the draw's parse, `HmRow.drawn`); it says nothing about the prover's leaves. The attack
(an off-leaf read) is then priced by `off_le`, not assumed away. It only constrains reads `rd` records, which is why B1
is about `rd`'s scope and not about `hown`.

## Check 4: `VBridge` is neither vacuous nor too strong for the model's V\*. Yes; too strong for V\* as staged (B1, B2)

**Axioms.** At the head (`probe-head.log`), each of the following prints `[propext, Classical.choice, Quot.sound]`:
`Flock.SecurityProofs.RecursiveSound` and `RecursiveZK`; in `FlockSoundness.Discharge.Recursion`, `zk_sessions_recursive_full`,
`zk_sessions_recursive_upto`, `sessions_le`, `sessions_stage_le`, `ZkOuter.accepts_le`, `ZkOuter.off_le`,
`ZkOuter.ofBase_surj`, `ZkOuter.badUnits_nonempty`, `prob_seqC_exists_le` and `exG_seqC_le`; also
`ZkReg.zk_session_regDrawnR`, `Registered.Reads.prob_offOn_le`, and the probe's three `RT1261` theorems. That is 17
lines, with no `sorryAx` and no errors. `#print axioms` follows the imported proofs transitively, so this covers every
proof the guarantees use. The kernel replay is still `check`'s.

**Jointly satisfiable apart from an accepted session.** At a V\* whose registered reads have history-determined roots,
each premise has a witness. `hS`/`hA3` are the live law's, as at every `zk_session_soundR` user. `hr` is satisfiable for
`k` large, as on `main`. `hCR` and the finder budgets are the existing open form. `ZkOuter`'s fields are the session's
setup (`hc`, `hpub`, `hDraw`, `hRec`, `y₀` from `setupZK…_of_acceptsZK`), `rd` from the registrant's openings, and `hown`
from aligning `rd` with the reads file. `VBridge` itself is deterministic and one-directional, as ruled (Daniel, 5 Oct
6:11 PM PDT). Its `Good` premise now holds at every unit, which the plan's gap 2 needed. I found nothing that makes it
false at such a V\*, and nothing that makes the premises contradictory.

**Too strong at V\* as staged.** B1: with `rec-acc` outside `rd`, `Good` doesn't tie the sums, and a forged sum passes.
B2: with `dirs` a public input, the session isn't in `ZkOuter`'s scope at all.

## Check 5: `RecursiveZK`'s change is value-hash only. Yes, and benign

In the lock (`verity/Security/lean-audit.json`, `e7bf84caf` against `b4784eb8e`), the guarantee record
`Flock.SecurityProofs.RecursiveZK` is unchanged: `type_hash` `444c0683…`, the same signature, no assumptions. It reads
the same 10 module groups at both commits. The only one whose digest changed is `Specs.Flock.Guarantees.Recursive`
(`0aa6793a…` → `8a6f905c…`), because the definition `Flock.Guarantees.RecursiveZK` moved `8d6fab44…` → `68bb5616…` and
`RecursiveSound` was restated. The Specs source text of `RecursiveZK` is that of `e7bf84caf`. The only modules new to
its import closure are `Recursive/Multi.lean` and `Recursive/ZkReg/Off.lean` (449 → 451 modules). The only new instance
attribute in the closure is `attribute [instance] VLaw.fintypeΩ VLaw.nonemptyΩ` (`Flock.lean:284`), which can't fire on
`RecursiveZK`'s types. `tools/lean` is unchanged.

The elaborated definitions, compared directly (`ProbeZK.lean` at both commits, `zk.diff`): same type hash
(`3944470172`), same 51 used constants, and value hash `1464948433` → `3022295254`. The whole difference is one name, in
the used-constants list and once in the `pp.all` term: `Flock.Guarantees.RecursiveSound._proof_1` → `_proof_3`. That
constant is the `Nat.AtLeastTwo 2` proof inside `instOfNatAtLeastTwo` for the `(2 : ℝ≥0∞)` of `2 ^ (-193)`. Lean
abstracts it once per module and shares it between the two statements, so restating `RecursiveSound` renumbered it.
Same proposition, same statement.

## Check 6: the lock is the audit's, and nothing outside the lane changed. Yes

- `sha256(verity/Security/lean-audit.json)` at `b4784eb8e` is `0007ba9c67419924…`, equal to the lock in
  art:10380efa…'s `out/audit-verity_Security/lean-audit.json`. The audited commit is `c5a34134d`, which is the head
  minus the lock commit.
- Against `main`'s lock: two new guarantees (`RecursiveSound`, `RecursiveZK`), 12 new `reads` modules (the lane's), and
  183 existing reads lists extended with the two guarantees. No definition's digest outside the lane changed. The
  policy additions (`exempt`, `assumptions`, `meaning`, `reads_exempt` for `Specs.Flock` and `Proofs.Flock.Recursive`)
  extend Daniel's 4 Oct C-Flock exception, as the PR says.
- The audit's `verity/Security/Proofs` failure is `generate-Proofs.Warden.DifftestMain.log`:
  "`verity.protocols.accounting.communication.warden` comes from `/workspace/research/src/c5a34134d…/…`, not from the
  checkout". That is the run's Python shim importing the source snapshot instead of the audit's tree, not a Lean failure,
  and it is independent of this PR.

## Check 7: `hTags` forces `I.count ≤ 1`. Yes

`RT1261.tagsOk_count : TagsOk I → I.count ≤ 1 := fun h => h.2.2.2` elaborates (the probe), at `TagsOk`
(`Discharge/DecodeZL/Statements.lean:87`) and `Exec.Inputs.count`. So each session is one table, and its `y₀ :
DrawSetupZK I mPts S₀ (dj S₀)` and `dj` are its own; the #1264 class of defect can't occur here.

## Check 8: the merge is clean, and `main` hasn't moved under the branch. Yes

`git merge-tree --write-tree origin/main b4784eb8e` is clean (tree `d3d8e571…`). `origin/main` (`c305471c5`) is 65 commits
past the merge base `7b410fbf6`, and none of them touches a `.lean` file, a lock, `tools/lean`, a lakefile, a manifest
or a toolchain.

## Check 9: what Limits and Premise leave out

Blocking: B1 and B2. Non-blocking:

1. **The bound is small only where V\*'s laws draw every unit.** One bad unit anywhere breaks `Good`, so the outer bound
   carries `Lm.miss 1`, the chance a draw misses one fixed unit. Unless V\*'s sessions are proved in full, that is close
   to `1`. This is the price of gap 2's fix and is visible in the statement. A Limits line would help a reader.
2. **`zs` is total.** Piece G must give `rd` at every history, including ones where a dishonest gateway's commitment has
   no opening at some read. There `rd` must leave the read out, and `VBridge` must hold without `RegAgree` at it. I
   believe it does, because the commit positions bind the layer's tops through `obK`/`cmt`, but nothing checks it yet.
3. **Finder budgets are free reals.** `qF, qS, qW, qR` and `q i` are parameters the statement doesn't relate to any
   running time. That is the soundness package's convention, unchanged.
4. **`RecursiveZK`'s lock record churns when `RecursiveSound` is restated.** The two Specs statements share an
   auxiliary proof (check 5), so any edit to `RecursiveSound` moves `RecursiveZK`'s definition digest, and with it the
   statement-review trigger, although `RecursiveZK` didn't change. That's harmless but noisy. Stating the `2 ^ (-193)`
   once as a named constant in the Specs module would stop it.
5. **Later sessions' names read earlier outcomes.** That is the prover's adaptivity (check 1a), and it's harmless.

Already disclosed and fine: the forward direction only, `hOuter` a joint simulator for sessions in a row, `cmt`/`obK`
not linked to `gatewayLeaf`, no HVZK or beacon corollary, and no kernel replay or `check` yet.

## Probe bugs (mine, not the PR's)

- `Probe1261.lean`'s `#eval` listing what each guarantee's proof uses, and whether the proof reaches
  `zk_sessions_recursive_full`, printed empty lists. The second run shows why: in this toolchain
  `ConstantInfo.value?` is `none` for an imported theorem (`hasValue=false size=0` for both guarantees), so a
  `getUsedConstants` walk over a theorem's value sees nothing. It doesn't affect any finding. Each guarantee's type is
  the Specs statement itself (`Flock.SecurityProofs.RecursiveZK : Flock.Guarantees.RecursiveZK`), the statement's
  content is checked on the Specs definitions (check 5), and `#print axioms` covers the proofs.
- The first draft of the probe named `Law` without its namespace (`FlockSoundness.Audit.Law`). I fixed it before
  launch. The `if_pos` deprecation warnings in the probe are harmless.
