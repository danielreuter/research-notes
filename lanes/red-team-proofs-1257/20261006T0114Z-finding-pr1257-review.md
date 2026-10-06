---
id: red-team-proofs-1257/20261006T0114Z-finding-pr1257-review
campaign: proofs
lane: red-team-proofs-1257
kind: finding
status: final
repo: verity
origin: pr:1257@8bb07eeb90e090395089efb90c5981716e2802e2
---
# Red team, PR #1257 (Flock.Guarantees.EndToEnd and its proof): NO-GRANT

Reviewed 6:14 PM PDT, 5 Oct, by red-team-proofs-1257 (agent bc-b9c1b330-d613-5466-afde-bfa0ceb41cdd) for the proofs
coordinator. The review is of head `8bb07eeb90e090395089efb90c5981716e2802e2` of `cursor/flock-e2e-95d4`, base `main`
`7b410fbf6`, read in a separate worktree (`/tmp/rt1257`). I built nothing and ran no Lean. File references are relative to
`verity/Security/` unless they start with `backends/` or `tools/`.

**Verdict: NO-GRANT.** At `J = nTab I ≥ 2` tables the statement's hypotheses cannot all hold, except when the whole draw fits
in 8 blocks (`⌈kd / c.g⌉ ≤ 8`). The theorem therefore says nothing about the multi-table session that its docstring and the
PR body describe, and neither of them says so (finding 1). At `J = 1` I found no unsatisfiable hypothesis. The proof is the
three steps the body claims, and the audit-policy entries are honest. Each fix I would accept for finding 1 is small.

## Check 1: the statement says what the body says. Passes, except at J ≥ 2 (finding 1)

- **The event** is `LiveAcceptsZK I o ∧ K₀ ≤ (P.wrong (XplurZC …)).card` (`Specs/Flock/Guarantees/EndToEnd.lean:87-88`).
  `LiveAcceptsZK` is `AcceptsZK` of the live transcript: `setupOf (zkInputs I)` sets up, every table passes `Zk.shapeOk`,
  and the real `Flock.Zk.verify` returns `.ok ()` (`Proofs/Flock/Soundness/Discharge/ZkExec/Event.lean:48-55`). So the
  event is "flock-verify --zk accepts ∧ at least K₀ units wrong", as claimed.
- **Wrong** means the unit is not `Correct` in the committed transcript: its committed gates differ from `localEval` of its
  committed inputs (`Proofs/Flock/Soundness/Audit/Circuit.lean:182-199`). The committed transcript is `XplurZC`, the
  plurality behind each commit string (`Discharge/ZkLink/CompiledLink.lean:138`). The units are those of
  `keyProg c hU n`, which is `n` copies of the circuit's VU rows (`Discharge/Placed/Keyed.lean:56`), partitioned at
  `Layout.outsOf`. This matches the body and the docstring. That the count is a Prop of `σ`, independent of the outcome, is
  disclosed in item 1 of "stops short".
- **The right-hand side** is exactly `C(n−K₀, kd)/C(n, kd) + ksAvgStrictZ + ENNReal.ofReal(Q_s · (2t'(1+k)/2^256 +
  1/(eM) + k/(eR_w)) / (1−ρ))` (`EndToEnd.lean:89-94`), with `Q_s = ∑ p, |ΩcZ p| / |L.Ω|`. This is the body's
  binomial miss + ε_ks + δ_link.
- **The setting** is "one `--zk` session of `J = nTab I` tables, `kd / J` in each" (`EndToEnd.lean:25-26`, and the body's
  "In words"). At `J ≥ 2` it is not delivered (finding 1).

## Check 2: the statement is not vacuous. Fails at J ≥ 2 (finding 1)

- `TableCRZ` (`Discharge/ZkLink/StrictZ.lean:182`, built on `SessCRZ` and `Finder.CR`, `Proofs/Flock/Soundness/StrictCR.lean:86`)
  and `LinkCRZC` (`CompiledLink.lean:548`) are per-prover claims about the simulated prover's finders. An honest prover's
  finders find no collision, so both hold for it. These are the named `cr/sha-512` and `ecr/sha-512`, and item 6 discloses
  that Lean does not check the budgets.
- `RecordCustodyZKJ` is `RecordsLiveZKJ ∧ DrawFileZK dj (.subset kd) n` (`Proofs/Flock/Soundness/Assumptions/Zk.lean:48`).
  `TagsOkZJ` (`Composed/DefsJ.lean:522`) and A3 (`Assumptions.lean:97`) are each satisfiable on their own.
- `ρ < 1` together with `hr`: `rateZ j k = 2^logLen / (e·k)` (`Discharge/ZkLink/Compiled.lean:394`), which is below 1 once
  `k > 2^logLen / e`. That is satisfiable.
- The RHS is well below 1 for realistic parameters: the miss term is small at moderate `kd` and `K₀`, and δ_link is small at
  large `M` and `R_w`. `K₀` can be anything up to `n`.
- **Finding 1** (blocking): `y₀`, at `EndToEnd.lean:58`, is a setup of the whole draw at the per-table `m_pts`. Together with
  `hCust.2`, this is unsatisfiable at `J ≥ 2` once `⌈kd / c.g⌉ > 8`.

## Check 3: the proof uses only what it claims. Passes

`Proofs/Flock/EndToEnd.lean:19-25` is three steps:
1. `Discharge.Composed.zk_session_soundJ_custody`.
2. `rw [Law.subset_miss hkd hK₀, Discharge.ZkLink.linkBoundZC, ite_eq_left hA2]`, where `linkBoundZC` is `if LinkCRZC … then
   ofReal … else ⊤` (`CompiledLink.lean:557`) and `subset_miss` is at `Audit/Law.lean:142`.
3. `exact`.

The new files contain no `sorry`, `axiom` or `native_decide`. The four proof terms inside `σ` are all `theorem`s:
- `rsZJ_computes` (`DefsJ.lean:327`)
- `decodesOnZKJ_of_runsOnZCJ` (`DefsJ.lean:508`)
- `runsZCJ_live` (`DefsJ.lean:665`)
- `drawOkZKJ_of_file` (`Composed/CustodyJ.lean:86`)

I did not rerun `r20261006-001047-00a2` (`--no-replay --no-runs`), as the assignment allowed.

## Check 4: the audit-policy entries are honest. Passes (finding 3 is a note)

- **`exempt`** (`lean-audit.json:5`) is honest about why `Specs` cannot import the module. Exemption only takes the module out
  of the orphan check (`tools/lean/audit.py:574-581`). The source scans still read it, since they cover every file of the
  package.
- **`meaning`** (`lean-audit.json:59`) is what makes the reads walk digest `Flock.Guarantees.EndToEnd`
  (`audit.py:707-747`). The record has a reads entry for the module (digest `368b4aa5…`, definition `cd66de8b…`).
- **`reads_exempt`** (`lean-audit.json:234`) waives only the "read outside the `layers` spec" failure, and cites Daniel's
  ruling (4 Oct, 1:30 PM PDT).
- **The four proof terms do not affect meaning.** They are proofs of Props, so proof irrelevance applies and `meaningDeps`
  contributes nothing for a theorem (`tools/lean/Facts.lean:193-196`). The walk still covers every constant in their
  arguments, so the digest covers everything the statement reads.
- **The record** `Flock.SecurityProofs.EndToEnd` (`lean-audit.json:402`: owner `@proofs`, `assumptions: []`, type hash
  `98d68470…`) has the same shape as `Pouw.SecurityProofs.EndToEnd` (owner `@compute-accounting`, `assumptions: []`).
- Finding 3 covers the replay gap and the definition count.

## Check 5: the "stops short" list. Incomplete

Finding 1 belongs in it. So does `scopeOk`'s restriction (finding 2).

## Findings

### 1. BLOCKING: vacuous at J ≥ 2 tables unless ⌈kd / c.g⌉ ≤ 8, and not disclosed

The theorem binds `y₀ : DrawSetupZK I (mPtsOf c.g (kd / nTab I)) S₀ (dj S₀)` (`EndToEnd.lean:58`). That is a setup of
`zkInputs I` at the **whole** draw `dj S₀`, at the **per-table** `m_pts`. The chain that forces the constraint:

1. `y₀.x : DrawSetup (zkInputs I) mPts S₀ (dj S₀)` (`Discharge/ZkLink/TablesAt.lean:160-161`) carries
   `h : Stmt.setupH … (some (dj S₀)) … = .ok st` and `hmPts : st.mPts = mPts` (`Discharge/Integrate/Sites.lean:38-54`).
2. `setupH_mPts_drawn` (`Discharge/Exec/Pts.lean:123`) gives `st.mPts = mPtsOf st.c.g ud.proved.size`, where `ud` decodes
   the whole draw.
3. `setupH_facts` (`Pts.lean:32`), with `zkTyped ht` (`Discharge/ZkBind/At.lean:41`) and `hc`, gives `st.c = c`.
4. `hCust.2 : DrawFileZK dj (.subset kd) n` (`Assumptions/Zk.lean:48`, `Discharge/ZkLink/DrawOk.lean:125`) gives
   `ud = drawOf (.subset kd) n S₀`.
5. `drawOf_proved` (`DrawOk.lean:128`) and the third conjunct of `ofJson_shape` (`CustodyJ.lean:34-38`) give
   `ud.proved.size = kd`.

So the hypotheses force `mPtsOf c.g kd = mPtsOf c.g (kd / nTab I)`.

Here `mPtsOf g x = 24 + max 3 (log2ceil ⌈x/g⌉)` (`Pts.lean:23`, with `PT_LOCAL = 24` and `log2ceil` from
`backends/flock/verifier/lean/Flock/Net.lean:14`). Let `m = ⌈kd/g⌉` and `b = log2ceil m`. At `J ≥ 2`,
`⌈kd/(Jg)⌉ ≤ ⌈m/2⌉`, whose `log2ceil` is at most `b − 1`. For `m > 8`, `b ≥ 4`, so the left side is `24 + b` and the right
side is at most `24 + max 3 (b − 1) = 24 + b − 1`. So at `J ≥ 2` the hypotheses hold together only when `⌈kd / c.g⌉ ≤ 8`,
where both sides are `24 + 3`.

The prover chooses `g`: `backends/flock/python/verity_flock/circuit.py:589-592` doubles it while `2·g·U.n ≤ 4096`. So
`g = 1` for any unit of more than 2048 rows, and there `kd ≤ 8`. A smaller example: `g = 1`, `kd = 16`, `J = 2` would need
`28 = 27`.

The real verifier does not have this constraint. Each table sets up at its part draw (`inputsJ`, `drawJ`), with `kd / J`
units and `m_pts = mPtsOf c.g (kd / J)`, and `planZJ`'s tables are built that way (`DefsJ.lean:74, 153-159`). Only the
fallback `y₀`, whose `refused` table `tableZJ` uses where no table sets up (`DefsJ.lean:153-156`; `TablesAt.lean:233`), is
typed at the whole draw.

The constraint is inherited from `zk_session_soundJ_custody` on `main` (`CustodyJ.lean:190`, the same binder at
`7b410fbf6`). `zk_session_soundJ` alone does not fix `y₀` to the draw file. But this PR is the one that states the guarantee
for "`J = nTab I` tables" and records it.

At `J = 1`, `nTab I = 1` makes the two sides equal, and I found nothing else unsatisfiable. `J = 1` is the GPU prover's
configuration (`backends/flock/pod/gemm_hill.py:496`). But `Proofs/Flock/Soundness/Discharge/ZkReg/SoundHJ.lean:8` calls
`--session-tables J` "the production configuration", and the docstring (`EndToEnd.lean:25-27`) and the body both promise
`J` tables.

**Fixes I would accept**, any one of:
- (a) State the theorem at one table (`I.count ≤ 1`, or `nTab I = 1`), and say so in the docstring and in the body's mode
  list (item 4).
- (b) Make the fallback per-table, so that `y₀` is satisfiable at `J ≥ 2`. For example, take it as a
  `DrawSetupZJ (inputsJ I j₀) … (drawJ I (dj S₀) j₀)`, or take the refused table as its own binder at the per-table
  `m_pts`.
- (c) At minimum, disclose the restriction (`J ≥ 2` only when `⌈kd / c.g⌉ ≤ 8`) in the docstring and in "stops short",
  with the scratch lemma below landed as a theorem so that the constraint is stated in Lean.

**Scratch Lean, not run.** I could not run it: this VM must not build `verity/Security`, and it has no pod access. I'm asking
someone with a built tree to run `lake env lean` on it, from `verity/Security`.

~~~lean
import Proofs.Flock.Soundness.Discharge.Composed.CustodyJ
open FlockSoundness FlockSoundness.Discharge FlockSoundness.Discharge.Exec FlockSoundness.Discharge.ZkExec
  FlockSoundness.Discharge.ZkLink FlockSoundness.Discharge.ZkBind FlockSoundness.Discharge.Composed

/-- `EndToEnd`'s `y₀` and `hCust.2` force the whole draw's `m_pts` to equal the per-table one. -/
theorem e2e_forces_mPts {n : ℕ} (I : Inputs) (ht : I.tags.typed = false) {c : Flock.Circuit}
    (hc : HmRow.parse (zkTags I) I.circuitFile I.tables = .ok c) (kd : ℕ)
    (dj : Finset (Fin n) → Lean.Json) {S₀ : Finset (Fin n)}
    (y₀ : DrawSetupZK I (mPtsOf c.g (kd / nTab I)) S₀ (dj S₀))
    (hdj : DrawFileZK dj (.subset kd) n) :
    mPtsOf c.g kd = mPtsOf c.g (kd / nTab I) := by
  obtain ⟨ud, hud, hm⟩ := setupH_mPts_drawn y₀.x.h
  have hcst := (setupH_facts y₀.x.h).1
  rw [zkTyped ht] at hcst
  simp only [Bool.false_eq_true, ↓reduceIte] at hcst
  have hst : y₀.x.st.c = c := Except.ok.inj (hcst.symm.trans hc)
  have hDe := hdj S₀ ud hud
  have hsz : ud.units.size = kd := (ofJson_shape hud).2.2 kd (by rw [hDe]; rfl)
  have hp : ud.proved.size = kd := by rw [hDe, drawOf_proved, ← hDe, hsz]
  rw [← y₀.x.hmPts, hm, hst, hp]

/-- An instance where it fails: `g = 1`, `kd = 16`, `J = 2`. -/
example : mPtsOf 1 16 ≠ mPtsOf 1 8 := by
  simp [mPtsOf, Flock.log2ceil, Flock.PT_LOCAL, Nat.log2]  -- 28 ≠ 27; `Nat.log2` is well-founded, so not `decide`
~~~

### 2. Non-blocking: `scopeOk`'s restriction is not in "stops short"

`hscope : scopeOk c = true` (`EndToEnd.lean:54`; `Discharge/Layout/Scope.lean:37`) requires:
- exactly one leaf group (`inGroups.size == 1`);
- a unit that returns its outputs (`outNet == unitNet`) with no tail stage;
- `unitLog ≤ 32`;
- reads at its ports (`portReadsB`);
- v1 ports only (`v1Ports`).

The body lists it only as "the circuit's scope check". Item 4 ("One mode") should name it.

### 3. Non-blocking: two notes on the audit record

- The exempt module `Specs.Flock.Guarantees.EndToEnd` is not under either package's `roots`, so neither audit's kernel
  replay names it (`audit.py:1239-1253` replays `facts["modules"]`, the modules under `roots`). The source scans and the
  transitive axiom walk do cover it. The `exempt` reason could say this. Nothing is unsound: the only declaration in it is a
  `def` of a Prop, and its value is digested through `meaning`.
- The body says the statement reads "3809 definitions in 177 modules". The record lists 177 modules and **3345**
  definitions under `Flock.SecurityProofs.EndToEnd`, counting `definitions` over the `reads` modules whose `guarantees`
  include it. Correct the count or say what 3809 counts.

## Label

None (NO-GRANT). After finding 1 is fixed, a re-review of the new head needs only to check that fix, plus the two-line
body edits for findings 2 and 3.
