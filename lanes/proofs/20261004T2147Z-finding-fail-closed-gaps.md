---
id: proofs/20261004T2147Z-finding-fail-closed-gaps
campaign: flock
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: bc-7509ae1c-1900-5288-b462-8a00b5d07123 (flock-design, for proofs), relaying the fail-closed lane's report on cursor/verifier-fail-closed-95d4
---

# fail-closed: what `flock_verify_sound` covers, and four gaps

Branch `cursor/verifier-fail-closed-95d4`, as reported at `5c71a0479` and rechecked at its head `0049dd691`. Every commit
named here is on origin; a commit not on `main` names its branch or PR.

## The theorem and its scope

`FailClosed.flock_verify_sound (zk : Bool) (I : Inputs)` (`FailClosed/One.lean`, `5234d2e30`) states, at every statement,
the claims of the statement's case over every session that `flock-verify verify` accepts and the statement check
(`Flock.ProvedScope.check`, `77450049e`) lets through:

- hidden outputs with `--zk`: `(∀ hn : I.count ≤ 1, SoundZH) ∧ SoundZHJ ∧ ViewZHJ`;
- hidden outputs without `--zk`: `SoundExecH`;
- public outputs with `--zk`: `(∀ hn : I.count ≤ 1, SoundZ ∧ ViewZ) ∧ SoundZJ`;
- public outputs without `--zk`: `SoundExec`.

Each claim's event is `FlockVerifyAccepts zk I t := if zk then VerifiesZK I t else Verifies I t`, and each claim copies its
headline's binders: `SoundExec` is `flock_headline_exec_dec`'s, `SoundExecH` `flock_headline_exec_hidden_dec`'s, `SoundZ`,
`SoundZJ` and `ViewZ` are `Composed`'s `zk_session_sound`, `soundJ` and `view`, and `SoundZH`, `SoundZHJ` and `ViewZHJ` are
`ZkHidden`'s. The sixteen `FailClosed` headlines (`8a94dd3ed`) make these eight claims and stay pinned as lemmas. The axioms
are `propext`, `Classical.choice` and `Quot.sound`.

The check refuses, each with its own message: a statement before `hm96-sha512` rows; a typed statement; no retained
rounds; Merkle leaves other than `hm96-sha512/v1`; more than one table without `--zk`; `--public-inputs`; a circuit that
doesn't parse or a public file that doesn't load; a shared-row public file; and a circuit outside scope v1 (`scopeOk`,
equal to the soundness package's `Layout.scopeOk` by `FailClosed.scopeOk_eq`, `5c71a0479`). From `bc4a02e45` it also
refuses a `vus_per_block` that isn't a power of two at parse (D9), and from `0049dd691` a draw by a law no claim draws by
(D12; gap 3).

Discharged at every accepted session (`dbaf8e8ac`): the reference setups `x₀` and `y₀` at one table (`setup_of_verifies`,
`setupH_of_verifies`, `setupZ_of_verifiesZK`, `setupZH_of_verifiesZK`) and the rate hypothesis `hr` (`hr_exec`,
`hr_execH`, `hr_z`, `hr_zj`, `hr_zh`, `hr_zhj`, through `exists_k`). Still named assumptions: the coin server's custody of
the record and the draw (`RecordCustodyZK`, `RecordCustodyZKJ`), A3 (uniform random bytes), `cr/sha-512`, and for the
views the honest Ligerito prover `LigProver` and `hash-derived-key`.

## Gaps

1. **`hdm` is unchecked.** `ViewZ` and `ViewZHJ` take `hdm : ∀ S y, avoidsMask y.x.st = true`, and the verifier doesn't
   check `avoidsMask`. Its verifier side is #1062's refusal of an output group past its unit's slot (D11, `e5ef81367`,
   head `09c9f08d5` on `cursor/flock-d3-ofrows-95d4`, open), and no Lean proof derives `hdm` from the check. Only zero
   knowledge reads it; soundness doesn't.
2. **The J forms' `y₀` at more than one table.** In `SoundZJ` and `SoundZHJ`, `y₀ : DrawSetupZK(H) I mPts S₀ (dj S₀)` is a
   setup of the whole statement, used only as the refused-table fallback of `tableZJ` and `tableZHJ`. An accepted session
   at `count > 1` gives table setups at `mPtsOf g (kd / nTab I)`, while a whole-statement setup at a `kd`-unit draw has
   `mPtsOf g kd`; the two differ once a draw spans more than 8 blocks per table. The generic claims then hold only by
   choosing `dj` off the law's support. The `_custody_json` corollaries (`zk_session_soundJ_custody_json`,
   `zk_session_soundHJ_custody_json`, whose `hdj` fixes `dj` to the subset draw's JSON) are vacuous whenever
   `mPtsOf g kd ≠ mPtsOf g (kd / nTab I)`, since `UnitDraw.ofJson` refuses a subset draw whose size isn't `kd`. This was
   found by reading the definitions; there is no Lean proof of the vacuity. The fix, a fallback from a setup at table
   inputs (for example `DrawSetupZJ (inputsJ I 0) …`), restates pinned statements and needs a statement reviewer.
3. **Draw laws no claim models.** The claims draw by the stratified law (`SoundExec(H)`, `SoundZ(H)`) or, under `--zk`, by
   the subset law (`SoundZJ`, `SoundZHJ`). At `5c71a0479` the verifier also accepted bernoulli and work draws (with or
   without a closure) in every mode, and subset draws without `--zk`, with no claim over them. From `0049dd691` the branch
   refuses them (`ProvedScope.drawLaw`, D12, `test_lean_draw_laws.py`); the live server and upstream still verify them.
   The same commit's PROTOCOL text names one more case no claim covers: a session without a draw, verified against the
   population's statement. Seed coins (`--coins seed`, the default without `--zk`) are still accepted, and A6 leaves them
   outside every headline (`8526b5436`).
4. **`Verifies` is matched to `verifyCmd` by reading.** `Main.lean` is the executable's root module and no library
   exports it. So `Exec.recordDraw` is a textual copy of `Main.recordDraw`, `Exec.setupOf` is `buildSession`'s hm96 branch
   without `checkRegistered`, and `Checks t zk I := ProvedScope.check t zk I.circuitFile I.publicFile I.tables I.count
   false` matches `verifyCmd`'s call argument by argument only by reading (the argument is `FailClosed/Scope.lean`'s
   module docstring, `5c71a0479`). `verifyCmd`'s extra refusals (`checkRegistered`, `CoinTree.checkFresh`, an unreadable
   session file) only shrink the event, and with `--public-inputs` the check refuses every session. One difference is not
   a refusal: a later session whose draw has the same canonical form as an earlier session's is verified against the
   earlier setup.

## Contradictions in docs and citations (observations, not fixes)

- **Table 1** (`backends/numerical/python/verity_numerical/bench/views.py` on main): `_FLOCK_MCA` cites "Lean
  table_sound", and the soundness string says "knowledge soundness under SHA-512 CR and …" without naming a theorem. Its
  rows include the typed configs (`FLOCK_CIRCUIT_TYPED_CONFIG`, `FLOCK_CIRCUIT_TYPED_HIDDEN_CONFIG`), which the check
  refuses, and frame-v3 and vllm-block (`FLOCK_CONFIG`, `FLOCK_VLLM_CONFIG`), which the Lean verifier doesn't implement.
  Main's hidden-output pin string says "(Stmt.setupHidden: no soundness theorem yet)", which fail-closed's `b7da5c634`
  changes, since `SoundExecH` covers it.
- **PROTOCOL numbering.** Fail-closed's `fb3d13bc0` added the uncovered-form deviation as D10, colliding with main's D10
  (#1040's identifier, `3f19e44bc`) and #1062's D11 (`e5ef81367`). `f4fb1583a` renumbers it D12, so D10 to D12 now agree
  across main, #1062 and fail-closed. §16.15 still collides: fail-closed's is "The forms the soundness proof covers",
  canonical-io's (`cursor/canonical-io-95d4`, `5630d3e78`) "The canonical I/O format".
- **`backends/flock/README.md`** on main says C-Flock ZK (M1/M2) is on draft PRs #123 and #138. Both are closed, and
  `--zk` landed in #793 (`4394c78cf`).
- **`protocols/sampled_proofs/verity_sampled_proofs/one_stage/draw.py`** on main cites
  `FlockSoundness.Audit.Work.work_escape_le`. The theorem is in `Audit/Work.lean`, but its namespace, and the pinned name,
  is `FlockSoundness.Audit.Law.work_escape_le`.
- **The verifier README** on main says no theorem covers `Stmt.setupHidden` yet; `b7da5c634` on fail-closed fixes it.

The `flock` campaign's approach registry (`campaigns/flock/APPROACHES.md`) cites this note where these gaps are the
evidence.
