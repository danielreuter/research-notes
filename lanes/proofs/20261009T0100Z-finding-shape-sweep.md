---
id: proofs/20261009T0100Z-finding-shape-sweep
campaign: proofs
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs), top's asks on Daniel's 5:11 PM PDT property shape (1791504819.201559) and 5:59 PM PDT conjecture ruling (1791507775.763779); sweep by bc-96f8c980; tables art:cb189f04, art:8d1b7e92 (with sort), art:d5a93839 (conjectures)
---

# Shape sweep: every listed guarantee against "one shape for every property" (#1581, 74e3270a4)

Tree: `origin/main` at `95292860f`, read in a detached, read-only worktree (`/tmp/wt-shape`, removed at the end). Nothing
was built and no repository file changed. Paths are from the repository root, and a citation `F:n` is file `F`, line `n`.
The table is `art:cb189f04` (the evidence store, kind `lean-shape-sweep/v1`), and `art:8d1b7e92` adds the `sort` column: one row per guarantee, tab-separated, the header first, and no other line.

I started at `30b63d200`, which was `origin/main` when the sweep began. `main` then moved 85 commits and landed #1569,
#1574 and 29 new properties, so I moved the worktree to `95292860f` and swept that. Under `Security/`:

- From `9c8323458` (the first sweep) to `30b63d200`, nothing changed.
- From `30b63d200` to `95292860f`, 60 files changed. #1574 added `Security/Proofs/Flock/Soundness/Discharge/FailClosed/`
  (`One`, `Scope`, `Mask`, `Exec`, `Composed`, `ZkHidden`, and its root `FailClosed.lean`) and edited 11 files beside it
  under `Discharge/` (`Composed/Base`, `Composed/Headline`, `Composed/Sound`, `HdecCor/Headlines`,
  `HiddenExec/HeadlineExec`, `Integrate/Headline`, `Layout/Scope`, `ZkHidden/DefsJ`, `ZkHidden/Sound`, `ZkHidden/View`,
  `ZkLink/TablesAt`). #1569 added `Security/Definitions/Core/Advice.lean`
  and `Security/Proofs/Core/Advice.lean`, changed `PrivatePartition` and dropped `AdviceBinding` from
  `Security/Models/Core/Assumptions.lean`. network-accounting added `Security/Properties/NetworkCertifier.lean`,
  `Security/Properties/CertifierNetwork.lean`, their proofs and `Security/Proofs/NetworkCertifier/Accepted.lean`.
  compute-accounting added `Security/Properties/Pouw/Commit.lean` and its proof. The rest is lakefiles, manifests and the
  two locks.
- No guarantee's signature or type hash changed in either lock. `Security/lean-audit.json` gained one guarantee
  (`flock_verify_sound`, now 276) and `Security/Properties/lean-audit.json` gained 29 (now 71), so the table has 347 rows.
  The 317 rows of the first sweep keep their statements; only the recorded hashes of modules they read changed, chiefly
  `Flock.*` for #1574.

## For top

### Counts per owner and verdict, all 347

| Owner | FIT | RESTATE | COMPLETENESS | LEMMA | FROZEN | Total |
|---|---|---|---|---|---|---|
| @compute-accounting | 23 | 20 | 0 | 89 | 74 | 206 |
| @lean | 0 | 0 | 1 | 4 | 3 | 8 |
| @memory-accounting | 0 | 0 | 0 | 0 | 12 | 12 |
| @network-accounting | 4 | 18 | 4 | 0 | 5 | 31 |
| @proofs | 0 | 0 | 0 | 75 | 15 | 90 |
| **All** | **27** | **38** | **5** | **168** | **109** | **347** |

The 317 rows that were on `main` at the first sweep:

| Owner | FIT | RESTATE | COMPLETENESS | LEMMA | FROZEN | Total |
|---|---|---|---|---|---|---|
| @compute-accounting | 15 | 12 | 0 | 89 | 73 | 189 |
| @lean | 0 | 0 | 1 | 4 | 3 | 8 |
| @memory-accounting | 0 | 0 | 0 | 0 | 12 | 12 |
| @network-accounting | 3 | 9 | 2 | 0 | 5 | 19 |
| @proofs | 0 | 0 | 0 | 75 | 14 | 89 |
| **All** | **18** | **21** | **3** | **168** | **107** | **317** |

The 30 rows new on `main` are 9 FIT, 17 RESTATE, 2 COMPLETENESS and 2 FROZEN: the 29 properties and `flock_verify_sound`.

Every FIT and RESTATE row is in the Properties package. Security's 276 are 168 LEMMA, 107 FROZEN and 1 COMPLETENESS
(`Nci.Guarantees.Inference`), so none of its guarantees is yet a property of a function.

### The first sweep's 208 passes

38 of the 208 fit: 18 as they stand and 20 after a mechanical restatement, and all 38 are in Properties. Of the other
170, 154 are lemmas that move to `Proofs/`, 14 are FROZEN (Pous's 12, whose models are in the random-oracle model with no
function, and `TileCheck4WordsCore` and `TileCheck8WordsCore`, whose function is a Definitions-level model) and 2 are
completeness theorems (`Nci.Guarantees.Inference` and `CertifierDevice.LmsCorrect`). Of the first sweep's 109 failures,
93 are FROZEN, 14 are lemmas (relations between conjectures, now fine in `Proofs/`), 1 is completeness (`IssuerSigns`) and
1 is a restatement (`IssuerVerifies`, once `ValidKey` is its subject).

### Completeness theorems in Properties today

Four whole statements are completeness theorems. None has a concrete instance in Lean.

- `IssuerSigns` (`Security/Properties/CertifierDevice.lean:217`): Move to Proofs with its honest case as written (ValidKey, q < 2^H, prepare succeeds); no concrete instance exists yet.
- `LmsCorrect` (`Security/Properties/CertifierDevice.lean:196`): Move to Proofs; no Lean instance (verity/core/devices/certifier/lean/scripts/issuer_vectors.py could supply one); it pairs with the LMS-forgery disjunct of AcceptedRowsAreProgramRows.
- `DeviceOutputAccepted` (`Security/Properties/CertifierNetwork.lean:166`): Move to Proofs with its honest case as written (HonestTiming, NoFault, Closed, SyncsDeclared, SyncsAdmitted, LeavesLeft, ValidKey and the configuration's facts); no Lean instance exists: verity/core/devices/certifier/lean/CertifierDevice/SmokeMain.lean runs the device and certifies its records by hand on the wall clock but doesn't run the network check, so it is a starting point for one.
- `HonestAccepted` (`Security/Properties/NetworkCertifier.lean:158`): Move to Proofs with its honest case as written; no Lean instance (the network difftest's accepted transcripts could supply one); it pairs with AcceptsIff's forward half.

The following RESTATE properties also have a completeness half that moves to `Proofs/`: the converse of an iff, or the
existence half of `KPrimeLeast`. I normalized each iff to its acceptance form first: the half
"acceptance implies the condition" stays, and the half "the condition implies acceptance" moves. For a refusal iff
("refuses exactly when D"), that keeps "D implies refusal" (restated as acceptance implies not D) and moves "a refusal is
D" (an honest input is never refused).

- `AcceptsExactly` (`Security/Properties/Nci.lean:153`)
- `CheckAccepts` (`Security/Properties/Nci.lean:161`)
- `CheckRefuses` (`Security/Properties/Nci.lean:157`)
- `RejectsExactly` (`Security/Properties/Nci.lean:149`)
- `AcceptMeans` (`Security/Properties/Pouw/Check.lean:59`)
- `GridRefusals` (`Security/Properties/Pouw.lean:86`)
- `KPrimeLeast` (`Security/Properties/Pouw.lean:106`)
- `KPrimeRefuses` (`Security/Properties/Pouw.lean:101`)
- `AcceptsIff` (`Security/Properties/NetworkCertifier.lean:141`)
- `AnswerAccepts` (`Security/Properties/NetworkCertifier.lean:118`)
- `UndecidedIff` (`Security/Properties/NetworkCertifier.lean:179`)
- `CoinAccepts` (`Security/Properties/Pouw/Commit.lean:83`)
- `CoinRaises` (`Security/Properties/Pouw/Commit.lean:60`)
- `DomainRefusals` (`Security/Properties/Pouw/Commit.lean:48`)
- `DrawCoinAccepts` (`Security/Properties/Pouw/Commit.lean:114`)
- `EpochSaltAccepts` (`Security/Properties/Pouw/Commit.lean:108`)
- `KeyRefusals` (`Security/Properties/Pouw/Commit.lean:88`)
- `LeafRefusals` (`Security/Properties/Pouw/Commit.lean:54`)
- `SaltRefusals` (`Security/Properties/Pouw/Commit.lean:102`)

For instances, the pattern exists in Flock's `Security/Proofs/Flock/Soundness/Discharge/*/NonVacuous*.lean` lemmas (for example
`setupZJ_of_acceptsZK`, `Security/Proofs/Flock/Soundness/Discharge/Composed/NonVacuousJ.lean:39`), which build an honest
instance of EndToEnd's hypotheses. Python vectors could seed the rest:
`verity/core/devices/certifier/lean/scripts/issuer_vectors.py` for LMS and the issuer, the
network difftest's accepted transcripts for `HonestAccepted`, and the pouw difftests for the window and the check.

### The frozen-list seed, grouped by primary reason

109 properties. Each line gives the reasons (primary first), the sentence for its frozen-list file, and the properties it
covers with file:line.


**hash** (10)

- Reasons `hash,world-unlisted,scope`. It takes the table and link finders' collision bounds (TableCRZ, LinkCRZC) as hypotheses instead of a collision disjunct tied to the run, and two premises that aren't on the list: A3 (the verifier's IO.getRandomBytes is uniform) and live-verifier custody (RecordCustodyZKJ). It also takes hscope (scopeOk), which flock_verify_sound now derives from acceptance. (3: `Security/Proofs/Flock/EndToEnd/Statement.lean`: `EndToEnd` (:60); `Security/Proofs/Flock/EndToEndHidden/Statement.lean`: `EndToEndHidden` (:58); `Security/Proofs/Flock/EndToEndRegistered/Statement.lean`: `EndToEndRegistered` (:58))
- Reasons `hash,world-unlisted,scope`. It takes the table and link finders' collision bounds (TableCRZ, LinkCRZC) as hypotheses instead of a collision disjunct tied to the run, and live-verifier custody (RecordCustodyZKJ), a premise that isn't on the list; it also takes hscope (scopeOk), which flock_verify_sound now derives from acceptance. (3: `Security/Proofs/Flock/EndToEndDrawn/Statement.lean`: `EndToEndDrawn` (:44); `Security/Proofs/Flock/EndToEndHidden/Statement.lean`: `EndToEndHiddenDrawn` (:123); `Security/Proofs/Flock/EndToEndRegistered/Statement.lean`: `EndToEndRegisteredDrawn` (:131))
- Reasons `hash,obligation,world-unlisted,scope`. It takes the fork finders' collision resistance (_hCR) as a hypothesis instead of the fork form and InnerSound as an open obligation; beside VBridge, the one listed premise it takes, it takes A3 (_hA3), the outer sessions' custody (ZkOuter's field hRec) and their scope (ZkOuter's parameter hscope). (1: `Security/Proofs/Flock/Recursive/Statements.lean`: `RecursiveSound` (:54))
- Reasons `hash,obligation,no-function`. It takes HashDerivedKeyHm96 as a hypothesis and the outer proof's zero knowledge as an open obligation, and as a simulation statement it has no acceptance of a function to take. (1: `Security/Proofs/Flock/Recursive/Statements.lean`: `RecursiveZK` (:113))
- Reasons `hash,scope`. It takes HashDerivedKey (_hKey) as a hypothesis, and avoidsMask (_hdm) as a scope condition that the verifier doesn't refuse; Security/Proofs/Flock/Soundness/Discharge/FailClosed/Mask.lean:9-11 derives it from the setup, so restating on that removes the scope reason. (1: `Security/Proofs/Flock/ZeroKnowledgeHidden/Statement.lean`: `ZeroKnowledgeHidden` (:49))
- Reasons `hash,world-unlisted`. Scope now follows from acceptance, but it still takes TableCRZ as a hypothesis and bounds the link by if LinkCRZC then the bound else top, and ViewZ takes HashDerivedKeyHm96; it also takes A3 (UniformRandomBytes), DrawOkZK, RecordsLiveZK and their H and J forms, premises that aren't on the list. (1: `Security/Proofs/Flock/Soundness/Discharge/FailClosed/One.lean`: `flock_verify_sound` (:631))

**conjecture** (72)

- Reasons `conjecture,no-function`. It is a consequence of the named open conjecture ActivationsIncompressible, stated over NCI's model rather than NciCheck.evaluate, and the one ruling on conjectures decides it. (1: `Security/Models/Nci/Guarantees.lean`: `IuReads` (:89))
- Reasons `conjecture,no-function`. It is a consequence of the named open conjectures ActivationsIncompressible and PartialSumsIncompressible, stated over NCI's model rather than NciCheck.evaluate, and the one ruling on conjectures decides it. (2: `Security/Models/Nci/Guarantees.lean`: `Training` (:50), `UpdatedMatMul` (:39))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTNCP, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (1: `Security/Models/Pouw/Assumptions/NCP/GamePinned.lean`: `GammaFromTTNCP` (:45))
- Reasons `conjecture,obligation,vacuous,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevRev1, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. It also takes TileProofSoundAll, an open obligation that holds trivially until TileRead lands. (1: `Security/Proofs/Pouw/PearlC/HiddenGamma.lean`: `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` (:118))
- Reasons `conjecture,obligation,vacuous,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevRev1, given the model conditions RowSeedNoise and SplitClosed, which are definitions, not assumptions (Security/Models/Pouw/Assumptions/PearlC/TTOutRowSeed.lean), stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. It also takes TileProofSoundAll, an open obligation that holds trivially until TileRead lands. (1: `Security/Proofs/Pouw/PearlC/RowSeedKGamma.lean`: `pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCap1000_8192` (:130))
- Reasons `conjecture,obligation,vacuous,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevRev1, given the model conditions CodeSeedNoise, RelabelClosed, RowSeedNoise and SplitClosed, which are definitions, not assumptions (Security/Models/Pouw/Assumptions/PearlC/TTOutRowSeed.lean), stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. It also takes TileProofSoundAll, an open obligation that holds trivially until TileRead lands. (1: `Security/Proofs/Pouw/PearlC/RowSeedKGamma.lean`: `pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCodeCap1000_8192` (:148))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevRev1, given the model conditions RowSeedNoise and SplitClosed, which are definitions, not assumptions (Security/Models/Pouw/Assumptions/PearlC/TTOutRowSeed.lean), stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Proofs/Pouw/PearlC/RowSeedGamma.lean`: `pearlCSampledSm120v1RowSeed_8192` (:1259), `pearlCSampledSm120v2RowSeedCap1000_8192` (:1294))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TT, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/Game.lean`: `EndToEnd` (:50), `GammaFromTT` (:70))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTNCP_U, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/NCP.lean`: `GammaFromTTNCP_U_C2` (:198), `GammaFromTTNCP_U_v1` (:188))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutFp4Sm120, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaFp4Sm120_16384` (:102), `GammaFp4Sm120_8192` (:113))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCH100Rev1, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaH100Rev1_16384` (:330), `GammaH100Rev1_8192` (:341))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDevRev1, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (17: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaSm120v1Cast16Rev1_8192` (:352), `GammaSm120v1Cast32p06Rev1_8192` (:374), `GammaSm120v1Cast8p72Rev1Cap1000_16384` (:397), `GammaSm120v1Cast8p72Rev1Cap1000_8192` (:410), `GammaSm120v1Cast8p72Rev1_16384` (:422), `GammaSm120v1Cast8p72Rev1_8192` (:433), `GammaSm120v1LoopCast16Rev1_8192` (:444), `GammaSm120v1LoopCast32p06Rev1_8192` (:467), `GammaSm120v1LoopCast8Rev1_8192` (:480), `GammaSm120v1LoopCast8p72Rev1Cap1000_16384` (:125), `GammaSm120v1LoopCast8p72Rev1Cap1000_16384OfCap400` (:504), `GammaSm120v1LoopCast8p72Rev1Cap1000_8192` (:56), `GammaSm120v1LoopCast8p72Rev1Cap1000_8192OfCap400` (:517), `GammaSm120v1LoopCast8p72Rev1_16384` (:529), `GammaSm120v1LoopCast8p72Rev1_8192` (:540), `GammaSm120v1Rev1_16384` (:551), `GammaSm120v1Rev1_8192` (:562))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDevRev1ChainOnly, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (4: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaSm120v1Cast32p06ChainOnlyRev1_8192` (:363), `GammaSm120v1Cast8p72ChainOnlyRev1_8192` (:385), `GammaSm120v1LoopCast32p06ChainOnlyRev1_8192` (:456), `GammaSm120v1LoopCast8p72ChainOnlyRev1_8192` (:492))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDev, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (8: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaSm120v2Cap1000_16384` (:573), `GammaSm120v2Cap1000_8192` (:584), `GammaSm120v2Cast16Cap1000_8192` (:595), `GammaSm120v2Cast8p72Cap1000_8192` (:606), `GammaSm120v2LoopCast16Cap1000_8192` (:651), `GammaSm120v2LoopCast8Cap1000_8192` (:664), `GammaSm120v2LoopCast8p72Cap1000_8192` (:675), `GammaUnpromotedCap1000_8192` (:720))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDevChainOnly, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaSm120v2Cast8p72ChainOnlyCap1000_8192` (:618), `GammaSm120v2LoopCast8p72ChainOnlyCap1000_8192` (:687))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDevChainCap, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (3: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaSm120v2ChainCap1000_16384` (:629), `GammaSm120v2ChainCap1000_8192` (:640), `GammaUnpromotedChainCap1000_8192` (:731))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutPearlCDevUOnly, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `GammaUOnlySm120Rev1_8192` (:698), `GammaUOnlyUnpromotedCap1000_8192` (:709))
- Reasons `conjecture,obligation,hash,vacuous`. It takes TTOutTilePearlCDevRev1, the open obligation TileReadSound and the binding TileReadBinds, with collision resistance inside the prover class (Security/Proofs/Pouw/PearlC/FlockTile/Statement.lean:32-33, :47-51), and it holds trivially for an empty class until TileRead lands. (1: `Security/Proofs/Pouw/PearlC/FlockTile/Statement.lean`: `HiddenFlockSm120v1LoopCast8p72Rev1Cap1000_8192` (:42))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTileFp4Sm120, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `SampledFp4Sm120_16384` (:137), `SampledFp4Sm120_8192` (:148))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCH100Rev1, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `SampledH100Rev1_16384` (:742), `SampledH100Rev1_8192` (:753))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevRev1, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (10: `Security/Models/Pouw/Guarantees/PearlC.lean`: `SampledSm120v1Cast8p72Rev1Cap1000_16384` (:765), `SampledSm120v1Cast8p72Rev1Cap1000_8192` (:779), `SampledSm120v1Cast8p72Rev1_16384` (:792), `SampledSm120v1Cast8p72Rev1_8192` (:805), `SampledSm120v1LoopCast8p72Rev1Cap1000_16384` (:160), `SampledSm120v1LoopCast8p72Rev1Cap1000_8192` (:174), `SampledSm120v1LoopCast8p72Rev1_16384` (:818), `SampledSm120v1LoopCast8p72Rev1_8192` (:831), `SampledSm120v1Rev1_16384` (:843), `SampledSm120v1Rev1_8192` (:855))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDev, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `SampledSm120v2Cap1000_16384` (:867), `SampledSm120v2Cap1000_8192` (:879))
- Reasons `conjecture,no-function,hash`. It is a consequence of the named open conjecture TTOutTilePearlCDevChainCap, stated over the PoUW game, whose oracle H is drawn uniformly and whose commitments are ideal (Security/Definitions/Pouw/Game/Defs.lean:11, :28), not over a Lean function. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `SampledSm120v2ChainCap1000_16384` (:891), `SampledSm120v2ChainCap1000_8192` (:903))

**falsified** (2)

- Reasons `falsified,vacuous,conjecture,no-function,hash`. Its premise TTOutPearlC is falsified (the first promotion into +0 is priced, Security/Models/Pouw/Assumptions/PearlC/TTOut.lean:34-36), so it is vacuous for the real system; it is also a game statement with ideal hashes. (2: `Security/Models/Pouw/Guarantees/PearlC.lean`: `Gamma16384` (:307), `Gamma8192` (:319))

**obligation** (5)

- Reasons `obligation,no-function`. It takes KnowledgeSound and LinkSound (Security/Proofs/Flock/Soundness/Audit/OneStage.lean:85, :94), open obligations of the backend, as hypotheses, and it is about the abstract one-stage audit rather than a Lean function. (5: `Security/Proofs/Flock/Soundness/Audit/Influence.lean`: `audit_exfiltration` (:332); `Security/Proofs/Flock/Soundness/Audit/OneStage.lean`: `audit_profile` (:163); `Security/Proofs/Flock/Soundness/Audit/Window.lean`: `audit_window_split_of_record` (:364); `Security/Proofs/Flock/Soundness/Audit/Work.lean`: `audit_work_floor` (:537), `audit_work_whole_stratum` (:519))

**scope** (2)

- Reasons `scope,world-unlisted`. It takes honest timing (each frame handed at the bucket the Program gives it, Security/Properties/CertifierDevice.lean:166) as a hypothesis; it leaves the list once the device refuses to mark a record complete after a late frame, which network-accounting is doing. (1: `Security/Properties/CertifierDevice.lean`: `CompleteRows` (:160))
- Reasons `scope`. It takes |tag| < 2^32 and every |part| < 2^64 as hypotheses, which the Lean frameBytes doesn't refuse (it wraps the length; Python's frame refuses), so it leaves the list once the port refuses them and the bounds come from acceptance. (1: `Security/Properties/Pouw/Commit.lean`: `FrameInjective` (:156))

**no-function** (18)

- Reasons `no-function,world-unlisted`. It is stated over an arbitrary certifier Interaction and takes JitterBounded and W2 (Regenerates) or W4 (Packed, Allocated) about it, not the network check's code; AcceptedRunsAreProgramRuns now carries an accepted run to NetTiming.Accepted, which is the restatement path. (4: `Security/Models/NetworkCertifier/Guarantees.lean`: `EncardDecodableLeConstantRate` (:266), `EncardDecodableLeConstantRatePerWindow` (:293), `EncardIngressObsDecodableLe` (:308), `EncardIngressObsDecodableLePerWindow` (:367))
- Reasons `no-function,hash`. It is about the abstract m1p and chain-band models in the random-oracle model (Security/Definitions/Pous/Game/Oracle.lean:82), not the PoUS setup check's code, and Security/Models/Pous/Guarantees/P2.lean:15-16 says none states that the deployed P2 is secure. (12: `Security/Models/Pous/Guarantees.lean`: `BandMultiMeetsFamily` (:634), `BandMultiMeetsFamilyD0` (:694), `BandMultiMeetsFamilyD1` (:680), `BandMultiMeetsFamilyD2` (:668), `ChainDenseMeets64` (:648); `Security/Models/Pous/Guarantees/P2.lean`: `P2ErrorSplitB19Uncond` (:137), `P2MeetsM1pB19Uncond` (:40), `P2MeetsM1pFamilyUncond` (:50), `P2MeetsM1pW8192Uncond` (:61), `P2SlackB19Uncond` (:84), `P2SlackFamilyFreeBlocks` (:162), `P2SlackFamilyUncond` (:111))
- Reasons `no-function`. Its function is tileCheck8 or tileCheck4, a model in Security/Definitions/Pouw/PearlC rather than executable code, so it fits only if top rules that a Definitions-level check is a named function; it would then be restated with ComputesWords opened and the step's w >= 24 as a definition. (2: `Security/Models/Pouw/Guarantees/PearlCTileCheck.lean`: `TileCheck4WordsCore` (:33), `TileCheck8WordsCore` (:22))

### Questions for top

1. **Must a naming condition sit behind a named conclusion?** In Lean, `∀ x, A → B` and `∀ x, (A → B)` are one term, so a
   check that reads binders can't tell a condition that picks out what the conclusion talks about from a premise. The
   check can tell them apart only if the conclusion is a named definition. I recommend requiring it. It decides 10
   restatements: `Reports`, `Witnesses`, `ContentIndependent`, `FailClosed`, `BucketCost`, `BucketCost3`,
   `LevelsCount`, `DrawMisses`, `AcceptedRunsAreProgramRuns` and `EncardAcceptedObservationsLe`.
2. **What is the shape when acceptance is an event inside `Pr[…]` or a counted set?** That covers every Flock headline,
   `flock_verify_sound` (`FlockVerifyAccepts`, `Security/Proofs/Flock/Soundness/Discharge/FailClosed/One.lean:41`), every
   PoUW game statement and `EncardAcceptedObservationsLe`. My reading: acceptance is the event, and the bound is the
   conclusion. I gave those rows their verdicts on their other reasons: the Flock and PoUW rows are FROZEN for those,
   and `EncardAcceptedObservationsLe` is RESTATE.
3. **How does a zero-knowledge statement fit?** It has no acceptance: `RecursiveZK`, `ZeroKnowledgeHidden`, and the `ViewZ`
   and `ViewZHJ` conjuncts that `flock_verify_sound` bundles with soundness. Is it an always-returns property of the
   prover's output law, or `no-function`? I recommend the first, with ZK split out of `flock_verify_sound` into a
   property of its own.
4. **Which half of a refusal iff is completeness?** Read literally, "→ stays, ← is completeness" would keep "a refusal is
   Malformed" in `RejectsExactly` and move "Malformed is refused", the opposite of what I did. I normalized to the
   acceptance form first, as described under the completeness theorems. This decides three: `RejectsExactly`,
   `CheckRefuses` and `CoinRaises`.
5. **Is a Bool decider's equality always-returns?** One example is `OnGridMeans` (`onGrid = true ↔ IsPoint`). I read it as
   always-returns (FIT). The other reading is an acceptance iff to split. The same question covers `isOk = decide P` for
   an `Except` function: I split those (`GridRefusals`, `KPrimeRefuses`, `DomainRefusals`, `LeafRefusals`,
   `KeyRefusals`, `SaltRefusals`).
6. **Are fixed-input evaluations properties or vectors?** These are `LevelsServed`, `Bucket8192`, `KPrimeServed`,
   `KPrimeExactAtEquality`, `PublicItems`, `DepthServed` and `CoinNumbers`. They are FIT by the binder rule, since they
   take no binders. I'd keep them as properties.
7. **Is "no error field" an acceptance equation?** This is `CheckAccepts`' acceptance:
   `∀ k, (check j).getObjVal? "error" ≠ .ok (.str k)`.
8. **Is a binding property's pair of acceptances one acceptance?** `CoinBinding` takes two acceptances of `coinReason` and
   concludes the same coin, or a collision among the strings the two checks hash. I marked it FIT.
9. **Is `Honest p dev eg` the listed premise `trusted-nebius-host`?** It is stated over an abstract `Device` record
   (`Security/Properties/NetworkCertifier.lean:219`), in `AcceptedRowsAreProgramRows` and `AcceptedRunsAreProgramRuns`.
   The alternative is for the property to quantify over `CertifierDevice.step`'s outputs, so that `Honest` becomes a
   theorem under the premise. I marked both RESTATE on the first reading.
10. **Do the verifier's randomness and its custody go on the premise list?** These are A3 (`UniformRandomBytes`) and
    live-verifier custody: `RecordCustodyZKJ` in the six `EndToEnd*`, and `DrawOkZK`, `RecordsLiveZK` and their H and J
    forms in `flock_verify_sound` (`Security/Proofs/Flock/Soundness/Discharge/FailClosed/One.lean:294`, `:296`, `:339`,
    `:341`). After the hash reason, they are the last blockers of those seven; `RecursiveSound` takes A3 and its outer
    sessions' custody too, beside the open obligation `InnerSound`. They read as physical premises, about the host's
    `getrandom` and the verifier's process.
11. **Is a Definitions-level check a named function?** This covers `tileCheck8` and `tileCheck4` at `coreOps`, in
    `TileCheck8WordsCore` and `TileCheck4WordsCore` (`Security/Models/Pouw/Guarantees/PearlCTileCheck.lean:22`, `:33`). If
    so, both become RESTATE.
12. **Are `FlockVBridge.unit_check` and `unit_recOpen` properties of `Flock.RecOpen.check`, or VBridge lemmas?** Both take
    `Flock.RecOpen.check c = .ok ()`. And is their `hms` (`ms.node = Sha512.hash`) a naming definition? I marked both
    LEMMA.
13. **Does moving the 168 lemmas out of the lock count as a claims change?** It changes what `audit.py --update` records
    and DMs Daniel about. I'd treat it as a pure move with a `--moved` file. Lemma here includes the six
    `GammaFp4*Lut256` γ values, which take no hypothesis.

The one ruling on conjectures decides 72 rows: 69 PoUW γ statements (each takes a TT or TT_OUT premise) and NCI's
`Training`, `UpdatedMatMul` and `IuReads`. Two more, `Gamma16384` and `Gamma8192`, are frozen as `falsified` first: their
premise `TTOutPearlC` is falsified.

### Rules I applied without asking

- I counted acceptance as one equation of a named Lean function's result, or `Protocol.Accepts`
  (`∃ pub prof, check p c e = .accept pub prof`, `verity/core/protocols/interface/CoreProtocol/Protocol.lean:65`).
- A condition that a `Nat` function doesn't refuse, but whose `Int` `?` port does, is a restatement against the port: the
  scope then comes from acceptance through `GridRefusals` or `KPrimeRefuses`.
- I marked lemmas that take an acceptance but conclude a Proofs-internal structure (the `refSetup` and
  `setupZJ_of_acceptsZK` lemmas, whose conclusion is a `DrawSetupZJ`) LEMMA. They are steps of a discharge, not claims.
- I marked `hash` on the PoUW game and Pous statements because their models draw the hash as a random oracle
  (`Security/Definitions/Pouw/Game/Defs.lean:11`, `:28`; `Security/Definitions/Pous/Game/Oracle.lean:82`). That assumes
  the hash.
- The 87 evaluator equalities that top mentions (`Evaluate.X.f = Verity.X.f`) are in neither lock at `95292860f`. The
  `Evaluate` package's docstrings say "Must equal …", but no such theorem is listed, so they have no row. Read as
  always-returns, they would be FIT.
- Core's statements (`Verity.Guarantees.*`: the TC gadgets, `PrivateOutBitsLe`, `RegisteredMeets`) and the properties in
  `Security/Properties/Pous.lean` are in no lock, so they have no row either.

## Device models and math (Daniel, 5:59 PM PDT)

Daniel's ruling, recorded by #1583 in `.agents/skills/lean-proofs/SKILL.md`, sorts every named conjecture into device
models and math before anything else is listed. This section is the starting sort that ci's frozen list and
compute-accounting's restatements work from. I read `origin/main` at `4ed16dcd5` in a fresh read-only worktree (removed at
the end). Its `Security/` tree is identical to `95292860f`, the commit the rest of this report swept, so the 347 rows are
the same. Two tables are in the evidence store:

- `art:8d1b7e92` (`shape-sweep-v2.tsv`) is `art:cb189f04` with a ninth column, `sort`. A cell lists the Props the row takes as
  hypotheses, as `Name=sort` pairs separated by `;`, or `-` when the row rests on none. Only the `action` of `Gamma16384`,
  `Gamma8192` and `TTOutPearlCDevRev1OfGranted` changed; every other field is as before.
- `art:d5a93839` (`conjectures.tsv`) has one row per Prop: where it is, who owns it, its sort, its device part and math part, the test it
  needs, the evidence that exists today, its status as its docstring states it, and how many table rows rest on it.

The list is every Prop the first sweep classed M-conj, M-emp or falsified, plus `TTH1T` and `RowDrawn`: 49 in all. I left
out three kinds of statement. The world premises the first sweep already classed P (`GemmHopperStep`, `GemmAmpereStep`,
`TrustedNebiusHost`, `JitterBounded`, `HonestClock`, `UniformSecret`) are device or world statements already. The open
obligations (`TileProofSound`, `TileReadSound`, `KnowledgeSound`, `LinkSound`, `AnchorsSound`) are to be discharged from
C-Flock, not conjectured. The hash premises the first sweep classed H already fall under the rule that collision
resistance is stated as a reduction. `RowDrawn` is the one I kept, because it sits among the RowSeed conditions.

### How I sorted

A Prop is **mixed** when its statement reads a device record, or quantifies over a cost model or machine whose meaning is a
device. That covers the whole TT and TT_OUT family, `TTH1T` and `A2`. Its device part is the record (the accumulator step,
`G`, the maps for the ticket, `U`, the flags and the forming) together with what the cost model must be: W1 at the device's
measured prices, with no cheaper unpriced path, and the honest kernel within `W_ref`. Its math part is the game
inequality at a fixed record, cost model and noise semantics.

A Prop is **finite** when it is about finite objects and names no device: the three H1T word conditions and NCI's two
incompressibility Props. **Math** covers `FragLanes`, `FragDraw`, `B1Prime`, the RowSeed conditions and `RowDrawn`.
**Empirical** covers `HonestTileCapRate`, a confidence limit on the honest kernel's served tiles.

No Prop is **device** alone. Daniel's example, `TTOutPearlC`, comes out mixed under this rule (question 1 asks whether
that is right). The device models proper are definitions, not Props: `devH100`, `devSm120v1`, `devSm120v2` and
`devFp4Sm120` in `Security/Definitions/Pouw/PearlC/`, with their prices. The captures check them, and nothing in Lean names
the claim that they match the hardware. Each split therefore creates a new device Prop, scoped to one device setting.

A row rests on a Prop when it takes it as a hypothesis. A lemma that concludes a conjecture does not rest on it, so
`ttOutPearlCWitness`, `A2WordsIff`, `TTNCPUIff` and `TTNCPUWitness` get `-`. The one exception is `GammaFromTT`, whose
premise sits inside its conclusion's definition; I counted it as resting on `TT`.

### Counts

| Sort | Props | Props with a row | Rows resting on one |
|---|---|---|---|
| device | 0 | 0 | 0 |
| mixed | 33 | 18 | 81 |
| math | 10 | 8 | 9 |
| finite | 5 | 4 | 5 |
| empirical | 1 | 0 | 0 |
| all | 49 | 30 | 87 |

A row can rest on Props of more than one sort, so the last column doesn't add up to 87. The 87 rows are 74 FROZEN and 13
LEMMA. No FIT, RESTATE or COMPLETENESS row rests on any Prop, so ci's conditional list draws only on rows that this sweep
already froze or demoted. Of the 87, 81 rest on a mixed Prop. The other six rest only on math or finite ones: NCI's
`Training`, `UpdatedMatMul` and `IuReads`, the two H1T relation lemmas `h1tDistinctLive` and `h1tRunningOfDistinct`, and
`TTOutRowSeedSkipClass`.

The ruling changes three actions in the table:

- `Gamma16384` and `Gamma8192` come off the guarantee list. Their premise `TTOutPearlC` is falsified: the first promotion
  into +0 is priced, and every program skips it (`Security/Models/Pouw/Assumptions/PearlC/TTOut.lean:34-36`).
- `TTOutPearlCDevRev1OfGranted` is to be stated for G = 0 only. Its premise `TTOutPearlCDev` is falsified at G = 4, which
  is the H100's setting and sm_120 v1's (`Security/Models/Pouw/Guarantees/PearlC.lean:934-936`). Question 4 is about what
  remains.

### The mixed Props and their splits

The 33 mixed Props fall into nine families. Within a family the split is the same, and only the device setting differs.

1. **TT_OUT at the H100**: `TTOutPearlC` and `TTOutTilePearlC` (falsified, rated D), and `TTOutPearlCH100Rev1` and
   `TTOutTilePearlCH100Rev1` (rev1, rated B). The device part is `devH100`: Hopper's step promoted every 4 atoms, with
   G = 4, W1 at `Prices.h100`, and a cost model that charges a wgmma its whole shape and fits the honest H100 kernel within
   `W_ref`. The Hopper captures check the step. The prices come from Rounds 10 and 11, and nobody has rated W1's
   completeness on the H100. The math part is the inequality that no cost-bounded program earns more than T/(1 − 1/400)
   of the credit, except with probability ε.
2. **TT_OUT at sm_120 v1** (`devSm120v1`, G = 4): `TTOutPearlCDevRev1`, `TTOutTilePearlCDevRev1`,
   `TTOutPearlCDevRev1ChainOnly`, `TTOutTilePearlCDevRev1ChainOnly`, `TTOutPearlCDevUOnly` and `TTOutTilePearlCDevUOnly`.
   The device part is the E4M3 m16n8k32 step ⟨[32], 26, −133⟩ at G = 4, the prices `Prices.sm120` or `Prices.sm120Loop`,
   and sm_120's W1 accounting: a tensor-core instruction is charged its whole fragment, and no cheaper path goes unpriced.
   The math part is the same inequality at rev1's credit, with the first promotion into +0 removed. Two of these Props are
   also used at other settings: `TTOutTilePearlCDevRev1` once at sm_120 v2, and the U-only form once at G = 0.
3. **TT_OUT at sm_120 v2** (`devSm120v2`, G = 0): `TTOutPearlCDev`, `TTOutTilePearlCDev`, `TTOutPearlCDevChainOnly`,
   `TTOutTilePearlCDevChainOnly`, `TTOutPearlCDevChainCap` and `TTOutTilePearlCDevChainCap`. The device part is family 2's
   with G = 0. The math part is the inequality at the debited credit, or at the chain credit within the cap. At G = 0,
   rev1's credit equals this one. Four rows take one of these at a record of any G: `CapAnti`, `ChainCapOfCap` and
   `OfGranted` take `TTOutPearlCDev`, and `TTOutTilePearlCDevChainCapOfCap` takes the tile form.
4. **TT_OUT for NVFP4 at sm_120**: `TTOutFp4Sm120` and `TTOutTileFp4Sm120`, granted at C on #556's domain. The device part
   is `devFp4Sm120`: UE4M3 scales per 16 elements, k = 64, 27 fraction bits, a 36-bit window, the floor −174, and W1 at
   `Fp4Prices.sm120`. Inside it sits `PinnedScales`, the claim that the reference's statistics meet the pinned scales.
   That claim is math, argued and not proved, so this split leaves a second math piece. The math part is the inequality
   at the FP4 credit.
5. **Generic TT_OUT forms**: `TTOut`, `TTOutTile`, `TTOutU`, `TTOutTileU`, `TTOutFp4`, `TTOutTileFp4`,
   `TTOutFp4ChainOnly` and `TTOutTileFp4ChainOnly`. They fix no device. Each instance is its own assumption, and its split
   is that instance's. No row takes any of them.
6. **RowSeed targets**: `TTOutRowSeed` and `TTOutTileRowSeed` are proved from rev1 and the RowSeed conditions, so they
   take rev1's split on the split workload.
7. **TT, TTNCP and TTNCP_U** (`M_4090`). The device part is the claim that W1 at the RTX 4090's prices bounds what its
   programs cost (the problem statement §3.1; `M4090` is draft semantics in `Dimension/Embed.lean`). NCP's checked values
   are exact integer arithmetic, so no device step is modelled. The math part is the bound
   Pr[credited work > T/(1 − γ₀)] ≤ ε. TTNCP credits 3·m·k·n per unit and needs γ₀ ≥ d/(3k); TTNCP_U reads route U's int32
   accumulator at the bias β = 128. All five rows that rest on these take the cost model generically.
8. **TTH1T**. The device part is the claim that `MH100w`, at any price table meeting H32, is the H100's cost. The measured
   table meets H32, but co-issued mixes cost 21.33 to 21.45 per register in time, below H32's 32, so H32 bounds additive
   W1 work, not time. The math part is the claim that a program right on many tiles costs at least (1 − γ)·32 per right
   word, on all but an η share of salts. No row takes it.
9. **A2**. The device part is the machine: the 4090's programs and their W1 costs (`M_4090`, draft). The math part is the
   claim that every program of the machine is matched on the checked words by an algebraic one at cost/(1 − γ₂). No row
   takes it; `A2WordsIff` only relates it to another form.

In Lean the cost model is abstract (`Security/Definitions/Pouw/PearlC/Game.lean:60`), and every TT_OUT row reads
`∀ CM sem, TTOut… CM … → …`. The device meaning of the cost model lives only in docstrings
(`Security/Models/Pouw/Assumptions/PearlC/TTOutRev1.lean:35-42`). So the math part isn't closed math until a concrete W1
cost model and the noise semantics are Lean definitions, and until then the device part has no Lean statement to name
(question 2).

### Which conjectures have a running test

Running on `main` today:

- **The step maps against captures.** `Security/Proofs/Pouw/PearlC/Sm120Checks.lean` checks the E4M3 step against
  `fp8-sm120-mma-k32.json` and `-k1536.json`. `Fp4Checks.lean` checks the NVFP4 step against `nvfp4-sm120-mma-k64.json` and
  `-k1536.json`. `verity/ml/circuits/ops/tests/test_total_fp8.py` replays Hopper's E4M3 wgmma. These cover the device
  part's step, not its prices or W1's completeness.
- **The honest kernel's tensor-core instructions.** `benchmarks/pouw/pearl_c_sm120/sass_gate.py` refuses a build whose
  instructions aren't the intended ones for FP8, and `benchmarks/pouw/pearl_c4/sass.py` does the same for FP4. With the
  prices, this is half of "the honest kernel fits `W_ref`".
- **The verifier's accounting against the Lean.** `benchmarks/pouw/tests/test_price_twins_accounting.py` and the debit
  reference's tests (`verity/core/protocols/pouw/tests/test_pouw_pearl_c_debit.py`, `test_pouw_pearl_c4.py`) pin the
  credit and debit cap to the rule the guarantee is proved for. They test no premise, but they keep a falsified rule from
  coming back.
- **`HonestTileCapRate`.** `benchmarks/pouw/pearl_c_vllm/served_debit.py --per-input` is the measurement, and it runs. Its
  table has not landed, so no completeness number is cited yet.
- **`RowLocal`.** `devAt_rowLocal` proves it for every `devAt` record, so it needs no test.
- **The H1T words on vectors.** `Security/Proofs/Pouw/Fp8Atom/H1TChecks.lean` checks the words on vectors. That catches a
  wrong definition, not a collision, so it isn't a falsification test.

These still need one:

- **The math part of every TT_OUT form.** The docstrings cite the census attack search
  `benchmarks/pouw/pearlc_census.py` as the standing test (`TTOut.lean:83`), but it is not on `main`; it exists only on
  `origin/cursor/fp8-cap600-cb26` at `43dc9fe2a`. The falsifiers that rev1 and the U-only form cite,
  `pearlc_promotion_fusion.py` and `pearlc_u_only_skips.py`, are in neither the repository nor the notes. The ratings (B
  for the sm_120 forms, C for NVFP4) rest on runs whose code I can't read on `main`.
- **W1's completeness on each device**, that is, no cheaper unpriced path. On sm_120 it is rated B for the whole-fragment
  rule, from timed runs, and C for the whole row. The rating says completeness isn't searched (the branching rule, L2
  reductions, texture filtering, hand-written SASS) and names the falsifier: an unpriced path that gives exact words
  cheaper (`campaigns/pouw/red-team/ratings.md:51` in the notes). I found nothing for the H100.
- **The prices.** They come from recorded runs (`r20260930-063213-c94a`, `r20260930-061717-3e84`,
  `r20260930-081301-747b`, cited in `DevicePrices.lean`). I found no test on `main` that re-measures them.
- **TT, TTNCP, TTNCP_U, A2 and TTH1T.** No attack search exists on `main`. `benchmarks/pouw/gamma.py` prices the honest
  reference under W1 and derives the floor that unchecked work puts on γ. That is a necessary condition, not a search.
- **`FragDraw`.** A 2^-128 tail needs a proof or a computed bound, since sampling refutes only gross violations. The CPU
  runs behind its ratings (C at Λ = 12, B at Λ = 100) are not on `main`.
- **The three H1T conditions.** Deciding them by computation is out of reach: per input the words read 41 salt bits per
  slice (29 signs and three 4-bit tag lanes), so 2^(41·T) salts for up to 1,130 slices. They need the proof the Lean
  plans (M3 to M5), with a sampled search for a colliding or constant word as the running falsification test. The red
  team's simulation script (`h1_tagged.py`) is cited but is in neither the repository nor the notes.
- **NCI's two Props.** No test exists. The structural check in the next subsection is a computation over a declaration's
  wiring.
- **`B1Prime`.** This needs an attack search on a scheme whose blocks share a primitive; I found none.
- **The RowSeed conditions on the noise semantics and the cost model** (`RowSeedNoise`, `CodeSeedNoise`, `SplitClosed`,
  `RelabelClosed`, `FragmentPriced`). Each becomes a lemma once the noise derivation and a concrete W1 cost model are Lean
  definitions, and no test applies before then.
- **`RowDrawn`.** It needs restating, not testing. Its injective key idealizes the row leaf's collision resistance, so for a
  fixed leaf hash whose digest is shorter than a row it is false by counting. That is the same trap the ruling names, and
  the fix is a reduction to the leaf's collision resistance.
- **`FragLanes`.** This restricts the adversary rather than claiming anything about the world, so a claim resting on it
  covers only adversaries that meet it. `FragShareGain` already exhibits programs that break it, and no row rests on it.

### NCI on its face

Both NCI Props are about one fixed declaration and chain `(D, c)`, and neither has a distribution over inputs or weights
(`Security/Models/Nci/Assumptions.lean:44`, `:62`). They read only wiring and widths. The hard-coding trap applies on its
face. `Circuit` lets a computed gate read nothing (`Security/Definitions/Core/Circuit.lean:32-45`: only input gates are
required to read nothing), and `Chain` doesn't say where a product's weight operand comes from
(`Security/Definitions/Nci.lean:67-87`). So take a declaration that holds a weight entry in a constant gate, or recomputes
it from a wire narrower than b_w, and let R be one product of that entry together with the gates that produce the
weight. R holds a product of one weight entry and one input entry, so the Prop charges it b_w + b_a. But R reads only
the input entry and the narrow wire, fewer bits than that, so `ActivationsIncompressible` fails at that declaration. The docstring names cases of the same kind itself: a committed checkpoint, and layers before the first
multiplication committed in θ (`Assumptions.lean:13-24`). Those exclusions are written in the docstring, not in the Prop.

`UpdatedMatMul` and `IuReads` take the Props at the declaration they bound, so they say nothing at such a declaration.
`Training` takes them for every compliant declaration that implements T, so one such declaration can void its premise
for T.
Restating "over random inputs" doesn't fit a Prop that reads no values (question 9).

### Questions for top on what the ruling doesn't decide

1. **Is TT_OUT a device statement or a mixed one?** Daniel names `TTOutPearlC` as a device statement. Its Lean is a game
   inequality over an abstract cost model at a device record. I sorted it mixed. If the example decides the sort, all 28
   TT_OUT forms are device, and the conjectures section holds none of them. I recommend mixed, so that the inequality,
   which is where every attack lands, gets a falsification test of its own.
2. **Where do a concrete W1 cost model and the noise semantics live?** Until both are Lean definitions, no TT_OUT math part
   is closed math, and no device part is a Lean statement. Five of the RowSeed conditions become lemmas on the same day.
3. **Do `TTOutPearlCDevCapAnti`, `TTOutPearlCDevChainCapOfCap` and `TTOutTilePearlCDevChainCapOfCap` get OfGranted's G = 0
   treatment?** They take `TTOutPearlCDev` at a record of any G, just as `OfGranted` does. All three are LEMMA rows, so they
   leave the list either way.
4. **Keep or drop `OfGranted` at G = 0?** At G = 0, `TTOutPearlCDev` is rev1 (`TTOutRev1.lean:23`), so the restricted
   lemma is an identity. I'd drop it, and let each G = 0 setting cite rev1 directly.
5. **Is "falsified" kept per device setting?** `TTOutPearlCDev` is falsified at G = 4 and open at G = 0. ci's refusal needs
   the status keyed by Prop and setting, not by Prop. I recommend keying it by both.
6. **Are the generic reductions conditional?** `GammaFromTT`, `EndToEnd`, `gammaFromTTNCP`, `GammaFromTTNCP_U_C2` and
   `GammaFromTTNCP_U_v1` take TT at any cost model, not at a device. I listed them as resting on `TT`.
7. **Do the RowSeed conditions belong on the list?** Most are definitions, or lemmas once the cost model is concrete. I
   listed them as math so that ci sees them. Every row that takes one also takes rev1, except `TTOutRowSeedSkipClass`.
8. **Do the running tests live on `main`?** The standing test the docstrings cite is on a branch, and the cited falsifiers
   are nowhere I can read. For ci to refuse on a failing test, the test has to be in the tree ci checks. I recommend
   `main`, with a test ci runs.
9. **How is NCI restated?** "Over random inputs" needs values. The choices are a distribution over the weights and inputs
   given what an IU reads, which is an information statement, or a reduction. Which one is up to @lean, who owns the Props,
   and compute-accounting, who checks the falsifier.
10. **Does a device part measure work or time?** H32 holds for additive W1 work, but co-issued mixes cost less per register
    in time. `concurrent-budgets/sm120` is rated D if priced per operation at solo peaks. Each device part's measurement
    has to say which of the two it bounds.

## Addendum: #1574 and #1569

Both landed on `main` in the train merge `f78d2e51c` ("#1573 + #1569 + #1574"). I read them from `git show` and
`git diff` against their base `2546d8362` (heads `cb51eb3b2` and `ebfe2d217`), and checked that `main` holds the same text.

**#1574, `flock_verify_sound`** (`Security/Proofs/Flock/Soundness/Discharge/FailClosed/One.lean:631`; row in the table).
Its lock change adds this one guarantee and touches no other signature. A line number without a file in this part is in
`One.lean`. Its type branches on hidden outputs and `--zk`:
`SoundExec` (:104), `SoundExecH` (:196), `SoundZ` with `ViewZ` (:283, :437), `SoundZJ` (:329), `SoundZH` (:460),
`SoundZHJ` with `ViewZHJ` (:506, :604). Acceptance is `FlockVerifyAccepts` (:41), which is `Verifies` or `VerifiesZK`.
`Security/Proofs/Flock/Soundness/Discharge/FailClosed/Scope.lean:204` and `:213` define those as `Accepts ∧ Scope` and
`AcceptsZK ∧ ScopeZ`, where `Scope` is the statement
check that the code's `ProvedScope.check` runs (`verity/core/service/flock/FlockVerify.lean:380`). So scope now comes from
acceptance, and #1574 resolves the first sweep's `scope` finding for its own statement. The six `EndToEnd*` still take
`hscope` until they are restated on it.

When `SoundZ` is opened, it still takes four hypotheses:
- `hA3 : UniformRandomBytes` (:292), `hDraw : DrawOkZK` (:294) and `hRec : RecordsLiveZK` (:296): world-unlisted.
- `hCR : TableCRZ` (:303): a hash hypothesis.

Its link bound is `linkBoundZC` (:318), which is `if LinkCRZC then … else ⊤`. That is a hash split, not a disjunct tied to
the run.

`ViewZ` takes `hKey : HashDerivedKeyHm96` (:441), which is hash. The non-ZK `SoundExec` takes `hCR` as a `LinkCRL`
hypothesis (:119). The remaining binders (`hk`, `hRw`, `hM`, `hρ`, `hr`, `ht'`) are the analysis's own parameters.

Verdict: FROZEN, `hash` then `world-unlisted`. To leave the list it needs:
- the fork-form collision disjunct in place of `TableCRZ`, `LinkCRZC` and `LinkCRL`;
- `HashDerivedKeyHm96` as a reduction;
- question 10 for A3 and custody;
- question 3 for the ZK conjuncts.

**#1569, `RegisteredMeets`** (`Security/Models/Core/Guarantees/PrivatePartition.lean:29`, proved at
`Security/Proofs/Core/PrivatePartition.lean:59`). It is in neither lock, before or after; #1569's lock diff changes only
the Mathlib hashes, so it has no row.

The change follows the hash rule. #1569 deletes the premise `AdviceBinding` (formerly
`Security/Models/Core/Assumptions.lean:43`, an injective SHA-512 root over all partitions, which the first sweep found
refutable). The new conclusion is "`r`'s partition fits the public count, or `H` has a collision between a string `r₀`
hashes and a different one `r` hashes", over the two registrations' `hashInputs`
(`Security/Definitions/Core/Advice.lean:142`). The disjunct is tied to the run, and it holds for every `H`.

On the shape, it would be FROZEN `no-function`. Its acceptance is `Registered`
(`Security/Definitions/Core/PrivatePartition.lean:74`), a statement that some registration meets `Q` and has the root,
not a function's result. The registration proof's check, which would be the function, isn't stated in Lean.

Its other two hypotheses are format facts about names:
- `F.Separated` (`Security/Definitions/Core/Advice.lean:62`), for the frame-v3 framing;
- `A.Decodes` (`Security/Definitions/Core/Advice.lean:125`), for partition v2's rows.

By the rule, a name becomes a definition. Lean has only a toy framing (`Framing.unary`, with `unary_separated` at
`Security/Proofs/Core/Advice.lean:200`) and an existence proof for rows (`Rows.exists_decodes`,
`Security/Proofs/Core/Advice.lean:219`). It has neither
the deployed framing nor the deployed codec, so restating them as definitions needs those two written in Lean first.

