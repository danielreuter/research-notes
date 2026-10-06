---
id: proofs/20261006T2352Z-public-input-restack-plan
campaign: pouw-v2-e2e
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: pubin-scope (bc-f19f4dea, worker of the proofs coordinator bc-8416bc72), for top's 3:30 PM PDT mark
---

# pubin-scope: what PoUW's end-to-end needs at the v2 session's form

Read-only. Refs: main `40438bd85`; tip 82 = `origin/cursor/train-prep-82-on-caeb25908-4292` at `062e72525f12`, which is
main's `142dcc452` plus #1257 and #1332–#1335 (24 Flock files). Main has moved past `142dcc452` only outside
`verity/Security`, so tip 82 is still the base to restack onto. All dry runs below are `tools/move/restack.py
--dry-run --json` from main's copy. Nothing was pushed, and restack's scratch worktrees are gone. The dry runs left
only unreferenced local commit objects in `/workspace`'s object store, and their JSON outputs are in
`/tmp/pubin-scope/{lean,layout,chain}-*.json` on this VM. No Lean was built: every "builds" claim below is an
inference, not a build.

## TL;DR

- **TT is the wrong slot.** `Pouw.Assumptions.TT` is the timing (hardware) assumption of the ideal-commitment game. No
  proof-system theorem goes in it, so leave `Pouw.Guarantees.EndToEnd` as it is. C-Flock enters PoUW at the hidden
  audit's open obligation `Pouw.PearlC.Assumptions.TileProofSoundAll P TR D HA ηzk`. That obligation is the `hzk`
  hypothesis of `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` (giving `GγHidden`). It is met through
  `tileProofSoundAll_of_tileGame` by one `TileGame` per tile.
- **No Flock theorem on main or tip 82 covers a v2 `--zk` session with the verifier's public inputs.** Two reasons:
  - Every `Flock.Guarantees.EndToEnd*` on tip 82 takes `hscope : Layout.scopeOk c = true` (every row a
    `sha512/row/v1` row) and `hpt : pub.tables = none`. A v2 session has canonical rows (every row an unsegmented
    `sha512/row/v2` row), so it is outside them.
  - Their event `LiveAcceptsZK I` sets up through `Inputs`, which has no `publicInputs`. So `HmIn.checkOwn … none`
    refuses every circuit with public-input ports, and the event is false on `TileRead`. The run that `flock-verify
    verify --zk --public-inputs F_σ` actually accepts is in no theorem: on main this is a form ahead of its proof.
- **What's missing, in order:**
  - `Canonical.zk_session_sound_canonicalP` (frozen in words in #1201's `Gaps.lean`) and its custody/json forms.
  - A guarantee in `EndToEndHidden`'s form at canonical rows and `own`.
  - The verifier un-refusing `--public-inputs` at `canonicalOk`, landing with it.
  - On the PoUW side: a C-Flock `HiddenAudit`, a `FlockSoundness.Game → Verity.Game` bridge, and the per-tile
    `TileGame`.
  - L4 (`--zk --registered`, public input ℓ) adds the canonical registered-reads gap (#1320's V3 plus
    `RegisteredRowC`).
- **None of the stack's declarations is on main or tip 82.** I checked these 16 names, with 0 hits on tip 82 for each:
  `setupOfP`, `AcceptsZKP`, `zk_session_soundHP(R)`, `RecordCustodyZKP`, `public_pinnedC`, `canonicalOk`, `formatOk`,
  `statementRules`, `flock_verify_sound`, `zk_session_sound_canonical`, `zk_session_soundC_verifies`,
  `ownAtDrawsHP_of_check`, `ownAtDraws_of_check`, `zk_session_soundR_own`, `checkSession`, `tableUnits`. What *is*
  superseded:
  - #1179's y₀ edits, which tip 82 already has (`cef6316b0`, `642a0886d`).
  - #1049, which #1121 supersedes (#1121 contains it plus the API fix-up `6f1eb2551`).
  - #1170's lock selection, which must be recomputed after the move and tip 82.
- **Shortest path:**
  1. Restack #1179, then #1192, onto tip 82. Rebase #1201 onto #1192 first (1 conflict) and carry it along.
  2. Then the new work: canonical-P in the Flock area; L4's registered gap in parallel.
  3. The PoUW-side bridge can start now.
  - Drop #1170 (redo it), #1049 and #1060.
  - Port the P family from #1121's head, not by restacking a branch 2,000+ commits behind main.

## 1. What PoUW's end-to-end at the v2 session's form needs

### Where the proof system plugs into PoUW (main = tip 82 here)

- `Pouw.Guarantees.EndToEnd` (`Specs/Pouw/Guarantees/Game.lean`) and its proof `Pouw.SecurityProofs.EndToEnd :=
  Pouw.Proofs.endToEnd` (`Proofs/Pouw/Game.lean`, by `gammaFromTT`, `theorem1`, `workWeightedSampling` in
  `Proofs/Pouw/Theorem1.lean`) are over the ideal-commitment game. `AuditAccepts (correctSet P U H s
  (A.transcript U H s))` opens the drawn tiles. Its hypothesis `Assumptions.TT CM P D γ₀ ε` (`Specs/Pouw/Assumptions/
  Game.lean`) is `CM.Queries ∧ Pr[T/(1−γ₀) < Σ_{u∈checkedSet} Wmm] ≤ ε q N`. That is the device's time per unit of
  checked work. **TT is instantiated with the cost model, protocol, domain, γ₀ and ε of a device (the
  hardware/timing facts), never with a Flock theorem.** There is no proof-system slot in `EndToEnd`.
- The proof system's slot is the hidden audit (`Definitions/Pouw/PearlC/Hidden.lean`). There, `HiddenAudit Q R S`
  has the fields `Root`, `Opening`, `root`, `game : (Q → R) → S → Workload → Root → ℕ → Verity.Game Bool` and
  `Bounded`, and `GγHidden CM P TR D HA γ η ηzk` is `GγSampled`'s bound with the drawn tiles proved, not opened, at
  `+ t·ηzk(q)`. The chain:
  - `Pouw.PearlC.gammaHidden_of_sampled_all` (`Proofs/Pouw/PearlC/HiddenGamma.lean`): `GγSampled` +
    `TileProofSoundAll P TR D HA ηzk` give `GγHidden`.
  - `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` is that theorem at Pearl-C rev1, with `hzk : TileProofSoundAll …`
    still a hypothesis. **Discharging this `hzk` at the C-Flock v2 hidden audit is "PoUW's end-to-end at the v2
    session's form".** The citation names both guarantees (10-03 ruling).
  - `TileProofSoundAll` (`Specs/Pouw/Assumptions/PearlC/HiddenTile.lean`, the open obligation) ⇐
    `tileProofSoundAll_of_tileGame` (`Proofs/Pouw/PearlC/HiddenTileGame.lean`). That theorem needs `HA.Bounded =
    BoundedByInduced Cls`, plus a `TileGame P TR HA Cls ηzk U τ o H s g` for every tile
    (`Definitions/Pouw/PearlC/HiddenTileGame.lean`) with these fields:
    - `G : Verity.Game Out`, `verdict`, and `game_eq : HA.game H s U (HA.root U τ o) g = G.map verdict`;
    - `bad_le : Cls … → Pr[verdict ∧ Bad] ≤ ηzk q`;
    - `good_of_accept : verdict x ∧ ¬Bad → g ∈ goodTiles ∪ blankTiles`.

### What the Flock side must supply

`bad_le` must come from a Flock soundness guarantee about the v2 session the verifier accepts. `Cls` is that
guarantee's CR hypotheses (`TableCRZ` at cr/sha-512, `LinkCRZC` at ecr/sha-512), stated without reading goodness.
`good_of_accept` is the binding: an accepted, non-Bad TileRead instance at the public `t_s` read the window's
committed rows at `tile_at(t_s)` (TileRead's gates, L4, hm96 binding).

None of the candidates does this:

- **tip 82 `Flock.Guarantees.EndToEnd`, `EndToEndDrawn`, `EndToEndHidden`, `EndToEndHiddenDrawn`**
  (`Proofs/Flock/*/Statement.lean`): J tables (`y₀ : DrawSetupZ(H)J (inputsJ I 0) …`), law `Law.execOS src (.subset
  kd) n`, wrongness `wrongRegZ` at `XplurZC`. Bound: `C(n−K₀,kd)/C(n,kd) + ksAvgStrictZ + δ_link`, or `ε_ks + δ_link`
  at the drawn units. All of them carry `hscope : Layout.scopeOk c = true` and `hpt : pub.tables = none`. `scopeOk`
  includes `v1Ports c` (`c.ports.all fun p => !p.v2 && …`, `Layout/Scope.lean`). **A v2 session fails it.** Their
  event `LiveAcceptsZK I` runs `setupOf (zkInputs I)`, and `Inputs` (`Discharge/Exec/Event.lean`) has no
  `publicInputs`. So `Stmt.setupTables … I.closure` runs `HmIn.checkOwn pi pop none`, which throws on any circuit
  naming public-input ports ("pass the verifier's own recomputation"). **On TileRead the event is false, so the
  theorem is vacuous there.**
- **tip 82 `EndToEndRegistered`(`Drawn`)**: J tables, `own : Array Registered.Port`, event `LiveAcceptsZKR I own`, at
  `scopeOk`. Its second conjunct concludes `rd.Checked` from the premise `OwnReadsHJ …`, which nothing discharges
  (#1121's `ownAtDraws_of_check` does, at one plan). Registered `own` ports are not `--public-inputs` (HmIn) ports.
- **`ZeroKnowledgeHidden`**: the zero-knowledge half (`ZkViewAtJ`, 2^−193, `hash-derived-key`), not soundness.
- **`RecursiveSound`** (`Proofs/Flock/Recursive/Statements.lean`): V*'s outer sessions `ZkOuter`
  (`Recursive/Flock.lean`) are `scopeOk`, one plan (`DrawSetupZK`), `--registered`, with the verifier's own values as
  registered `own` ports and `hown : … OwnReads …` a field. `InnerSound I εin` (`Recursive/Defs.lean`) is a
  hypothesis. The recursion is a later path: InnerFold refuses public-input inner statements (note
  `lanes/proofs/20261006T1940Z-draft-units-to-inner-layout`, steps 6 and 8).

### The missing theorems, in Lean terms

- **T1. `FlockSoundness.Discharge.Canonical.zk_session_sound_canonicalP`.** #1201's `Canonical/Gaps.lean` freezes it
  in words: `zk_session_sound_canonical` (#1192, `Canonical/Headline.lean`) at a different event, units and
  extraction.
  - **Event:** `LiveVerifiesZKP I own`, i.e. `AcceptsZK` with every table's `setupHidden` at `some own`, and
    `ProvedScope.check` with `publicInputs` true.
  - **Units:** those of `keyProgP` (`keyProg`'s gates plus one gate per public leaf bit).
  - **Extraction:** `Xpub pubOnes pubZeros XplurZC`.
  - **Unchanged:** J tables, `y₀ : DrawSetupZHJ (inputsJ I 0) …`, `hv : scopeOk (circZ I) = false`, the law, the
    parameters, and the bound `miss(K₀) + ksAvgStrictZ + linkBoundZC`.
  - **Reused:** the binding fact `Canonical.public_pinnedC` (#1201, `Canonical/PubIn.lean`) is proved. The event and
    key-program definitions are #1049's (`setupOfP`, `AcceptsZKP`, `keyProgP`, `pubOnes`, `pubZeros`, `SpecP`,
    `setupHidden_specP`), which `Gaps.lean` notes "do not read the circuit's form".
- **T2.** T1's `_custody` / `_custody_json` / drawn forms, as `zk_session_soundC_custody_json` is for the canonical
  headline: over the printed draw file, with the record custody `RecordCustodyZKJ`'s P sibling (#1049 has
  `Assumptions.ZkPubIn.RecordCustodyZKP` at one plan).
- **T3. The guarantee.** Proposed names `Flock.Guarantees.EndToEndCanonicalP` and `…Drawn`: `EndToEndHidden(Drawn)`'s
  statement without `hscope`/`hpt`, at canonical rows and `own`, so that `Pr[LiveVerifiesZKP I own o ∧ K₀ ≤ |wrong|]
  ≤ miss + ε_ks + δ_link`. It needs:
  - "wrong" measured against the public file (`wrongRegZ`, tip 82 step A, #1332) at canonical rows, where #1192
    counts `Partition.wrong`;
  - the drawn-unit form (step B, #1333).
  - `Statement.lean` and proof go under `Proofs/Flock/EndToEndCanonicalP/`, like tip 82's.

  `bad_le` reads this.
- **T4. Verifier.** `ProvedScope.statementRules` drops `!publicInputs` at a statement that `canonicalOk` passes; Rust
  `proved_scope::statement_why` drops `public_inputs` there. `FailClosed.flock_verify_sound` gains the case
  (`SoundZHJC` at `own`). `Gaps.lean`: "The verifier change goes in with the headline."
- **T5. L4's form** (`--zk --registered`, public input ℓ, P registered v2 entry rows).
  - Under `formatOk`, `Registered.checkPort` refuses every `v2` row (tip 82 `Flock/Registered.lean:135`).
  - #1320 (`cursor/registered-row-v2-95d4`, draft, not in tip 82: `Port.fits` takes an unsegmented v2 row) is V3.
  - Then `Gaps.lean`'s `RegisteredRowC` / `registered_rowC` (a frozen `sorry` there), the registered reads in the
    canonical `--zk` event (`rd.Off`, `qR²/2^513`), and T1 at `own`: the HRP analogue, with #1121's
    `ownAtDrawsHP_of_check` discharging `OwnReads`.
- **T6. PoUW side** (new; no Flock dependency to start).
  - A `FlockSoundness.Game → Verity.Game` translation with `prob` preserved. The two inductives have the same shape
    but are distinct types (`Proofs/Flock/Soundness/Game/Basic.lean` vs `Definitions/Core/Game.lean`), and no bridge
    exists.
  - The C-Flock `HiddenAudit`: Root = the window root; `game` = the TileRead session's live game through the bridge;
    `Bounded = BoundedByInduced Cls` with `Cls` = T3's CR hypotheses.
  - The honest prover's `ProverBounded` pin (`HiddenAudit`'s docstring requires it beside any citation).
  - `TileGame` per tile from T3 (`bad_le`) and TileRead + L4 (`good_of_accept`).
  - `tileProofSoundAll_of_tileGame` then discharges `hzk`.
- **Recursive path, later:** `InnerSound` at a public-input inner statement (#1261's `InnerSound` instantiated with
  F_σ) and InnerFold `--public-inputs` (note steps 6 and 8).

## 2. Per PR of the stack

Restack results are in the dry-run outputs (`plain` = a plain merge onto the target; `moved` = after rerunning the
move script, merged with the move as base). There are two moves:
- The **Lean move** `bcb527224` (base `7e71bfdca`, landed in `7b410fbf6`) is in tip 82. #1179, #1170 and #1192 contain
  only the earlier layout move.
- The **layout move** `f0dde01ec` (base `2095960db`): #1201, #1049 and #1121 don't even contain its base, so they need
  the layout move first, then the Lean move.

The rename move `afc9d352d` is in tip 82 too, but touches no Flock path.

**#1179 `cursor/verifier-fail-closed-95d4`** (head `ca8e3a26c`, 59 files, +9593/−463; merge base `378453fb3`, 1052
behind main).
- **Adds (none on tip 82):**
  - `Flock/ProvedScope.lean` (`statementRules`, including `(!publicInputs, "public input ports (--public-inputs)")`,
    `check`, `lawWhy`), Rust `proved_scope.rs`, `flock-circuit.rs`, and the D12 drawless refusal.
  - `Discharge/FailClosed/{One,Composed,Exec,Mask,Scope,ZkHidden}.lean` with `FailClosed.flock_verify_sound (zk) (I)`
    over `FlockVerifyAccepts zk I`.
  - Docs (PROTOCOL §16.15), `agree.py`, `ci.py`, tests, and 6.7k lock lines.
- **Superseded:** its y₀-at-table-0 restatement in `Composed/DefsJ`, `ZkHidden/DefsJ` (and `CustodyJ`, `SoundJ`, …)
  is tip 82's `cef6316b0` / `642a0886d` (#1257), the same text. Take tip 82's side.
- **Restack** (lean.py from `bcb527224` onto tip 82): *conflicted at moved, 4 files*:
  - `Composed/DefsJ.lean` and `ZkHidden/DefsJ.lean`: take tip 82's.
  - `Integrate/Headline.lean`: one doc paragraph.
  - `backends/flock/tests/test_lean_zk.py`: #1179's D12 `_passes`/`DRAWLESS` edits against tip 82's.

  Its new FailClosed files move cleanly. The lock merges textually but must be regenerated (`audit.py --build
  --update` through `research run` on node 1). The plain merge has 14 conflicts.
- **Hazard:** landing #1179 makes `flock-verify` refuse `--public-inputs` everywhere. That is PoUW v2's form (note
  steps 3–5). See Q1.

**#1170 `cursor/flock-lock-reduction-95d4`** (head `1d8b99cdf`, on an older #1179). It changes locks only: from 874
pins to 41 (the 16 Table 1 theorems and 24 Partitioning pins; drop about 750 lemma pins; the verifier and level3 locks
keep no pin), plus three doc commits (`8d4561fc3`, `d6e821e9a`, `980746b56`).
- **Restack:** *conflicted at moved, 7 files*: both locks, `Soundness/ASSUMPTIONS.md`, and #1179's 4.
- **Superseded:** the selection predates the move (the soundness lock is now part of `verity/Security/lean-audit.json`:
  778 FlockSoundness guarantees on main) and tip 82's 29 `Flock.*` guarantees. **Drop it and redo it** on the
  restacked #1179: re-select the pins, cherry-pick the three doc commits, then `audit.py --update`.

**#1192 `cursor/canonical-v1-95d4`** (head `57a52cf1f`, 29 files, +4917; merge base `378453fb3`; it lacks #1179's
current head, 29 own commits).
- **Adds:**
  - `ProvedScope`'s `rowOk`, `formatOk` and `canonicalOk tags zk c := zk && tags.hiddenOutputs && c.outNet ==
    c.unitNet && formatOk c`, with `check = scopeOk c || canonicalOk …`.
  - `Discharge/Canonical/{All,Chain,Commit,Format,Gaps,Headline,OutCopy,Outputs,Reads,Rows,Session,Shared,Sites,
    Statements,Verifier}.lean`, about 3.6k Lean lines.
  - `zk_session_soundC_verifies` and `zk_session_sound_canonical` (J tables, already at table-0 `y₀`; counts
    `Partition.wrong` at `XplurZC`, not tip 82's `wrongRegZ`).
  - Edits to `FailClosed/{One,Scope,ZkHidden,Composed}`, `Main.lean`, `circuit.rs`, `proved_scope.rs`, and the
    canonical-format tests.
- **Superseded:** nothing. It needs a T3-style restatement (step A) to become a guarantee.
- **Restack** (lean.py onto tip 82, standalone): *conflicted at moved, 5 files*: `backends/flock/tests/
  test_lean_verifier.py`, plus #1179's 4 (`test_lean_zk.py`, both `DefsJ`, `Integrate/Headline`), which it inherits
  from the older #1179 it contains. The plain merge has 30 conflicts.
  - #1192 merges *cleanly* onto #1179's current head (`git merge-tree ca8e3a26c 57a52cf1f`), and its own patch touches
    none of those 4. So restacked onto S1, its expected conflict is `test_lean_verifier.py` alone.

**#1201 `cursor/canon-pubin-95d4`** (head `e30302586`, 5 own commits, 9 files, +983/−59; on an older #1192
`da5d1f42c`, 1693 behind main).
- **Adds:**
  - `Canonical/PubIn.lean` (`PublicPinnedC`, `ownWord`, `public_pinnedC`, 803 lines).
  - `Gaps.lean`'s frozen T1 and its tails / registered-reads gaps.
  - Tests (a canonical statement with a public-input port sets up under the verifier's own file and is refused for its
    ports), `proved_scope.rs`, PROTOCOL §16.16, and the lock.
- **It does not contain T1.**
- **Restack:** its own patch onto #1192's current head (`git merge-tree --merge-base=da5d1f42c 57a52cf1f
  e30302586`) has *1 conflict*: `backends/flock/tests/test_lean_canonical_format.py`. So rebase it onto #1192 and
  carry it through #1192's restack, rather than moving it twice from far behind.
  - Layout dry run from `f0dde01ec` onto `7e71bfdca`: *conflicted at base* (merging the layout move's base
    `2095960db`), 1 file: `backends/flock/verifier/PROTOCOL.md`. The plain merge has 2 conflicts.

**#1049 `cursor/zk-pubin-95d4`** (head `3c652848e`, 22 files, +7031; merge base 2747 behind main).
- **Adds:**
  - `Discharge/ZkPubIn/*` (20 files, about 5.1k Lean lines) and `Assumptions/ZkPubIn.lean`.
  - Event level, which doesn't read the form: `Defs` (`setupOfP`, `AcceptsZKP`, `AcceptsZKRP`, `LiveAcceptsZKP`,
    `ownWord`, `OwnWords`, `LeavesPublic`, `keyProgP`, `pubBit`, `pubOnes`, `pubZeros`), `Spec` (`setupHidden_specP`),
    `Setup`, `Tables`, `Reg` (about 950 lines).
  - Row level, at scopeOk rows: `Flat`, `HmP`, `KeyWire`, `InPin`, `Sites`, `SiteP`, `KeyP`, `Bind` (about 3.2k
    lines).
  - Session level, one plan with the stratified law: `Count`, `Composed`, `Runs`, `Sound`, `SoundCustody` (about
    970 lines), giving `zk_session_soundHP`, `zk_session_soundHRP` and the `_custody` forms.
- **Superseded:** #1121 contains it and adapts it to main's v2-output-row API (`6f1eb2551`: `hv : p.v2 = false` in
  `checkRows_words`, `outBitRow_ne_none`). Its row and session levels are the wrong form for v2 (`scopeOk`, one plan).
  **Drop it as a PR**, along with #1060.
  - Layout dry run: *conflicted at base*, 1 file: the root import list `FlockSoundness.lean` (`ZkPubIn` vs main's
    `ZkEveryCoin` and `PadNonvanishing40`; a union). The plain merge has 1 conflict.
  - **Chained**, with that union resolved on a scratch index (local commit `26b3ac668`, never pushed), then layout.py
    onto `7e71bfdca` (clean, `edb59155b`), then lean.py onto tip 82: **clean**, `cdf859b42`. Against tip 82 that's 24
    files, +7059/−7:
    - the 20 files at `verity/Security/Proofs/Flock/Soundness/{Discharge/ZkPubIn/*, Discharge/ZkPubIn.lean,
      Assumptions/ZkPubIn.lean}`;
    - `import Proofs.Flock.Soundness.Discharge.ZkPubIn` in `Proofs/Flock/Soundness.lean`;
    - the custody assumption's `upstream` entry `live-verifier-custody-pub` in `Proofs/lean-audit.json`;
    - 1845 stale record lines in `verity/Security/lean-audit.json`, to regenerate;
    - `moves.json` entries.

    So the move costs nothing for ZkPubIn's files. Whether they build at tip 82 is unbuilt here; the drift check under
    #1121 says the only expected breaks are the `hv` binders that `6f1eb2551` fixes.

**#1121 `cursor/own-at-draws-hp-b-95d4`** (head `6257a46f8`, not draft, contains #1049, 18 own commits, merge base
2086 behind).
- **Adds over #1049 (none on tip 82):**
  - `Flock.Registered.checkStmt`, `checkSession` and `tableUnits` (`Main.checkRegistered` moved into the library;
    `Main.lean` is `FlockVerify.lean` after the move).
  - `ZkReg/Own.lean` (`ownReads`, `ownAtDraws_of_check`) and `zk_session_soundR_own`.
  - `ZkPubIn/Own.lean` (`ownAtDrawsHP_of_check`), plus edits to `ZkReg/Checked` and `CheckedH`.
  - `6f1eb2551`.
- **Drift:** #1049's 18 imported modules changed from its base to tip 82 only by import renames, apart from `HiddenExec/
  {SiteH,Ret,KeyH,Copies,Sites}`. The only signature changes there are the `hv` binders that `6f1eb2551` already
  follows. **So #1121's head is the source to port from.**
  - Layout dry run: *conflicted at base*, 4 files (the plain merge has the same 4):
    - `FlockSoundness.lean` and `Discharge/ZkReg.lean`: import unions (`ZkReg.Own` vs main's `ZkReg.{DefsHJ,BindHJ,
      CheckedHJ,SoundHJ,SoundHJCustody}`).
    - `soundness/lean-audit.json`: `merge.py` refuses it ("regenerate the record on the merged tree"), because
      `ZkReg.checkRegistered` is read on one side only.
    - `Discharge/ZkReg/Checked.lean`: a **real proof conflict**. Both sides changed `Registered.checkPort`, and the
      `split at h` scripts follow two different shapes of it. This needs a build to resolve, so the dry run can't go
      further.

    Port its own files rather than restacking the branch: `ZkReg/Own.lean` 277 lines, `ZkPubIn/Own.lean` 146, and the
    `checkSession` / `tableUnits` verifier code.

## 3. The shortest path

**Base:** tip 82 (`062e72525f12`), or main once train 82 lands (they differ outside `verity/Security` only).

- **S0. PoUW-side scaffold** (now, in parallel with everything; touches `Proofs/Pouw` only): T6's Game bridge
  (`FlockSoundness.Game → Verity.Game`, strategies, `prob`, about 100–200 lines), the C-Flock `HiddenAudit` value, and
  the composed theorem stated with T3 as a hypothesis. Its `good_of_accept` needs TileRead's Definition (compute-
  accounting's step 3 in the inner-layout note). Without it, state the binding as a named hypothesis. Where it lives:
  Q3.
- **S1. Restack #1179 onto tip 82:**
  - `restack.py origin/cursor/verifier-fail-closed-95d4 --script tools/move/lean.py --move-commit bcb527224 --onto
    062e72525f12`;
  - resolve the 4 files (two take-theirs, one doc paragraph, one test merge);
  - one node-1 `audit.py --build --update` for the lock;
  - `check`.

  The patch won't be byte-identical (the DefsJ hunks drop out), so under the 6 Oct ruling any red-team grant on
  #1179 doesn't carry by itself. The remaining delta is FailClosed, ProvedScope and Rust. Sequencing it against PoUW
  v2 is Q1.
- **S2. Restack #1192 onto S1:** first merge #1179's head into #1192 (clean), then restack; expect one conflict,
  `test_lean_verifier.py`. Then rebase #1201's 5 commits onto it (1 conflict, in `test_lean_canonical_format.py`) and
  regenerate the lock once for both.
- **S3. T1 + T2 (the bulk, one Lean lane, on S2).** Three parts:
  - **Port** #1121's event-level files as they are (`ZkPubIn/{Defs,Spec,Setup,Tables,Reg,Own}`, about 1.1k lines, at
    their moved paths under `Proofs/Flock/Soundness/Discharge/ZkPubIn/`). The #1049 chain shows the move is
    mechanical: the path prefix `backends/flock/verifier/lean/soundness/FlockSoundness/` becomes
    `verity/Security/Proofs/Flock/Soundness/`, imports `FlockSoundness.` become `Proofs.Flock.Soundness.`, and there
    are no conflicts.
  - **Re-prove** rows, sites and binding at canonical rows at `keyProgP`. These replace #1049's scopeOk `Flat`, `HmP`,
    `KeyWire`, `InPin`, `Sites`, `SiteP`, `KeyP`, `Bind` (about 3.2k lines there), and build on #1192's `Rows`,
    `Sites`, `Commit`, `OutCopy`, `Session` and #1201's `public_pinnedC`. A public gate is one gate whose registered
    bit `public_pinnedC` gives (`Gaps.lean`).
  - **Lift** the session to J tables and canonical: `Count`, `Composed`, `Runs`, `Sound`, `SoundCustody` → `…J`,
    sized like main's ZkHidden J-lift (`DefsJ` 666 + `CustodyJ` 168 + `CustodyJJson` 69 + `SoundJ` 83 lines).

  Then T4 (Lean `ProvedScope`, Rust `proved_scope.rs`, the `flock_verify_sound` case, tests: an F_σ refusal and a
  one-word forgery) and new pins. The event-level port can start on tip 82 before S1–S2 land.
- **S4. T3 guarantee** (on S3): `Statement.lean` and proof, following #1332 and #1333's restatements at canonical rows;
  lock with `audit.py --update`. Daniel gets the guarantee-record DM automatically; nobody signs off.
- **S5. T5 for L4** (a second Lean lane, in parallel with S3 on S2): #1320's V3, `RegisteredRowC`, the registered reads
  in the canonical `--zk` event, the HRP analogue at `own`, and #1121's `checkSession` / `ownAtDraws_of_check` lifted
  to HJ. Different files from S3 (ZkReg and Registered vs ZkPubIn); the two meet only in T3's registered form.
- **S6. Close T6:** instantiate S0 with S4 (and S5 for L4's binding). That discharges `hzk` of
  `pearlCHidden…_8192`'s v2 counterpart.
- **Drop:** #1170 (redo after S1), #1049 and #1060 (superseded by #1121), and #1201 as a separate branch (it rides S2).
  #1121 is a source to port from, not a branch to restack: its verifier changes (`checkSession`, `tableUnits`) go
  with S5.
- **Parallel:**
  - S0 ∥ S1–S2.
  - S3's event-level port ∥ S1–S2.
  - S3 ∥ S5, as two Lean lanes, two `.lake`s, builds on node 1 only.
  - S4 waits for S3; S6 waits for S4 and S5.
  - The recursive path (`InnerSound` at F_σ, InnerFold `--public-inputs`) comes after S4.

## 4. Owner questions (with recommendations)

- **Q1 (Daniel): does #1179 land before T4?**
  - #1179 makes `flock-verify` refuse `--public-inputs`, which is PoUW v2's direct-path form (inner-layout note,
    steps 3–5). Main today accepts that form with no theorem, which the 10-04 ruling forbids.
  - *Recommend:* land #1179 fail-closed, and re-admit `--public-inputs` with T1 (T4). PoUW v2's direct path waits for
    T1 either way.
- **Q2 (Daniel or @lean): an interim `scopeOk` P guarantee** (#1121's HP family at J tables on v1 rows)?
  - *Recommend no:* v2 sessions are canonical, and a v1 P theorem would be a second family to retire.
- **Q3 (@lean): where the PoUW × C-Flock composition lives.**
  - The Proofs package has no layer rule (`Proofs/lean-audit.json` has only `Proofs.Pouw.Dimension.Lifting`), so
    `Proofs.Pouw` may import `Proofs.Flock`. A guarantee statement can't go in `Specs.Pouw`, though, since `Specs`
    imports only `Definitions`, `Specs` and Mathlib, and C-Flock's definitions are still in Proofs.
  - *Recommend:* state it beside `Flock.Guarantees` (`Proofs/Pouw/PearlC/FlockTile/Statement.lean`) until Flock's spec
    is extracted.
- **Q4 (Daniel): #1170.** Redo the reduction after S1 against main's current lock (including tip 82's 29 `Flock.*`
  guarantees), or drop it?
  - *Recommend:* redo, as one lock-only commit after S1.
- **Q5 (compute-accounting, through the coordinator): does the staged TileRead statement pass `canonicalOk`** (outputs
  from the unit net, every row an unsegmented v2 row)?
  - If its unit has a tail, the tails gap is on the path too. `Gaps.lean` calls that gap the biggest: verifier change
    V2, `OutputsComputedC`, and a program whose unit is the VU.
  - *Recommend:* check `ProvedScope.check` on step 3's first staged toy statement.
