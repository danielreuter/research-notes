---
id: proofs/20261009T0012Z-finding-premises-sweep
campaign: proofs
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs), Daniel's condition 4 on the fork form (top, 1791502303.401289); sweep by bc-96f8c980
---

## Addendum (proofs): what tonight's check 5415 changes

The sweep reads main `9c8323458`. Check 5415 is landing three PRs that move some of its rows:

- **#1574 (`flock_verify_sound`, the verifier fails closed).** It closes the scope rows on typed statements and
  `scopeOk` (§2.2 `ht`/`hscope`, §3 #13): the verifier refuses every form the proof doesn't cover, and the new guarantee
  quantifies `∀ hs : Scope I` with no scope hypothesis. Its conjuncts still take `TableCRL` (`hKS`) and `LinkCRL` (`hCR`)
  as antecedents, plus A3, so it joins §5's list of statements that need the fork form. The six `EndToEnd*` keep their
  `ht`/`hscope` until they're restated through it or retired.
- **#1569 (`RegisteredMeets`, run-tied).** It deletes `AdviceBinding` (§1b, §3 #8).
- **#1541 (network-accounting).** It deletes `LmsEufCma` (§1b, §3 #9) and `Sha512CollisionFreeOn`.

There is one open question, network-accounting's to top (1791502876.563219): do hypotheses that can be decided from the
configuration or trace count as premises? This report doesn't count them separately. `ValidKey`, `CompleteRows`' timing
and `SplitClosed`/`RelabelClosed` are its "uncertain" rows.


# Premises sweep: Lean properties and guarantees against "Writing a property" (Daniel, 8 Oct)

Tree: `origin/main` at `9c8323458`, a detached, read-only worktree. Nothing was built and no repository file changed.
Paths are relative to `Security/` unless they start with `verity/`. A citation `F:n` is file `F`, line `n`.
Scope:
- `lean-audit.json`: 275 guarantees, and 86 entries in its `assumptions` map.
- `Properties/lean-audit.json`: 42 guarantees; it has no assumptions map.
- Every assumptions module under `Models/*/Assumptions*` and `Proofs/Flock/Soundness/Assumptions*`.
- The binders of every listed guarantee. For the 273 guarantees whose lock signature is the constant
  `X.SecurityProofs.G : X.Guarantees.G`, I read the hypotheses from the `def G : Prop` body (a closure over statement
  modules), because the lock doesn't record them (§2.0).

Counting rule: a guarantee **passes** if it takes no hypothesis beyond P or V and the claim's own math side
conditions (parameter ranges, `0 ≤ η`). Iffs and non-vacuity witnesses pass. A named conjecture taken as an antecedent
fails. That includes relation lemmas between two conjectures (`A → B`), which are fine as `Proofs` lemmas but not as
properties.

## 0. For Daniel

1. 317 guarantees (275 Security, 42 Properties). 208 pass as is: Pous 12/12, Pouw 77/162, Flock 75/89, Nci 5/8, NetTiming 0/4, Properties 39/42.
2. Only P/V: 1 (`CompleteRows`, whose honest-timing premise is inline and unnamed), or 3 if `ValidKey` counts as signing-key state. None takes only V: `RecursiveSound` also takes H and S.
3. H, M or S: 106–108. Pouw 85 (72 "a TT/TT_OUT conjecture implies γ", 13 lemmas between conjectures), Flock 14 (9 headlines, each H and S, plus 5 lemmas taking `KnowledgeSound`/`LinkSound`), NetTiming 4 (W2/W4 assumed of an arbitrary certifier), Nci 3 (incompressibility), Properties 0–2.
4. No SHA-512 use is in fork form. Six `EndToEnd*` take `TableCRZ`/`LinkCRZC` as antecedents. `RecursiveSound` takes `_hCR` and splits on CR in its bound (`boundCR`/`slackCR`/`linkBoundZC`: `if CR then … else 1/⊤`). The hidden audit puts CR inside its prover class (a Definitions/ file).
5. Vacuous for the real system: `Gamma16384` and `Gamma8192` (their premise `TTOutPearlC` is falsified), `TTOutPearlCDevRev1OfGranted` at H100 and sm_120 v1, and `HiddenFlock…`/`TileProofSoundAll` until TileRead lands (they hold trivially for an empty class).
6. Likely vacuous at SHA-512 (uncertain): the uniform `KnowledgeSound`/`LinkSound`, since a prover with a built-in collision breaks them, and `RowDrawn`'s injective key once a row has ≥ 16 words.
7. Refutable but used by no listed guarantee: Core's `AdviceBinding` (an injective SHA-512 root over all partitions) and `LmsEufCma` (every verifying signature was signed).
8. Scope: all six `EndToEnd*` exclude typed statements and circuits failing `scopeOk`. flock-verify accepts both (`HmRow.lean:1300`), and it never runs `scopeOk`.
9. The audit can't see any of this. It records no hypothesis inside a `def G : Prop` body and no open binder, so only 2 of 275 guarantees list an assumption. A check that "refuses any other hypothesis in Properties/" has to read `def` bodies first.

## 1. Named assumptions

Classes:
- P: physical premise or outside-world function.
- V: VBridge.
- H: hash or crypto hardness taken as a hypothesis.
- M: an unproved math or model claim. Sub-kinds: `conj` (a conjecture), `obl` (an open obligation to prove),
  `emp` (empirical), `fact` (provable code or math), `def` (a definition no statement takes as a premise).
- S: a scope hypothesis.

"Users" means listed guarantees that take the assumption as a premise, found from their binders and `def` bodies. The
map's own user lists are per module (`check.py:993-1030`), so they are coarse: where they differ, the row gives the
binder count.

### 1a. The 86 entries of `lean-audit.json`'s `assumptions` map

**@proofs (C-Flock), 9 entries**

| Name | file:line | Reading | Class | Users |
|---|---|---|---|---|
| `Flock.Assumptions.VBridge` | `Proofs/Flock/Soundness/Assumptions/Recursive.lean:48` | V*'s circuits accept only an accepted inner transcript, register the firewall's commitments, decode the rounds' messages, and draw every such wire (:24-46). | V | 1: `RecursiveSound` (`Proofs/Flock/Recursive/Statements.lean:74`) |
| `FlockSoundness.Assumptions.SHA512CRStrict` | `Proofs/Flock/Soundness/Assumptions.lean:52` | For one finder with ≤ q evaluations on every outcome, Pr[collision] ≤ q²/2^513 (:37-51). | H | 8: the six `EndToEnd*` via `TableCRZ` (e.g. `Proofs/Flock/EndToEnd/Statement.lean:94-95`); `RecursiveSound` via `_hCR` (`Statements.lean:76-78`) and `ZkOuter.CR` (`Recursive/Flock.lean:138-143`); `HiddenFlockSm120v1…` via `F.Cls` (`Proofs/Pouw/PearlC/FlockTile/Statement.lean:32-33`). The map says 9 (per module). |
| `…SHA512CRExpected` | `Proofs/Flock/Soundness/Assumptions.lean:77` | For one finder of expected cost T, Pr[collision] ≤ T/2^256 (:57-76). | H | 8: the six `EndToEnd*` via `LinkCRZC` (`Soundness/Discharge/ZkLink/CompiledLink.lean:548-552`); `RecursiveSound` via `linkBoundZC`'s split (`CompiledLink.lean:557-563`); `HiddenFlock…` via `F.Cls` |
| `…UniformRandomBytes` (A3) | `Proofs/Flock/Soundness/Assumptions.lean:97` | The verifier's `IO.getRandomBytes` is a uniform source, stated over a model source because the `IO` constant is opaque (:83-96). | P (an outside-world function: the verifier's randomness; Definitions/ should list it, not a hypothesis) | 4: `EndToEnd` (:77), `EndToEndHidden` (:75), `EndToEndRegistered` (:75), `RecursiveSound` (:58). The `…Drawn` variants draw in-game. |
| `…HashDerivedKey` | `Proofs/Flock/Soundness/Assumptions.lean:189` | The pinned hm96 key is not among the 2^-64 bad keys, so hiding holds at 2^-193 (:184-188). | H (the rule: state it as a reduction) | 0 direct; 2 through `Zk.HashDerivedKeyHm96` |
| `…Hm96Hiding` | `Proofs/Flock/Soundness/Assumptions.lean:182` | Statistical hiding δ₁ of (M·y, H(sp‖y)) (:169-181). | M-def (the predicate `HashDerivedKey` instantiates) | 0 |
| `…HmRowComputes` | `Proofs/Flock/Soundness/Assumptions.lean:165` | The circuit's `sha512x3`/`hm96` slots compute the row commit string; "still to prove (phase 2i)" (:162-163). | M-fact | 0 in the headline binders. The map lists 9 per module. The binding comes from `rsZJ_computes` (`EndToEnd/Statement.lean:89`). Uncertain whether a proof path still takes it. |
| `…Zk.HashDerivedKeyHm96` | `Proofs/Flock/Soundness/Assumptions/Zk.lean:19` | `HashDerivedKey` at `ZkView.My`/`saltHash` | H | 2: `RecursiveZK` (`Statements.lean:121`), `ZeroKnowledgeHidden` (`Proofs/Flock/ZeroKnowledgeHidden/Statement.lean:59`) |
| `…Zk.RecordCustodyZKJ` (`live-verifier`) | `Proofs/Flock/Soundness/Assumptions/Zk.lean:48` | The record flock-verify reads is the live session's, and the draw file is the verifier's own draw. "No check of the record establishes either" (:25-28, :43-47). | S: it covers only live records, which the verifier can't refuse. It becomes P only if restated as "the verifier's own storage is intact" (uncertain which). | 6: every `EndToEnd*` (e.g. `EndToEnd/Statement.lean:80`). `RecursiveSound` gets the single-table form through `ZkOuter.hRec` (`Recursive/Flock.lean:68`). |

**@lean (Nci), 2 entries**

| Name | file:line | Reading | Class | Users |
|---|---|---|---|---|
| `Nci.Assumptions.ActivationsIncompressible` | `Models/Nci/Assumptions.lean:44` | No IU of ≤ Γ gates reading ≤ K novel bits rebuilds weights or activations from fewer bits than their width. Assumed only for chains above Γ work and IUs reading ≤ K; without the cap it fails for honest training (:13-24). | M-conj (compute-bounded incompressibility) | 3: `UpdatedMatMul` (`Models/Nci/Guarantees.lean:42`), `Training` (:55), `IuReads` (:90) |
| `Nci.Assumptions.PartialSumsIncompressible` | `Models/Nci/Assumptions.lean:62` | The same, for partial sums under every partition into IUs. | M-conj | 2: `UpdatedMatMul` (:43), `Training` (:56) |

**@network-accounting (NetTiming), 4 entries.** Each is stated of an arbitrary `Certifier`, and the guarantees
quantify over every `Interaction` (`Models/NetworkCertifier/Guarantees.lean:266-270`).

| Name | file:line | Reading | Class | Users |
|---|---|---|---|---|
| `NetTiming.Regenerates` (W2) | `Models/NetworkCertifier/Assumptions.lean:28` | The wire at step k is a fixed function of the observation; "no physical feature, ack, backpressure … passes" (:24-27). | P plus code (uncertain split): the code part is a property of core's certifier to prove, and the "no physical feature" part is device-intact. | 2: `EncardDecodableLeConstantRate` (`Guarantees.lean:270`), `…PerWindow` (:297) |
| `NetTiming.Packed` (W4) | `Models/NetworkCertifier/Assumptions.lean:37` | The occupied slots of a row form a prefix. | M-fact (core's certifier code; `Properties/CertifierDevice.lean:114` states the device's `Packed`) | 2: `EncardIngressObsDecodableLe` (:308), `…PerWindow` (:367) |
| `NetTiming.Allocated` (W4) | `Models/NetworkCertifier/Assumptions.lean:44` | At most `r ℓ` real frames per bucket. | M-fact (certifier code) | 2: the same two (:308, :367) |
| `NetTiming.JitterBounded` (J) | `Models/NetworkCertifier/Assumptions.lean:66` | A step's timing offset takes one of D classes. | P (the device clock: an outside-world function) | 4: all four (:270, :297, :308, :367) |

**@compute-accounting (Pouw), 71 entries.** The TT_OUT rows are grouped by file. Every γ statement has the form
`∀ CM sem, TTOut… CM … → Gγ CM …` with `CM` abstract (`Models/Pouw/Assumptions/PearlC/TTOutRev1.lean:41-42`).

| Name(s) | file:line | Reading | Class | Users |
|---|---|---|---|---|
| `Pouw.Assumptions.TT` | `Models/Pouw/Assumptions/Game.lean:26` | Tight transcript: the correct units' work is ≤ T/(1−γ₀) except with ε. "False when γ₀ ≥ 1" (:24-25). | M-conj | 2: `Pouw.EndToEnd`, `GammaFromTT` |
| `Pouw.NCP.Assumptions.TTNCP` | `Models/Pouw/Assumptions/NCP/Assumptions.lean:22` | NCP's tight transcript | M-conj | 1: `gammaFromTTNCP`. The iff `TTNCPUIff` passes. |
| `Pouw.NCP.Assumptions.TTNCP_U` | `Models/Pouw/Assumptions/NCP/RouteUAssumptions.lean:24` | NCP's tight transcript on route U | M-conj | 2: `GammaFromTTNCP_U_C2` (`Models/Pouw/Guarantees/NCP.lean:198`), `GammaFromTTNCP_U_v1`. `TTNCPUIff` (:152) and `TTNCPUWitness` (:210) pass. |
| `…PearlC.Assumptions.TTOut`, `TTOutTile` | `Models/Pouw/Assumptions/PearlC/TTOut.lean:22`, `:92` | The generic per-output and per-tile TT_OUT forms | M-def | 0 directly; the named forms below instantiate them |
| `TTOutPearlC` | `TTOut.lean:85` | TT_OUT(1/400) for Pearl-C. **Falsified** (rating D): the first promotion into +0 is priced (:33-35). It also carries the cross-group hole (:43-48). | M-conj, falsified | 2 fail: `Gamma16384` (`Models/Pouw/Guarantees/PearlC.lean:307`), `Gamma8192` (:319). The witness `ttOutPearlCWitness` passes. |
| `TTOutPearlCDev`, `TTOutTilePearlCDev` | `TTOut.lean:130`, `:136` | TT_OUT per device; the device sets G (`Definitions/Pouw/PearlC/Device.lean:62, 83, 88`) | M-conj (not falsified at G=0, sm_120 v2) | 8 + 2 γ statements, e.g. `GammaSm120v2Cap1000_16384`, `GammaUnpromotedCap1000_8192` (`Guarantees/PearlC.lean:720`), `SampledSm120v2Cap1000_8192`, plus 4 relation lemmas |
| `TTOutPearlCDevRev1`, `TTOutTilePearlCDevRev1` | `Models/Pouw/Assumptions/PearlC/TTOutRev1.lean:46`, `:52` | The rev1 repair: the first promotion is not priced. At G=0 it equals `TTOutPearlCDev` (:23). | M-conj | 17 + 16 γ statements (e.g. `GammaSm120v1Rev1_8192`, `SampledSm120v1Rev1_8192`, `pearlCSampledSm120v1RowSeed_8192`, the three `pearlCHidden*`, `HiddenFlock…`), plus 6 relation lemmas |
| `TTOutPearlCH100Rev1`, `TTOutTilePearlCH100Rev1` | `TTOutRev1.lean:57`, `:64` | rev1 at the H100 (G=4) | M-conj | 4: `GammaH100Rev1_16384`/`_8192`, `SampledH100Rev1_16384`/`_8192` |
| `TTOutPearlCDevChainOnly`, `TTOutPearlCDevRev1ChainOnly` | `Models/Pouw/Assumptions/PearlC/TTOutChainOnly.lean:22`, `:33` | Chain-only credit | M-conj | 2 + 4: e.g. `GammaSm120v2Cast8p72ChainOnlyCap1000_8192`, `GammaSm120v1Cast8p72ChainOnlyRev1_8192` |
| `TTOutPearlCDevChainCap`, `TTOutTilePearlCDevChainCap` | `Models/Pouw/Assumptions/PearlC/DeviceChainCap.lean:58`, `:65` | Chain credit at the cap | M-conj | 3 + 2: `GammaSm120v2ChainCap1000_16384`/`_8192`, `GammaUnpromotedChainCap1000_8192`, `SampledSm120v2ChainCap1000_16384`/`_8192`, plus 2 relation lemmas |
| `chainCreditDev`, `pearlCProtocolDevChainCap`, `pearlCTilesDevChainCap` | `DeviceChainCap.lean:23`, `:31`, `:37` | Definitions the ChainCap forms read | M-def | 0 as premises |
| `TTOutPearlCDevUOnly`, `TTOutU` | `Models/Pouw/Assumptions/PearlC/TTOutUOnly.lean:79`, `:53` | TT_OUT on the useful output only | M-conj | 2: `GammaUOnlySm120Rev1_8192`, `GammaUOnlyUnpromotedCap1000_8192`, plus the relation lemma `TTOutPearlCDevRev1OfUOnly` |
| `CorrectU`, `correctSetU`, `WinsU`, `GγU` | `TTOutUOnly.lean:25`, `:32`, `:36`, `:40` | Definitions | M-def | 0 as premises. `GammaUImpliesGamma` (GγU → Gγ, between definitions) passes. |
| `TTOutFp4`, `TTOutTileFp4`, `TTOutFp4Sm120`, `TTOutTileFp4Sm120` | `Models/Pouw/Assumptions/PearlC/TTOutFp4.lean:21`, `:27`, `:84`, `:91` | NVFP4 TT_OUT | M-conj | 4: `GammaFp4Sm120_16384`/`_8192`, `SampledFp4Sm120_16384`/`_8192` |
| `TileProofSound`, `TileProofSoundAll` | `Models/Pouw/Assumptions/PearlC/HiddenTile.lean:28`, `:47` | A drawn tile's proof is accepted only on a good or blank tile, up to ηzk. It is an open obligation to discharge from C-Flock (:5-17). CR is inside the class `HA.ProverBounded` (`Definitions/Pouw/PearlC/Hidden.lean:26-34`). It holds for an empty class (`HiddenTile.lean:44-46`). | M-obl, with H inside the class | 4: `gammaHidden_of_sampled_all` and the three `pearlCHiddenSm120v1LoopCast8p72Rev1*Cap1000_8192` |
| `FragDraw` | `Models/Pouw/Assumptions/PearlC/RowSeedAssumptions.lean:27` | The fragment noise distribution; "Nothing here proves it". C6 idealizes the leaf's CR (:11-12). | M-conj (with H inside: the leaf's CR) | 1: `TTOutRowSeedSkipClass` (`Guarantees/PearlC.lean:204`, a relation lemma) |
| `Fp8Atom.H1T.DistinctLiveH1T`, `H1TRunningWords` | `Models/Pouw/Assumptions/Fp8Atom/H1TAssumptions.lean:27`; `…/H1TRunningAssumptions.lean:32` | "Assumed until proved" (:13-14), and simulation evidence; the two are equivalent (`H1TRunningAssumptions.lean:24-26`). | M-conj | 2 relation lemmas: `h1tDistinctLive`, `h1tRunningOfDistinct`. These are the only guarantees whose lock `assumptions` list is non-empty. |
| `Dimension.A1_cost_quad` | `Models/Pouw/Assumptions/Dimension/PipeAssumptions.lean:27` | A1's quadratic-cost form | proved, by `a1CostQuadHolds` (Forest.lean:85) | 1: `a1CostQuadHolds` (passes; it is the proof) |
| `Dimension.Assumptions.A2_algebraicSufficiency` | `Models/Pouw/Assumptions/Dimension/Assumptions.lean:75` | Every program of the machine is matched by an algebraic one (:65-74). | M-conj | 1: the iff `A2WordsIff` (`Models/Pouw/Guarantees/Dimension.lean:26`), which passes |
| `Machine`, `.Prog`, `.cost`, `.outputs`, `wordSet` | `Dimension/Assumptions.lean:51`, `:53`, `:55`, `:57`, `:61` | Definitions | M-def | 0 as premises |
| `Dimension.Embed.A1fpOn`, `CanonicalNaN`, `FpOK`, `FpOpnd`, `FpPipe`, `FpStep`, `NaNGap` | `Models/Pouw/Assumptions/Dimension/EmbedAssumptions.lean:68`, `:91`, `:48`, `:40`, `:54`, `:43`, `:85` | A1's FP form and FP-semantics conditions | M-def | 0 as premises. `a1fpIff` (`Embed.lean:177`), `a1fpOnRangeGap` (:229) and `ttNCPM4090NanGap` (:253) are math and pass. |
| `Dimension.H100.Floor`, `H32`, `Prices100` (+ `.mac`, `.tc`, `.ffma`, `.int32`, `.fp64`, `.other`), `Shape100` (+ 9 shapes, `.k`, `.elems`, `.regPrice`), `nominalMac` | `Models/Pouw/Assumptions/Dimension/H100Assumptions.lean:105`, `:116`, `:85-98`, `:53-80`, `:101`, `:119` | H100 price and shape definitions; `H32` is a price-floor condition | M-def | 0 as premises. `distinctWritesMH100` (`∀ pr, H32 pr → …`, `H100W.lean:100`), `H32LoopFree` and `H32Measured` pass. |

That is 9 + 2 + 4 + 71 = 86 entries.

### 1b. Named assumptions the map lacks

| Name | file:line | Owner | Reading | Class | Users |
|---|---|---|---|---|---|
| `B1Prime` | `Models/Pous/Assumptions.lean:22` | @memory-accounting | Conjecture B1′ | M-conj | 0 listed. It appears only in the unlisted defs at `Models/Pous/Guarantees.lean:146`, `:158`, `:214`. |
| `LemmaA` | `Models/Pous/Assumptions.lean:30` | @memory-accounting | A lemma taken as a hypothesis | M-fact | 0 listed (the same unlisted defs) |
| `PrimeP16448` | `Models/Pous/Assumptions/P2.lean:14` | @memory-accounting | p is prime: an ECPP certificate, not checked in Lean | M-fact | 0 listed |
| `Verity.Assumptions.GemmHopperStep`, `GemmAmpereStep` | `Models/Core/Assumptions.lean:28`, `:38` | core (none in the map) | The device's BF16 k16 step is `tcDotTotal` on the pipeline, from captures (:21-37). | P (hardware semantics: a device premise) | 0. No lock entry reads `Models.Core.Assumptions`. |
| `StepInputs` | `Models/Core/Assumptions.lean:18` | core | The step's domain | M-def | 0 |
| `AdviceBinding` | `Models/Core/Assumptions.lean:43` | core | "cr/sha-512 as the advice root's binding": `advice` is injective over `(n : ℕ) × Partition C n` (:41-44). | H in the forbidden "no collision exists" form; refutable (§3) | 0 |
| `TrustedNebiusHost` | `Models/Core/Assumptions.lean:51` | core | The device runs its stated code on the host (:46-50). | P (device intact) | 0 |
| `LmsEufCma` | `Models/Core/Assumptions.lean:58` | core | `∀ m σ, verify m σ = true → signed m` (:54-59) | H; refutable as written (§3, uncertain) | 0 |
| `KeyedStreamsUniform` (A4) | `Proofs/Flock/Soundness/Assumptions.lean:121` | @proofs | `verity.randomness` streams pass one test as uniform bytes, up to η: a PRF/dual-PRF of SHA-512's compression function (:101-120) | H (the rule: a reduction) | 0 listed |
| `UniformSecret` (A5) | `Proofs/Flock/Soundness/Assumptions.lean:142` | @proofs | The window secret is uniform: the OS CSPRNG (:127-141). | P (an outside-world function) | 0 listed |
| `PadNonvanishing`, `PadNonvanishing40` | `Proofs/Flock/Soundness/Assumptions.lean:198`; `…/Assumptions/Zk.lean:22` | @proofs | X_L + κ ≠ 0 on the level-0 domain, "never 0" (:192-197) | M-fact (provable math) | 0 listed |
| `RecordCustodyZK` | `Proofs/Flock/Soundness/Assumptions/Zk.lean:38` | @proofs | `RecordCustodyZKJ` at one table | S (as above) | 0 listed |
| `Padded` (W3), `UntimedStatus` (W5), `FailClosed` (W6) | `Models/NetworkCertifier/Assumptions.lean:33`, `:50`, `:59` | @network-accounting | Certifier code facts. `Properties/CertifierDevice.lean:178` proves a `FailClosed` of core's device, and it passes. | M-fact | 0 listed |
| `FramesReadNoTimingAdvice`, `OccupancyReadsOwnBlock` | `Models/NetworkCertifier/Assumptions.lean:78`, `:85` | @network-accounting | Dataflow conditions on the Program | M-fact or S (uncertain) | 0 listed |
| `TTOutTilePearlC` | `Models/Pouw/Assumptions/PearlC/TTOut.lean:121` | @compute-accounting | The per-tile `TTOutPearlC`; **falsified** (:103-104) | M-conj, falsified | 0 listed |
| `HalfApartH1T` | `Models/Pouw/Assumptions/Fp8Atom/H1TAssumptions.lean:33` | @compute-accounting | An H1T spacing condition | M-conj | 0 listed |
| `FragLanes`, `FloorTc` | `Models/Pouw/Assumptions/Dimension/H100Assumptions.lean:160`, `:144` | @compute-accounting | `FragLanes` "can fail" (:151-155); `FloorTc` is a price floor. | M-conj; M-def | 0 listed |
| RowSeed conditions: `RowLocal`, `RowSeedNoise`, `SplitClosed`, `TTOutRowSeed`, `TTOutTileRowSeed`, `CodeSeedNoise`, `RelabelClosed`, `FragmentPriced` | `Models/Pouw/Assumptions/PearlC/TTOutRowSeed.lean:95`, `:115`, `:151`, `:162`, `:173`, `:189`, `:197`, `:321` | @compute-accounting | Conditions "for the statement reviewer" on `sem`'s noise and on the domain's closure. `TTOutRowSeed*` are the conjectures. | M-conj. `SplitClosed`/`RelabelClosed` restrict the domain, so they may be S (uncertain). | `RowSeedNoise` 7, `SplitClosed` 7, `CodeSeedNoise` 3, `RelabelClosed` 3, `RowLocal` 3, `TTOutRowSeed` 3, `TTOutTileRowSeed` 1, `FragmentPriced` 1. E.g. the `pearlCHidden*RowSeed*` pair, `pearlCSampledSm120v1RowSeed_8192`, `pearlCSampledSm120v2RowSeedCap1000_8192`, `ttOutRowSeedCode_of_ttOut`. |
| `PearlCSem.RowDrawn` (C6) | `TTOutRowSeed.lean:336` | @compute-accounting | Each row's noise is one oracle draw at an **injective** key. "Commitments are ideal here: it abstracts the row leaf's collision resistance" (:332-335). | H, hidden in a definition | 1: `TTOutRowSeedSkipClass` (`Guarantees/PearlC.lean:204`, `hD`) |
| `pearlCProtocolDevRev1KRowCap`, `pearlCTilesDevRev1KRowCap` | `Models/Pouw/Assumptions/PearlC/TTOutRowSeedK.lean:19`, `:25` | @compute-accounting | Definitions | M-def | Read by the 2 `pearlCHidden*RowSeed*`, not as premises |
| `TTOutTileU`, `TTOutTilePearlCDevUOnly`; `TTOutFp4ChainOnly`, `TTOutTileFp4ChainOnly`; `pearlCProtocolDevChainCapK`, `pearlCTilesDevChainCapK` | `PearlC/TTOutTileUOnly.lean:19`, `:35`; `PearlC/TTOutFp4ChainOnly.lean:21`, `:26`; `PearlC/DeviceChainCapKernel.lean:19`, `:23` | @compute-accounting | More TT_OUT forms, and definitions | M-conj; M-def | 0 listed |
| `HonestClock` (×2) | `Models/Pouw/Assumptions/Deadline.lean:31`; `PearlC/Deadline.lean:18` | @compute-accounting | The verifier's clock is honest. | P (the verifier's clock: an outside-world function) | 0 listed |
| `HonestTileCapRate` | `Models/Pouw/Assumptions/PearlC/HonestCap.lean:78` | @compute-accounting | An honest tile exceeds the cap at most ε of the time: an empirical upper confidence limit (:60-77) | M-emp | 0 listed |
| `TileReadSound`, `TileReadBinds` | binders at `Proofs/Pouw/PearlC/FlockTile/Statement.lean:47-51`, described at :30-36 | @compute-accounting | T3 at the session, and the binding: open obligations. CR sits in `F.Cls`. | M-obl (H inside the class) | 1: `HiddenFlockSm120v1LoopCast8p72Rev1Cap1000_8192` |
| `Analysis.KnowledgeSound`, `LinkSound` | `Proofs/Flock/Soundness/Audit/OneStage.lean:85`, `:94` (`TwoStage.lean:121`, `:130`) | @proofs | Each is a "named hypothesis": a bound uniform over every `R`, `τ`, `tgt` (:82-98). | M-obl (likely unsatisfiable at SHA-512, §3) | 5: `audit_profile`, `audit_exfiltration`, `audit_window_split_of_record`, `audit_work_floor`, `audit_work_whole_stratum` |
| `AnchorsSound` | `Proofs/Flock/Soundness/Audit/OneStage.lean:247` | @proofs | Anchors' soundness | M-obl | 0 listed (not checked further) |

## 2. Inline hypotheses

### 2.0 Why the lock shows none

The audit tool can't see hypotheses inside a statement:
- `Facts.lean:284-292` runs `forallTelescope` without unfolding the type, so the hypotheses of a `def G : Prop` body are
  invisible to it.
- `check.py:934-941` records only closed `Prop` binders, so open binders like `hTT : TTOut… CM …` are dropped.

So 273 of 275 guarantees have `assumptions: []`, and every hypothesis below is in no assumptions record. The rows list
the hypotheses that are not the claim's own antecedent (that is, not the event being bounded and not a math side
condition).

### 2.1 `Flock.Guarantees.RecursiveSound` (`Proofs/Flock/Recursive/Statements.lean:54`)

| Binder | Line | Text | Class |
|---|---|---|---|
| `_hS` | :57 | `∀ j, Law.ExecStrata (Vs j).law.σs …` | S: V*'s laws are well-stratified. The laws are public, so this is checkable; uncertain whether the verifier refuses the rest. |
| `_hA3` | :58 | `∀ j, UniformRandomBytes (Vs j).law.Lb (Vs j).law.src` | P (an outside-world function) |
| `_hr` | :64 | `rateZ (planZAt …) i k ≤ ρ` at every history | Passes: `rateZ = 2^logLen/(e·k)` (`Soundness/Discharge/ZkLink/Compiled.lean:394-395`) is a parameter condition. |
| `_hbr` | :74 | `Flock.Assumptions.VBridge zs dg N k Rw x wmsg Sk cmt msg` | V |
| `q`, `_hCR` | :75-78 | `∀ i < I.r, ∀ ω pos, (forkAt (obS Vs) σ (cmtS cmt) … i ω pos).CR H512 (q i)` | **H**: `Finder.CR` is `SHA512CRStrict` with cost `fun _ => q` (`Proofs/Flock/Soundness/StrictCR.lean:86-87`), and "Lean doesn't check that the finder stays within it" (:82-85). The conclusion carries √(q i²/2^513) (:88), from `Finder.CR.le` (:89-94). |
| `_hin` | :80 | `InnerSound I εin` | M-obl: the inner protocol's soundness, a composition premise not discharged here. Uncertain whether it counts as the claim's own antecedent. |
| fields of `zs`, i.e. `ZkOuter` | `Recursive/Flock.lean:54-72` | `hscope : scopeOk c = true` (:54), `ht : I.tags.typed = false` (:57), `hDraw : ∀ ω, DrawOkZK …` (:66), `hTags : TagsOk I` (:67), `hRec : RecordsLiveZK I dj wr` (:68), `hown : … → OwnReads …` (:71-72) | S, carried as structure fields, so they appear in no binder. `hRec` is the record custody (S, or P). `hown` is a condition on accepted outcomes (S, uncertain). |
| conclusion: `boundCR` | `Recursive/Flock.lean:159-160` | `if zo.CR … τ then zo.bound … τ else 1` | **H in the conclusion**: `ZkOuter.CR` (:138-143) = `TabCR` (via `TableCRZ`, strict) ∧ `RegCRZC` (`Recursive/ZkReg/RegLink.lean:155-157`, `Finder.CR`) ∧ `oneRun … .CR H512 qR`. |
| conclusion: `linkBoundZC`, inside `bound` | `CompiledLink.lean:557-563`, used at `Recursive/Flock.lean:151` | `if LinkCRZC … then … else ⊤` | **H** (`ecr/sha-512`) in the conclusion |
| conclusion: `slackCR` | `Proofs/Flock/Recursive/Stage.lean:181-182` | `if zo.TabCR … τ then zo.stageSlack … else 1` | **H** in the conclusion |

`boundCR`, `slackCR` and `linkBoundZC` are classical case splits, not hypotheses. The statement is true without CR.
But at every prover whose finders fail the CR predicate, the bound is 1 or ⊤, and no one can decide that predicate for a
given τ. So in effect it is "assume CR". The rule's form would replace each with `bound + Pr[τ's finder outputs a
SHA-512 collision]`; the `Finder.ev (ind (IsColl H))` machinery for that already exists (`StrictCR.lean:80`, `:89-94`).

### 2.2 The other Flock headlines

All six `EndToEnd*` share one binder pattern. Lines are for `Proofs/Flock/EndToEnd/Statement.lean`; the others are at
`EndToEndDrawn/Statement.lean:47-81`, `EndToEndHidden/Statement.lean:61-97` and `:126-161`, and
`EndToEndRegistered/Statement.lean:61-97` and `:134-169`.

| Binder | Line | Text | Class |
|---|---|---|---|
| `ht` | :64 | `I.tags.typed = false` | **S**: flock-verify accepts typed statements (`verity/core/service/flock/Flock/HmRow.lean:1300`, `FlockVerify.lean:592`), and no statement covers them. |
| `hU` | :65 | `Built c.unit` | Implied by `hc` (`parse_built`, `Soundness/ExecRows.lean:198-201`), so redundant. It passes, but should go. |
| `hpt` | :66 | `pub.tables = none` | S (uncertain whether the verifier refuses a public file with tables) |
| `hscope` | :67 | `Discharge.Layout.scopeOk c = true` | **S**: these are "three conditions on the session's circuit that the verifier doesn't check" (`Soundness/Discharge/Layout/Scope.lean:8-12`). It also excludes `sha512/row/v2` rows (:16-17, :32-33). flock-verify never calls `scopeOk` (no match under `verity/core/service/flock/`). |
| `hdiv` | :69 | `kd % nTab I = 0` | S (uncertain whether the verifier refuses an uneven split) |
| `y₀` | :71 | `DrawSetupZJ (inputsJ I 0) … S₀ d₀` | Passes: every accepted draw supplies one (`EndToEnd_refSetup`, :56-59). The old whole-draw form was vacuous and is fixed. |
| `hTags` | :79 | `TagsOkZJ I` (public outputs, retained rounds, hm96 leaf: `Soundness/Discharge/Composed/DefsJ.lean:528-529`); `TagsOkZHJ` (`ZkHidden/DefsJ.lean:506`) in the Hidden and Registered statements | S. It splits by mode, and the union over the six statements still excludes typed statements. |
| `hCust` | :80 | `RecordCustodyZKJ …` | S or P (§1a) |
| `TableCRZ` antecedent | :94-95 | `(∀ ω j, TableCRZ … qF qS) →` | **H** (`SHA512CRStrict`) |
| `LinkCRZC` antecedent | :97 | `LinkCRZC … k Rw M t' →` | **H** (`SHA512CRExpected`) |

`ZeroKnowledgeHidden` (`Proofs/Flock/ZeroKnowledgeHidden/Statement.lean:49`) takes:
- `_ht : typed = false` (:52): S.
- `_hdm : … avoidsMask y.x.st = true` (:56-57): S. `avoidsMask` is defined in the proofs
  (`Soundness/Discharge/Composed/Base.lean:166`), and flock-verify never calls it.
- `_hKey : HashDerivedKeyHm96` (:59): H.

`RecursiveZK` (`Statements.lean:113`) takes:
- The outer session's simulation bound at ε_o (:118-120). M-obl: a composition premise that `ZeroKnowledgeHidden`
  should discharge (uncertain whether it counts as the claim's own antecedent).
- `HashDerivedKeyHm96` (:121): H.

### 2.3 Elsewhere

- `Pouw.Guarantees.PearlC.HiddenFlockSm120v1LoopCast8p72Rev1Cap1000_8192`
  (`Proofs/Pouw/PearlC/FlockTile/Statement.lean:42`) takes `0 ≤ ηzk` (:45, math),
  `TTOutTilePearlCDevRev1` (:46, M), `TileReadSound` (:47-48, M-obl) and `TileReadBinds` (:49-51, M-obl). CR is inside
  `F.Cls` (:32-33), and the session is a parameter (:38-41).
- `TTOutRowSeedSkipClass` (`Models/Pouw/Guarantees/PearlC.lean:204`) takes `hD : RowDrawn` (H in disguise),
  `hF : FragDraw` (M) and `hC4` (a RowSeed condition, M). None of them is in the map.
- `CompleteRows` (`Properties/CertifierDevice.lean:160`) takes `hs.map Prod.snd = handingBuckets …` (:166), "honest
  timing, stated over the trace" (:33-36). P (the device clock), but inline and unnamed.
- `IssuerVerifies` (`Properties/CertifierDevice.lean:209`) and `IssuerSigns` (:217) take `ValidKey i.key` (:203-206,
  :212, :220). Under the rule this is P (signing-key state), but it is not listed in Definitions/. It may be S instead
  (uncertain).
- `Nci.Guarantees.Training` (`Models/Nci/Guarantees.lean:50`) takes the ∀-D antecedent (:53-56), which is the claim's own
  antecedent. Its satisfiability is in §3.
- NetTiming's `hacc`/`hdec` (`Guarantees.lean:271-272`) are the decoding claim's own antecedent and pass. Its `hW2`, `hW4`,
  `hr` and `hJ` are named (§1a).
- The PoUW random-oracle model has no binder: every game draws the oracle uniformly from Q → R, so grinding and
  collisions are inside ε (`Models/Pouw/Assumptions/Game.lean:23-25`). This is an idealized hash, not SHA-512, and it is
  stronger than CR. I class it M-model; it could be read as H (uncertain).

## 3. Hypotheses that can't all hold, or make a statement vacuous

| # | Statement(s) | Why | Vacuous? |
|---|---|---|---|
| 1 | `Gamma16384` (`Models/Pouw/Guarantees/PearlC.lean:307`), `Gamma8192` (:319) | Their premise `TTOutPearlC` is falsified (`TTOut.lean:33-35`; the docstrings at `Guarantees/PearlC.lean:304-305`, `:316-317` say so). | **Yes**, for the real system. Not vacuous in Lean: `ttOutPearlCWitness` satisfies it in some model. |
| 2 | `TTOutPearlCDevRev1OfGranted` (`Guarantees/PearlC.lean:938`) | Its premise, the granted rows, is falsified at the H100 and sm_120 v1, both G=4 (doc :934-936; `TTOutRev1.lean:10-11`, `:26-28`; `Device.lean:62`, `:83`). | **Yes** at those devices; non-trivial only at G=0 (sm_120 v2, `Device.lean:88`). |
| 3 | `HiddenFlockSm120v1…` (`FlockTile/Statement.lean:42`); `TileProofSoundAll` and its 4 users | Both hold for an empty class (`FlockTile/Statement.lean:38-40`; `HiddenTile.lean:44-46`; `Definitions/Pouw/PearlC/Hidden.lean:36-40`), and the session is a parameter until TileRead's Definition lands (`Statement.lean:38`). | **Yes** for the real audit, until TileRead lands. `Hidden.lean:36-40` requires citing them beside the honest prover's `ProverBounded` theorem. |
| 4 | The 5 audit lemmas taking `KnowledgeSound`/`LinkSound` (`Audit/OneStage.lean:85`, `:94`) | Both are uniform over every prover `τ`. At SHA-512, "some strategy has a SHA-512 collision built in and opens a commitment two ways after no evaluations, and no soundness bound holds for it" (`Definitions/Pouw/PearlC/Hidden.lean:32-34`; `Soundness/Assumptions.lean:50-51`). | **Likely**, at a small εks or δlink at a SHA-512 session (uncertain: it depends on the session, but the cited docstrings say exactly this). |
| 5 | `RecursiveSound` (`_hCR`, :76-78) | `Finder.CR` never checks its budget (`StrictCR.lean:82-85`), so `q i` below the fork finder's real cost (at worst `q i = 0`) is a claim cr/sha-512 doesn't make. | Not vacuous in Lean, but at an unchecked q no evidence can establish it. |
| 6 | `RecursiveSound`'s conclusion (`boundCR`, `slackCR`, `linkBoundZC`) | Split on undecidable CR predicates: the bound is 1 or ⊤ wherever CR fails (§2.1). | Not vacuous, but it gives no bound you can use for a concrete prover. |
| 7 | `TTOutRowSeedSkipClass` (`Guarantees/PearlC.lean:204`) | `RowDrawn` wants `key` injective on m rows × 2^(32k) word tuples (`TTOutRowSeed.lean:336-340`). At a SHA-512 row leaf into 512 bits that is false once m·2^(32k) > 2^512, i.e. k ≥ 16. It holds only for an ideal key into a large Q (`rowDrawn_satisfiable`, :335). | **Yes** at a real SHA-512 key (uncertain: Q is abstract) |
| 8 | `AdviceBinding` (`Models/Core/Assumptions.lean:43-44`) | Injectivity of a 512-bit root over `Σ n, Partition C n`, an infinite domain, is false by counting. | **Refutable** at its intended instance; used by no listed guarantee |
| 9 | `LmsEufCma` (`Models/Core/Assumptions.lean:58-59`) | `∀ m σ, verify m σ = true → signed m` ranges over every σ, and the holder's signature on any m at an unused leaf verifies. So it is false if `signed` means signed in the run, and trivial otherwise. | **Refutable** (uncertain: depends on the `signed` instance); used by no listed guarantee |
| 10 | `Nci.Training` (`Models/Nci/Guarantees.lean:53-56`) | It needs every compliant D implementing T to run a chain with incompressibility. The assumption fails where layers before the first multiplication are committed in θ (`Models/Nci/Assumptions.lean:13-19`). | **Possibly**, for such T (uncertain) |
| 11 | Every PoUW γ: `∀ CM sem, TT… CM → Gγ CM` | `CM` is abstract (`TTOutRev1.lean:41-42`) and the real cost model is never pinned. With the ROM (§2.3), these are statements about an idealized hash and an unnamed cost model. | No, but they don't say which model is the real system. |
| 12 | `TT` (`Game.lean:26`) | "False when γ₀ ≥ 1 or for zero noise in natural models" (:25). The statements fix γ₀ < 1. | No |
| 13 | The six `EndToEnd*` | `ht` and `hscope` cover a strict subset of what flock-verify accepts (§2.2). | No, but this is S |
| 14 | Pous's 12 | Theorems about the abstract model `m1p` only; "none of them says the deployed P2 is secure" (`Models/Pous/Guarantees/P2.lean:15-16`). | No, but they say nothing about the deployed P2. |

## 4. Per owner

Counts are failing guarantees that take at least one hypothesis of the class; a guarantee can count in several.
"Map" counts the owner's assumption-map entries by class.

| Owner | Guarantees: total / pass / fail | P | V | H | M | S | Map entries |
|---|---|---|---|---|---|---|---|
| @proofs (Flock) | 89 / 75 / 14 | 4 | 1 | 9 | 7 | 8 | 9: V 1, H 4 (+1 def), M 1, P 1, S 1 |
| @compute-accounting (Pouw) | 162 / 77 / 85 | 0 | 0 | 6 (in a class or definition) | 85 | 0–7 (uncertain) | 71: M-conj 24 (one falsified), M-obl 2, M-def 44, proved 1 |
| @compute-accounting (Properties) | 27 / 27 / 0 | – | – | – | – | – | – |
| @lean (Nci) | 8 / 5 / 3 | 0 | 0 | 0 | 3 | 0 | 2: M-conj |
| @network-accounting (NetTiming) | 4 / 0 / 4 | 4 | 0 | 0 | 2 | 0 | 4: P 1, P plus code 1, M-fact 2 |
| @network-accounting (Properties) | 15 / 12 / 3 | 1–3 | 0 | 0 | 0 | 0–2 | – |
| @memory-accounting (Pous) | 12 / 12 / 0 | – | – | – | – | – | 0 (3 unmapped M, unused) |
| core (not in the lock) | – | – | – | – | – | – | 0 (6 unmapped: P 3, H 2, def 1; unused) |

For the Pouw H column, the 6 are `HiddenFlock…`, `gammaHidden_of_sampled_all` and the three `pearlCHidden*` (CR
in the class), plus `TTOutRowSeedSkipClass` (`RowDrawn`).

Most consequential, per owner:
- **@proofs**:
  1. `RecursiveSound`: `_hCR` (H, with an unchecked budget), the CR splits in `boundCR`/`slackCR`/`linkBoundZC`, and S in
     `ZkOuter`'s fields (§2.1).
  2. The six `EndToEnd*`: the `TableCRZ`/`LinkCRZC` antecedents (H), plus `ht` and `hscope`, which flock-verify doesn't
     enforce (S).
  3. `RecordCustodyZKJ` in all six (S, or P).
  4. The uniform `KnowledgeSound`/`LinkSound` in 5 audit lemmas (§3 #4).
  5. `ZeroKnowledgeHidden`'s `_hdm`, unchecked by the verifier (S).
- **@compute-accounting**:
  1. Every γ rests on a TT/TT_OUT conjecture (72 statements).
  2. `Gamma16384`/`Gamma8192` rest on a falsified one.
  3. The hidden-audit trio and `HiddenFlock…` put CR in the prover class (`Definitions/Pouw/PearlC/Hidden.lean:26-34`, a
     trusted file) and are degenerate at an empty class.
  4. `RowDrawn`'s injective key (H in a definition).
  5. The ROM and the abstract `CM` (§3 #11).
- **@lean**:
  1. Incompressibility is the whole content of `UpdatedMatMul`, `Training` and `IuReads`.
  2. `Training`'s antecedent may be unsatisfiable (§3 #10).
- **@network-accounting**:
  1. The four NetTiming bounds quantify over an arbitrary certifier with W2/W4 as hypotheses. Under the rule, they should
     be stated of core's `CertifierDevice`, with only device-intact and clock premises.
  2. `CompleteRows`' honest timing is inline and unnamed.
  3. `ValidKey` is unlisted key state.
- **@memory-accounting**: none. `B1Prime`, `LemmaA` and `PrimeP16448` are read only by unlisted defs.

## 5. To raise before the `RecursiveSound` statement edit

Other statements take `SHA512CRStrict`/`SHA512CRExpected` (or a CR predicate) and need the same fork form ("it holds,
or the prover's runs yield a SHA-512 collision"; for commit-then-coin, two runs sharing a commitment):

1. **The six `EndToEnd*`.** `TableCRZ` (strict; the knowledge finders are `twoRuns`/`forkFinder` sharing a commitment,
   `StrictCR.lean:100`, `:134`) and `LinkCRZC` (expected-time, `CompiledLink.lean:548-552`) are antecedents at
   `EndToEnd/Statement.lean:94-97`, `EndToEndDrawn/Statement.lean:78-81`, `EndToEndHidden/Statement.lean:94-97` and
   `:158-161`, and `EndToEndRegistered/Statement.lean:94-97` and `:166-169`.
2. **Inside `RecursiveSound` itself, beyond `_hCR`.** The conclusion's `boundCR` (`Recursive/Flock.lean:159-160`,
   covering `TabCR`, `RegCRZC` and `oneRun.CR`), `slackCR` (`Stage.lean:181-182`) and `linkBoundZC`
   (`CompiledLink.lean:557-563`, `ecr`) are CR case splits. Edit `_hCR` alone and CR stays in the bound. `regBoundZC`
   (`RegLink.lean:162-164`) has the same shape, if it is used downstream.
3. **The hidden audit.** CR is in the prover class: `HA.ProverBounded` (`Definitions/Pouw/PearlC/Hidden.lean:26-34`, a
   Definitions/ file) and `F.Cls` (`FlockTile/Statement.lean:32-33`). This touches `TileProofSoundAll`'s 4 users and
   `HiddenFlock…`, all @compute-accounting.
4. **The expected-time form.** `SHA512CRExpected` bounds by E[cost]/2^256, so the link term's fork form is
   `δ_link ≤ … + Pr[the link finder outputs a collision]`, with the 2^-256 bound moved into a separate reduction.
5. **The reductions' budgets.** `Finder.CR` takes `q` unchecked (`StrictCR.lean:82-85`). The reduction lemma that turns
   `Finder.ev (IsColl)` into q²/2^513 should state the finder's real cost.
6. **The other hash premises the rule names.** `KeyedStreamsUniform` (`Soundness/Assumptions.lean:121`) and
   `HashDerivedKey`/`Hm96Hiding` (:182-190, through `HashDerivedKeyHm96` in `RecursiveZK` and `ZeroKnowledgeHidden`)
   become reductions. So should Core's `AdviceBinding` and `LmsEufCma`: unused today, but in the forbidden form.
7. **Intermediate lemmas.** 87 `.lean` files use these predicates, so the edit moves them together:
   - 47 under `Proofs/Flock/Soundness/Discharge` (ZkHidden 10, ZkReg 9, Composed 9, Exec 8, ZkLink 5, ZkExec 2,
     ZkBind 2, PrivateCircuit 2).
   - 5 in `Soundness/CROnly`, 3 in `Soundness/ZK`, 3 in `Soundness/Audit`, 2 in `Soundness/Registered`, 1 in
     `Soundness/Binding`.
   - `Soundness/{Teeth,StrictCR,Soundness,LinkFinder,Headline,E2E,Assumptions}.lean`.
   - 4 in `Recursive/ZkReg`, plus `Recursive/{Transfer,Statements,Stage,Flock}.lean`.
   - The 4 `EndToEnd*` statement directories and their 4 `.lean` roots.
   - 2 in `Proofs/Pouw/PearlC/FlockTile`, and `Definitions/Pouw/PearlC/Hidden.lean`.
8. **The check itself.** "The check refuses any other hypothesis in Properties/" holds only once `check.py`/`Facts.lean`
   unfold `def G : Prop` bodies and record open binders (§2.0). Today every Flock and Pouw statement would pass it, and
   the scope fields inside the `ZkOuter` structure (§2.1) would still escape a binder-only check.
