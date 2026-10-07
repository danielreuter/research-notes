---
id: 20261007T0350Z-draft-specs-sort
campaign: platform-redesign
lane: specs-sort
kind: draft
status: open
repo: verity
origin: f5360e4e15eeab2304793ba41dd3dd2ce38f670a
---

# Sorting Security's statements for the platform redesign

This sorts what `verity/Security/` states into the redesign's trees (Properties/, Models/, Definitions/, or out), for
@lean's move to a top-level `Security/` and for the Security page (Notion, draft of 7 Oct). It is read-only, at main
`f5360e4`: every listed guarantee (1,705 in `verity/Security/lean-audit.json` and 7 in the C-Flock verifier's, 1,712 in
all) and the 77 `Specs/` modules. Nothing was built, audited or run; statements are read from the locks' signatures and
the source.

The full table is **art:c8a862868c6f80da79644052e3bf037a45667efd7959a61933f40632c57d991b** (`specs-sort/v0`). It has one
row per guarantee (name, area, stating module, target, the function it's about, the verifier modules and definitions it
reads, named assumptions, and flags: `cr-assumption`, `completeness`, `nonvacuity`, `scope`, `setting`) and one row per
Specs module. Points the leads' review of the page already makes are cited by topic, not repeated: ml/ hiding, PoUW's
2⁻¹⁰⁰, CompleteSampled, RowDrawn, Lake and layers, spec_alert's records, the replay key, staged instances, the
certifier's difftest, LmsEufCma, C-Flock's 874 in Proofs/Flock, the 280 readers of `HmRow.parse`, PoUS's Models list,
and compute-accounting's PoUW split.

What each target means here:

- **Properties**: a claim about a core/ function. A *claim* is what Table 1, the docs or a user relies on; a
  *component* is what one of the verifier's checks establishes when it returns ok.
- **Models**: a claim about a Lean model of code that runs as Python. For 41 PoUW rows it's a claim about the device
  cost model, with no verifier function at all.
- **Definitions**: a statement that core/'s version of a function equals its mathematical twin. The twin goes in
  Definitions/, the proof in Proofs/.
- **out**: nothing outside Lean relies on it: an internal lemma, a non-vacuity witness or instance check, or completeness.
- **unforced**: NCI, which has no code to tag.

"Relies on" follows Daniel's guarantee ruling (4 Oct, 2:03 PM PDT). For PoUW, that's the 151 names #1156 keeps plus
the 47 it lifts (158 together); for C-Flock, the names #1170 keeps. Both PRs are open, so every row that is *out*
because nothing cites it rests on them.

## Summary

Listed guarantees, area × target:

| area | Properties | Models | Definitions | out | unforced | total |
|---|---|---|---|---|---|---|
| Flock | 25 | 26 | 25 | 805 | 0 | 881 |
| Pouw | 0 | 154 | 0 | 653 | 0 | 807 |
| Pous | 0 | 12 | 0 | 0 | 0 | 12 |
| NetworkCertifier | 0 | 4 | 0 | 0 | 0 | 4 |
| Nci | 0 | 0 | 0 | 0 | 8 | 8 |
| all | 25 | 196 | 25 | 1458 | 8 | 1712 |


Where they're stated: 239 in Specs/ (PoUW 215, NCI 8, PoUS 12, the certifier 4), 77 in `Definitions.Pouw`, 1,389 in
Proofs (C-Flock 874, PoUW 515), and 7 in the verifier package itself.

The 77 Specs/ modules, area × target:

| area | modules | target |
|---|---|---|
| Core | 6 | unforced |
| Nci | 2 | unforced |
| NetworkCertifier | 2 | Models |
| Pous | 5 | Models |
| Pouw | 62 | Models 61, out 1 (`Specs.Pouw.Assumptions.PearlC.HonestCap`) |

The proposed C-Flock property list has **25 properties: 8 claims and 17 components**. C-Flock also has 25 twin
statements for Definitions/ and 26 rows for Models/.

## 1. Specs/ and the guarantees outside C-Flock

### Core: 6 modules, no listed guarantee since #1169

- `Specs.Core.Assumptions` holds the hardware step semantics (`GemmHopperStep`, `GemmAmpereStep`, `StepInputs`),
  `TrustedNebiusHost`, and two assumptions about fixed functions, `AdviceBinding` and `LmsEufCma`. No listed
  guarantee takes them.
- `Specs.Core.Guarantees.Circuit` holds facts about the correct units of a circuit (composition, cones, openings,
  refinement). They're about `verity.primitives.circuits.partition`, and NCI and PoUW use them as lemmas.
- `Specs.Core.Guarantees.Game` says how sound games compose (`SoundAnd`, `SoundMono`, `SoundInterleave`,
  `SoundBatch`, `SoundBind`). It's soundness vocabulary, a Definitions/ candidate.
- `Specs.Core.Guarantees.PrivatePartition` says what a private partition's public predicates establish. It's about the
  partition checker and `experimental/verity_experimental/private_circuits`. `RegisteredMeets` takes `AdviceBinding`.
- `Specs.Core.Guarantees.TC` relates the tensor-core step relation (`verity_catalog.silicon.relation`, in Lean
  `Definitions.Core.TC.Relation`) to the step semantics (`Definitions.Core.TC.Spec`), two Lean transcriptions of
  Python checked against each other. Its `AmpereStepComplete`, `HopperStepComplete` and `PackSoundComplete` are
  completeness statements.
- `Specs.Core.Guarantees` is the index, `def G`.

### NCI: 2 modules, 8 guarantees, unforced (no code)

- `Nci.SecurityProofs.Training`, `UpdatedMatMul` and `Inference` are claims of the policy: throttle frontier training,
  leave inference alone.
- `ReadBound`, `IuReads`, `FullPositions`, `OtherPositions` and `LoomisWhitney` are steps of the throttling proof that
  are listed as guarantees.
- `Specs.Nci.Assumptions` assumes compute-bounded incompressibility of activations and partial sums.
- `four_names` makes each one `Nci.SecurityProofs.G : Nci.Guarantees.G`.

### Network certifier: 2 modules, 4 guarantees, Models

All four are about the Lean model `Certifier` of `verity/protocols/accounting/communication/certifier/` (`audit.py`:
`Audit.check_link`, `Audit.check_ingress_link`; `schedule.py`: `expected_grids`):
`NetTiming.SecurityProofs.EncardDecodableLeConstantRate`, `EncardDecodableLeConstantRatePerWindow`,
`EncardIngressObsDecodableLe` and `EncardIngressObsDecodableLePerWindow`. The assumptions module states W2 to W6, J and
Theorem 3's dataflow conditions. AGENTS.md calls the package `communication.warden`, but the tree has
`communication/certifier` and no warden.

### PoUS: 5 modules, 12 guarantees, Models

All 12 are about the Python protocol, in an ideal-hash model, and none about the Lean grader:

- the four `BandMultiMeetsFamily` statements (plain, D0, D1, D2): `schemes/band.py`, `Band`;
- `ChainDenseMeets64`: `schemes/dense.py`, `Dense`;
- the 7 in `Specs.Pous.Guarantees.P2` (`P2ErrorSplitB19Uncond`, `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond`,
  `P2MeetsM1pW8192Uncond`, `P2SlackB19Uncond`, `P2SlackFamilyFreeBlocks`, `P2SlackFamilyUncond`): `schemes/p2.py`,
  `P2Params` and `encode_segment`;
- each of them through `verifier.py` (`VerifierKey.check`) and `audit.py` (`MemoryChallenger`).

The grader (`verity/protocols/accounting/space/pous/lean/`, Lean only) has no listed guarantee: its `lean-audit.json`
has no `guarantees`. It has one escape, `@[extern "lean_internal_set_max_memory"] setMaxMemory` (`Grader/Main.lean:27`).
It grades a submission against the 73 statements `Grader/Registry.lean` names (`pinnedTargets`). These are all
`Pous.Guarantees.*` from `Specs.Pous.Guarantees`, 5 of them listed, and `Main.lean` loads them at run time with
`importModules`. `Proofs.Pous.Targets`, exempt from the audit, holds each one as a `sorry` stub. So the 73 are the
grader's input and the protocol's claims, not properties of the grader.

`Specs.Pous.Guarantees.SecureErasure` is the secure-erasure model, and none of it is listed. The assumptions modules hold
B1′, Lemma A and `PrimeP16448`. The 7 P2 guarantees read `Params.ρ = 18/19`, `δ = 1/100`, `expansion = 21/20` and
`εMax = 2⁻¹²⁸` from `Definitions.Pous.Accounting.Params`. Those are numbers in the spec, not core/ settings.

### PoUW: 62 modules, 807 guarantees

The modules are 61 Models and 1 out (`Assumptions.PearlC.HonestCap`, completeness's one assumption):

- `Specs.Pouw.Guarantees.*` (7 modules): Game, Deadline, NCP and PearlC are about `audit.py`'s `Verifier` and the
  schemes; Dimension and Barrier are about the cost model.
- `Assumptions.Dimension.*` (25) and `Assumptions.Fp8Atom.*` (5): the device cost model (M4090, MH100, the pipes,
  H-1T), with no verifier function.
- `Assumptions.NCP.*` (6): NCP's game, chain, route U and TT_NCP (`schemes/ncp.py`).
- `Assumptions.PearlC.*` (14 besides HonestCap): Pearl-C's TT_OUT forms, chain cap, deadline and hidden-tile obligation
  (`schemes/pearl_c*.py`, `audit.py`); `RowSeedAssumptions` holds FragDraw.
- `Assumptions`, `Assumptions.Game`, `Assumptions.Deadline`, `Assumptions.Pinned`: TT, HonestClock, the index, and the
  pinned headline statements.

The guarantees:

- **Models, 154.** 113 are about `verity/protocols/accounting/work/pouw/audit.py` (`Verifier.audit`,
  `Verifier.check_tile`) and the schemes (`schemes/pearl_c.py`, `pearl_c4.py`, `ncp.py`, `window.py`). 41 are about the
  cost model with no verifier function: TileBound 28, Dimension 7, Fp8Atom 3, AlignedExact 1, SecurityProofs.Dimension 1
  and SecurityProofs.Barrier 1.
- **out, 653.** 555 are lemmas #1156 drops, 91 are non-vacuity witnesses or sanity checks, and 7 are completeness.
- Of the 154 Models rows, 98 are stated inline in `Proofs.Pouw.*`, 45 in `Specs.Pouw.Guarantees.*`, 8 in
  `Specs.Pouw.Assumptions.*` and 3 in `Definitions.Pouw.*`.
- #1156 drops all 16 statements of `Specs.Pouw.Assumptions.Pinned`, so they're out here: `Usefulness`, the four
  `Milestone*`, `Int32Decode`, `Int32Transcript`, `Int8KBound`, `NoisedKBound`, `GammaBudget`, `CopyBound`, two
  completeness statements and three witnesses. Whether the headline statements should go is compute-accounting's call.
- Four witnesses are kept by #1156, or lifted, but are out here: `Pouw.PearlC.ttOutPearlCWitness`,
  `Pouw.SecurityProofs.NCP.IndependentWitness`, `Pouw.SecurityProofs.NCP.TTNCPUWitness` and
  `Pouw.TileBound.support_admits_open`.
- `reads_exempt` calls `Proofs.Pouw.PearlC.Gamma` "non-vacuity witnesses", but two of its statements are numeric claims
  #1156 keeps: `pearlCGamma16384` (Γ ≤ 536953/103540000 under `TTOutPearlC` at 1/400) and `pearlCGamma8192`
  (Γ ≤ 281273/52340000). They're Models here.

## 2. C-Flock

There are 881 rows: 874 in `Proofs/Flock`, whose reads are exempt, and 7 in the verifier package. By module family:

| family | rows | Properties | Models | Definitions | out |
|---|---|---|---|---|---|
| Soundness.Discharge | 483 | | | | 483 |
| Soundness.Audit | 97 | | 25 | | 72 |
| Level3 | 56 | | | 21 | 35 |
| Soundness.ZK | 53 | | | | 53 |
| Soundness.CROnly | 33 | | | | 33 |
| Soundness.Refine | 32 | | | | 32 |
| Verifier (`Proofs.Flock.Verifier`) | 18 | 12 | | 2 | 4 |
| Soundness.Binding | 11 | | | | 11 |
| VBridge | 11 | | | | 11 |
| verifier package (`Flock.*`) | 7 | 5 | | 2 | |
| EndToEnd* (4 modules) | 8 | 6 | | | 2 |
| Recursive | 2 | 1 | 1 | | |
| ZeroKnowledgeHidden | 1 | 1 | | | |
| 20 other Soundness families | 69 | | | | 69 |

The 20 other Soundness families are Types 9, KeyedDraw 8, ExecDrawOS 7, Registered 7, StrictCR 6, ExecStratified 4,
E2E 4, Teeth 4, Instance 4, Knowledge 3, Soundness 3, Compose 2, and 1 each for ExecDraw, Certificate, Merkle,
Headline, Rope, ComposeDag, Session and CompiledSound.

### The 25 proposed properties

"Reads" counts the verifier modules, and the definitions in them, that the lock records the statement as reading. A
module's definitions are the union over every guarantee that reads it, so these counts are upper bounds; the art has
each property's list.

| property | tier | about | stated in | modules / definitions read | flags |
|---|---|---|---|---|---|
| `EndToEnd`, `EndToEndDrawn` | claim | `Flock.Zk.verify` (`flock-verify verify --zk`), after `setupOf`, `Zk.shapeOk`, `Setup.ofCircuit` | `Proofs.Flock.EndToEnd.Statement`, `…EndToEndDrawn.Statement` | 42 / 1,717 | hash hypotheses, 5 scope hypotheses, custody, rate |
| `EndToEndHidden`, `EndToEndHiddenDrawn` | claim | the same, hidden outputs (`HmOut.parse`, `HmOut.loadPublic`) | `Proofs.Flock.EndToEndHidden.Statement` | 42 / 1,717 | the same |
| `EndToEndRegistered`, `EndToEndRegisteredDrawn` | claim | `Flock.Zk.verify` with `Flock.Registered.check` | `Proofs.Flock.EndToEndRegistered.Statement` | 43 / 1,745 | hash hypotheses, 4 scope hypotheses, custody, rate |
| `RecursiveSound` | claim | `Flock.Zk.verify` on the outer statement V*, whose circuit checks the inner proofs | `Proofs.Flock.Recursive.Statements` | 43 / 1,745 | `Fork.CR H512`, `VBridge`, `InnerSound I εin`, rate |
| `ZeroKnowledgeHidden` | claim | the transcript `flock-circuit --zk` produces (`backends/flock/live`, Rust), as `Flock.Zk.verify` reads it | `Proofs.Flock.ZeroKnowledgeHidden.Statement` | 36 / 1,550 | `HashDerivedKeyHm96`, untyped only |
| `merkle_binding`, `opens_binding`, `climb_binding`, `merkleCheck_opens`, `MerklePair.hm96_inputs`, `MerklePair.sha256_inputs`, `MerklePair.sha512_inputs`, `MerkleScheme.collision_hash` | component | `Flock.merkleCheck`, `Flock.opens`, `Flock.climb`, `Flock.MerkleScheme` | `Proofs.Flock.Verifier.Merkle` | 2–5 / 74–135 | none |
| `Registered.check_ok`, `Registered.opensLeaf_binding` | component | `Flock.Registered.check`, `Flock.Registered.opensLeaf` | `Proofs.Flock.Verifier.Registered` | 17 / 715; 6 / 251 | none |
| `squeeze_answers`, `squeeze_retained` | component | `Flock.Transcript.squeeze` | `Proofs.Flock.Verifier.Transcript` | 4 / 118 | none |
| `CircuitType.check_ok` | component | `Flock.CircuitType.check` | `Flock.CircuitType` (verifier package) | 2 / 52 | none |
| `Layout.check_ok` | component | `Flock.Layout.check` | `Flock.Layout` (verifier package) | 3 / 117 | none |
| `HmNets.check_ok` | component | `Flock.HmNets.check` | `Flock.HmNets` (verifier package) | 14 / 402 | none |
| `checkInRange_ok` | component | `Flock.checkInRange` | `Flock.Statement` (verifier package) | 2 / 3 | states 27, 1024, 64 |
| `mkRegion_ok` | component | `Flock.mkRegion` | `Flock.RowLeaf` (verifier package) | 2 / 6 | names `Flock.PT_LOCAL` (24) |

What the claims assume, and what they read:

- **Hypotheses.** `EndToEnd`, `EndToEndDrawn`, `EndToEndHidden` and `EndToEndHiddenDrawn` take five scope hypotheses:
  - `I.tags.typed = false` (untyped statements only);
  - `pub.tables = none`;
  - `Discharge.Layout.scopeOk c` (one leaf group, outNet = unitNet, unitLog ≤ 32, port reads, v1 ports);
  - `kd % nTab I = 0`;
  - `TagsOkZJ`, or `TagsOkZHJ` for Hidden (hiddenOutputs fixed, retainRounds, merkleLeaf hm96-sha512/v1).

  They also take two named assumptions, `UniformRandomBytes` and `RecordCustodyZKJ` (the record that
  `verify --zk --session-tables J` reads is the one the challenger wrote for the live session, and its draw file is the
  one `flock-verify draw` printed), plus the rate bound `rateZ … ≤ ρ < 1` and `TableCRZ` and `LinkCRZC`. The
  Registered pair drops `pub.tables = none` and adds the registered ports `own`.
- **The verifier checks none of the five scope conditions.** Typed, `pub.tables`, `scopeOk`, `nTab` and `TagsOk` have
  no hit in `backends/flock/verifier/lean`. Under the page's rule, each must become a rejection in `Flock.Zk.verify`,
  or the claim must cover those inputs.
- **The bounds are formulas.** Each bound is C(n−K₀,kd)/C(n,kd) + ksAvgStrictZ(plan …) + Σ (2t′(1+k)/2²⁵⁶ + 1/(eM) +
  k/(eRw))/(1−ρ), and 2²⁵⁶ is its only literal.
- **Reads.** The claims read 36 to 43 of the 43 verifier modules that any guarantee reads. 10 of the 25 properties read `Flock.HmRow.parse`:
  the 8 claims, `Registered.check_ok` and `Registered.opensLeaf_binding`. Each claim reads 59 parsing, decoding or
  loading definitions, and the page's rule asks for a Definitions/ twin of each. Among them are `HmRow.parse`,
  `HmRow.parseTyped`, `HmRow.loadPublic`, `HmIn.parse`, `HmOut.parse`, `HmLinks.parse`, `Net.parse`, `Program.decode`,
  `Layout.ofJson`, `CircuitType.ofJson`, `Draw.*OfJson`, `Record.decode`, `Zk.decode` and `decodeProof`.
- **Partial defs.** Each claim reads 14 of the verifier's 25 `partial def` escapes: `Flock.canon`, `Program.resolve`,
  `Program.parseParts`, `Program.Ty.ofJson`, `Program.Ty.leaves`, `Program.domainError`, the private
  `Program.composite`, `fnRefs` and `getDef`, `Qcall.cut`, `Qword.DCut.locate`, `owner` and `units`, and
  `Extract.evalDef`. `Registered.check_ok` reads `canon`. Lean gives a `partial def` no equations, so none of these can
  be proven to match a twin until it's made total.
- **Settings.** Through their definitions, the claims read 60 of the verifier's all-caps definitions, nearly all of
  them constants. Among them:
  `Zk.K_PAD` 192, `Zk.INNER_LOG_INV_RATE` 3, `Zk.RANK_SLACK` 64, `Zk.RANK_POINTS` 4, `Zk.TAU_SALT_BYTES` 192,
  `Tags.MAX_TABLES` 64, `HmRow.MAX_COMPS` 2¹⁶, `HmRow.SALT_BYTES` 192, `HmRow.ROW_SEG_BITS` 8192, `PT_LOCAL` 24,
  `Extract.WIDE_FAN_IN` 4096 and `Qcall.PARAM_MAX` 65536.
- **Components.** The Merkle and registered bindings already take the page's reduction form: two accepted openings that
  differ give a pair with different inputs and equal SHA-256 or SHA-512 outputs. That covers `merkle_binding`,
  `opens_binding`, `climb_binding`, `opensLeaf_binding`, `MerklePair.*_inputs` and `MerkleScheme.collision_hash`.
  `merkle_binding` and `opens_binding` take `ms.Sized`, a condition on the scheme rather than on the input.

### Definitions/ (25)

These are 4 net twins, `HmNets.hm96Net_get`, `HmNets.sha512x3Net_get`, `HmNets.hmLaid_eq` and `HmNets.shaLaid_eq`
(the net the verifier embeds is the one built from the reference gadget), and 21 Level3 statements that the verifier's
GF(2¹²⁸) and GF(2²⁵⁶) arithmetic and row-v2 encoding equal the mathematical ones: `F128.poly_add`,
`F128.poly_injective`, `F128.poly_mul`, `GF128.add_eq`, `GF128.inv_eq`, `GF128.mul_eq`, `GF128.xinv_mul_x`,
`GF256.add_eq`, `GF256.mul_eq`, `G_irreducible`, `Q_irreducible`, `RowV2.enc_inj`, `RowV2.packBits_length`,
`RowV2.prefix_size`, `T_xK`, `clmul_spec`, `phi_injective`, `phi_surjective`, `reduce_spec`, `toAdj_injective` and
`toAdj_surjective`.

### Models/ (26)

- `Flock.SecurityProofs.RecursiveZK` is about the firewall's release. On main, `firewallLeaf`, the commitments it is
  about, exists only in Lean (`Proofs.Flock.Recursive.Statements`). The Python firewall is
  `verity/protocols/verification/sampled_proofs/service.py`'s `Stream.deliver`, and it computes no such commitment.
- 10 statements size the sampled-proofs draw, and Python cites each: `Audit.Law.work_escape_le` (`one_stage/draw.py:24`,
  pouw `circuit/plan.py:111`), `record_sizing` and `record_sizing_one_fewer` (`plan.py:112`), `covers_window`
  (`plan.py:97`), `harm_le_unsoundWork` and `closure_escape` (`plan.py:9`), `stratified_miss_eq_greedy`
  (`verity/protocols/profile.py:346`), `Audit.audit_work_whole_stratum` (`plan.py:8`), `audit_work_floor`
  (`plan.py:181`) and `audit_window_split_of_record` (`plan.py:182`).
- 2 are cited only from experimental/, by `consumers.py`: `Audit.Partition.audit_exfiltration` and
  `card_admissible_le`. Whether that makes them guarantees is open.
- 13 are `Audit.Partitioning.SecurityProofs.*`, the choice of partition and law for the sampled audit:
  `Achievability`, `Concentration`, `ConverseAsymptotic`, `ConverseExact`, `ExfiltrationOptimum`, `GranularityChoice`,
  `GranularityOptimum`, `HeavyUnit`, `NestedEscape`, `RefinementRule`, `RiskConcave`, `UnequalCost` and `UnequalDraws`.

### out (805)

- 716 internal lemmas of the soundness or ZK proof.
- 35 Level3 lemmas.
- 38 non-vacuity witnesses or instance checks, 28 of them kept by #1170 (listed in §3).
- 11 VBridge gadget soundness statements, which feed RecursiveSound's named assumption `Flock.Assumptions.VBridge`.
- 3 `table_sound*`. Table 1 cites these (`verity_numerical/bench/views.py:222, :386, :402, :418`), so its cells have to
  re-point to a numeric corollary of EndToEnd first.
- 2 `*_refSetup`.

## 3. Rule conflicts

### Hash properties taken as hypotheses

70 rows are flagged (C-Flock 68, PoUW 2), plus two Core assumptions. They take four shapes:

- **C-Flock's CR hypotheses are per finder.** `TableCRZ` and `LinkCRZC` ask `SHA512CRStrict` or `SHA512CRExpected` only
  of the finders built from the prover being bounded. LinkCRZC's docstring says "A2 is a hypothesis about one finder,
  since some finder outputs a collision after no evaluations". `Teeth.not_strict_const` and `not_expected_const` show
  that both fail for a constant hash. So the page's objection ("a program that just prints it wins") doesn't apply, but
  they are still hypotheses. The page's form would move the finders' collision probability into the bound.
- **Hiding and uniformity of a fixed function** (`HashDerivedKeyHm96`, `Hm96Hiding`, `KeyedStreamsUniform`) aren't
  collision resistance and can't be reduced to a SHA-512 collision. The page has no rule for them. hm96 §3 shows that
  hiding fails for at most 2⁻⁶⁴ of keys; the assumption is that the pinned key isn't one of them.
- **`AdviceBinding`** (`Specs.Core.Assumptions`) is `Function.Injective` of the advice root over every partition of
  every size. It's false for a hash into a fixed-size digest, so it is vacuous in the page's sense. Only
  `PrivatePartition`'s `RegisteredMeets` takes it, and no listed guarantee does.
- **Idealizations.** `RowDrawn` and `FragDraw` are in the leads' review, and so is `LmsEufCma`.

Each name, by hypothesis (names without a prefix are under `FlockSoundness.`):

- `TableCRZ` (SHA512CRStrict, q²/2^513, at each table's knowledge finders), 31:
  - `Flock.SecurityProofs.EndToEnd` (Properties)
  - `Flock.SecurityProofs.EndToEndDrawn` (Properties)
  - `Flock.SecurityProofs.EndToEndHidden` (Properties)
  - `Flock.SecurityProofs.EndToEndHiddenDrawn` (Properties)
  - `Flock.SecurityProofs.EndToEndRegistered` (Properties)
  - `Flock.SecurityProofs.EndToEndRegisteredDrawn` (Properties)
  - out: `Discharge.Composed.zk_session_composed`, `Discharge.Composed.zk_session_sound`, `Discharge.Composed.zk_session_soundJ`, `Discharge.Composed.zk_session_soundJ_custody`, `Discharge.Composed.zk_session_soundJ_custody_json`, `Discharge.Composed.zk_session_sound_custody`, `Discharge.ZkBind.zk_flock_countC_execOS_at`, `Discharge.ZkBind.zk_flock_countC_execOS_keyProg`, `Discharge.ZkHidden.zk_flock_countC_execOS_crH`, `Discharge.ZkHidden.zk_session_composedHJ`, `Discharge.ZkHidden.zk_session_soundH`, `Discharge.ZkHidden.zk_session_soundHJ`, `Discharge.ZkHidden.zk_session_soundHJ_custody`, `Discharge.ZkHidden.zk_session_soundHJ_custody_json`, `Discharge.ZkHidden.zk_session_soundH_custody`, `Discharge.ZkLink.ksAvgZC_le_strict`, `Discharge.ZkLink.ksBoundAccZ_le_strict`, `Discharge.ZkLink.zk_flock_countC_execOS_cr`, `Discharge.ZkLink.zk_flock_countC_execOS_m1_cr`, `Discharge.ZkLink.zk_flock_countC_execOS_strict`, `Discharge.ZkReg.zk_session_soundHJR`, `Discharge.ZkReg.zk_session_soundHJR_custody`, `Discharge.ZkReg.zk_session_soundHR`, `Discharge.ZkReg.zk_session_soundHR_custody`, `Discharge.ZkReg.zk_session_soundR`
- `LinkCRZC` (SHA512CRExpected at the link finders), 6:
  - `Flock.SecurityProofs.EndToEnd` (Properties)
  - `Flock.SecurityProofs.EndToEndDrawn` (Properties)
  - `Flock.SecurityProofs.EndToEndHidden` (Properties)
  - `Flock.SecurityProofs.EndToEndHiddenDrawn` (Properties)
  - `Flock.SecurityProofs.EndToEndRegistered` (Properties)
  - `Flock.SecurityProofs.EndToEndRegisteredDrawn` (Properties)
- `Fork.CR H512 q` (strict CR per fork), 1:
  - `Flock.SecurityProofs.RecursiveSound` (Properties)
- `SHA512CRStrict` taken directly, 9:
  - out: `CROnly.expected_of_strict`, `Registered.TwoOpenings.conflict_strict`, `Teeth.not_strict_const`, `Teeth.strict_of_injective`, `ZK.GK.Model.gk_simulate`, `ZK.GK.Model.gk_simulate_coins`, `ZK.GK.Model.gk_simulate_coins_keyed`, `ZK.GK.gk_simulate_avg`, `ZK.GK.gk_simulate_hm96`
- `SHA512CRExpected` taken directly, 2:
  - out: `Teeth.expected_of_injective`, `Teeth.not_expected_const`
- `HashDerivedKeyHm96` (the pinned hm96 key hides at 2^-193), 8:
  - `Flock.SecurityProofs.RecursiveZK` (Models)
  - `Flock.SecurityProofs.ZeroKnowledgeHidden` (Properties)
  - out: `Discharge.Composed.zk_session_composed`, `Discharge.Composed.zk_session_view`, `Discharge.ZkEveryCoin.zk_session_view_all`, `Discharge.ZkHidden.zk_session_composedHJ`, `Discharge.ZkHidden.zk_session_viewH`, `Discharge.ZkHidden.zk_session_viewHJ`
- `Hm96Hiding` at δ₁ (the fixed hm96 hash at a key), 14:
  - out: `CROnly.hm96Hiding_gap`, `CROnly.hm96_sha512_bad_keys`, `Discharge.ZkSession.coinLeaf_fresh`, `Discharge.ZkSession.coin_fresh`, `Discharge.ZkSession.coin_fresh_key`, `ZK.GK.gk_simulate_hm96`, `ZK.GK.prefinalClose_hm96`, `ZK.GK.rewindClose_hm96`, `ZK.Session.adaptive_prefinal_hm96`, `ZK.Session.adaptive_prefinal_hm96_tape`, `ZK.Session.session_shvzk_hm96`, `ZK.Table.table_shvzk_hm96`, `ZK.ideal_leaf_swap`, `ZK.ideal_leaves_swap`
- `KeyedStreamsUniform` (the fixed keyed SHA-512 derivation's streams are uniform), 6:
  - out: `Audit.Law.keyedWindowReg_audit_of_record`, `Audit.Law.keyedWindowReg_extraction_audit_of_record`, `Audit.Law.keyedWindow_audit_of_record`, `Audit.Law.keyedWindow_escape_le`, `Audit.Law.keyedWindow_escape_le_of_names`, `Audit.Law.keyedWindow_extraction_audit_of_record`
- `PearlCSem.RowDrawn` (row leaf's CR idealized as an injective key), 2:
  - `Pouw.SecurityProofs.PearlC.TTOutRowSeedSkipClass` (Models)
  - out: `Pouw.PearlC.rowDrawn_satisfiable`
- `Assumptions.FragDraw` (per-row draw idealized), 1:
  - `Pouw.SecurityProofs.PearlC.TTOutRowSeedSkipClass` (Models)


### Completeness: 13 listed, all out

10 have "complete" in their names, and 3 are in `Proofs.Flock.Soundness.ZK.Complete`. None is cited:

- `FlockSoundness.Discharge.Composed.Lincheck.lincheck_complete` (Proofs.Flock.Soundness.Discharge.Composed.Inner.Lincheck; out)
- `FlockSoundness.Types.compose_complete` (Proofs.Flock.Soundness.Types.Flat; out)
- `FlockSoundness.ZK.Table.inner_complete` (Proofs.Flock.Soundness.ZK.Complete; out)
- `FlockSoundness.ZK.padColumn_honest` (Proofs.Flock.Soundness.ZK.Complete; out)
- `FlockSoundness.ZK.padOnto_M1` (Proofs.Flock.Soundness.ZK.Complete; out)
- `FlockSoundness.ZK.padsOnto_monomial` (Proofs.Flock.Soundness.ZK.Complete; out)
- `Pouw.NCP.GameProofs.leadComplete` (Proofs.Pouw.NCP.GameProofs; out)
- `Pouw.NCP.RouteUProofs.leadCompleteU` (Proofs.Pouw.NCP.RouteUProofs; out)
- `Pouw.PearlC.completeSampledDevRev1K` (Proofs.Pouw.PearlC.Completeness; out)
- `Pouw.PearlC.pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_llama31_8b` (Proofs.Pouw.PearlC.Completeness; out)
- `Pouw.PearlC.pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b` (Proofs.Pouw.PearlC.Completeness; out)
- `Pouw.Proofs.d1Complete` (Proofs.Pouw.Exact; out)
- `Pouw.Proofs.honestComplete` (Proofs.Pouw.Witness; out)


More completeness that isn't listed:

- `CompleteSampled`, in `Definitions.Pouw.PearlC.Completeness` (in the leads' review).
- `Pouw.Pinned.D1Complete` and `HonestComplete`, the statements `d1Complete` and `honestComplete` prove.
- `Specs.Core.Guarantees.TC`'s `AmpereStepComplete`, `HopperStepComplete` and `PackSoundComplete`.
- `Assumptions.PearlC.HonestCap.HonestTileCapRate`, completeness's assumption.

One borderline case: `P2ErrorSplitB19Uncond`, `P2SlackB19Uncond` and `P2SlackFamilyUncond` include `sch.Correct`, the
decoder's correctness, as a conjunct. That's correctness, not honest acceptance.

Three statements mention completeness but aren't completeness, since they only take it as a hypothesis:
`NetTiming…EncardIngressObsDecodableLe` takes `StatusComplete`, and `Pouw.Sanity.tt_admitsRef_bound` and
`tt_false_of_gamma0_ge_one` take `P.Complete D`.

### Non-vacuity witnesses and instance checks: 129 (PoUW 91, C-Flock 38)

A `*` marks a name #1156 or #1170 keeps, or one that's lifted. Names without a prefix are under `FlockSoundness.`:

- `Audit.InfluenceWitness.A` (2): `accepts`, `influence`
- `Audit.InfluenceWitness.Ex` (1): `exfil`
- `Audit.InfluenceWitness.Gen` (1): `harm_witness`
- `Audit.InfluenceWitness.Two` (2): `accepts`, `influence`
- `Audit.InfluenceWitness.W` (3): `count`, `lemma47`, `three_mem_exits`
- `Audit.Partitioning.Witness` (11): `achievability`\*, `concentration`\*, `converse`\*, `exfiltration`\*, `granularity`\*, `heavyUnit`\*, `nestedEscape`\*, `refinement`\*, `riskConcave_needs_k_two`\*, `riskConcave_needs_small_p`\*, `unequal`\*
- `Discharge.Composed` (8): `drawSetupZK_whole_empty_16_2_1`\*, `e2e_forces_mPts`\*, `mPtsOf_16_8`\*, `mPtsOf_16_ne_8`\*, `y0_binder_16_2_1`\*, `zk_session_soundJ_custody_json_nonvacuous`\*, `zk_session_soundJ_custody_nonvacuous`\*, `zk_session_soundJ_nonvacuous`\*
- `Discharge.ZkHidden` (7): `drawSetupZKH_whole_empty_16_2_1`\*, `y0_binderH_16_2_1`\*, `zk_session_composedHJ_nonvacuous`\*, `zk_session_soundHJ_custody_json_nonvacuous`\*, `zk_session_soundHJ_custody_nonvacuous`\*, `zk_session_soundHJ_nonvacuous`\*, `zk_session_viewHJ_nonvacuous`\*
- `Discharge.ZkReg` (2): `zk_session_soundHJR_custody_nonvacuous`\*, `zk_session_soundHJR_nonvacuous`\*
- `ZK.Session` (1): `sent_admits`
- `Pouw.Barrier.Proofs` (5): `additiveWitness`, `genericWitness`, `relationAdmits`, `relationWitness`, `tablesAffineWitness`
- `Pouw.Dimension` (18): `a1CostWitness`, `a1W1Witness`, `a1Witness`, `a2Witness`, `a2Witness4090`, `a2WitnessPipe`, `a2WitnessQuad`, `alg4090Witness`, `algWitness`, `algWitnessCausal`, `causalWitness`, `liftMinRankL5eWitness`, `liftMinRankWitness`, `minRank2Witness`, `minRankGeWitness`, `pipeChainConsistent`, `pipeWitness`, `pipeWordWitness`
- `Pouw.Dimension.A2Words` (1): `a2WitnessExtra`
- `Pouw.Dimension.Embed` (2): `m4090ChainConsistent`, `nanGapConsistent`
- `Pouw.Dimension.Forest` (2): `quadChainConsistent`, `quadChainConsistentTight`
- `Pouw.Dimension.H100` (2): `denseLaneWitness`, `mh100WordsConsistent`
- `Pouw.Dimension.OpenPipe` (2): `openPipeWitness`, `openQuadChainConsistent`
- `Pouw.Dimension.RouteUProofs` (6): `a1CostWitnessU`, `alg4090WitnessU`, `algWitnessU`, `algWrappedWitnessU`, `pipeChainConsistentU`, `pipeWitnessU`
- `Pouw.Fp8Atom.H1T.Proofs` (1): `h1tNonVacuous`
- `Pouw.NCP.ChainProofs` (1): `leadIndWitness`
- `Pouw.NCP.GameProofs` (2): `leadWitness`, `ttncpWitness`
- `Pouw.NCP.Proofs` (1): `signedPermWitness`
- `Pouw.NCP.RelationWitness` (1): `relationFreeWitness`
- `Pouw.NCP.RouteUProofs` (1): `leadUWitness`
- `Pouw.NCP.WordProofs` (2): `wordFinalWitness`, `wordNzWitness`
- `Pouw.PearlC` (4): `rowDrawn_satisfiable`, `ttOutPearlCH100Rev1Witness`, `ttOutPearlCWitness`\*, `ttOutTilePearlCH100Rev1Witness`
- `Pouw.Proofs` (3): `copyNzWitness`, `gameCanBeLost`, `ttWitness`
- `Pouw.Sanity` (31): `Wmm_eq_zero`, `Wref_eq_zero_of_Wmm`, `Y_last`, `blockEnd_full`, `blockEnd_last`, `certified_le`, `checkIdx_depth_zero`, `copy_zero_noise`, `default_pos`, `fullGroups_inDomain`, `identical_checked`, `index_collision`, `lone_unit_over_budget`, `milestone_hypotheses_consistent`, `noisedAct_rank_zero`, `omega_lt_inv_one_sub`, `pr_of_isEmpty`, `randomized_of_deterministic`, `reductionGamma_lt_of_omega_lt_one`, `rowShare_covers`, `single_unit_not_inDomain`, `transcript_indep_of_q_zero`, `tt_admitsRef_bound`, `tt_event_empty`, `tt_false_depth_zero`, `tt_false_of_gamma0_ge_one`, `tt_false_rank_zero`, `tt_false_zero_noise`, `wins_T_zero_iff`, `wins_empty`, `wins_of_gamma_ge_one`
- `Pouw.SecurityProofs.NCP` (2): `IndependentWitness`\*, `TTNCPUWitness`\*
- `Pouw.TileBound` (4): `realizesAt_nonvacuous`, `support_admits_openAt`, `support_admits_open`\*, `tile_chain_satisfiable`


### Settings

- `Flock.mkRegion_ok` names `Flock.PT_LOCAL` in its statement.
- The 8 claims read 60 all-caps verifier definitions, nearly all constants, through their definitions (§2). Whether "reads a setting" means the
  statement's own text or the closure of the definitions it reads decides whether all 8 are refused.
- The 7 PoUS P2 guarantees read spec constants (`Params.ρ`, `δ`, `expansion`, `εMax`), which is no conflict. The PoUW
  and certifier Models state their numbers in the spec too: Lean can't read a Python setting.

### Scope hypotheses

The 8 C-Flock claims take them, as listed in §2. No Models row was checked for scope; the page's rule binds core/.

## 4. What retiring `lean-audit.json` drops

| key | today | read by | what the page relies on it for |
|---|---|---|---|
| `guarantees` | 1,705 (Security) and 7 (verifier): owner, signature, named assumptions, type hash | `tools/lean/audit.py` 859–885 (statement hash, closed named assumptions, `four_names`); `tools/research/src/research/spec_alert.py` 43–55 and `merge.py` 1222–1283 (Daniel's DM) | "confirms every property has a proof"; "messages Dan with each changed property before and after" |
| `reads` | 538 modules in Security (Proofs 339, Definitions 90, Specs 66, Flock 43) and 16 in the verifier: each definition's hash and its readers | `audit.py` 905–928 and 1041; `spec_alert.py` 48–55 | the alert's changed definitions: the only place a weakened definition shows (in the leads' review) |
| `layers` | 25 rules in Security, 1 in Proofs | `audit.py` 840 | "Imports point one way"; Lake doesn't enforce it (in the leads' review) |
| `meaning` | 26 module prefixes in Security; `[Flock]` in the verifier | `audit.py` 683 and 976–989 | which modules count as spec, the basis of "Properties/ reads core/ only through the function a property is about" |
| `reads_exempt` | 15 in Security (11 C-Flock, 4 PoUW), 1 in the verifier (`Flock`) | `audit.py` 976–989 | C-Flock's exception ("excepted until proofs extracts its spec", Daniel, 4 Oct 1:30 PM PDT); without it the 874 C-Flock rows and 4 PoUW modules fail the read check |
| `assumptions` | 30 modules | `audit.py` | "Write its assumptions into it": a named `Prop` in an assumptions module, taken as a hypothesis |
| `four_names` | `Nci`, `NetTiming` | `audit.py` 885 (`four_named`, 1150) | `X.SecurityProofs.G : X.Guarantees.G` |
| `escapes` | 25 `partial def`s in the verifier, 1 `@[extern]` in the PoUS grader | `audit.py` 823 | the page's "short list kept in Definitions/" of externs |
| `runs` | 2 (`Proofs.Pouw.Bulk`, `Proofs.NetworkCertifier.DifftestMain`) | `audit.py` 1384 and 1434; the certifier's `difftest_vectors.py`, pouw's `fp8atom_vectors.py` | the certifier's model-versus-Python check (in the leads' review) |
| `dependencies` | 9 Lean packages in Security, 14 in Proofs | `audit.py` 1550–1556 | "a change to the Lean version or the pinned Lean libraries is treated like a change to what we claim"; `spec_alert` doesn't diff it today |
| `exempt`, `compile_time`, `upstream` | Proofs: 5 exempt modules, 1 compile-time tactic, 3 upstream watches; PoUS: `submissions` | `audit.py` 832, 369 and 609, 1543 | what is a test rather than a proof; `tools/lean/upstream.py` |

Readers of `lean-audit.json` besides `audit.py` and `spec_alert`:

- `verity/protocols/accounting/space/pous/tests/test_pous_protocol.py:300`: each PoUS claim cites a guarantee.
- `verity/protocols/accounting/work/pouw/tests/test_lean_package.py`.
- `benchmarks/pouw/harness/price_twins.py:50` (`REPO_AUDIT`), `price_twins.json` and `benchmarks/pouw/tests/test_exhaustion.py`.
- The certifier's `tests/test_network_certifier_lean_difftest.py` and `lean/scripts/difftest_vectors.py`; pouw's
  `lean/scripts/fp8atom_*`.
- `tools/check/`: `check.py`, `declaration.py`, `move_check.py`, `train.sh`, `pyproject.toml` and its tests.
- `tools/lean/`: `cache.py`, `lean_audit.py`, `lean_changed.py`, `merge.py`, `upstream.py` and their tests.
- `tools/move/`: `layout.py`, `lean.py`, `rename.py` and `rename_map.toml`.
- `tools/research/src/research/`: `merge.py`, `queue.py`, `jobs/cli.py`, `jobs/dispatch.py`, `jobs/trains.py` and
  `store/vocab.py`.
- `tests/test_lean_packages.py` and `tests/test_repository.py`.

## Five facts the move needs

1. **PoUS's grader hard-codes Security's location.** `TRUSTED.sha256` pins 44 Security files as
   `../../../../../Security/…`, which resolves to `verity/Security/`: 32 of `Definitions/Pous`, 5 of `Specs/Pous`, 2 of
   `Proofs/Pous`, and Security's and Proofs' lakefiles, manifests and toolchain. `grade.sh` builds the trusted layer in
   `verity/Security/Proofs`, `check.sh` verifies `TRUSTED.sha256`, and `Grader/Registry.lean` names 73
   `Pous.Guarantees.*`. A move to `Security/` changes every one of these paths.
2. **Claims are stated in all three trees.** PoUW's 154 Models rows are stated in `Proofs.Pouw` (98), Specs (53) and
   `Definitions.Pouw` (3), and 159 out PoUW statements sit in `Specs.Pouw.Assumptions.*`. Moving `Definitions/` or
   the assumptions modules wholesale carries claims with them. The art gives each row's stating module.
3. **C-Flock's Properties/ is extracted from Proofs/, not moved from Specs/.** The 8 claims are stated in
   `Proofs.Flock.*/Statement(s).lean`, and the 17 components in `Proofs.Flock.Verifier.*` (12) and the verifier package
   (5). Their twins would be most of the verifier: 42–43 modules, 59 parsers, and 14 `partial def`s that must be made
   total first.
4. **Only 254 of the 1,712 aren't out**: 25 Properties, 196 Models, 25 Definitions and 8 unforced. Every out that
   rests on "nothing cites it" depends on #1156 and #1170, both open.
5. **`lean-audit.json` has about 30 readers outside `audit.py` and `spec_alert`** (§4), across `tools/check`,
   `tools/lean`, `tools/move`, `tools/research`, two protocol test suites, the PoUW benchmarks and the certifier's
   difftest. Retiring it means re-pointing each one.

## Where the page and the tree disagree

These are beyond the leads' review. Page: Security (Notion `3f1399515d9e8152b350d48711b7704b`, draft of 7 Oct).

1. **Introduction, "every part of it has proven properties."** The verifier's 25 `partial def`s are recorded as "no
   proof is about it, and the agreement tests cover it" (`backends/flock/verifier/lean/lean-audit.json`, `escapes`), and
   14 of them sit inside every C-Flock claim. The PoUS grader has no listed property at all
   (`verity/protocols/accounting/space/pous/lean/lean-audit.json`).
2. **Status, "C-Flock is the exception: its verifier is already Lean"**, against Writing a property, "No scope
   hypotheses." Every C-Flock claim takes untyped-only, `scopeOk`, `nTab` and `TagsOk`, four take `pub.tables = none`,
   and the verifier checks none of them (`verity/Security/Proofs/Flock/EndToEnd/Statement.lean` and its siblings).
3. **Writing a property, "state the actual number."** C-Flock's bounds are formulas over n, kd, K₀ and the plan (the
   same files).
4. **Writing a property, "Properties/ reads core/ only through the function a property is about."** Each claim reads
   1,550 to 1,745 verifier definitions in 36 to 43 modules, and `meaning` lists the whole verifier (`Flock`) as spec
   (both locks).
5. **Introduction, "every guarantee is about the code that runs."** C-Flock's claims assume `RecordCustodyZKJ` about
   the live session's record and draw file (`verity/Security/Proofs/Flock/Soundness/Assumptions/Zk.lean`). RecursiveZK
   is about commitments (`firewallLeaf`) that no code on main computes
   (`verity/protocols/verification/sampled_proofs/service.py`).
6. **Writing a property, "Never assume a hash function is collision-resistant … a program that just prints it wins."**
   C-Flock's CR hypotheses are per finder, which escapes that objection (LinkCRZC's docstring,
   `Teeth.not_strict_const`). Hiding and uniformity of fixed functions (`HashDerivedKeyHm96`, `Hm96Hiding`,
   `KeyedStreamsUniform`) can't be reduced to a collision at all, and the page has no rule for them.
7. **What runs is what's proven, "a short list kept in Definitions/ … the only places core/ may use `@[extern]` or
   `@[implemented_by]`."** Today that list is each package's `escapes`, and it holds the PoUS grader's extern
   `setMaxMemory` (`Grader/Main.lean:27`), which sets Lean's memory limit rather than touching the outside world.
8. **What runs is what's proven, "a change to the Lean version or the pinned Lean libraries is treated like a change to
   what we claim"**, and Changes, "as spec_alert does today." `spec_alert` diffs only `guarantees` and `reads`
   (`tools/research/src/research/spec_alert.py` 43–55), not `dependencies`, so a toolchain or Mathlib bump sends no
   alert today.
9. **What runs is what's proven, "core/ never imports Security/."** The PoUS grader imports only Lean, but at run time
   it loads Security's compiled `Pous.Guarantees` and pins 44 Security files by path (`TRUSTED.sha256`, `grade.sh`).
