---
id: 20261007T0401Z-report-pouw-models-list
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: danielreuter/verity
origin: compute-accounting worker bc-1a0cff8a-efe2-568f-bfe5-d91d752c5815
---

# PoUW's guarantees under the draft Security layout, and what PoUW's verifier needs to enter core/

Read at `origin/main` dcc929336. Its `verity/Security/lean-audit.json` and the PoUW, Security and C-Flock verifier
paths are the same as at f5360e4e1, where the reading began. The layout is the Notion draft "Security" (7 Oct,
https://app.notion.com/p/3f1399515d9e8152b350d48711b7704b). It has four directories:

- `Definitions/`: what things mean.
- `Properties/`: what a `core/` function guarantees.
- `Proofs/`: why each property holds.
- `Models/`: Lean models of verifiers that still run as Python, and their properties.

This note sorts what exists today. It proposes no redesign.

## 1. The guarantees

`lean-audit.json` lists 807 guarantees under `Pouw.`. Every one of them is a theorem in a file under
`verity/Security/Proofs/Pouw/`. Each is put in one of four classes:

- **Models/**: a statement about an audit that a Python verifier runs:
  - `verity.protocols.accounting.work.pouw.audit.Verifier`;
  - `schemes/pearl_c_work.audit` (Pearl-C and Pearl-C4);
  - `ncp-v1` through `audit.Verifier`;
  - for the deadline, the hidden audit and the completeness theorems, the Python named at those items.
- **Models/, completeness**: an audit's completeness. The draft does not require completeness, but existing
  completeness theorems may stay.
- **D1, no verifier**: a statement about protocol D1's audit. No registered scheme implements D1
  (`schemes.SCHEMES` has `ncp-v1`, `ncp-v1-shift24`, `pearl-fp8-v4`, the `pearl-c-h100-*` schemes, `pearl-c-sm120-v1`
  and `pearl-c-nvfp4-v0`). So these are properties of no running verifier.
- **Proofs/ lemma**: not a property of any verifier. It stays a lemma in `Proofs/`. The vocabulary and named
  assumptions it reads are already `Definitions/` and `Specs/` material, as noted per group.

| group | count | Models/ | completeness | D1 | Proofs/ lemma |
|---|---:|---:|---:|---:|---:|
| PearlC | 395 | 300 | 3 | 0 | 92 |
| Dimension | 154 | 0 | 0 | 0 | 154 |
| TileBound | 63 | 0 | 0 | 0 | 63 |
| SecurityProofs | 47 | 21 | 0 | 0 | 26 |
| NCP | 42 | 2 | 0 | 0 | 40 |
| Fp8Atom | 41 | 0 | 0 | 0 | 41 |
| Sanity | 31 | 0 | 0 | 0 | 31 |
| Proofs | 20 | 0 | 0 | 3 | 17 |
| Barrier | 10 | 0 | 0 | 0 | 10 |
| AlignedExact | 4 | 0 | 0 | 0 | 4 |
| **total** | **807** | **323** | **3** | **3** | **478** |

### Groups that are all one class (Proofs/ lemmas)

- **Dimension (154)**: `Proofs/Pouw/Dimension/*Proofs.lean` and `Lifting.lean`. These cover Theorem D, the A1 and A2
  routes and the H100 machine facts. Their machine and pipeline models are `Definitions/Pouw/Dimension/`, and their
  named assumptions `Specs/Pouw/Assumptions/Dimension/`. They are hardness analysis behind the TT assumptions, and no
  verifier reads them.
- **TileBound (63)**: the slot model's bounds (`Proofs/Pouw/TileBound/{Fp8,Fp8Depth,Proofs,WinogradStrassen,Witness}.lean`).
  The model is `Definitions/Pouw/TileBound/`.
- **AlignedExact (4)**: counting lemmas (`Proofs/Pouw/TileBound/AlignedExact.lean`).
- **Fp8Atom (41)**: the floating-point atom models and the H1T facts (`Proofs/Pouw/Fp8Atom/`). The models are
  `Definitions/Pouw/Fp8Atom/`, and the assumptions `Specs/Pouw/Assumptions/Fp8Atom/`.
- **Barrier (10)**: `Proofs/Pouw/Barrier/Proofs.lean`, the barrier classes and their witnesses. The vocabulary is
  `Definitions/Pouw/Barrier/`.
- **Sanity (31)**: non-vacuity and consistency checks (`Proofs/Pouw/Sanity.lean`).

### PearlC (395)

**Models/ (300)**: every theorem in these files whose name starts `pearlCGamma`, `pearlCSampled` or `pearlCHidden`,
plus `gammaHidden_of_sampled_all`. By statement:

- **148 are `Gγ`** (`Definitions/Pouw/PearlC/Game.lean`): the work law's credit rule with every unit checked. Each is
  at one device record, cap and shape (8192³, 16384³, the served shapes `n24576k4096` and so on, `qwen3_8b`,
  `llama31_8b`).
- **148 are `GγSampled`** (`Definitions/Pouw/PearlC/Tile.lean`): the sampled tile audit, as
  `pearl_c_work.audit`/`check_drawn` and `audit.Verifier.check_tile` run it.
- **4 are `GγHidden`** (`Definitions/Pouw/PearlC/Hidden.lean`): `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192`,
  `pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCap1000_8192`, `pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCodeCap1000_8192`
  and `gammaHidden_of_sampled_all`.
  - Their verifier is not in the core Python. It is `benchmarks/pouw/served_zk/served_commit.py` `check`, plus the
    Lean C-Flock verifier for each tile's proof.
  - Each is generic in `HA : HiddenAudit`. No C-Flock `HiddenAudit` instance exists in Lean.
  - They take `TileProofSoundAll` (`Specs/Pouw/Assumptions/PearlC/HiddenTile.lean`) as a hypothesis. That is an open
    obligation, not an assumption.

The protocol each statement models:

- the Pearl-C device records (`pearl-c-h100-*`, `pearl-c-sm120-v1`): `DeviceRev1`, `DeviceKernelWref` and the
  `Sm120` files;
- Pearl-C4 (`pearl-c-nvfp4-v0`): `pearlC{Gamma,Sampled}Fp4*`;
- the U-only reading (`schemes/pearl_c_u.py`): the `*UOnly*` statements.

Per file, the Models/ count is:

- `CapLoopGamma` 8, `ChainCapKernelGamma` 6, `ChainCapLoopGamma` 4, `ChainOnlyGamma` 4, `DeviceCapGamma` 8;
- `DeviceCapRev1Gamma` 6, `DeviceChainCapGamma` 4, `DeviceFp4Gamma` 2, `DeviceRev1Gamma` 6, `DeviceSm120CapRev1Gamma` 8;
- `DeviceSm120Gamma` 16, `DeviceSm120KernelGamma` 120, `DeviceSm120LoopGamma` 16, `Fp4ChainOnlyGamma` 6;
- `Fp4HotGamma` 10, `Fp4IssueGamma` 8, `Gamma` 2, `HiddenGamma` 2, `KernelWrefGamma` 4, `RowSeedGamma` 10;
- `RowSeedKGamma` 7, `ServedMixedRev1Gamma` 8, `ServedRev1Gamma` 24, `TileCapRev1Gamma` 3, `TileUOnlyGamma` 2;
- `UOnlyGamma` 2, `UOnlyLoopGamma` 4.

**Models/, completeness (3)**: `completeSampledDevRev1K`, `pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b` and
`pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_llama31_8b` (`Completeness.lean`, `CompleteSampled`). Each rests on
`HonestTileCapRate`. Its measurement is still cited as `art:<pending: FP8 served table>`
(`Specs/Pouw/Assumptions/PearlC/HonestCap.lean`, lines 50 and 76). That table is
`art:d660922ddc61879c999d6d397e85a2128bedc57dbef034b98ed3979e921bfc13` (#1001), rebuilt as
`art:e9e8ba3976f8061f2655c6900cf5b948ccca7b0ac804b0a9f4d064315c6f3d93` (#1183). Both are PRESERVED.

**Proofs/ lemmas (92)**: none of these states what a verifier accepts.

- **Implications between named assumptions (TT_OUT forms)**:
  - `ttOut*_of_*` and `ttOutTile*_of_*`: `ChainOnly`, `Fp4ChainOnly`, `ChainCap_of_cap`, `Rev1_of_granted`,
    `Rev1_of_uOnly`, `RowSeedCode_of_ttOut`, `TileRowSeedCode_of_ttOutTile`, `ttOut_of_ttOutRowSeed` and
    `ttOutTile_of_ttOutTileRowSeed`;
  - `*_cap_anti`, `ttOutTilePearlCDevRev1_cap_transfer`, the eight `*_sm120v2_loop` equivalences, `ttOut_wref`,
    `ttOutTile_wref`, `ttOutRowSeed_code`, `ttOutTileRowSeed_code`, `ttOutPearlCDev_h100` and
    `ttOutTilePearlCDev_h100`.

  The assumptions themselves are `Specs/Pouw/Assumptions/PearlC/` (`TTOut*`, `TTOutRowSeed*`, `TTOutUOnly`, `HonestCap`
  and `HiddenTile`).
- **Witnesses of satisfiability**: `ttOutPearlCWitness`, `ttOutPearlCH100Rev1Witness`, `ttOutTilePearlCH100Rev1Witness`,
  `pearlCTilesDevRev1_total`, `rowDrawn_satisfiable` and `pearlCShapeFp4_headline`.
- **Facts about a record or a domain** (vocabulary in `Definitions/Pouw/PearlC/Device*.lean`): `devAt_hopper`,
  `devAt_sm120_floor`, `devAt_rowLocal`, the `devSm120v1*`/`devSm120v2*` `_domain`, `_domain_row` and `_flags` lemmas,
  `pearlCDomainDev_split`, `pearlCDomainDev_unpromoted`, `creditDevRev1_h100`, `chainCap_flagged_le`, `sm120Issue_eq`
  and `rowCap_agg`.
- **γ's numeric value at a record** (30 lemmas, `gammaFp4*`, each `gammaFp4… d … sh = <rational>`):
  `Fp4IssueGamma` 6, `Fp4HotGamma` 16 and `Fp4ChainOnlyGamma` 8. The γ they compute enters the Models/ statements as a
  number.
- **Probability and relabelling lemmas**: `pr_comp_equiv`, `qtree_union_bound`, `fragSkip_count_le` and
  `fragSkip_saving_le`.
- **Implications between audit statements**: `gammaSampledU_implies_gammaSampled` (`GγSampledU` → `GγSampled`).
- **The hidden audit's batch step**: `tileProofSoundAll_of_tileGame`. This is a reduction toward the open obligation,
  not a verifier property.

### SecurityProofs (47): the `Specs/Pouw/Guarantees/` statements

**Models/ (21)**:

- **`Game`**: `Theorem1`, `WorkWeightedSampling`, `EndToEnd` and `GammaFromTT`.
  - These are generic over the integer game.
  - `WorkWeightedSampling` is cited in the certificates of `pearl-c-*` and `pearl-fp8-v4`. All four are cited in
    `ncp-v1`'s certificate (`schemes/pearl_c.py`, `schemes/pearl_kw.py` and `schemes/ncp.py`, `Certificate.theorems`).
  - `audit.WorkProfile` states `EndToEnd`.
- **`Deadline`**: `WorkBetweenSaltAndDeadline`, `SpareCapacityAtDeadline`, `PearlCSampledByDeadline` and
  `PearlCSm120Rev1Cap1000ByDeadline_{8192,16384,qwen3_8b,llama31_8b}`.
  - The deadline rule is in no core verifier.
  - It is checked only by `benchmarks/pouw/exhaustion/audit.py`.
- **`PearlC`**: `GammaSm120v1LoopCast8p72Rev1Cap1000_{8192,16384}`, `SampledSm120v1LoopCast8p72Rev1Cap1000_{8192,16384}`,
  `GammaFp4Sm120_{8192,16384}` and `SampledFp4Sm120_{8192,16384}`.
- **`NCP`**: `GammaFromTTNCP_U_v1` (cited by `ncp-v1`) and `GammaFromTTNCP_U_C2`.

**Proofs/ lemmas (26)**:

- `Barrier.Generic` and `Dimension.A2WordsIff`.
- The NCP identities: `Cancel`, `Stacked`, `Range`, `RangeU`, `WrapU`, `BiasU8Iff`, `CheckedUEq`, `CheckedUFinal`,
  `MmWUExact`, `YUChecked`, `Int7Int32UPos`, `NCPWordFloorIndU`, `WrapFinalOnlyIndU`, `WrapWordFloorIndU`, `TTNCPUIff`,
  `ShiftBy24Admissible`, `IndependentWitness` and `TTNCPUWitness`.
  - `ncp-v1`'s certificate lists all but `Range` and `BiasU8Iff` among its theorems.
  - They are arithmetic identities and witnesses behind `GammaFromTTNCP_U`, not statements of what the audit accepts.
- `PearlC.GammaFp4Sm120LoopLut256_{8192,16384}`: γ's numeric value.
- `PearlC.GammaUImpliesGamma`: `GγU` → `Gγ`.
- `PearlC.TTOutRowSeedOfTTOut` and `PearlC.TTOutTileRowSeedOfTTOutTile`: reductions between assumptions.
- `PearlC.TTOutRowSeedSkipClass`: a probability bound on the skip class.

### NCP (42)

- **Models/ (2)**: `NCP.GameProofs.gammaFromTTNCP` and `NCP.RouteUProofs.gammaFromTTNCP_U`, `ncp-v1`'s γ.
- **Proofs/ lemmas (40)**: everything else in `Proofs/Pouw/NCP/`:
  - `ChainProofs` 8, `ExtraIdentityProofs` 1, `GameProofs` 8, `Proofs` 3, `RelationProofs` 4;
  - `RelationWitness` 4, `RouteUProofs` 5, `RouteUWordProofs` 2, `WordProofs` 5.

  Their vocabulary is `Definitions/Pouw/NCP/`, and their assumptions `Specs/Pouw/Assumptions/NCP/`.

### Proofs (20): `Pouw.Proofs.*`

- **D1, no verifier (3)**: `gammaBudget` (`Reduction.lean`), `milestoneExhaustion` (`Theorem1.lean`) and
  `milestoneRequirement` (`Milestone.lean`). These state D1's γ and requirement at `D1.m1`.
- **Proofs/ lemmas (17)**:
  - `Copy`: `copyBound`, `copyNzWitness`;
  - `Exact`: `d1Complete`, `int32Decode`, `int32Transcript`, `int8KBound`, `noisedKBound`, `usefulness`;
  - `M1`: `milestoneERSeparated`, `milestoneInstance`, `milestoneWref`, `noiseRange_of_factor_bounds`;
  - `Witness`: `freeModel_queries`, `gameCanBeLost`, `honestComplete`, `outputPriced_queries`, `ttWitness`.

  Their vocabulary is `Definitions/Pouw/{D1,M1,Witness,Basic}`.

The full list, guarantee by guarantee, is in the appendix.

## 2. What PoUW's verifier needs to enter core/ (a Lean `Pouw.verify`)

**Today.**

- There is no Lean `Pouw.verify` and no `verity/core/`.
- PoUW's verifier is Python:
  - `audit.Verifier` (`check_tile`, `audit`);
  - `schemes/pearl_c_work.py` (`audit`, `_audit`, `check_records`, `records_root`, `draw_key`, `draw`, `exclusion_tiles`,
    `check_drawn`, `check_opened`, `tile_cap`);
  - `coins.py` (`coin_reason`) and `audit.draw_coin`;
  - `window.py` (`window_problem`, `tile_at`, `bucket`, `k_prime`).
- The only executable Lean verifier is C-Flock's: `backends/flock/verifier/lean/`, with `Flock/Verify.lean` `verify`
  and `Flock/Zk.lean` `verify`.
- An executable Lean spec of `verity.randomness` v2 is `verity/Security/Proofs/Flock/Soundness/Randomness.lean`, in
  `security_proofs`, not in a code package.

The draft's rules that bear on each item:

- a property covers every input the function accepts, with no scope hypotheses;
- no hash function is assumed collision-resistant, and a property reduces to finding a SHA-512 collision;
- `Definitions/` never reuses `core/` code.

The Models/ statements are mostly per shape and per record. Their domains are `U.InDomain P D` at one shape each
(`pearlCDomainDevAt … sh8192`, the served shapes, the `qwen3_8b` and `llama31_8b` mixes) or whole-tile layouts. So a
`Pouw.verify` would have to refuse every workload outside the union of those domains, or the statements would be widened.

### 2a. The tile check (L3)

**What exists** (PRs #983 and #731, merged):

- **Definitions**: `Definitions/Pouw/PearlC/TileCheck.lean` (`TileCheck`, `TileCheck.Accepts`, `TileWordsGood`, and
  L3 as `TileCheck.Computes`, `TileCheck.ComputesCap` and `TileCheck.ComputesWords`), `TileCheck8.lean` (`pc8`) and
  `TileCheck4.lean` (`pc4`).
- **The circuits**: `TileCircuit`, `Tile4Circuit`, `RowCircuit`, `Row4Circuit`, `WholeCircuit` and `WholeCircuit4`.
- **Proofs**: `Proofs/Pouw/PearlC/TileCheck.lean` (`TileCheck.computes_of`, `TileCheck.mem_of_computes`),
  `TileCheck8.lean`, `TileCheck4.lean`, `TileCheck8Words.lean`, `TileCheck4Words.lean`, `TileProtocol.lean`,
  `PeelExists4.lean` and `Block4Sem.lean`.
- **The word half is proved** for the plain Programs, in `TileCheckWords.lean`:
  `tileCheck8_computesWords{,_pearlC,_domain,_wide}` and `tileCheck4_computesWords{,_pearlC,_domain}`.

**What's missing:**

- **The cap half of L3.** `TileCheck.ComputesCap` has no proof.
  - Its docstring says the Program has no debit or cap yet, so the check leaves the activations' debit free.
  - The cap is now in Python gates: `circuit/cap.py`'s `Pc8TileCap`, the split `Pc8CapWordUnit`, `Pc8CapStrip`,
    `Pc8CapRowDigest`, `Pc8CapRowTally`, `Pc8CapTile` and `Pc8CapTally`, and `pc8.Shape.cap`.
  - No Lean `TileCheck` instance of the cap Programs exists, and no proof that they compute `TR.capOK`.
  - The docstring's pointer "(the replay shortcut, `PROTOCOL.md`)" names a phrase that is no longer in `PROTOCOL.md`.
- **The hiding Program.**
  - `TileCheck`'s `Collides` describes the hiding Program by its TurboSHAKE128 leaf `pouw/tile-h0/v1`. No `TileCheck`
    instance of the hiding tile unit (`Pc8TileHidden`, `PearlTileDigest` in `circuit/leaves.py`) exists.
  - No bound on `Collides` exists either, as a reduction to a collision finder.
- **Named hypotheses still in L3's words.**
  - `Pc8OpsAgree` and `Pc4OpsAgree`: core's primitives agree with the row ops.
  - `Noise8OK`.
  - `Pc8EntryOK` below step width 24. `tileCheck8_computesWords_wide` discharges it at w ≥ 24.
- **Scope.** L3 is stated on whole-tile shapes (`Shape8`, `Shape4`). A shape with a narrower last tile (m = 80) is
  outside it, so the verifier would have to refuse it.
- **L8.** That the verifier's public inputs are `anchorsOf` is named in `TileCheck`'s docstrings and stated nowhere.
- **Not locked.** None of the L3 theorems is a guarantee in `lean-audit.json`.
- **A known difference.** The work law excludes a failing weight row and accepts its tiles, while
  `TileCheck.Accepts` and `TileGood` refuse them (`PROTOCOL.md`, approaches registry
  `pouw/work-law-weight-row-exclusion`).
- **The per-tile proof's soundness.**
  - `TileProofSoundAll` (`Specs/Pouw/Assumptions/PearlC/HiddenTile.lean`) is an open obligation.
  - `tileProofSoundAll_of_tileGame` (`Proofs/Pouw/PearlC/HiddenTileGame.lean`) reduces it to a `TileGame` per tile.
  - No C-Flock `TileGame` or `HiddenAudit` instance exists. One would be built from `flock_e2e_drawn_hm96_reads`, the
    hm96 binding, L3 and L8.
- **No executable Lean** of `check_tile`/`check_opened` exists. On the hidden route the tile check is a C-Flock proof
  that the Lean Flock verifier checks.

### 2b. The window gates (L4)

**On `main`:**

- **Python**: `verity/protocols/accounting/work/pouw/window.py` (`PUBLIC`, `GRID_BITS`, `bucket`, `k_prime`, `tile_at`
  and `window_problem`). Its docstring says: "It is not proved yet: no Program states it."
- **No PoUW Lean** for the window.
- **Related C-Flock Lean** (for `plan.draw`'s per-call strata, not PoUW's tile window):
  - `Proofs/Flock/Soundness/Audit/Window.lean`: `Law.stratified`, with modelling lines M1 and M2 outside the
    statements;
  - `Proofs/Flock/Soundness/PlanDraw.lean`: its docstring still names `protocols/pouw/verity_pouw/circuit/plan.py`;
  - `KeyedDraw.lean` and `Audit/RegDraw.lean`.

**PRs:**

- **#1426** (OPEN, base `main`, `cursor/pouw-window-gates-layout-e3fa`) gives the window a layout gates can read:
  - entry rows of 240 bytes as `hm96-sha512/row/v2`;
  - dense side trees at D_A = 13 and D_B = 17;
  - side domains, and F_σ public inputs in `verity/flock-public-inputs/v1`.

  A follow-up commit is to add the pass's -h3 tile-tree root to each entry.
- **#1427** (OPEN draft, stacked on #1426, `cursor/pouw-window-l4-e3fa`) adds `circuit/window_statement.py`:
  - `PouwWindowStatement_v1` (`window_problem` over 16 entry rows) and `_v2` (gates);
  - circuit-check passes, and the gates agree with Python on 42 cases;
  - its blockers are listed under "What's missing".

**What's missing:**

- **A Lean Definition** of the window statement (`window_problem`).
- **A proof** that `PouwWindowStatement_v2` computes it, which is L4's analogue of `TileCheck.Computes`.
- **The 16 entries as registered reads.** They are not yet bound as `--registered` reads of the window root.
  `backends/flock/verifier/lean/Flock/Registered.lean` accepts only `hm96-sha512/row/v1`, and v2 rows wait on #1320
  (OPEN).
- **Regenerated pins** once the entry row gains the -h3 tile-tree root.
- **A check slot.** The circuit_check suite runs out of memory on a 16 GB VM (#1427).
- **The window's draw and credit in PoUW Lean** (see 2c): uniform subset:K′ over N padded tiles, and the credit at
  grid level g_ℓ.

Labels: `window.py`'s "L2, L3, L4" are the joint note's (the advice, the draw and the window statement). Lean's "L3" is
the tile check. The letters overlap but name different lists.

### 2c. The draw from live coins

**Python:**

- `coins.py`: the epoch coins are committed as hm96-sha512 leaves in a frame-v3-sha512 tree, and each is opened once,
  after `after`. `coin_reason` checks an opening.
- `audit.draw_coin`.
- `pearl_c_work.draw_key` and `draw`: `derive(coin, "verity/pouw/pearl-c-draw/v1", …)`, then t work-weighted draws with
  replacement over the credited-cell tickets, by `Key.uniform` and bisection.
- `audit.Sampled.select`.
- `window.k_prime`: uniform subset:K′, without replacement.

**Lean:**

- `GγSampled` (`Definitions/Pouw/PearlC/Tile.lean`) quantifies over ideal independent `Ticket` draws weighted by the
  whole tile's `Wref`. Its docstring says the draw is independent of the oracle and the salt, so its source must be
  fixed after the commitment (F8).
- Core's `Definitions/Core/Game.lean` has live coin nodes.
- `verity.randomness` v2's executable spec is `Proofs/Flock/Soundness/Randomness.lean` (`derive`, `stream`, `uniform`,
  `subset` on `Flock.Sha512.hash`), tied to Python by vectors (`backends/flock/tests/lean/RandomnessVectors.lean`).
- `Proofs/Flock/Soundness/KeyedDraw.lean` bounds a keyed `Key.subset` draw's escape. Its window form carries a
  pseudorandomness slack η.

**What's missing:**

- **The coin commitment in Lean.** Nothing models the epoch-coin commitment or `coin_reason`.
- **The draw's law.** No PoUW lemma says that `draw_key`'s work-weighted draw, with replacement, realizes
  `GγSampled`'s `Ticket` law, or comes within an η of it. `KeyedDraw` covers `Key.subset` only.
- **The window's law.** No PoUW statement covers its uniform subset:K′ law. `GγSampled` is with replacement and
  work-weighted.
- **Ticket weights.** `GγSampled`, `HonestTileCapRate` and `CompleteSampled` weigh a tile by its whole `Wref`, while
  `pearl_c_work` weighs it by its credited cells (`PROTOCOL.md`, "Not here yet"; red team #1014).
- **Randomness' location.** It sits in `security_proofs` (`Proofs/Flock/`), not in code that a `Pouw.verify` could call.
- **Python paths a core verifier would refuse**, since no statement covers them:
  - `audit.Verifier.audit` with bare source bytes on an epoch without a coin commitment;
  - `pearl_c_work.audit_replay`, a recorded Fiat–Shamir draw whose docstring says it "supports no claim";
  - the `Lottery` selection, for which `WorkProfile` gives no bound.

### 2d. The work law's debit and cap, and V-EX

**Lean:**

- `Definitions/Pouw/PearlC/Game.lean`: `debitOf`, `creditOf`, and the score with the cap.
- `Skip.lean` and `SkipP.lean` (`chainDebit`, `wordFlags`), and `SaltDead.lean`: the forming debit.
- `DeviceRev1.lean`: `creditDevRev1`, `wrefDevRev1`, and `pearlCTilesDevRev1` with `capOK`.
- `DeviceKernelWref.lean`: `wrefDevRev1K` and `pearlCTilesDevRev1K`.
- `Tile.lean`: `TileRules`, `TileGood`, credited rows, `Wcred`, the tile share.
- The -h3 per-row cap (C2): `pearlCProtocolDevRev1RowCap` and `pearlCTilesDevRev1RowCap`, in
  `Specs/Pouw/Assumptions/PearlC/TTOutRowSeed.lean`.
- `Completeness.lean` and `Specs/Pouw/Assumptions/PearlC/HonestCap.lean`.

**Python:**

- `pearl_c_work.check_opened`, `tile_cap`, `check_records`, `records_root`, `exclusion_tiles`, `volunteer`, `Split`
  and `split_check`;
- `schemes/pearl_c_debit.py`, the debit replay.

**What's missing in Lean:**

- **V-EX.** Voluntary rows (`voluntary_a`, `voluntary_b`, their caps ⌈m/64⌉ and ⌈n/64⌉, and the exemption from the
  per-row check and R1) appear in no Lean file.
- **Credited-cell tickets** (see 2c).
- **The declaration.**
  - Lean models the channel split as outside the unit (`Game.lean`, "The channel split").
  - No Lean models the `Split` record, `split_check`, the kept width `k_kept` or the zero-past-|K| check.
  - No Lean models filler or real rows, `records_root`, or the exclusion tiles (one opened tile per excluded row).
- **The per-row cap's Python.** The row cap is in Lean, but its Python (`row_cap`) is not on `main`. It comes with the
  -h3 PRs (#1278, superseded by #1405 and then #1423).
- **The cap in the hidden route.** That needs L3's `ComputesCap` (see 2a).
- **The difference on excluded weight rows** (see 2a).
- **No executable Lean** of the debit replay or the cap test. The Lean definitions are ℚ-valued specifications.

### 2e. The -h3 digests: `sha512/row-seg/v1` and `hm96-sha512`

**On `main`:**

- **Rows.** `circuit/leaves.py` commits rows as `hm96-sha512/row-seg/v1` (`sha512/row-seg/v1`) or `hm96-sha512/row/v2`.
- **The tile digest** is still TurboSHAKE128: `PearlTileDigest`, `pouw/tile-h0/v1`.
- **The per-row seeds** (-h3) are not on `main`. The registered schemes use hashing h0, h1 or h2.
- **Certificates.** `pearl-c-*`'s certificates claim `cr/blake3`, with `xof/blake3` and `cr/sha-256` beyond h0.
  `ncp-v1`'s claims `cr/sha-256`.
- **Open PRs**:
  - #1423 (OPEN): "-h3 is SHA-512 (C1); BLAKE3 formats to archive/". It replaces #1405, which superseded #1278 and #1308.
  - #1424 (OPEN, stacked): "the served pass digests over A roots are SHA-512".

**Lean that exists, all in C-Flock's verifier and analysis:**

- `backends/flock/verifier/lean/Flock/HmRow.lean`: `ROW_SCHEMA_SEG`, `sha512/row-seg/v1`'s prefixes and digest, and
  the `row/v2` checks.
- `Flock/Hm96.lean`, `Flock/Hash.lean` (SHA-512) and `Flock/Tags.lean` (`rowSegIdentity`).
- `Flock/Registered.lean`, on `row/v1` only.
- `Proofs/Flock/Soundness/Discharge/Hidden/Rows.lean` and `Hidden/Wide/RowCommit.lean`.
- The guarantees `FlockSoundness.{CROnly,Registered}.flock_e2e_drawn_hm96_reads`.

**PoUW's Lean:**

- PoUW models the seeds through the uniform oracle `H : Q → R`:
  - `TTOutRowSeed.lean` and `TTOutRowSeedK`, with conditions C0 to C3 and `RowSeedNoise`;
  - `Proofs/Pouw/PearlC/RowSeedCode.lean`: the code-form seed u·2³² + i as a relabelling, at error (q + R)/2^128;
  - `RowSeedGamma` and `RowSeedKGamma`.

**What's missing:**

- **The seed's input.** No Lean ties the oracle query to the seed's actual input under #1423:
  salt ‖ leaf_i ‖ root_B ‖ u·2³² + i, with leaf_i an hm96-sha512 row-seg leaf.
- **A SHA-512 tile digest.** No Lean defines PoUW's tile digest under SHA-512. `TileCheck`'s `Collides` still names the
  TurboSHAKE128 `pouw/tile-h0/v1` leaf.
- **The hm96 binding of τ's rows.** It is part of the open `TileProofSoundAll`.
- **`Registered.lean` on `row/v2`** (#1320).
- **PoUW's own tags in Lean.** No executable Lean exists of the epoch-coin commitment, `records_root`, the
  `draw_after` tag or `draw_key`'s context.
- **Collision resistance by reduction.** The PoUW certificates' collision-resistance claims would be restated as
  reductions to a SHA-512 collision finder, as the draft requires and as C-Flock's per-finder `cr/sha-512` and
  `ecr/sha-512` are.

## Appendix: every PoUW guarantee, by group, class and file

Columns: group, class (M = Models/, C = Models/ completeness, D = D1 with no verifier, L = Proofs/ lemma), file under
`verity/Security/`, count, names.

~~~text
PearlC M Proofs/Pouw/PearlC/CapLoopGamma.lean (8): Pouw.PearlC.pearlCGammaSm120LoopRev1_16384 Pouw.PearlC.pearlCGammaSm120LoopRev1_8192 Pouw.PearlC.pearlCGammaUnpromotedCap1000Loop_16384 Pouw.PearlC.pearlCGammaUnpromotedCap1000Loop_8192 Pouw.PearlC.pearlCSampledSm120LoopRev1_16384 Pouw.PearlC.pearlCSampledSm120LoopRev1_8192 Pouw.PearlC.pearlCSampledUnpromotedCap1000Loop_16384 Pouw.PearlC.pearlCSampledUnpromotedCap1000Loop_8192
PearlC M Proofs/Pouw/PearlC/ChainCapKernelGamma.lean (6): Pouw.PearlC.pearlCGammaDevChainCapKAt Pouw.PearlC.pearlCGammaSm120v2LoopCast8ChainCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast8ChainCap1000_8192 Pouw.PearlC.pearlCSampledDevChainCapKAt Pouw.PearlC.pearlCSampledSm120v2LoopCast8ChainCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast8ChainCap1000_8192
PearlC M Proofs/Pouw/PearlC/ChainCapLoopGamma.lean (4): Pouw.PearlC.pearlCGammaUnpromotedChainCap1000Loop_16384 Pouw.PearlC.pearlCGammaUnpromotedChainCap1000Loop_8192 Pouw.PearlC.pearlCSampledUnpromotedChainCap1000Loop_16384 Pouw.PearlC.pearlCSampledUnpromotedChainCap1000Loop_8192
PearlC M Proofs/Pouw/PearlC/ChainOnlyGamma.lean (4): Pouw.PearlC.pearlCGammaDevKChainOnlyAt Pouw.PearlC.pearlCGammaDevRev1KChainOnlyAt Pouw.PearlC.pearlCSampledDevKChainOnlyAt Pouw.PearlC.pearlCSampledDevRev1KChainOnlyAt
PearlC M Proofs/Pouw/PearlC/DeviceCapGamma.lean (8): Pouw.PearlC.pearlCGammaSm120Rev1_16384 Pouw.PearlC.pearlCGammaSm120Rev1_8192 Pouw.PearlC.pearlCGammaUnpromotedCap1000_16384 Pouw.PearlC.pearlCGammaUnpromotedCap1000_8192 Pouw.PearlC.pearlCSampledSm120Rev1_16384 Pouw.PearlC.pearlCSampledSm120Rev1_8192 Pouw.PearlC.pearlCSampledUnpromotedCap1000_16384 Pouw.PearlC.pearlCSampledUnpromotedCap1000_8192
PearlC M Proofs/Pouw/PearlC/DeviceCapRev1Gamma.lean (6): Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_16384_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap_8192
PearlC M Proofs/Pouw/PearlC/DeviceChainCapGamma.lean (4): Pouw.PearlC.pearlCGammaUnpromotedChainCap1000_16384 Pouw.PearlC.pearlCGammaUnpromotedChainCap1000_8192 Pouw.PearlC.pearlCSampledUnpromotedChainCap1000_16384 Pouw.PearlC.pearlCSampledUnpromotedChainCap1000_8192
PearlC M Proofs/Pouw/PearlC/DeviceFp4Gamma.lean (2): Pouw.PearlC.pearlCGammaFp4At Pouw.PearlC.pearlCSampledFp4At
PearlC M Proofs/Pouw/PearlC/DeviceRev1Gamma.lean (6): Pouw.PearlC.pearlCGammaDevRev1At Pouw.PearlC.pearlCGammaH100Rev1_16384 Pouw.PearlC.pearlCGammaH100Rev1_8192 Pouw.PearlC.pearlCSampledDevRev1At Pouw.PearlC.pearlCSampledH100Rev1_16384 Pouw.PearlC.pearlCSampledH100Rev1_8192
PearlC M Proofs/Pouw/PearlC/DeviceSm120CapRev1Gamma.lean (8): Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1Cap_16384 Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1Cap_8192 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1Cap_16384 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1Cap_8192
PearlC M Proofs/Pouw/PearlC/DeviceSm120Gamma.lean (16): Pouw.PearlC.pearlCGammaSm120v1Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1Rev1_8192 Pouw.PearlC.pearlCGammaSm120v2Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2ChainCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2ChainCap1000_8192 Pouw.PearlC.pearlCGammaUOnlySm120v1Rev1_8192 Pouw.PearlC.pearlCGammaUOnlySm120v2Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v1Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1Rev1_8192 Pouw.PearlC.pearlCSampledSm120v2Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2ChainCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2ChainCap1000_8192 Pouw.PearlC.pearlCSampledUOnlySm120v1Rev1_8192 Pouw.PearlC.pearlCSampledUOnlySm120v2Cap1000_8192
PearlC M Proofs/Pouw/PearlC/DeviceSm120KernelGamma.lean (120): Pouw.PearlC.pearlCGammaSm120v1Cast16ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast16ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast16Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast16Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast32Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast32Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast32p06ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast32p06ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast32p06Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast32p06Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast8p72ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast8p72ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1Cast8p72Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast16ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast16ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast16Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast16Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast32Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast32Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast32p06ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast32p06ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast32p06Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast32p06Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast8Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast8Rev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72ChainOnlyRev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72ChainOnlyRev1_8192 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1_8192 Pouw.PearlC.pearlCGammaSm120v2Cast16Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast16Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast16ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast16ChainOnlyCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast32Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast32Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast32p06Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast32p06Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast32p06ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast32p06ChainOnlyCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast8p72Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast8p72Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2Cast8p72ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2Cast8p72ChainOnlyCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast16Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast16Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast16ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast16ChainOnlyCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast32Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast32Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast32p06Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast32p06Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast32p06ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast32p06ChainOnlyCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast8Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast8Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast8p72Cap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast8p72Cap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCast8p72ChainOnlyCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCast8p72ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v1Cast16ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast16ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast16Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast16Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast32Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast32Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast32p06ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast32p06ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast32p06Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast32p06Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast8p72ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast8p72ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1Cast8p72Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast16ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast16ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast16Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast16Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast32Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast32Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast32p06ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast32p06ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast32p06Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast32p06Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast8Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast8Rev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72ChainOnlyRev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72ChainOnlyRev1_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1_8192 Pouw.PearlC.pearlCSampledSm120v2Cast16Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast16Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast16ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast16ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast32Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast32Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast32p06Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast32p06Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast32p06ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast32p06ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast8p72Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast8p72Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2Cast8p72ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2Cast8p72ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast16Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast16Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast16ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast16ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast32Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast32Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast32p06Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast32p06Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast32p06ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast32p06ChainOnlyCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast8Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast8Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast8p72Cap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast8p72Cap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCast8p72ChainOnlyCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCast8p72ChainOnlyCap1000_8192
PearlC M Proofs/Pouw/PearlC/DeviceSm120LoopGamma.lean (16): Pouw.PearlC.pearlCGammaSm120v1LoopRev1_16384 Pouw.PearlC.pearlCGammaSm120v1LoopRev1_8192 Pouw.PearlC.pearlCGammaSm120v2LoopCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopCap1000_8192 Pouw.PearlC.pearlCGammaSm120v2LoopChainCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2LoopChainCap1000_8192 Pouw.PearlC.pearlCGammaUOnlySm120v1LoopRev1_8192 Pouw.PearlC.pearlCGammaUOnlySm120v2LoopCap1000_8192 Pouw.PearlC.pearlCSampledSm120v1LoopRev1_16384 Pouw.PearlC.pearlCSampledSm120v1LoopRev1_8192 Pouw.PearlC.pearlCSampledSm120v2LoopCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopCap1000_8192 Pouw.PearlC.pearlCSampledSm120v2LoopChainCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2LoopChainCap1000_8192 Pouw.PearlC.pearlCSampledUOnlySm120v1LoopRev1_8192 Pouw.PearlC.pearlCSampledUOnlySm120v2LoopCap1000_8192
PearlC M Proofs/Pouw/PearlC/Fp4ChainOnlyGamma.lean (6): Pouw.PearlC.pearlCGammaFp4ChainOnlyAt Pouw.PearlC.pearlCGammaFp4Sm120ChainOnlyAt_16384 Pouw.PearlC.pearlCGammaFp4Sm120ChainOnlyAt_8192 Pouw.PearlC.pearlCSampledFp4ChainOnlyAt Pouw.PearlC.pearlCSampledFp4Sm120ChainOnlyAt_16384 Pouw.PearlC.pearlCSampledFp4Sm120ChainOnlyAt_8192
PearlC M Proofs/Pouw/PearlC/Fp4HotGamma.lean (10): Pouw.PearlC.pearlCGammaFp4HotAt Pouw.PearlC.pearlCGammaFp4Sm120HotAt_16384 Pouw.PearlC.pearlCGammaFp4Sm120HotAt_8192 Pouw.PearlC.pearlCGammaFp4Sm120HotChainOnlyAt_16384 Pouw.PearlC.pearlCGammaFp4Sm120HotChainOnlyAt_8192 Pouw.PearlC.pearlCSampledFp4HotAt Pouw.PearlC.pearlCSampledFp4Sm120HotAt_16384 Pouw.PearlC.pearlCSampledFp4Sm120HotAt_8192 Pouw.PearlC.pearlCSampledFp4Sm120HotChainOnlyAt_16384 Pouw.PearlC.pearlCSampledFp4Sm120HotChainOnlyAt_8192
PearlC M Proofs/Pouw/PearlC/Fp4IssueGamma.lean (8): Pouw.PearlC.pearlCGammaFp4Sm120At_16384 Pouw.PearlC.pearlCGammaFp4Sm120At_8192 Pouw.PearlC.pearlCGammaFp4Sm120Issue_16384 Pouw.PearlC.pearlCGammaFp4Sm120Issue_8192 Pouw.PearlC.pearlCSampledFp4Sm120At_16384 Pouw.PearlC.pearlCSampledFp4Sm120At_8192 Pouw.PearlC.pearlCSampledFp4Sm120Issue_16384 Pouw.PearlC.pearlCSampledFp4Sm120Issue_8192
PearlC M Proofs/Pouw/PearlC/Gamma.lean (2): Pouw.PearlC.pearlCGamma16384 Pouw.PearlC.pearlCGamma8192
PearlC M Proofs/Pouw/PearlC/HiddenGamma.lean (2): Pouw.PearlC.gammaHidden_of_sampled_all Pouw.PearlC.pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192
PearlC M Proofs/Pouw/PearlC/KernelWrefGamma.lean (4): Pouw.PearlC.pearlCGammaDevKAt Pouw.PearlC.pearlCGammaDevRev1KAt Pouw.PearlC.pearlCSampledDevKAt Pouw.PearlC.pearlCSampledDevRev1KAt
PearlC M Proofs/Pouw/PearlC/RowSeedGamma.lean (10): Pouw.PearlC.pearlCGammaDevRev1RowSeedAt Pouw.PearlC.pearlCGammaSm120v1RowSeed_16384 Pouw.PearlC.pearlCGammaSm120v1RowSeed_8192 Pouw.PearlC.pearlCGammaSm120v2RowSeedCap1000_16384 Pouw.PearlC.pearlCGammaSm120v2RowSeedCap1000_8192 Pouw.PearlC.pearlCSampledDevRev1RowSeedAt Pouw.PearlC.pearlCSampledSm120v1RowSeed_16384 Pouw.PearlC.pearlCSampledSm120v1RowSeed_8192 Pouw.PearlC.pearlCSampledSm120v2RowSeedCap1000_16384 Pouw.PearlC.pearlCSampledSm120v2RowSeedCap1000_8192
PearlC M Proofs/Pouw/PearlC/RowSeedKGamma.lean (7): Pouw.PearlC.pearlCGammaDevRev1KRowSeedAt Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1RowSeedCap1000_8192 Pouw.PearlC.pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCap1000_8192 Pouw.PearlC.pearlCHiddenSm120v1LoopCast8p72Rev1RowSeedCodeCap1000_8192 Pouw.PearlC.pearlCSampledDevRev1KRowSeedAt Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1RowSeedCap1000_8192 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1RowSeedCodeCap1000_8192
PearlC M Proofs/Pouw/PearlC/ServedMixedRev1Gamma.lean (8): Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_llama31_8b Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_llama31_8b_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_llama31_8b Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_llama31_8b_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b_of_cap400
PearlC M Proofs/Pouw/PearlC/ServedRev1Gamma.lean (24): Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n24576k4096 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n24576k4096_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n28672k4096 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n28672k4096_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k12288 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k12288_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k14336 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k14336_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k4096 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n4096k4096_of_cap400 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n6144k4096 Pouw.PearlC.pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_n6144k4096_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n24576k4096 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n24576k4096_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n28672k4096 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n28672k4096_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k12288 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k12288_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k14336 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k14336_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k4096 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n4096k4096_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n6144k4096 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_n6144k4096_of_cap400
PearlC M Proofs/Pouw/PearlC/TileCapRev1Gamma.lean (3): Pouw.PearlC.pearlCSampledDevRev1KAt_of_cap Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_16384_of_cap400 Pouw.PearlC.pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_8192_of_cap400
PearlC M Proofs/Pouw/PearlC/TileUOnlyGamma.lean (2): Pouw.PearlC.pearlCSampledUOnlySm120Rev1_8192 Pouw.PearlC.pearlCSampledUOnlyUnpromotedCap1000_8192
PearlC M Proofs/Pouw/PearlC/UOnlyGamma.lean (2): Pouw.PearlC.pearlCGammaUOnlySm120Rev1_8192 Pouw.PearlC.pearlCGammaUOnlyUnpromotedCap1000_8192
PearlC M Proofs/Pouw/PearlC/UOnlyLoopGamma.lean (4): Pouw.PearlC.pearlCGammaUOnlySm120LoopRev1_8192 Pouw.PearlC.pearlCGammaUOnlyUnpromotedCap1000Loop_8192 Pouw.PearlC.pearlCSampledUOnlySm120LoopRev1_8192 Pouw.PearlC.pearlCSampledUOnlyUnpromotedCap1000Loop_8192
PearlC C Proofs/Pouw/PearlC/Completeness.lean (3): Pouw.PearlC.completeSampledDevRev1K Pouw.PearlC.pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_llama31_8b Pouw.PearlC.pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_qwen3_8b
PearlC L Proofs/Pouw/PearlC/ChainOnlyGamma.lean (4): Pouw.PearlC.ttOutPearlCDevChainOnly_of_ttOut Pouw.PearlC.ttOutPearlCDevRev1ChainOnly_of_ttOut Pouw.PearlC.ttOutTilePearlCDevChainOnly_of_ttOut Pouw.PearlC.ttOutTilePearlCDevRev1ChainOnly_of_ttOut
PearlC L Proofs/Pouw/PearlC/DeviceCapGamma.lean (2): Pouw.PearlC.pearlCDomainDev_unpromoted Pouw.PearlC.ttOutPearlCDev_cap_anti
PearlC L Proofs/Pouw/PearlC/DeviceCapRev1Gamma.lean (1): Pouw.PearlC.ttOutPearlCDevRev1_cap_anti
PearlC L Proofs/Pouw/PearlC/DeviceChainCapGamma.lean (3): Pouw.PearlC.chainCap_flagged_le Pouw.PearlC.ttOutPearlCDevChainCap_of_cap Pouw.PearlC.ttOutTilePearlCDevChainCap_of_cap
PearlC L Proofs/Pouw/PearlC/DeviceFp4Gamma.lean (1): Pouw.PearlC.pearlCShapeFp4_headline
PearlC L Proofs/Pouw/PearlC/DeviceGamma.lean (3): Pouw.PearlC.devAt_hopper Pouw.PearlC.ttOutPearlCDev_h100 Pouw.PearlC.ttOutTilePearlCDev_h100
PearlC L Proofs/Pouw/PearlC/DeviceRev1Gamma.lean (3): Pouw.PearlC.creditDevRev1_h100 Pouw.PearlC.ttOutPearlCDevRev1_of_granted Pouw.PearlC.ttOutTilePearlCDevRev1_of_granted
PearlC L Proofs/Pouw/PearlC/DeviceSm120Gamma.lean (5): Pouw.PearlC.devAt_sm120_floor Pouw.PearlC.devSm120v1_domain Pouw.PearlC.devSm120v1_flags Pouw.PearlC.devSm120v2_domain Pouw.PearlC.devSm120v2_flags
PearlC L Proofs/Pouw/PearlC/DeviceSm120LoopGamma.lean (2): Pouw.PearlC.devSm120v1Loop_domain Pouw.PearlC.devSm120v2Loop_domain
PearlC L Proofs/Pouw/PearlC/DeviceSm120v2LoopEquiv.lean (8): Pouw.PearlC.ttOutPearlCDevChainCap_sm120v2_loop Pouw.PearlC.ttOutPearlCDevChainOnly_sm120v2_loop Pouw.PearlC.ttOutPearlCDevUOnly_sm120v2_loop Pouw.PearlC.ttOutPearlCDev_sm120v2_loop Pouw.PearlC.ttOutTilePearlCDevChainCap_sm120v2_loop Pouw.PearlC.ttOutTilePearlCDevChainOnly_sm120v2_loop Pouw.PearlC.ttOutTilePearlCDevUOnly_sm120v2_loop Pouw.PearlC.ttOutTilePearlCDev_sm120v2_loop
PearlC L Proofs/Pouw/PearlC/Fp4ChainOnlyGamma.lean (10): Pouw.PearlC.gammaFp4ChainOnly_sm120Issue_lut256_16384 Pouw.PearlC.gammaFp4ChainOnly_sm120Issue_lut256_8192 Pouw.PearlC.gammaFp4ChainOnly_sm120Issue_rcpApprox_16384 Pouw.PearlC.gammaFp4ChainOnly_sm120Issue_rcpApprox_8192 Pouw.PearlC.gammaFp4ChainOnly_sm120Loop_lut256_16384 Pouw.PearlC.gammaFp4ChainOnly_sm120Loop_lut256_8192 Pouw.PearlC.gammaFp4ChainOnly_sm120Loop_rcpApprox_16384 Pouw.PearlC.gammaFp4ChainOnly_sm120Loop_rcpApprox_8192 Pouw.PearlC.ttOutFp4ChainOnly_of_ttOut Pouw.PearlC.ttOutTileFp4ChainOnly_of_ttOut
PearlC L Proofs/Pouw/PearlC/Fp4HotGamma.lean (16): Pouw.PearlC.gammaFp4HotChainOnly_sm120Issue_lut256_16384 Pouw.PearlC.gammaFp4HotChainOnly_sm120Issue_lut256_8192 Pouw.PearlC.gammaFp4HotChainOnly_sm120Issue_rcpApprox_16384 Pouw.PearlC.gammaFp4HotChainOnly_sm120Issue_rcpApprox_8192 Pouw.PearlC.gammaFp4HotChainOnly_sm120Loop_lut256_16384 Pouw.PearlC.gammaFp4HotChainOnly_sm120Loop_lut256_8192 Pouw.PearlC.gammaFp4HotChainOnly_sm120Loop_rcpApprox_16384 Pouw.PearlC.gammaFp4HotChainOnly_sm120Loop_rcpApprox_8192 Pouw.PearlC.gammaFp4Hot_sm120Issue_lut256_16384 Pouw.PearlC.gammaFp4Hot_sm120Issue_lut256_8192 Pouw.PearlC.gammaFp4Hot_sm120Issue_rcpApprox_16384 Pouw.PearlC.gammaFp4Hot_sm120Issue_rcpApprox_8192 Pouw.PearlC.gammaFp4Hot_sm120Loop_lut256_16384 Pouw.PearlC.gammaFp4Hot_sm120Loop_lut256_8192 Pouw.PearlC.gammaFp4Hot_sm120Loop_rcpApprox_16384 Pouw.PearlC.gammaFp4Hot_sm120Loop_rcpApprox_8192
PearlC L Proofs/Pouw/PearlC/Fp4IssueGamma.lean (7): Pouw.PearlC.Fp4Prices.sm120Issue_eq Pouw.PearlC.gammaFp4_sm120Issue_lut256_16384 Pouw.PearlC.gammaFp4_sm120Issue_lut256_8192 Pouw.PearlC.gammaFp4_sm120Issue_rcpApprox_16384 Pouw.PearlC.gammaFp4_sm120Issue_rcpApprox_8192 Pouw.PearlC.gammaFp4_sm120Loop_rcpApprox_16384 Pouw.PearlC.gammaFp4_sm120Loop_rcpApprox_8192
PearlC L Proofs/Pouw/PearlC/Gamma.lean (1): Pouw.PearlC.ttOutPearlCWitness
PearlC L Proofs/Pouw/PearlC/HiddenTileGame.lean (1): Pouw.PearlC.tileProofSoundAll_of_tileGame
PearlC L Proofs/Pouw/PearlC/KernelWrefGamma.lean (2): Pouw.PearlC.ttOutTile_wref Pouw.PearlC.ttOut_wref
PearlC L Proofs/Pouw/PearlC/Rev1Witness.lean (3): Pouw.PearlC.pearlCTilesDevRev1_total Pouw.PearlC.ttOutPearlCH100Rev1Witness Pouw.PearlC.ttOutTilePearlCH100Rev1Witness
PearlC L Proofs/Pouw/PearlC/RowSeedCode.lean (5): Pouw.PearlC.pr_comp_equiv Pouw.PearlC.ttOutRowSeedCode_of_ttOut Pouw.PearlC.ttOutRowSeed_code Pouw.PearlC.ttOutTileRowSeedCode_of_ttOutTile Pouw.PearlC.ttOutTileRowSeed_code
PearlC L Proofs/Pouw/PearlC/RowSeedFragment.lean (2): Pouw.PearlC.fragSkip_count_le Pouw.PearlC.fragSkip_saving_le
PearlC L Proofs/Pouw/PearlC/RowSeedGamma.lean (7): Pouw.PearlC.devAt_rowLocal Pouw.PearlC.devSm120v1_domain_row Pouw.PearlC.devSm120v2_domain_row Pouw.PearlC.pearlCDomainDev_split Pouw.PearlC.rowCap_agg Pouw.PearlC.ttOutTile_of_ttOutTileRowSeed Pouw.PearlC.ttOut_of_ttOutRowSeed
PearlC L Proofs/Pouw/PearlC/RowSeedSkip.lean (2): Pouw.PearlC.qtree_union_bound Pouw.PearlC.rowDrawn_satisfiable
PearlC L Proofs/Pouw/PearlC/TileCapRev1Gamma.lean (1): Pouw.PearlC.ttOutTilePearlCDevRev1_cap_transfer
PearlC L Proofs/Pouw/PearlC/TileUOnlyGamma.lean (2): Pouw.PearlC.gammaSampledU_implies_gammaSampled Pouw.PearlC.ttOutTilePearlCDevRev1_of_uOnly
PearlC L Proofs/Pouw/PearlC/UOnlyGamma.lean (1): Pouw.PearlC.ttOutPearlCDevRev1_of_uOnly
SecurityProofs M Proofs/Pouw/Deadline.lean (7): Pouw.SecurityProofs.PearlCSampledByDeadline Pouw.SecurityProofs.PearlCSm120Rev1Cap1000ByDeadline_16384 Pouw.SecurityProofs.PearlCSm120Rev1Cap1000ByDeadline_8192 Pouw.SecurityProofs.PearlCSm120Rev1Cap1000ByDeadline_llama31_8b Pouw.SecurityProofs.PearlCSm120Rev1Cap1000ByDeadline_qwen3_8b Pouw.SecurityProofs.SpareCapacityAtDeadline Pouw.SecurityProofs.WorkBetweenSaltAndDeadline
SecurityProofs M Proofs/Pouw/Game.lean (4): Pouw.SecurityProofs.EndToEnd Pouw.SecurityProofs.GammaFromTT Pouw.SecurityProofs.Theorem1 Pouw.SecurityProofs.WorkWeightedSampling
SecurityProofs M Proofs/Pouw/NCP.lean (2): Pouw.SecurityProofs.NCP.GammaFromTTNCP_U_C2 Pouw.SecurityProofs.NCP.GammaFromTTNCP_U_v1
SecurityProofs M Proofs/Pouw/PearlC.lean (8): Pouw.SecurityProofs.PearlC.GammaFp4Sm120_16384 Pouw.SecurityProofs.PearlC.GammaFp4Sm120_8192 Pouw.SecurityProofs.PearlC.GammaSm120v1LoopCast8p72Rev1Cap1000_16384 Pouw.SecurityProofs.PearlC.GammaSm120v1LoopCast8p72Rev1Cap1000_8192 Pouw.SecurityProofs.PearlC.SampledFp4Sm120_16384 Pouw.SecurityProofs.PearlC.SampledFp4Sm120_8192 Pouw.SecurityProofs.PearlC.SampledSm120v1LoopCast8p72Rev1Cap1000_16384 Pouw.SecurityProofs.PearlC.SampledSm120v1LoopCast8p72Rev1Cap1000_8192
SecurityProofs L Proofs/Pouw/Barrier.lean (1): Pouw.SecurityProofs.Barrier.Generic
SecurityProofs L Proofs/Pouw/Dimension.lean (1): Pouw.SecurityProofs.Dimension.A2WordsIff
SecurityProofs L Proofs/Pouw/NCP.lean (18): Pouw.SecurityProofs.NCP.BiasU8Iff Pouw.SecurityProofs.NCP.Cancel Pouw.SecurityProofs.NCP.CheckedUEq Pouw.SecurityProofs.NCP.CheckedUFinal Pouw.SecurityProofs.NCP.IndependentWitness Pouw.SecurityProofs.NCP.Int7Int32UPos Pouw.SecurityProofs.NCP.MmWUExact Pouw.SecurityProofs.NCP.NCPWordFloorIndU Pouw.SecurityProofs.NCP.Range Pouw.SecurityProofs.NCP.RangeU Pouw.SecurityProofs.NCP.ShiftBy24Admissible Pouw.SecurityProofs.NCP.Stacked Pouw.SecurityProofs.NCP.TTNCPUIff Pouw.SecurityProofs.NCP.TTNCPUWitness Pouw.SecurityProofs.NCP.WrapFinalOnlyIndU Pouw.SecurityProofs.NCP.WrapU Pouw.SecurityProofs.NCP.WrapWordFloorIndU Pouw.SecurityProofs.NCP.YUChecked
SecurityProofs L Proofs/Pouw/PearlC.lean (6): Pouw.SecurityProofs.PearlC.GammaFp4Sm120LoopLut256_16384 Pouw.SecurityProofs.PearlC.GammaFp4Sm120LoopLut256_8192 Pouw.SecurityProofs.PearlC.GammaUImpliesGamma Pouw.SecurityProofs.PearlC.TTOutRowSeedOfTTOut Pouw.SecurityProofs.PearlC.TTOutRowSeedSkipClass Pouw.SecurityProofs.PearlC.TTOutTileRowSeedOfTTOutTile
NCP M Proofs/Pouw/NCP/GameProofs.lean (1): Pouw.NCP.GameProofs.gammaFromTTNCP
NCP M Proofs/Pouw/NCP/RouteUProofs.lean (1): Pouw.NCP.RouteUProofs.gammaFromTTNCP_U
NCP L Proofs/Pouw/NCP/ChainProofs.lean (8): Pouw.NCP.ChainProofs.int7Int32 Pouw.NCP.ChainProofs.leadDepth Pouw.NCP.ChainProofs.leadIndWitness Pouw.NCP.ChainProofs.paramsYLink Pouw.NCP.ChainProofs.wrapFinalOnlyInd Pouw.NCP.ChainProofs.wrapIdentity Pouw.NCP.ChainProofs.wrapWordFloorInd Pouw.NCP.ChainProofs.zeroInputInt32
NCP L Proofs/Pouw/NCP/ExtraIdentityProofs.lean (1): Pouw.NCP.ExtraIdentityProofs.admissibleExtraIdentity
NCP L Proofs/Pouw/NCP/GameProofs.lean (8): Pouw.NCP.GameProofs.lastChecked Pouw.NCP.GameProofs.leadComplete Pouw.NCP.GameProofs.leadWitness Pouw.NCP.GameProofs.oneSegment Pouw.NCP.GameProofs.rangeLead Pouw.NCP.GameProofs.segmentLead Pouw.NCP.GameProofs.threeBlock Pouw.NCP.GameProofs.ttncpWitness
NCP L Proofs/Pouw/NCP/Proofs.lean (3): Pouw.NCP.Proofs.signedPermWitness Pouw.NCP.Proofs.wrap Pouw.NCP.Proofs.wrapInt7
NCP L Proofs/Pouw/NCP/RelationProofs.lean (4): Pouw.NCP.RelationProofs.ncpFinalOnly Pouw.NCP.RelationProofs.ncpWordFloor Pouw.NCP.RelationProofs.reductionIf Pouw.NCP.RelationProofs.reductionOnlyIf
NCP L Proofs/Pouw/NCP/RelationWitness.lean (4): Pouw.NCP.RelationWitness.independentRelationFree Pouw.NCP.RelationWitness.ncpFinalOnlyInd Pouw.NCP.RelationWitness.ncpWordFloorInd Pouw.NCP.RelationWitness.relationFreeWitness
NCP L Proofs/Pouw/NCP/RouteUProofs.lean (5): Pouw.NCP.RouteUProofs.int7Int32U Pouw.NCP.RouteUProofs.int7Int32UUnsigned Pouw.NCP.RouteUProofs.leadCompleteU Pouw.NCP.RouteUProofs.leadUWitness Pouw.NCP.RouteUProofs.mmWU_eq
NCP L Proofs/Pouw/NCP/RouteUWordProofs.lean (2): Pouw.NCP.RouteUWordProofs.ncpFinalOnlyIndU Pouw.NCP.RouteUWordProofs.reductionOnlyIfU
NCP L Proofs/Pouw/NCP/WordProofs.lean (5): Pouw.NCP.WordProofs.wordBound Pouw.NCP.WordProofs.wordFinalWitness Pouw.NCP.WordProofs.wordFloor Pouw.NCP.WordProofs.wordNzWitness Pouw.NCP.WordProofs.wordZeroNoise
Proofs D Proofs/Pouw/Milestone.lean (1): Pouw.Proofs.milestoneRequirement
Proofs D Proofs/Pouw/Reduction.lean (1): Pouw.Proofs.gammaBudget
Proofs D Proofs/Pouw/Theorem1.lean (1): Pouw.Proofs.milestoneExhaustion
Proofs L Proofs/Pouw/Copy.lean (2): Pouw.Proofs.copyBound Pouw.Proofs.copyNzWitness
Proofs L Proofs/Pouw/Exact.lean (6): Pouw.Proofs.d1Complete Pouw.Proofs.int32Decode Pouw.Proofs.int32Transcript Pouw.Proofs.int8KBound Pouw.Proofs.noisedKBound Pouw.Proofs.usefulness
Proofs L Proofs/Pouw/M1.lean (4): Pouw.Proofs.milestoneERSeparated Pouw.Proofs.milestoneInstance Pouw.Proofs.milestoneWref Pouw.Proofs.noiseRange_of_factor_bounds
Proofs L Proofs/Pouw/Witness.lean (5): Pouw.Proofs.freeModel_queries Pouw.Proofs.gameCanBeLost Pouw.Proofs.honestComplete Pouw.Proofs.outputPriced_queries Pouw.Proofs.ttWitness
Dimension L Proofs/Pouw/Dimension/A2WordsProofs.lean (4): Pouw.Dimension.A2Words.a2ExtraOutputs Pouw.Dimension.A2Words.a2Separation Pouw.Dimension.A2Words.a2WitnessExtra Pouw.Dimension.A2Words.emptyQuadPipe
Dimension L Proofs/Pouw/Dimension/CausalProofs.lean (3): Pouw.Dimension.algBoundCausal Pouw.Dimension.algWitnessCausal Pouw.Dimension.causalWitness
Dimension L Proofs/Pouw/Dimension/EmbedProofs.lean (14): Pouw.Dimension.Embed.a1fpFadd Pouw.Dimension.Embed.a1fpHalf Pouw.Dimension.Embed.a1fpIff Pouw.Dimension.Embed.a1fpOnRangeGap Pouw.Dimension.Embed.canonicalNaNSat Pouw.Dimension.Embed.embedFp Pouw.Dimension.Embed.embedM4090 Pouw.Dimension.Embed.m4090ChainConsistent Pouw.Dimension.Embed.nanGapConsistent Pouw.Dimension.Embed.perWordM4090 Pouw.Dimension.Embed.perWordM4090Gap Pouw.Dimension.Embed.perWordOfA1fp Pouw.Dimension.Embed.ttNCPM4090NanGap Pouw.Dimension.Embed.ttNCPM4090OfA1fp
Dimension L Proofs/Pouw/Dimension/ForestProofs.lean (11): Pouw.Dimension.Forest.a1CostOfNonquad Pouw.Dimension.Forest.a1CostQuadHolds Pouw.Dimension.Forest.a1CostQuadNear Pouw.Dimension.Forest.algBoundQuad8 Pouw.Dimension.Forest.forestBound Pouw.Dimension.Forest.gridNear Pouw.Dimension.Forest.gridTwoAtom Pouw.Dimension.Forest.quadChainConsistent Pouw.Dimension.Forest.quadChainConsistentTight Pouw.Dimension.Forest.theorem1Family Pouw.Dimension.Forest.ttNCPQuadOfA2
Dimension L Proofs/Pouw/Dimension/Fp8MmaProofs.lean (3): Pouw.Dimension.Fp8Mma.ceiling4090 Pouw.Dimension.Fp8Mma.shapeTable4090 Pouw.Dimension.Fp8Mma.shapeWF4090
Dimension L Proofs/Pouw/Dimension/H100CiteProofs.lean (4): Pouw.Dimension.H100.denseWritesFragLanes Pouw.Dimension.H100.distinctWritesMeasured Pouw.Dimension.H100.distinctWritesPacked Pouw.Dimension.H100.fragLanesSat
Dimension L Proofs/Pouw/Dimension/H100DenseProofs.lean (5): Pouw.Dimension.H100.apartCert Pouw.Dimension.H100.denseCert Pouw.Dimension.H100.denseLaneWitness Pouw.Dimension.H100.denseWritesLegacy Pouw.Dimension.H100.legacyGamma
Dimension L Proofs/Pouw/Dimension/H100FloorProofs.lean (3): Pouw.Dimension.H100.distinctWritesFloor Pouw.Dimension.H100.distinctWritesLoopFree Pouw.Dimension.H100.h32Floor
Dimension L Proofs/Pouw/Dimension/H100FragProofs.lean (3): Pouw.Dimension.H100.accInOfFrag Pouw.Dimension.H100.denseWritesFrag Pouw.Dimension.H100.fragShareGain
Dimension L Proofs/Pouw/Dimension/H100LoopFreeProofs.lean (1): Pouw.Dimension.H100.h32LoopFree
Dimension L Proofs/Pouw/Dimension/H100MeasuredProofs.lean (1): Pouw.Dimension.H100.h32Measured
Dimension L Proofs/Pouw/Dimension/H100PeakTcProofs.lean (2): Pouw.Dimension.H100.distinctWritesPeakTc Pouw.Dimension.H100.floorTcPeakTc
Dimension L Proofs/Pouw/Dimension/H100Proofs.lean (8): Pouw.Dimension.H100.embedMH100 Pouw.Dimension.H100.h32Sat Pouw.Dimension.H100.honestSplitK100 Pouw.Dimension.H100.mh100Attains Pouw.Dimension.H100.mh100WordsConsistent Pouw.Dimension.H100.perWordMH100 Pouw.Dimension.H100.perWordMH100Floor Pouw.Dimension.H100.perWordMH100Words
Dimension L Proofs/Pouw/Dimension/H100WProofs.lean (9): Pouw.Dimension.H100.c2DistinctWords Pouw.Dimension.H100.c2FirstRunCopy Pouw.Dimension.H100.distinctLiveMH100 Pouw.Dimension.H100.distinctWritesAttained Pouw.Dimension.H100.distinctWritesLegacy Pouw.Dimension.H100.distinctWritesMH100 Pouw.Dimension.H100.distinctWritesMH100Floor Pouw.Dimension.H100.distinctWritesMH100On Pouw.Dimension.H100.floorTcSat
Dimension L Proofs/Pouw/Dimension/LiftProofs.lean (3): Pouw.Dimension.liftMinRankL5eWitness Pouw.Dimension.liftMinRankWitness Pouw.Dimension.minRankGeWitness
Dimension L Proofs/Pouw/Dimension/Lifting.lean (4): Pouw.Dimension.Lifting.card_le_pow_of_sub_mem Pouw.Dimension.Lifting.grid_card Pouw.Dimension.Lifting.slice_card_le_of_subspace Pouw.Dimension.Lifting.solutions_card_le
Dimension L Proofs/Pouw/Dimension/MinRankProofs.lean (1): Pouw.Dimension.minRank2Witness
Dimension L Proofs/Pouw/Dimension/MixingProofs.lean (7): Pouw.Dimension.a1W1Witness Pouw.Dimension.a2Witness4090 Pouw.Dimension.alg4090Witness Pouw.Dimension.algBound4090 Pouw.Dimension.mixingLemma Pouw.Dimension.ttNCPOfA1A2 Pouw.Dimension.ttNCPOfA1A2W1
Dimension L Proofs/Pouw/Dimension/OpenPipeProofs.lean (8): Pouw.Dimension.OpenPipe.a2QuadToOpen Pouw.Dimension.OpenPipe.algBoundOpenQuad Pouw.Dimension.OpenPipe.algBoundOpenQuad8 Pouw.Dimension.OpenPipe.openPipeWitness Pouw.Dimension.OpenPipe.openQuadChainConsistent Pouw.Dimension.OpenPipe.quadToOpen Pouw.Dimension.OpenPipe.theorem1Open Pouw.Dimension.OpenPipe.ttNCPOpenQuadOfA2
Dimension L Proofs/Pouw/Dimension/PipeProofs.lean (13): Pouw.Dimension.a1CostOfSplit Pouw.Dimension.a1CostWitness Pouw.Dimension.a2WitnessPipe Pouw.Dimension.a2WitnessQuad Pouw.Dimension.algBoundPipe Pouw.Dimension.algBoundQuad Pouw.Dimension.minRankGeFacts Pouw.Dimension.minRankGeShift16 Pouw.Dimension.pipeChainConsistent Pouw.Dimension.pipeWitness Pouw.Dimension.pipeWordWitness Pouw.Dimension.ttNCPOfA1costA2 Pouw.Dimension.ttNCPOfQuadA2
Dimension L Proofs/Pouw/Dimension/Proofs.lean (15): Pouw.Dimension.a1MinRank Pouw.Dimension.a1Witness Pouw.Dimension.a2Witness Pouw.Dimension.algBound Pouw.Dimension.algBoundWrapped Pouw.Dimension.algSharp Pouw.Dimension.algWitness Pouw.Dimension.dimLePriced Pouw.Dimension.pricedCount Pouw.Dimension.sanity_final_free Pouw.Dimension.sanity_h16_needed Pouw.Dimension.sanity_no_units Pouw.Dimension.secondDifference Pouw.Dimension.ttNCPAlg Pouw.Dimension.ttNCPOfA2
Dimension L Proofs/Pouw/Dimension/RouteUPipeProofs.lean (10): Pouw.Dimension.RouteUProofs.a1CostQuadUHolds Pouw.Dimension.RouteUProofs.a1CostWitnessU Pouw.Dimension.RouteUProofs.algBoundPipeU Pouw.Dimension.RouteUProofs.algBoundQuad8U Pouw.Dimension.RouteUProofs.algBoundQuadU Pouw.Dimension.RouteUProofs.pipeChainConsistentU Pouw.Dimension.RouteUProofs.pipeWitnessU Pouw.Dimension.RouteUProofs.ttNCPOfA1costA2U Pouw.Dimension.RouteUProofs.ttNCPOfQuadA2U Pouw.Dimension.RouteUProofs.ttNCPQuadOfA2U
Dimension L Proofs/Pouw/Dimension/RouteUProofs.lean (22): Pouw.Dimension.RouteUProofs.a1U Pouw.Dimension.RouteUProofs.alg4090WitnessU Pouw.Dimension.RouteUProofs.algBound4090U Pouw.Dimension.RouteUProofs.algBoundCausalU Pouw.Dimension.RouteUProofs.algBoundU Pouw.Dimension.RouteUProofs.algBoundWrappedU Pouw.Dimension.RouteUProofs.algBoundWrappedUUnsigned Pouw.Dimension.RouteUProofs.algSharpU Pouw.Dimension.RouteUProofs.algWitnessU Pouw.Dimension.RouteUProofs.algWrappedWitnessU Pouw.Dimension.RouteUProofs.combUV0Iff Pouw.Dimension.RouteUProofs.indepModShift Pouw.Dimension.RouteUProofs.indepModU Pouw.Dimension.RouteUProofs.mixingLemmaU Pouw.Dimension.RouteUProofs.pricedCountU Pouw.Dimension.RouteUProofs.secondDifferenceU Pouw.Dimension.RouteUProofs.ttNCPAlgU Pouw.Dimension.RouteUProofs.ttNCPOfA1A2U Pouw.Dimension.RouteUProofs.ttNCPOfA1A2W1U Pouw.Dimension.RouteUProofs.ttNCPOfA2U Pouw.Dimension.RouteUProofs.wordCUSubV0 Pouw.Dimension.RouteUProofs.wordUSubV0
TileBound L Proofs/Pouw/TileBound/Fp8.lean (18): Pouw.TileBound.bf16_closed_upto8 Pouw.TileBound.bf16_open_at8 Pouw.TileBound.cost_ge8 Pouw.TileBound.cost_ge8_support Pouw.TileBound.dp4a_closed_upto8 Pouw.TileBound.dp4a_open_at8 Pouw.TileBound.fmt8_closed_iff Pouw.TileBound.fp16_closed_upto8 Pouw.TileBound.fp16_open_at8 Pouw.TileBound.fp32_closed_upto8 Pouw.TileBound.fp32_open_at8 Pouw.TileBound.honest8_cost Pouw.TileBound.honest8_crossOn Pouw.TileBound.honest8_representable Pouw.TileBound.int8_closed_upto8 Pouw.TileBound.int8_open_at8 Pouw.TileBound.tf32_closed_upto8 Pouw.TileBound.tf32_open_at8
TileBound L Proofs/Pouw/TileBound/Fp8Depth.lean (6): Pouw.TileBound.bf16_pays_iff Pouw.TileBound.bf16_region_of_pays Pouw.TileBound.fp32_pays_iff Pouw.TileBound.fp32_region_of_pays Pouw.TileBound.tf32_pays_iff Pouw.TileBound.tf32_region_of_pays
TileBound L Proofs/Pouw/TileBound/Proofs.lean (36): Pouw.TileBound.bilin_support Pouw.TileBound.block_count Pouw.TileBound.cost_ge Pouw.TileBound.cost_ge_support Pouw.TileBound.cost_ge_supportAt Pouw.TileBound.crossOn_of_eval Pouw.TileBound.crossX_count Pouw.TileBound.crossY_count Pouw.TileBound.dp4a_closed_upto Pouw.TileBound.dp4a_open_at Pouw.TileBound.fmt_closed_iff Pouw.TileBound.fp16_closed_upto Pouw.TileBound.fp16_open_at Pouw.TileBound.fp32_closed_upto Pouw.TileBound.fp32_open_at Pouw.TileBound.honest_cost Pouw.TileBound.honest_crossOn Pouw.TileBound.honest_representable Pouw.TileBound.int8_closed_upto Pouw.TileBound.int8_open_at Pouw.TileBound.nLive_all Pouw.TileBound.open_dp4a Pouw.TileBound.open_fp16 Pouw.TileBound.open_fp32 Pouw.TileBound.open_int8 Pouw.TileBound.open_tf32 Pouw.TileBound.quad_support Pouw.TileBound.realizesAt_nonvacuous Pouw.TileBound.realizes_out_at Pouw.TileBound.support_admits_open Pouw.TileBound.support_admits_openAt Pouw.TileBound.tf32_closed_upto Pouw.TileBound.tf32_open_at Pouw.TileBound.tile_cost_ge Pouw.TileBound.tile_cost_ge_of_gates Pouw.TileBound.tile_count
TileBound L Proofs/Pouw/TileBound/WinogradStrassen.lean (2): Pouw.TileBound.int8_winograd_strassen_beats Pouw.TileBound.int8_winograd_strassen_beats_32
TileBound L Proofs/Pouw/TileBound/Witness.lean (1): Pouw.TileBound.tile_chain_satisfiable
Fp8Atom L Proofs/Pouw/Fp8Atom/Fp32Proofs.lean (6): Pouw.Fp8Atom.Proofs.addConformance Pouw.Fp8Atom.Proofs.rnAddAbsorb Pouw.Fp8Atom.Proofs.rnAddExact Pouw.Fp8Atom.Proofs.rnAddMono Pouw.Fp8Atom.Proofs.rnAddMoves Pouw.Fp8Atom.Proofs.wordsRepresentable
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TAtomProofs.lean (3): Pouw.Fp8Atom.H1T.Proofs.h1tAtomValue Pouw.Fp8Atom.H1T.Proofs.trunc14Cell Pouw.Fp8Atom.H1T.Proofs.trunc14Mono
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TFlipProofs.lean (1): Pouw.Fp8Atom.H1T.Proofs.h1tOneFlip
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TGammaProofs.lean (2): Pouw.Fp8Atom.H1T.Proofs.h1tGamma Pouw.Fp8Atom.H1T.Proofs.h1tUnitsDistinct
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TProofs.lean (14): Pouw.Fp8Atom.H1T.Proofs.h1tChainConformance Pouw.Fp8Atom.H1T.Proofs.h1tFormTable Pouw.Fp8Atom.H1T.Proofs.h1tNonVacuous Pouw.Fp8Atom.H1T.Proofs.h1tNotRawWord Pouw.Fp8Atom.H1T.Proofs.h1tPosCard Pouw.Fp8Atom.H1T.Proofs.h1tReadsFields Pouw.Fp8Atom.H1T.Proofs.h1tSaltConformance Pouw.Fp8Atom.H1T.Proofs.h1tTagTable Pouw.Fp8Atom.H1T.Proofs.h1tTupleInjective Pouw.Fp8Atom.H1T.Proofs.h1tTupleWrap Pouw.Fp8Atom.H1T.Proofs.h1tWrapDuplicate Pouw.Fp8Atom.H1T.Proofs.halfOfInvolution Pouw.Fp8Atom.H1T.Proofs.rnAddMovesHalf Pouw.Fp8Atom.H1T.Proofs.rnErr
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TRunningProofs.lean (3): Pouw.Fp8Atom.H1T.Proofs.h1tDistinctLive Pouw.Fp8Atom.H1T.Proofs.h1tGammaRunning Pouw.Fp8Atom.H1T.Proofs.h1tRunningOfDistinct
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TSliceProofs.lean (4): Pouw.Fp8Atom.H1T.Proofs.h1tChainMono Pouw.Fp8Atom.H1T.Proofs.h1tFormCover Pouw.Fp8Atom.H1T.Proofs.h1tRange Pouw.Fp8Atom.H1T.Proofs.h1tSlice
Fp8Atom L Proofs/Pouw/Fp8Atom/H1TTileProofs.lean (2): Pouw.Fp8Atom.H1T.Proofs.tth1tAllRight Pouw.Fp8Atom.H1T.Proofs.tth1tSat
Fp8Atom L Proofs/Pouw/Fp8Atom/Proofs.lean (6): Pouw.Fp8Atom.Proofs.adaCaptures Pouw.Fp8Atom.Proofs.alignedMono Pouw.Fp8Atom.Proofs.codeClasses Pouw.Fp8Atom.Proofs.conformance Pouw.Fp8Atom.Proofs.decodeInjective Pouw.Fp8Atom.Proofs.productExact
Sanity L Proofs/Pouw/Sanity.lean (31): Pouw.Sanity.Wmm_eq_zero Pouw.Sanity.Wref_eq_zero_of_Wmm Pouw.Sanity.Y_last Pouw.Sanity.blockEnd_full Pouw.Sanity.blockEnd_last Pouw.Sanity.certified_le Pouw.Sanity.checkIdx_depth_zero Pouw.Sanity.copy_zero_noise Pouw.Sanity.default_pos Pouw.Sanity.fullGroups_inDomain Pouw.Sanity.identical_checked Pouw.Sanity.index_collision Pouw.Sanity.lone_unit_over_budget Pouw.Sanity.milestone_hypotheses_consistent Pouw.Sanity.noisedAct_rank_zero Pouw.Sanity.omega_lt_inv_one_sub Pouw.Sanity.pr_of_isEmpty Pouw.Sanity.randomized_of_deterministic Pouw.Sanity.reductionGamma_lt_of_omega_lt_one Pouw.Sanity.rowShare_covers Pouw.Sanity.single_unit_not_inDomain Pouw.Sanity.transcript_indep_of_q_zero Pouw.Sanity.tt_admitsRef_bound Pouw.Sanity.tt_event_empty Pouw.Sanity.tt_false_depth_zero Pouw.Sanity.tt_false_of_gamma0_ge_one Pouw.Sanity.tt_false_rank_zero Pouw.Sanity.tt_false_zero_noise Pouw.Sanity.wins_T_zero_iff Pouw.Sanity.wins_empty Pouw.Sanity.wins_of_gamma_ge_one
Barrier L Proofs/Pouw/Barrier/Proofs.lean (10): Pouw.Barrier.Proofs.additive Pouw.Barrier.Proofs.additiveWitness Pouw.Barrier.Proofs.genericPr Pouw.Barrier.Proofs.genericWitness Pouw.Barrier.Proofs.relation Pouw.Barrier.Proofs.relationAdmits Pouw.Barrier.Proofs.relationWitness Pouw.Barrier.Proofs.segment Pouw.Barrier.Proofs.tablesAffine Pouw.Barrier.Proofs.tablesAffineWitness
AlignedExact L Proofs/Pouw/TileBound/AlignedExact.lean (4): Pouw.AlignedExact.card_block_le Pouw.AlignedExact.card_rows_le Pouw.AlignedExact.region_count_given_le Pouw.AlignedExact.region_count_le
~~~
