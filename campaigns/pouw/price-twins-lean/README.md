---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# Price twins: `Prices.sm120Loop` and the FP8 γ instances in the loop

30 Sep 2026. Worker bc-876ca543, for the FP8 coordinator (bc-824e54a2): item 3 of §10 of
`internal/pouw-fp8/pearl-c-lean-split.md`. This folder is staging only. Nothing here is pinned, and no file outside this
folder changed: not the store's `lean/`, `ttout-lean-staging/` or `ttout-fp4-staging/`. The pins below go to bc-22298e90
with the next bundle.

**Status (30 Sep, 14:25Z), for the RTX PRO coordinator (bc-2aa33ad8): publish these figures, each from its pin.**
The panel's "have no pin" and "pending" notes can go. All figures are at 8,192³ unless marked, and each is the larger
of FADD 8.00 and `1047/125` = 8.376:
- **FP8 chain-only at the kernel's casts** (this folder, `DeviceSm120KernelGamma.lean`):
  - v1 as written (32.06): 1.22614% (8.00), and 0.86723% at 16,384³;
  - v1 packed (16): 1.04800% (8.00), and 0.77682% at 16,384³;
  - v2 as written: 1.12103% (8.376), and 0.74062% at 16,384³;
  - v2 packed: 0.93200% (8.376), and 0.64454% at 16,384³.
- **v2's chain cap at the exact in-loop price** (`ChainCapKernelGamma.lean`, 13:48Z), at 8.376:
  - per unit: 0.35980%, and 0.35484% at 16,384³;
  - per audit tile: 0.36218% and 0.35604%, the unit cap's values.
- **v2-hot at `HotSizing.publicConst 64`** (`v2-hot/README.md`), forming credited / chain-only, all at 8.376:
  - at the statement's cast 8: 0.36217% / 0.83709%;
  - as written (32.06): 0.64670% / 1.12026%;
  - packed (16): 0.45696% / 0.93142%.
  - At the same cast v2-hot is **equal to v2 within 0.001 points**: v2 is 0.64699% / 1.12103% as written. The small
    gap is a normalization effect of crediting U's removal on both sides, not a cost difference
    (`v2-hot/README.md`, "v2-hot against v2 at the same cast").
- **v1-hot at `HotSizing.publicConst 64`** (`v1-hot/README.md`). bc-22298e90 GO'd it at 14:55Z
  (`statement-review-v1-hot.md`), and it stays staged until Daniel decides whether to adopt v1-hot:
  - at the statement's cast, forming credited 0.51176% (8.376) and chain-only 0.95930% (8.00), and 0.50564% / 0.73196%
    at 16,384³;
  - as written (32.06), 0.77931% / 1.22617%, both at FADD 8.00: the as-written cast is the one where forming credited
    is also larger at 8.00;
  - at the same cast it is equal to v1 within 0.001 points.
- **Pearl-C4 on the ruled `lut256` path, at 8.376** (`fp4-delta/README.md`), forming credited / chain-only. These are
  held behind the base-split fix, which moves none of them (`fp4-delta/README.md`, "Under the base-split fix"):
  - v1: 0.71732% / 1.93807%, and 0.61102% / 1.23638% at 16,384³;
  - v2: 0.71689% / 1.93528%, and 0.61091% / 1.23564% at 16,384³.

The rest of the uncited scan, and what each owner could change, is in `uncited.md`.

**Review: GO from bc-22298e90 on everything staged** (`statement-review-1350.md`, ~14:20Z, answering
`review-request-1350.md`). That is:
- this folder's 182 FP8 pins, the chain cap's six included;
- `v2-hot/`'s 132;
- `fp4-delta/`'s 59, which stay held behind the base-split fix.

v2-hot's merge still needs three things, listed in `v2-hot/README.md`: the rev lane's accounting lemma, the chain-only
`_of_ttOut`, and a TT_OUT grant naming both FP32 prices and the sizing rule.

**Status (30 Sep, 11:40Z):** bc-22298e90 gave the 128 FP8 pins a GO, conditional on rev2's record definitions
(`statement-review.md`). Its three notes are acted on in `statement-review-delta.md`, which adds 16 pins. At 13:05Z,
32 kernel chain-only pins at casts 32.06 and 16 were added, and at 13:48Z six chain-cap pins against the kernel's
`W_ref`. There are now 182 proposed FP8 pins in `proposed-pins.json`, and the full audit passes over them (the build
section, at the end).

**The rule.** γ is computed at the issue-bound FP32 add (8.00) and at the measured in-loop one (8.376), and the larger is
published. Until now the FP8 instances existed only at 8.00 (`Prices.sm120`) and the FP4 ones only at 8.38
(`Fp4Prices.sm120`). This folder adds the missing half of each pair. The four FP4 twins are a separate delta in
`fp4-delta/` (its `README.md`), restated at the repriced forming (`fs` 107.34 in the loop). v2-hot's price twins (the salted hot start,
a version change) are in `v2-hot/`, and v1-hot's (v1's groups from a salted start) in `v1-hot/`, each with its
`README.md`.

**What to cite for sm_120.** Cite the instances at the actual records, `devSm120v1` and `devSm120v2`:
bc-5382063c's `internal/pouw-fp8/device-sm120-staging/Pouw/PearlC/DeviceSm120Gamma.lean` at `Prices.sm120` (8.00), and
their twins at `Prices.sm120Loop` (8.376) in this folder's `DeviceSm120LoopGamma.lean`. Both ride on the TT_OUT rev2
bundle. The section "At the sm_120 records" below lists the pairs.

**The kernel as it runs.** The panel publishes γ against the honest kernel's cast: 32.06 as written, 16.00 packed, and
8.72 with wide stores (the target). Those figures are backed by `DeviceSm120KernelGamma.lean`:
- v1 rev1 and v2 at cap 1/1,000, per unit and per tile, at 8,192³ and 16,384³, at both FP32 prices;
- forming-credited at every cast, and chain-only at 8.72, 32.06 and 16;
- reproducing §13 of `internal/pouw/rtx-pro/theory-pearl-c-sm120.md` exactly.

See the section "γ against the kernel as it runs".

**Outcome.** Every twin builds, with only the standard axioms, and the kernel replays it. In the loop every FP8 γ is
above its issue-bound twin, so the rule publishes the loop values. For FP4 the issue-bound γ is below the existing
in-loop headline, so the headline stands.

**One caveat.** The FP8 in-loop record rounds the A-only forming (1.047) up to 2, because `Costs` holds whole numbers
(next section). The FP8 twins therefore sit 0.005 to 0.011 percentage points above the exact in-loop γ, and are safe
upper bounds on it. The kernel pins carry the 1.047 exactly.

**The convention.** The cast is credited at its cheapest implementation, 8.0, at both FP32 prices: the coordinator's
ruling of 10:49Z. There is one in-loop record, `Prices.sm120Loop`. Its FADD is the measured `1047/125` = 8.376, which
FP4's in-loop record now uses too (bc-824e54a2, 12:16Z). Where a table says "8.376", that exact value was used.

## The files (`Pouw/PearlC/`)

| File | Kind | What it holds |
| --- | --- | --- |
| `DevicePricesLoop.lean` | trusted, definitions only | `Prices.sm120Loop`, the one in-loop record, at FADD `1047/125` = 8.376 (twins and kernel pins) |
| `CapLoopGamma.lean` | proofs | the twins of `DeviceCapGamma`'s eight sm_120 instances (v2 at the cap 1/1,000, v1 under rev1) |
| `ChainCapLoopGamma.lean` | proofs | the twins of `DeviceChainCapGamma`'s four (v2 at the chain cap 1/1,000) |
| `UOnlyLoopGamma.lean` | proofs | the twins of `UOnlyGamma`'s two and `TileUOnlyGamma`'s two (U-only binding, 8192³) |
| `DeviceSm120LoopGamma.lean` | proofs | the twins of `DeviceSm120Gamma`'s 16 γ corollaries at `devSm120v1 Prices.sm120Loop` and `devSm120v2 Prices.sm120Loop`, and the two domain lemmas at those records |
| `DeviceKernelWref.lean` | trusted, definitions only | `W_ref` plus `c` per activation element (`wrefDevK`, `wrefDevRev1K`), and the protocol and tiles with it |
| `KernelWrefGamma.lean` | proofs | TT_OUT doesn't read `W_ref` (`ttOut_wref`, `ttOutTile_wref`), and the four general γ theorems against that `W_ref` |
| `DeviceChainOnly.lean` | trusted, definitions only | the chain-only credit, protocol and tiles |
| `TTOutChainOnly.lean` | trusted, an assumptions module | the four chain-only TT_OUT forms (each implied by the record's TT_OUT) |
| `ChainOnlyGamma.lean` | proofs | the record's TT_OUT gives the chain-only one (four lemmas), and four general chain-only γ theorems |
| `DeviceSm120KernelGamma.lean` | proofs, generated | the 120 kernel instances at `devSm120v1` and `devSm120v2`: casts 32, 32.06, 16 and 8.72 at FADD 8.00 or 8.376 (chain-only too at 8.72, 32.06 and 16), and the statement's cast 8 at 8.376, which is the exact in-loop value |
| `DeviceSm120v2LoopEquiv.lean` | proofs | v2's TT_OUT is the same statement at both FP32 prices, in all eight forms the twins use |
| `DeviceChainCapKernel.lean` | trusted, definitions only | the chain-cap protocol and tiles with `W_ref` at `wrefDevK` |
| `ChainCapKernelGamma.lean` | proofs | the two general chain-cap γ theorems against the kernel's `W_ref`, and v2's exact in-loop chain-cap values per unit and per tile |

`gen_kernel_gamma.py`, in this folder's root, writes `DeviceSm120KernelGamma.lean` (stdlib only, exact arithmetic).

Each twin copies its original's statement with the prices swapped. It has the same hypotheses (for FP8,
`hp : d.prices = Prices.sm120Loop` replaces `hp : d.prices = Prices.sm120`), uses the same general theorem
(`pearlCGammaDevAt`, `pearlCSampledDevRev1At`, `pearlCGammaDevChainCapAt`, `pearlCSampledDevUOnlyAt`,
`pearlCGammaFp4At`, …), and has the same proof shape (`norm_num` on the credit identity). Only ω and γ differ. The bundle's
`devSm120v1 (pr : Prices)` takes its prices as a parameter, so `devSm120v1 Prices.sm120Loop` meets the v1 twins' `hG` and
`hp` by `rfl`; an `example` in the axiom check confirms it.

## `Prices.sm120Loop`: the cast-credit convention, and why `qa` is rounded

`Prices.sm120Loop := ⟨1047/125, 2, ⟨40, 2⟩⟩`. It is the one 8.38 record, for the twins and the kernel pins alike.
- The FP32 add is 8.376, exact.
- A BF16 MAC is 2.
- The credited forming is 40: the noise atom 32 plus the E4M3 cast at 8.0.
- The A-only forming is `qa = 2`.

**The convention (the coordinator's ruling, 30 Sep 10:49Z).** The cast is credited at its cheapest implementation,
8.0, at both FP32 prices. That is the rule in `DevicePrices`, the panel's, and §13's.
- Crediting the cast higher raises `W_ref` and lowers γ, so 8.0 is the conservative choice.
- It keeps the published figures as they are (v2 0.6463%).
- It replaces the split doc's 44.31 (the cast at its 12.31 loop price), which this record used until 10:49Z. The retired
  `Prices.sm120LoopAdd` had the same credit, but `qa = 1`.

**Why `qa` is rounded.** The A-only forming measured in the loop is 1.047 per element (FADD/8). `Prices.costs` is
`Costs`, whose fields are `ℕ` (`Game.lean`, in the store's base and in the bundle), so the record rounds `qa` up to 2.
- That raises `W_ref` by `0.953·m·k` and leaves the credit alone, so γ rises at every shape. An honest program that fits
  the exact in-loop `W_ref` also fits this record's, which is larger.
- The kernel pins don't round. Their `W_ref` carries the difference exactly (`c = h − 8.953`), so they equal the
  panel's figures.
- **Whether a grant at `Prices.sm120` covers `Prices.sm120Loop`:**
  - **v2 (G = 0): yes, it's the same statement.** The FP32 add enters neither v2's credit nor its debit, and `qa`
    enters only `W_ref`, which TT_OUT doesn't read. `DeviceSm120v2LoopEquiv` proves this for all eight TT_OUT forms at
    `devSm120v2`: the cap, the chain cap, U-only and chain-only, each per unit and per tile.
  - **v1 (G = 4): no, it's a different statement.** Its credit prices the promotion adds at the record's add, so a v1
    grant has to name both records (bc-22298e90's note 1).

**How much the rounding costs the twins.** γ at the exact in-loop prices (fs 40, qa 1.047), computed with Python's
`Fraction` from the same formulas the Lean definitions use:

| | 8192³ | 16384³ |
| --- | --- | --- |
| v2 at the cap 1/1,000 (per unit and per tile; also U-only) | 0.36218% | 0.35604% |
| v1 under rev1, cap 1/400 (per unit and per tile; also U-only) | 0.51105% | 0.50528% |
| v2 at the chain cap 1/1,000, per unit | 0.35980% | 0.35484% |

The twins in the pin tables sit 0.011 percentage points above these at 8192³ and about 0.006 at 16384³. Two ways to pin
the exact values:
- change `Costs` to `ℚ≥0` (or `ℚ` with non-negativity hypotheses). This is a base change. In the bundle's policy, 36
  pins read `Game`'s definitions and 31 read `Device`'s; the audit would flag all of them as changed, and each would
  need a statement reviewer;
- restate the twins against `W_ref` plus 0.047 per element (the kernel pins' form at a cast of 8).

Neither is done here.

**The rounded twins are upper bounds; the exact in-loop values are pinned.** Each twin at `Prices.sm120Loop` is an upper
bound on the in-loop γ, labelled so in its docstring and in `proposed-pins.json`'s `labels`. The exact values, at
`qa` = 1.047, are pinned as the kernel form at the statement's own cast (`…LoopCast8…` in `DeviceSm120KernelGamma`).
Those are the figures to publish at 8.38:

| | Exact in-loop pin | 8,192³ | 16,384³ | The rounded twin |
| --- | --- | --- | --- | --- |
| v2 at the cap 1/1,000 | `pearlC{Gamma,Sampled}Sm120v2LoopCast8Cap1000_…` | 0.36218% | 0.35604% | 0.37349%, 0.36177% |
| v1 under rev1 | `pearlC{Gamma,Sampled}Sm120v1LoopCast8Rev1_…` | 0.51105% | 0.50528% | 0.52168%, 0.51065% |
| v2 at the chain cap, per unit | `pearlCGammaSm120v2LoopCast8ChainCap1000_…` (`ChainCapKernelGamma`, 13:48Z) | 0.35980% | 0.35484% | 0.37112%, 0.36056% |
| v2 at the chain cap, per audit tile | `pearlCSampledSm120v2LoopCast8ChainCap1000_…` (`ChainCapKernelGamma`, 13:48Z) | 0.36218% | 0.35604% | 0.37349%, 0.36177% |

Each exact value is still above its issue-bound twin (0.36162%, 0.35576%; 0.51056%, 0.50503%; 0.35925%, 0.35456%), so
8.38 still binds.

**The chain cap's exact values** (`ChainCapKernelGamma.lean`, 13:48Z) are stated as the kernel pins are, at
`devSm120v2 Prices.sm120Loop` with `c = 8 − 8953/1000`:
- `DeviceChainCapKernel.lean` swaps `W_ref` to `wrefDevK` in `pearlCProtocolDevChainCap` and its tiles, and changes
  nothing else;
- the two general theorems take the record's own chain-cap TT_OUT (`TTOutPearlCDevChainCap`, `TTOutTilePearlCDevChainCap`),
  since TT_OUT doesn't read `W_ref` (`ttOut_wref`);
- per unit, `W_ref = ω·(creditDev − ρ·chainCreditDev)`; per tile, a good tile's credit is the unit cap's, so γ is the unit
  cap's exact value;
- at 8.00 the kernel's `W_ref` at the statement's cast is the statement's own, so `DeviceSm120Gamma`'s chain-cap
  instances (0.35925%, 0.35456%) are already the issue-bound values. The U-only twins' exact values are the cap's and rev1's, but no pin states them under U-only binding.

**What the ruling moved** (fs 44 → 40 at 8.38). Every twin rose by at most 0.00006 points:

| Twin | Before | After | Move |
| --- | --- | --- | --- |
| v2 at the cap 1/1,000, 8192³ (unit, tile, U-only, and at `devSm120v2`) | 0.37348% | 0.37349% | +0.000011 |
| v2 at the cap 1/1,000, 16384³ (unit, tile, and at `devSm120v2`) | 0.36176% | 0.36177% | +0.000003 |
| v1 under rev1, 8192³ (unit, tile, U-only, and at `devSm120v1`) | 0.52167% | 0.52168% | +0.000010 |
| v1 under rev1, 16384³ (unit, tile, and at `devSm120v1`) | 0.51065% | 0.51065% | +0.000003 |
| v2 at the chain cap 1/1,000, per unit, 8192³ (and at `devSm120v2`) | 0.37106% | 0.37112% | +0.000058 |
| v2 at the chain cap 1/1,000, per unit, 16384³ (and at `devSm120v2`) | 0.36054% | 0.36056% | +0.000027 |

The chain cap's per-tile rows use the cap's γ and move with it. The 40 kernel pins at 8.38 keep every γ value. Only
their record's name (`Prices.sm120LoopAdd` to `Prices.sm120Loop`) and their `c` term (`h − 8 + 47/1000` to
`h − 8953/1000`) changed.

## The proposed pins

There are 182:
- the 16 below, which hold at any record with the right `G` and prices;
- 18 at the sm_120 records, in the next section, and the 8 v2 equivalence lemmas (`DeviceSm120v2LoopEquiv`);
- 134 against the kernel's `W_ref`, in the section after it: the two transfer lemmas, the four weaker-TT_OUT lemmas,
  eight general theorems and 120 instances (112, plus the 8 exact in-loop rows at the statement's cast);
- 6 for v2's chain cap against the kernel's `W_ref` (`ChainCapKernelGamma`): two general theorems and four exact
  in-loop instances.

The 16 below all live in namespace `Pouw.PearlC`. The issue-bound column is each original's γ. "Published" is the
larger of the two columns, which is what the rule publishes.

**v2 at the cap 1/1,000** (`G = 0`, `CapLoopGamma`):

| Pin | Twin of | γ at `Prices.sm120Loop`, an upper bound (`qa` rounded) | ω | Issue-bound γ | Published |
| --- | --- | --- | --- | --- | --- |
| `pearlCGammaUnpromotedCap1000Loop_8192` | `pearlCGammaUnpromotedCap1000_8192` | `522517/139900000` (0.37349%) | `349750/349317` | 0.36162% | loop |
| `pearlCGammaUnpromotedCap1000Loop_16384` | `pearlCGammaUnpromotedCap1000_16384` | `3000127/829300000` (0.36177%) | `2073250/2070927` | 0.35576% | loop |
| `pearlCSampledUnpromotedCap1000Loop_8192` | `pearlCSampledUnpromotedCap1000_8192` | `522517/139900000` (0.37349%) | `349750/349317` | 0.36162% | loop |
| `pearlCSampledUnpromotedCap1000Loop_16384` | `pearlCSampledUnpromotedCap1000_16384` | `3000127/829300000` (0.36177%) | `2073250/2070927` | 0.35576% | loop |

**v1 under rev1** (`G = 4`, cap 1/400, `CapLoopGamma`):

| Pin | Twin of | γ at `Prices.sm120Loop`, an upper bound (`qa` rounded) | ω | Issue-bound γ | Published |
| --- | --- | --- | --- | --- | --- |
| `pearlCGammaSm120LoopRev1_8192` | `pearlCGammaSm120Rev1_8192` | `310284613/59477920000` (0.52168%) | `148694800/148289813` | 0.51056% | loop |
| `pearlCGammaSm120LoopRev1_16384` | `pearlCGammaSm120Rev1_16384` | `1802569231/352995040000` (0.51065%) | `882487600/880181631` | 0.50503% | loop |
| `pearlCSampledSm120LoopRev1_8192` | `pearlCSampledSm120Rev1_8192` | `310284613/59477920000` (0.52168%) | `148694800/148289813` | 0.51056% | loop |
| `pearlCSampledSm120LoopRev1_16384` | `pearlCSampledSm120Rev1_16384` | `1802569231/352995040000` (0.51065%) | `882487600/880181631` | 0.50503% | loop |

**v2 at the chain cap 1/1,000** (`G = 0`, `ChainCapLoopGamma`). Per tile the γ is the unit cap's, as for the originals:

| Pin | Twin of | γ at `Prices.sm120Loop`, an upper bound (`qa` rounded) | ω | Issue-bound γ | Published |
| --- | --- | --- | --- | --- | --- |
| `pearlCGammaUnpromotedChainCap1000Loop_8192` | `pearlCGammaUnpromotedChainCap1000_8192` | `64899/17487500` (0.37112%) | `524625/523988` | 0.35925% | loop |
| `pearlCGammaUnpromotedChainCap1000Loop_16384` | `pearlCGammaUnpromotedChainCap1000_16384` | `373769/103662500` (0.36056%) | `1036625/1035476` | 0.35456% | loop |
| `pearlCSampledUnpromotedChainCap1000Loop_8192` | `pearlCSampledUnpromotedChainCap1000_8192` | `522517/139900000` (0.37349%) | `349750/349317` | 0.36162% | loop |
| `pearlCSampledUnpromotedChainCap1000Loop_16384` | `pearlCSampledUnpromotedChainCap1000_16384` | `3000127/829300000` (0.36177%) | `2073250/2070927` | 0.35576% | loop |

**U-only binding** (8192³ only, as are the originals; `UOnlyLoopGamma`):

| Pin | Twin of | γ at `Prices.sm120Loop`, an upper bound (`qa` rounded) | ω | Issue-bound γ | Published |
| --- | --- | --- | --- | --- | --- |
| `pearlCGammaUOnlySm120LoopRev1_8192` | `pearlCGammaUOnlySm120Rev1_8192` | `310284613/59477920000` (0.52168%) | `148694800/148289813` | 0.51056% | loop |
| `pearlCGammaUOnlyUnpromotedCap1000Loop_8192` | `pearlCGammaUOnlyUnpromotedCap1000_8192` | `522517/139900000` (0.37349%) | `349750/349317` | 0.36162% | loop |
| `pearlCSampledUOnlySm120LoopRev1_8192` | `pearlCSampledUOnlySm120Rev1_8192` | `310284613/59477920000` (0.52168%) | `148694800/148289813` | 0.51056% | loop |
| `pearlCSampledUOnlyUnpromotedCap1000Loop_8192` | `pearlCSampledUOnlyUnpromotedCap1000_8192` | `522517/139900000` (0.37349%) | `349750/349317` | 0.36162% | loop |

**FP4 at the issue-bound price.** The four Pearl-C4 twins moved to `fp4-delta/` at 11:15Z, restated at the repriced
block scale. The delta has its own pins file, for bc-22298e90 to take separately.

The same script also checks every existing value: at `Prices.sm120` it reproduces each FP8 original's ω and γ exactly,
and at `Fp4Prices.sm120` the FP4 headline.

**Named assumptions.** Each twin takes the same TT_OUT form as its original, at a record with the twin's prices:
`TTOutPearlCDev`, `TTOutTilePearlCDev`, and the `…Rev1`, `…ChainCap` and `…UOnly` forms. None of these hypotheses is
closed, so every record lists `assumptions: []`, as the originals do.

**Which bundle each file lands with.** The next bundle
(`ttout-lean-staging/rev1-tile-device-bundle/lean-audit.json`) pins the originals of `CapLoopGamma`'s and
`UOnlyLoopGamma`'s twins. It does not carry `DeviceChainCap*` or the FP4 files, and does not pin their instances. So
`ChainCapLoopGamma` lands when its originals do. `UOnlyLoopGamma` needs the bundle's
`TileUOnlyGamma`.

`proposed-pins.json` holds all 182 records, as `audit.py --update` wrote them in the build below (signature, assumptions,
type hash). It also holds five proposed `layers` entries:
- for `DevicePricesLoop`, `DeviceKernelWref` and `DeviceChainOnly`, which mirror `DevicePrices`'s entry;
- for `TTOutChainOnly`;
- for `DeviceChainCapKernel`, which may import only `DeviceChainCap` and `DeviceKernelWref` beyond Mathlib and
  `Pouw.Basic`.

It proposes one `assumptions` module, `TTOutChainOnly`. Its `labels` mark the 32 rounded twins, and name the exact
in-loop pin for each but the 8 U-only twins.

**For M2a's verify** (16:05Z), two files, both from the same build as `proposed-pins.json` (`0e330c31…`, the input the
merge plan froze):
- **`saltdead-readers.txt`** is the list the 13:52Z inbox entry asked for: the 150 of the 182 records that read
  `Pouw.PearlC.SaltDead` (`flatLine` and `support`, through `devAt`), one name per line.
  - They are exactly the pins that name `devSm120v1` or `devSm120v2`.
  - The 32 that don't are `CapLoopGamma`'s 8, `ChainOnlyGamma`'s 8, `KernelWrefGamma`'s 6, `ChainCapLoopGamma`'s 4,
    `UOnlyLoopGamma`'s 4 and `ChainCapKernelGamma`'s 2, as the merge plan estimated.
  - The per-pin reads of both the workspace's and the store's audit tools give the same list.
- **`proposed-pins-store-print.json`** holds the same 182 records, printed by the store's vendored audit tool
  (`lean/tools/lean`, `VENDORED-FROM 6746f408`) over a copy of the same build.
  - All 182 type hashes and assumptions lists equal `proposed-pins.json`'s. Only the signature text differs: `d.G = 0`
    and `↑(…)`, where the workspace's newer tool prints `Eq d.G 0` and `(…).cast`.
  - So it is the merge plan's option (b) for blocker 1, and the evidence for option (a).
  - `v2-hot/` has the same pair for M2b (its README, "Ready for M2b").

## At the sm_120 records: `DeviceSm120LoopGamma.lean`

bc-5382063c's `DeviceSm120Gamma.lean` (`internal/pouw-fp8/device-sm120-staging/`, 21 proposed pins) states the γ
corollaries at the actual records, `devSm120v1 Prices.sm120` (G = 4) and `devSm120v2 Prices.sm120` (G = 0). These are
the statements to cite for sm_120. Each twin here is `<this folder's instance> CM (devSm120vX Prices.sm120Loop) sem rfl
rfl hTT`. The two domain lemmas are copied at the in-loop records, so the twins are not vacuous either. The other five
of the 21 (`devAt_sm120_floor`, the flags and floor lemmas) already hold at every `pr : Prices` and need no twin.

| At `Prices.sm120` (8.00), `DeviceSm120Gamma` | At `Prices.sm120Loop` (8.376), `DeviceSm120LoopGamma` | 8.00 | 8.376, an upper bound |
| --- | --- | --- | --- |
| `devSm120v1_domain` | `devSm120v1Loop_domain` | | |
| `devSm120v2_domain` | `devSm120v2Loop_domain` | | |
| `pearlCGammaSm120v1Rev1_8192` | `pearlCGammaSm120v1LoopRev1_8192` | 0.51056% | 0.52168% |
| `pearlCGammaSm120v1Rev1_16384` | `pearlCGammaSm120v1LoopRev1_16384` | 0.50503% | 0.51065% |
| `pearlCSampledSm120v1Rev1_8192` | `pearlCSampledSm120v1LoopRev1_8192` | 0.51056% | 0.52168% |
| `pearlCSampledSm120v1Rev1_16384` | `pearlCSampledSm120v1LoopRev1_16384` | 0.50503% | 0.51065% |
| `pearlCGammaUOnlySm120v1Rev1_8192` | `pearlCGammaUOnlySm120v1LoopRev1_8192` | 0.51056% | 0.52168% |
| `pearlCSampledUOnlySm120v1Rev1_8192` | `pearlCSampledUOnlySm120v1LoopRev1_8192` | 0.51056% | 0.52168% |
| `pearlCGammaSm120v2Cap1000_8192` | `pearlCGammaSm120v2LoopCap1000_8192` | 0.36162% | 0.37349% |
| `pearlCGammaSm120v2Cap1000_16384` | `pearlCGammaSm120v2LoopCap1000_16384` | 0.35576% | 0.36177% |
| `pearlCSampledSm120v2Cap1000_8192` | `pearlCSampledSm120v2LoopCap1000_8192` | 0.36162% | 0.37349% |
| `pearlCSampledSm120v2Cap1000_16384` | `pearlCSampledSm120v2LoopCap1000_16384` | 0.35576% | 0.36177% |
| `pearlCGammaUOnlySm120v2Cap1000_8192` | `pearlCGammaUOnlySm120v2LoopCap1000_8192` | 0.36162% | 0.37349% |
| `pearlCSampledUOnlySm120v2Cap1000_8192` | `pearlCSampledUOnlySm120v2LoopCap1000_8192` | 0.36162% | 0.37349% |
| `pearlCGammaSm120v2ChainCap1000_8192` | `pearlCGammaSm120v2LoopChainCap1000_8192` | 0.35925% | 0.37112% |
| `pearlCGammaSm120v2ChainCap1000_16384` | `pearlCGammaSm120v2LoopChainCap1000_16384` | 0.35456% | 0.36056% |
| `pearlCSampledSm120v2ChainCap1000_8192` | `pearlCSampledSm120v2LoopChainCap1000_8192` | 0.36162% | 0.37349% |
| `pearlCSampledSm120v2ChainCap1000_16384` | `pearlCSampledSm120v2LoopChainCap1000_16384` | 0.35576% | 0.36177% |

The exact fractions are the ones in the tables above: v1 is rev1's row, v2's cap and U-only rows are the cap 1/1,000
row, and the chain cap's per-tile rows are also the cap 1/1,000 row. The rule publishes the 8.376 column. At the exact
in-loop forming it would be 0.51105% and 0.50528% (v1), 0.36218% and 0.35604% (v2 cap), and 0.35980% and 0.35484% (v2
chain cap, per unit). All three are pinned: the first two in `DeviceSm120KernelGamma`, the chain cap in
`ChainCapKernelGamma`.

`DeviceSm120LoopGamma` needs what `DeviceSm120Gamma` needs: the rev1 bundle plus rev2's items 1 and 2, as that folder's
README words them. Those are `device/`'s two chain-cap files; `devAt`'s `flags := fun A B => SkipP.unitFlagsAt p G A B`;
and `def devSm120v2 (pr : Prices) : PearlCDevice := devAt sm120E4m3 0 pr` after `devSm120v1`.

## γ against the kernel as it runs: `DeviceSm120KernelGamma.lean`

The statement's `W_ref` prices the E4M3 cast at the credited 8.0 per code. The kernel as it runs costs more
(`internal/pouw/rtx-pro/server.md`):
- 32.06 as written;
- 16.00 packed four per word;
- 8.72 packed with wide stores, measured by GPU 0 at 10:25Z. This is the kernel's target.

The panel's FP8 γ is against that kernel, and these pins back it. Every value at 8.72 reproduces §13 of
`internal/pouw/rtx-pro/theory-pearl-c-sm120.md` to all four decimals, forming-credited and chain-only, at both prices.

**How it is stated.**
- **The kernel's `W_ref`.** `DeviceKernelWref.lean` adds `c` per activation element to `W_ref` and changes nothing else
  (`wrefDevK`, `wrefDevRev1K`, and the protocol and tiles with them).
  - TT_OUT never reads `W_ref` (`ttOut_wref` and `ttOutTile_wref`, by `rfl`). So each forming-credited pin takes the
    record's own TT_OUT, the same hypothesis as its statement-`W_ref` instance.
  - `KernelWrefGamma.lean` has the four general theorems, at any record and any `c`.
- **The chain-only reading.** `DeviceChainOnly.lean` defines it as `creditChainOnly` does at the H100: the credit less
  `fs·m·k` (`creditDevChainOnly`), with the cap on the full credit. So the worst case is
  `ω = W_ref / (creditDevChainOnly − ρ·creditDev)`.
  - Its TT_OUT forms (`TTOutPearlCDevChainOnly` and its tile and rev1 forms, in the assumptions module
    `TTOutChainOnly`) follow from the record's TT_OUT
    (`ttOutPearlCDevChainOnly_of_ttOut` and three twins in `ChainOnlyGamma.lean`). They are strictly weaker
    assumptions, and the chain-only pins take them.
  - Neither `G_γ` nor `GγSampled` reads the credit, so the chain-only pins state the same game as the forming-credited
    ones, the kernel protocol's. `ChainOnlyGamma.lean` has four more general theorems.
- **The two prices.**
  - 8.00 is `Prices.sm120`, with `c = h − 8`.
  - 8.38 is `Prices.sm120Loop = ⟨1047/125, 2, ⟨40, 2⟩⟩`. It is the twins' record too, with the cast credited at 8.0
    per the 10:49Z ruling. Here `c = h − 8.953`: the honest cast less 8, plus the measured A-only 1.047 less the
    record's rounded 2.
  - Both give `W_ref` exactly, with no rounding.
- **Casts.** 32, the panel's "as written" figure; 32.06, measured; 16; and 8.72. The chain-only reading is stated at
  8.72, 32.06 and 16, the three casts the panel publishes chain-only (13:05Z for 32.06 and 16).

**The 112 instances at the kernel's casts**, at the real records `devSm120v1` and `devSm120v2`. The 8 more at the
statement's own cast (8) and 8.38 are the exact in-loop values; the `Prices.sm120Loop` section lists them. Each row is two pins, the per-unit `Gamma` and
the per-tile `Sampled`, which share one γ. Swap in `…Loop…` after `v1` or `v2` in a name for its 8.38 pin. "Larger"
is what the rule publishes.

| Law, size, honest cast, reading | Pins at FADD 8.00 (`Gamma` unit, `Sampled` tile) | γ at FADD 8.00 | γ at FADD `1047/125` = 8.376 (`…Loop…`) | Larger | Panel / §13, at 8.00 and the in-loop price |
| --- | --- | --- | --- | --- | --- |
| v1 rev1, 8192³, 8.72, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast8p72Rev1_8192` | `115361/22244300` (0.51861%) | `926193839/178429100000` (0.51908%) | 8.376 | 0.5186 / 0.5191 |
| v1 rev1, 16384³, 8.72, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast8p72Rev1_16384` | `2987/586724` (0.50910%) | `599303077/117663460000` (0.50934%) | 8.376 | 0.5091 / 0.5093 |
| v2 cap 1/1,000, 8192³, 8.72, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast8p72Cap1000_8192` | `1553551/419686000` (0.37017%) | `1555901/419688350` (0.37073%) | 8.376 | 0.3702 / 0.3707 |
| v2 cap 1/1,000, 16384³, 8.72, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast8p72Cap1000_16384` | `2986127/829286000` (0.36008%) | `332053/92143150` (0.36037%) | 8.376 | 0.3601 / 0.3604 |
| v1 rev1, 8192³, 8.72, chain-only | `pearlC{Gamma,Sampled}Sm120v1Cast8p72ChainOnlyRev1_8192` | `16547/1711100` (0.96704%) | `1724193839/178429100000` (0.96632%) | 8.00 | 0.9670 / 0.9663 |
| v1 rev1, 16384³, 8.72, chain-only | `pearlC{Gamma,Sampled}Sm120v1Cast8p72ChainOnlyRev1_16384` | `4317/586724` (0.73578%) | `50900181/6921380000` (0.73541%) | 8.00 | 0.7358 / 0.7354 |
| v2 cap 1/1,000, 8192³, 8.72, chain-only | `pearlC{Gamma,Sampled}Sm120v2Cast8p72ChainOnlyCap1000_8192` | `3548551/419686000` (0.84553%) | `3550901/419688350` (0.84608%) | 8.376 | 0.8455 / 0.8461 |
| v2 cap 1/1,000, 16384³, 8.72, chain-only | `pearlC{Gamma,Sampled}Sm120v2Cast8p72ChainOnlyCap1000_16384` | `4981127/829286000` (0.60065%) | `1661159/276429450` (0.60093%) | 8.376 | 0.6007 / 0.6009 |
| v1 rev1, 8192³, 16, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast16Rev1_8192` | `133561/22262500` (0.59994%) | `3277657/546100000` (0.60019%) | 8.376 |  |
| v1 rev1, 16384³, 16, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast16Rev1_16384` | `9689/1760900` (0.55023%) | `1943509231/353135980000` (0.55036%) | 8.376 |  |
| v2 cap 1/1,000, 8192³, 16, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast16Cap1000_8192` | `1917551/420050000` (0.45651%) | `639967/140017450` (0.45706%) | 8.376 |  |
| v2 cap 1/1,000, 16384³, 16, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast16Cap1000_16384` | `1116709/276550000` (0.40380%) | `3352477/829652350` (0.40408%) | 8.376 |  |
| v1 rev1, 8192³, 32, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast32Rev1_8192` | `173561/22302500` (0.77821%) | `1391793839/178894700000` (0.77800%) | 8.00 | 0.778% (the larger) |
| v1 rev1, 16384³, 32, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast32Rev1_16384` | `3763/587500` (0.64051%) | `754503077/117818660000` (0.64039%) | 8.00 | 0.641% (the larger) |
| v2 cap 1/1,000, 8192³, 32, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast32Cap1000_8192` | `143029/22150000` (0.64573%) | `2719901/420852350` (0.64628%) | 8.376 | 0.646% (the larger) |
| v2 cap 1/1,000, 16384³, 32, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast32Cap1000_16384` | `4150127/830450000` (0.49974%) | `197737/39545350` (0.50003%) | 8.376 | 0.500% (the larger) |
| v1 rev1, 8192³, 32.06, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast32p06Rev1_8192` | `173711/22302650` (0.77888%) | `1392993839/178895900000` (0.77866%) | 8.00 |  |
| v1 rev1, 16384³, 32.06, forming credited | `pearlC{Gamma,Sampled}Sm120v1Cast32p06Rev1_16384` | `1255/195834` (0.64085%) | `251634359/39273020000` (0.64073%) | 8.00 |  |
| v2 cap 1/1,000, 8192³, 32.06, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast32p06Cap1000_8192` | `2720551/420853000` (0.64644%) | `2722901/420855350` (0.64699%) | 8.376 |  |
| v2 cap 1/1,000, 16384³, 32.06, forming credited | `pearlC{Gamma,Sampled}Sm120v2Cast32p06Cap1000_16384` | `4153127/830453000` (0.50010%) | `1385159/276818450` (0.50039%) | 8.376 |  |

**The published "as written" figures are backed exactly.**
- v1 is 0.77821% at 8.00, the larger.
- v2 is 0.64628% at 8.38, the larger; that is bc-3006c44a's 0.6463%.
- At the measured 32.06 they become 0.77888% and 0.64699%.
- **Chain-only at 32.06 and 16** (13:05Z) backs the panel's 1.226% / 1.048% / 0.777% (v1) and 1.121% / 0.932% / 0.645%
  (v2) to three decimals. v1's is larger at 8.00 and v2's at 8.376, as for the forming-credited rows.

**The convention.** Both records credit the cast at 8.0, per the ruling in the `Prices.sm120Loop` section above. Under
it the kernel pins reproduce §13 at both prices. If the cast were credited at 12 in the loop (the retired convention),
the 8.38 γ would fall by about 0.045 points, and v2's published figure with it.

**The hook.** A new cast is one line in `CASTS` in `gen_kernel_gamma.py`; a new chain-only row is one entry in
`CHAIN_ONLY`. Rerun the script to regenerate `DeviceSm120KernelGamma.lean`. That is how 8.72 and 32.06 went in.

**Cross-check against bc-3006c44a's linear rule** (v1 chain-only ≈ 0.959% + 0.0111 points per unit above 8, at
8,192³). I evaluated the chain-only reading from the same formulas the pins use:

| Honest cast | 8.0 | 8.5 | 8.72 | 11.7 | 12.31 | 16 | 32 | 32.06 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Exact, 8.00 | 0.9590% | 0.9646% | 0.9670% | 1.0002% | 1.0070% | 1.0480% | 1.2255% | 1.2261% |
| Rule | 0.9590% | 0.9646% | 0.9670% | 1.0001% | 1.0068% | 1.0478% | 1.2254% | 1.2261% |

- They agree to 0.0002 points. The exact slope is 0.01113 per unit at 8 and 0.01110 as a secant to 32.
- The rule's crossings hold too: v1 chain-only crosses 1% at 11.68 (its "~11.7"), and v2 at 21.8 (its "up to about 22").
- So there is no disagreement. Two caveats:
  - the rule holds only at 8,192³ (at 16,384³ the slope is about half);
  - it is chain-only.
- The forming-credited counterpart at 8,192³ and 8.00 is 0.5106% + 0.0112 per unit. It matches the pins to 0.0007
  points; the line runs slightly high at 32 because the curve is concave.
- At 8.72 the pins give 0.96704% chain-only (8.00, the larger), against the rule's 0.96699% and §13's 0.9670.

## Where the FADD price of 32 still appears

Checked in the rev1 bundle's `Device*.lean` (and the `Game.lean` and `DeviceRev1.lean` they read) and in
`DeviceSm120Gamma.lean`. No sm_120 statement carries an FP32 add at 32. Every sm_120 instance reads the add as
`d.prices.add` (`creditDev`, `debitDev`, `firstAddDev`), which is 8 at `Prices.sm120` and 1047/125 at `Prices.sm120Loop`.

The add price 32 appears only on the H100 path, which is correct at H100 prices and should stay:
- `Prices.h100 := ⟨32, 2, Costs.adopted⟩` and `devH100` (`Device.lean`);
- `creditOf` and `debitOf` (`Game.lean`), whose `mkn/G` and `32/G` are the H100 add built in;
- `firstAddOf`'s `32·m·n` (`DeviceRev1.lean`);
- the H100 instances such as `pearlCGammaH100Rev1_*` (`DeviceRev1Gamma.lean`).

Every other 32 in the sm_120 path counts MACs or columns, not the add's price, and must not change to 8.38:
- the noise atom's 32 MACs in `debitDev`'s `(32 + add/G)` per flagged atom;
- `32·G` columns per promotion group and `k/32` atoms per row;
- the 32 noise lines, and `r = 32` in `Params.pi`;
- the forming's `fs`, where the noise atom is 32 of the 40.

## The build

The private copy was assembled in six steps:

1. Start from the store's `lean/submissions/pouw/`, as of 09:20Z.
2. Apply `ttout-lean-staging/rev1-tile-device-bundle/bundle.diff` with `patch -p1`. Every Lean hunk applies. Only the
   `lean-audit.json` hunk fails, because the store's file has moved on, so take the bundle's `lean-audit.json` instead.
3. Add `ttout-lean-staging/device/Pouw/PearlC/DeviceChainCap.lean` and `DeviceChainCapGamma.lean`.
4. Overlay `internal/pouw-fp8/ttout-fp4-staging/Pouw`, then this folder's `Pouw`, `fp4-delta/Pouw` and `v2-hot/Pouw`.
5. For `DeviceSm120Gamma` and its twins, apply rev2's two `Device.lean` items (the previous section) and add
   `internal/pouw-fp8/device-sm120-staging/Pouw/PearlC/DeviceSm120Gamma.lean`.
6. Add to the aggregator `Pouw/PearlC.lean`, after its last import, the imports of `DeviceChainCap`,
   `DeviceChainCapGamma`, `DeviceFp4`, `TTOutFp4`, `DeviceFp4Gamma` and `DeviceSm120Gamma`, then this folder's fourteen modules,
   `fp4-delta/`'s seven and `v2-hot/`'s two.

Then run `lake build`. The toolchain is Lean v4.34.0 with Mathlib at `5ed29652…`.

The checks, and what each gave:

- **`#print axioms`** on all 373 pins (the 182 here, `fp4-delta/`'s 59 and `v2-hot/`'s 132), each run as its pins
  were added: `[propext, Classical.choice, Quot.sound]` each.
- **Kernel replay** (`tools/lean/Replay.lean` on this folder's modules, twelve before 13:48Z): every constant is accepted, with the
  axioms propext, Classical.choice and Quot.sound.
- **Sources:** no `sorry`, `axiom`, `native_decide`, `decide +kernel`, `set_option`, `#eval`, `opaque` or `unsafe`.
- **The full audit, before step 5** (`tools/lean/audit.py --update`, with the 20 generic pins and the two layers added
  to the bundle's policy): PASS. It covered 9,457 declarations in 201 modules, found only the standard axioms, and
  replayed everything through the kernel; 379 pins. The only new records are the 20 pins. No existing pin's statement
  or read definitions changed (77 pins only print differently, which needs no reviewer).
- **The full audit, after step 5** (the 18 record-level pins and bc-5382063c's 21 added to the policy): PASS. It covered
  9,504 declarations in 203 modules and 418 pins, with only the standard axioms and a full kernel replay. The new records
  are the 18 pins. bc-5382063c's 21 records keep their type hashes and assumptions (they only print differently). The
  one changed definition is `devAt`, which is rev2's item 2, as that folder's README says.
- **The full audit with the kernel pins** (all 132 of this folder's pins, bc-5382063c's 21 and four layers added to the
  bundle's policy): PASS. It covered 9,635 declarations in 208 modules and 512 pins, with only the standard axioms and a
  full kernel replay. Relative to the policy before it, the new records are this folder's 56 new kernel pins. The only
  changed records are this folder's 16 earlier 8.38 kernel pins, which moved to `Prices.sm120LoopAdd` (since retired).
  No other pin or definition changed.
- **The full audit after the cast-credit ruling** (one 8.38 record, `Prices.sm120Loop` crediting the cast at 8.0): PASS.
  It covered 9,634 declarations in 208 modules and 512 pins, with only the standard axioms and a full kernel replay.
  - It adds no pin, and changes 72 of this folder's records, as expected: the 32 twins whose γ moved (the table in the
    `Prices.sm120Loop` section), and the 40 kernel pins at 8.38.
  - The kernel pins changed only their record's name and `c` term; every γ value is the same.
  - The two domain lemmas and the four FP4 twins are unchanged. No record outside this folder changed.
- **The full audit after the review notes** (`statement-review-delta.md`): PASS. It covered 9,658 declarations in 210
  modules and 528 pins, with only the standard axioms and a full kernel replay. The new records are the 16 pins of the
  delta. No pin record changed; the only definitions that moved module are the four chain-only props.
- **The kernel chain-only pins at 32.06 and 16** (13:05Z) were checked three ways. Each pass covered this folder and its
  two deltas.
  - `#print axioms` on the 32 new pins gave `[propext, Classical.choice, Quot.sound]`.
  - A kernel replay of `DeviceSm120KernelGamma` accepted 126 constants.
  - `audit.py --update --no-replay` passed at 13:04Z: 9,921 declarations in 217 modules and 683 pins.
  - The new records are these 32 and `fp4-delta/`'s 26. No record changed.
- **The chain cap against the kernel's `W_ref`** (13:48Z). Its two modules were added to the aggregator after
  `DeviceSm120KernelGamma`, and `DeviceChainCapKernel` got a `layers` entry.
  - `#print axioms` on the 6 pins gave `[propext, Classical.choice, Quot.sound]`.
  - A kernel replay of the two modules accepted 11 constants.
  - `audit.py --update --no-replay` passed: 9,996 declarations in 219 modules and 753 pins.
  - The new records are the 6 pins and the two definitions they read. No record changed.
- The 13:19Z audit (after `v2-hot/`'s additions) passed with 9,985 declarations in 217 modules and 747 pins. This
  folder's records were unchanged.
