---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# v2-hot's price twins: the salted hot start at both FP32 prices, generic over the H_i sizing rule

30 Sep 2026, 12:40Z; the fixed sizing rule's values added 13:10Z, the kernel's casts 13:19Z, and the review folded in
14:25Z.

**Status: GO from bc-22298e90 on all 132 pins** (`../statement-review-1350.md`, ~14:20Z, and
`../statement-review-v2-hot.md`'s 13:15Z and 13:55Z deltas). The 34 forming-credited pins first GO'd at their 12:25Z
state are re-GO'd as they are now.

**Still open before v2-hot can merge** (bc-22298e90, 13:55Z and 14:20Z):
- **the rev lane's accounting lemma:** `devSm120v2hot`'s protocol and tiles meet `HotUnitAccounting` and
  `HotTileAccounting`, and their chain-only forms, under the one `h` its record reads;
- **the chain-only `_of_ttOut`:** TT_OUT at the forming-credited v2-hot protocol gives it at the chain-only one, as
  `../Pouw/PearlC/ChainOnlyGamma.lean` does for v2. It can only be stated once the protocol is defined;
- **a TT_OUT grant** for `tt-out/pearl-c-sm120-unpromoted-hot` that names both FP32 prices (8.00 and `1047/125`) and the
  sizing rule, `HotSizing.publicConst 64`.

## Ready for M2b (16:05Z)

M2b merges only the GO'd set (bc-824e54a2, 15:55Z). From this folder, that set is:

| File | sha256 (first 16) | What it is |
| --- | --- | --- |
| `Pouw/PearlC/DeviceHot.lean` | `ac086cc310ba5500` | trusted, definitions only |
| `Pouw/PearlC/HotGamma.lean` | `842e9d04167d47fc` | proofs, generated |
| `v2-hot-pins.json` | `c11eafaa9d949f02` | the 132 GO'd records and one `layers` entry (`DeviceHot`) |
| `v2-hot-pins-store-print.json` | `516b26da1dcc4e4c` | the same 132 records, printed by the store's audit tool (option (b) below) |

Every file is unchanged since the GOs (13:22Z), and the records are the GO'd ones.

**Imports.** `DeviceHot` imports `DevicePrices` and `DevicePricesLoop`, and `HotGamma` imports `TileGamma` and
`DeviceHot`. `DevicePricesLoop` lands with M2a, so M2b goes after it, as planned.

**`SaltDead`: none of the 132 records reads it.** Every twin and value lemma is generic over the record. So M2b's verify
needs no moved-read allowance for them. This is exact: per-pin reads from both the workspace's and the store's audit
tools, over the same build.

**The printed signatures.** All 132 records print raw notation under the workspace's newer audit tool, such as
`Eq d.G 0` and `(…).cast`. That is the same effect as M2a's 168 (the merge plan's blocker 1).
- **Under the store's vendored tool** (`lean/tools/lean`, `VENDORED-FROM 6746f408`), run over a copy of the same build,
  they print as the store's records do: `d.G = 0` and `↑(…)`.
- **Every type hash and every assumptions list is equal** between the two tools. Only the signature text differs.
- So either of the plan's ways works:
  - **(a)** accept by type hash and assumptions (`--accept-print-only`);
  - **(b)** take `v2-hot-pins-store-print.json`, which a byte-equal check against the store tool's `--update` passes.

**It fits the rev lane's 11 pins.** bc-b58c6093's `DeviceV2Hot` imports this folder's `DeviceHot`, and its accounting
lemmas conclude `HotUnitAccounting` and the other three forms. I checked this with a scratch file that isn't staged:
- It composes their `TTOutPearlCDevHot` (moved to the kernel term by `ttOut_wref`), their
  `hotUnitAccounting_sm120v2hot`, this folder's `pearlCGammaSm120v2HotLoopCast8_8192` and
  `gammaHot_sm120v2HotLoopCast8_publicConst64_8192`.
- The result is `G_γ` at `1521365753/420071150000` (0.36217%), with only the standard axioms.
- It was built against these files, byte-identical to the store's.
- So their end-to-end compositions can cite the twins as they stand.

**What M2b still needs, none of it from this folder:**
- bc-22298e90's GO on bc-b58c6093's `OperandOK` guard, and on the compositions or the `W_ref ≥ 0` lemma;
- the TT_OUT grant naming both FP32 prices and `HotSizing.publicConst 64`.

**History.** GO from bc-22298e90 on the 34 forming-credited pins (`../statement-review-v2-hot.md`, ~12:50Z, which read
the 12:25Z state). Since that state:
- the 34 chain-only pins were added (12:30Z);
- the column-RMS pass's FMA is priced at the measured 8.46 (note (a) there, and the pous root's correction), which
  changes the 16 column-RMS values only;
- `HotSizing` now carries H_i's column scale as well as its cost, so one `h` fixes both (note 3);
- the public-constant rule takes its constant as a parameter;
- **13:10Z: the sizing rule is fixed as `HotSizing.publicConst 64`** (bc-b58c6093's rerun, `ttout-restatements.md` §8).
  16 value lemmas at `c₀ = 64` sit beside the any-`c₀` ones, each the any-`c₀` lemma applied at 64, so the published
  figures cite the fixed rule (below, "What the published figures cite").
- **13:19Z: the kernel's casts.** 32 twins and 16 values at `publicConst 64` at the as-written cast 32.06 and the packed
  16, so v2-hot can be set beside v2's published 0.647% at the same cast (below, "v2-hot against v2 at the same cast").
- **13:50Z: sent to bc-22298e90 for review** with everything since its GO (`../review-request-1350.md`, sets C1–C4): the
  16 `publicConst 64` values, the 48 at casts 32.06 and 16, the 34 chain-only pins, and the 34 GO'd pins as changed at
  12:36Z.

Worker bc-876ca543, for the pous root (bc-b729c175). Staging only: nothing here is pinned, and no file outside this
folder changed.

**The version.** `pearl-c-sm120 v2-hot` is v2 (no promotion, cap 1/1,000) with a salted hot start, from bc-3006c44a's
design (`internal/pouw/rtx-pro/theory-pearl-c-sm120.md` §14) as bc-b58c6093 measured it
(`internal/pouw/ttout-restatements.md` §8).
- Each word's accumulator starts at a per-row `H_i` instead of +0. `H_i`'s sign and mantissa come from a sub-domain of
  row i's `E_A` seed, and its exponent from a public sizing rule.
- U = fl(C̃ − H_i). C̃ and U change bit for bit, so this is a version change.
- The honest cost is the same `mma.sync` count plus:
  - one FP32 add per word, for U's removal;
  - the sizing rule's work;
  - one keyed-hash block per row.

## What is priced, and where

| Item | Where | Why |
| --- | --- | --- |
| U's removal, one FP32 add per word | credit and `W_ref` (`creditDevHot = creditDev + add·m·n`); the cap is on this credit | forced clean-up, credited (§14, Pearl-C4 T1's precedent) |
| `H_i` in the first atom's accumulator | nowhere | it replaces the zero fill, with no extra MMA or main-loop instruction (§8) |
| the sizing rule | `W_ref` only (`HotSizing.cost`); the record reads its column scale (`HotSizing.colMeanSq`) | `publicConst c₀`: nothing beyond forming's α_i·ρ_i. `colRms`: a pass over B̃, one FP32 FMA per element, `n·k` per unit at the measured 8.46 (§8), above both FP32 prices |
| the keyed-hash block per row | the hashing format's accounting (`docs/pouw/hashing-accounting.md`), not W1's `W_ref` | as `E_A`'s own seeds are |
| the cast and the in-loop A-only forming | `W_ref` (`c` per activation element, as in `../Pouw/PearlC/DeviceKernelWref.lean`) | the honest cast less the credited 8, plus, at 8.376, the measured 1.047 less the record's 2 |

## How the twins are stated

- **Over any protocol at any record, not at `devSm120v2hot`.** The record is the rev lane's and isn't staged. It needs
  the hot chain, U's removal step and the debit's replay on the hot chain, and `PearlCDevice`'s maps have no input for
  `H_i`, which comes from the seed.
  - So each twin holds for any protocol `P`, domain `D` and record `d` with `G = 0` and the twin's prices. The
    hypotheses are that `P` meets v2-hot's accounting at `d` (`HotUnitAccounting`, or `HotTileAccounting` per tile) and
    that TT_OUT holds at `P`.
  - The accounting says: a unit within the cap has `W_ref = wrefDevHot` and is credited at least
    `(1 − ρ)·creditDevHot`. That holds for any protocol whose credit is `creditDevHot − debit`, whose cap is
    `debit ≤ ρ·creditDevHot`, and whose `W_ref` is `wrefDevHot`.
  - `devSm120v2hot`'s protocol meets it by one lemma, once the rev lane defines it. TT_OUT at that protocol is
    `tt-out/pearl-c-sm120-unpromoted-hot` (rated B, `internal/pouw/red-team/v2-hot-start.md`).
- **One `h` for H_i and `W_ref`.** A `HotSizing` holds both parts of a rule:
  - `colMeanSq`, the square of the column scale in H_i's exponent, which the v2-hot record reads to form H_i;
  - `cost`, which `W_ref` reads.
  The rev lane's record and its one accounting lemma should take the same `h`, so that a protocol built on one rule
  can't be cited with another rule's cheaper `W_ref`. The general theorems keep `h` and the kernel term `c` as
  parameters for that lemma (bc-22298e90's note 3).
- **Generic over the H_i sizing rule.** Every twin is stated for every `h : HotSizing`, with γ written as
  `gammaHot d h c ρ s`, or `gammaHotChainOnly …` for the chain-only pins.
  - Choosing `HotSizing.publicConst` or `HotSizing.colRms` only instantiates `h`, so nothing is re-proved.
  - At casts 8 and 8.72, 32 value lemmas give the numbers for each rule, the public-constant ones for any `c₀`, and 16
    more give them at the fixed rule `HotSizing.publicConst 64` (`…_publicConst64_…`). At casts 32.06 and 16 only the
    16 `publicConst 64` values are given.
  - A third rule is a new `HotSizing` and a rerun of `gen_hot_gamma.py`.
- **v2-hot's TT_OUT differs between FADD 8.00 and 8.376.** U's removal puts the FP32 add into the credit. So unlike v2
  (`../Pouw/PearlC/DeviceSm120v2LoopEquiv.lean`), a grant has to name both prices.

## The values

v2-hot at the cap 1/1,000. Each value is two pins, per unit (`pearlCGamma…`) and per audit tile (`pearlCSampled…`),
with the same γ. The in-loop price is FADD `1047/125` = 8.376, `Prices.sm120Loop`'s, which FP4 now uses too
(bc-824e54a2, 12:16Z).

The pins are named after the record and cast:
- `…Sm120v2Hot{Cast8,Cast8p72,Cast32p06,Cast16}_…` at FADD 8.00;
- `…Sm120v2HotLoop{Cast8,Cast8p72,Cast32p06,Cast16}_…` at 8.376;
- the chain-only pins add `ChainOnly` before the shape.

The values are the lemmas `gammaHot_…` and `gammaHotChainOnly_…`, one per sizing rule. The public-constant tables'
values are pinned twice: for any `c₀` (`…_publicConst_…`) and at the fixed `c₀ = 64` (`…_publicConst64_…`).

### What the published figures cite

The fixed rule is `h := HotSizing.publicConst 64`. Each figure is one twin at that `h` and one value lemma, per unit
(`pearlCGamma…`) or per audit tile (`pearlCSampled…`):

| Published figure | Twin, at `h := HotSizing.publicConst 64` | Value lemma | Exact value |
| --- | --- | --- | --- |
| 0.36217%, forming credited, 8,192³, FADD 8.376 | `pearlC{Gamma,Sampled}Sm120v2HotLoopCast8_8192` | `gammaHot_sm120v2HotLoopCast8_publicConst64_8192` | `1521365753/420071150000` (0.36217%) |
| 0.837%, chain-only, 8,192³, FADD 8.376 | `pearlC{Gamma,Sampled}Sm120v2HotLoopCast8ChainOnly_8192` | `gammaHotChainOnly_sm120v2HotLoopCast8_publicConst64_8192` | `3516365753/420071150000` (0.83709%) |

| 0.64670%, forming credited, 8,192³, FADD 8.376, as-written cast 32.06 | `pearlC{Gamma,Sampled}Sm120v2HotLoopCast32p06_8192` | `gammaHot_sm120v2HotLoopCast32p06_publicConst64_8192` | `2724365753/421274150000` (0.64670%) |
| 1.12026%, chain-only, 8,192³, FADD 8.376, as-written cast 32.06 | `pearlC{Gamma,Sampled}Sm120v2HotLoopCast32p06ChainOnly_8192` | `gammaHotChainOnly_sm120v2HotLoopCast32p06_publicConst64_8192` | `4719365753/421274150000` (1.12026%) |

The 16,384³ rows and the casts 8.72 and 16 cite the same way, from the tables below. In every row the value at 8.376
is the larger of the two prices, so it is the one published; the 8.00 twins and values sit beside it.

### v2-hot against v2 at the same cast

v2's published 0.647% is at the as-written cast 32.06, and v2-hot's 0.36217% at the statement's 8, so the two can't be
compared as they stand. At the same cast, v2-hot (at `publicConst 64`) and v2 (cap 1/1,000, the kernel pins
`pearlC{Gamma,Sampled}Sm120v2{,Loop}{Cast32p06,Cast16}{,ChainOnly}Cap1000_…` in
`../Pouw/PearlC/DeviceSm120KernelGamma.lean`) give:

| Cast, reading | Shape | v2-hot, FADD 8.00 | v2-hot, FADD `1047/125` = 8.376 | v2-hot published (8.376) | v2 published (8.376) | v2-hot − v2, points |
| --- | --- | --- | --- | --- | --- | --- |
| 32.06 (as written), forming credited | 8,192³ | `1111/171940` (0.64616%) | `2724365753/421274150000` (0.64670%) | 0.64670% | 0.64699% | −0.00029 |
| 32.06 (as written), forming credited | 16,384³ | `230807/46158500` (0.50003%) | `461882417/92319350000` (0.50031%) | 0.50031% | 0.50039% | −0.00008 |
| 32.06 (as written), chain-only | 8,192³ | `13477/1203580` (1.11974%) | `4719365753/421274150000` (1.12026%) | 1.12026% | 1.12103% | −0.00077 |
| 32.06 (as written), chain-only | 16,384³ | `1024921/138475500` (0.74015%) | `2050647251/276958050000` (0.74042%) | 0.74042% | 0.74062% | −0.00020 |
| 16 (packed), forming credited | 8,192³ | `12793/2803000` (0.45640%) | `640455251/140157050000` (0.45696%) | 0.45696% | 0.45706% | −0.00010 |
| 16 (packed), forming credited | 16,384³ | `1675763/415025000` (0.40377%) | `3353941753/830071150000` (0.40405%) | 0.40405% | 0.40408% | −0.00003 |
| 16 (packed), chain-only | 8,192³ | `26093/2803000` (0.93090%) | `1305455251/140157050000` (0.93142%) | 0.93142% | 0.93200% | −0.00058 |
| 16 (packed), chain-only | 16,384³ | `2673263/415025000` (0.64412%) | `5348941753/830071150000` (0.64440%) | 0.64440% | 0.64454% | −0.00014 |

- **At the same cast, v2-hot is equal to v2 within 0.001 points**: 0.64670% against 0.64699% as written, and
  1.12026% against 1.12103% chain-only.
- **The gap is a normalization effect** (bc-22298e90, `../statement-review-1350.md` §5).
  - U's forced removal adds the same `add·n/k` per m·k to `W_ref`, and `(1 − ρ)` of it to the worst-case credit, in
    both readings.
  - `W_ref` exceeds that credit, so the ratio moves toward 1 and γ falls a little, by about
    `add·(n/k)·(W_ref − credit)/W_ref²`. That is proportional to `W_ref`'s surplus over the credited worst case.
  - Forming credited, the surplus is `qa + c + ρ·credit`, which grows with the cast. Chain-only, it also holds the
    forming `fs·m·k`, so it is large even at cast 8.
  - It says nothing about v2-hot being cheaper for an adversary or harder to undercut.
- **The gap by reading and cast:**

  | Casts | Reading | v2 − v2-hot, points |
  | --- | --- | --- |
  | 8 and 8.72 | forming credited | 0.000003–0.00002 (at cast 8, 8,192³: 0.36218% against 0.36217%) |
  | 8 and 8.72 | chain-only | 0.00012–0.00050 (at cast 8, 8,192³, 8.376: 0.83757% against 0.83709%) |
  | 32.06 and 16 | both | 0.00003–0.00077 (the table above) |
- In every row 8.376 is the larger price, for v2-hot and v2 alike.

**Forming credited, public-constant sizing (fixed at `c₀ = 64`; the same values hold for any constant):**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `30379/8401000` (0.36161%) | `1521365753/420071150000` (0.36217%) | 0.36217% (8.376) |
| 8 | 16,384³ | `491921/138275000` (0.35576%) | `140663893/39508150000` (0.35604%) | 0.35604% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `31099/8401720` (0.37015%) | `1557365753/420107150000` (0.37071%) | 0.37071% (8.376) |
| 8.72 | 16,384³ | `497921/138281000` (0.36008%) | `996647251/276569050000` (0.36036%) | 0.36036% (8.376) |

**Forming credited, column-RMS sizing (a pass over B̃ per unit, its FMA at the measured 8.46):**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `38839/8409460` (0.46185%) | `1944365753/420494150000` (0.46240%) | 0.46240% (8.376) |
| 8 | 16,384³ | `562421/138345500` (0.40653%) | `1125647251/276698050000` (0.40681%) | 0.40681% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `39559/8410180` (0.47037%) | `1980365753/420530150000` (0.47092%) | 0.47092% (8.376) |
| 8.72 | 16,384³ | `81203/19764500` (0.41085%) | `30747223/7478650000` (0.41113%) | 0.41113% (8.376) |

**Chain-only, public-constant sizing (fixed at `c₀ = 64`; the same values hold for any constant):**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `70279/8401000` (0.83656%) | `3516365753/420071150000` (0.83709%) | 0.83709% (8.376) |
| 8 | 16,384³ | `824421/138275000` (0.59622%) | `235663893/39508150000` (0.59649%) | 0.59649% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `70999/8401720` (0.84505%) | `3552365753/420107150000` (0.84559%) | 0.84559% (8.376) |
| 8.72 | 16,384³ | `830421/138281000` (0.60053%) | `1661647251/276569050000` (0.60081%) | 0.60081% (8.376) |

**Chain-only, column-RMS sizing (a pass over B̃ per unit, its FMA at the measured 8.46):**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `78739/8409460` (0.93631%) | `3939365753/420494150000` (0.93684%) | 0.93684% (8.376) |
| 8 | 16,384³ | `894921/138345500` (0.64687%) | `1790647251/276698050000` (0.64715%) | 0.64715% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `79459/8410180` (0.94480%) | `3975365753/420530150000` (0.94532%) | 0.94532% (8.376) |
| 8.72 | 16,384³ | `128703/19764500` (0.65118%) | `1802647251/276710050000` (0.65146%) | 0.65146% (8.376) |

**Cross-checks and readings:**
- **Against §14:** with public-constant sizing and the statement's cast, these are bc-3006c44a's figures. §14 gives
  0.3616% at 8.00 and 0.3622% at the in-loop price (its "8.38"), and "0.356%" at 16,384³.
- **Against v2:** forming credited, these equal v2's exact in-loop values
  (`../Pouw/PearlC/DeviceSm120KernelGamma.lean`'s `…LoopCast8…` pins, 0.36218% and 0.35604%) to within 0.00001 points.
  Chain-only they are within 0.0005 (the section "v2-hot against v2 at the same cast"). Crediting the removal is what
  keeps γ unchanged; left uncredited, it would cost about 0.095 points (§14).
- **Column-RMS costs about 0.10 points at 8,192³ and 0.05 at 16,384³.** That is in line with §8, which puts the pass at
  about 0.1% of the credit at m = 8,192. At decode's m = 32 it would be about 26%.
  - The FMA is at the measured 8.46 at both FP32 prices. At the FADD price (8.00 or 8.376) γ came out 0.001–0.005
    points lower, the non-conservative direction.
  - The pass is charged per unit, which is an upper bound when several units share B̃.
- **A grant names the prices and the sizing rule.** v2-hot's TT_OUT differs between the two prices. It also differs
  between sizing rules, since H_i sets where the chain starts. The grant should name the rule the panel publishes
  (public constant), and the assessor should say that its B carries to it (bc-22298e90's note 4).
- **Chain-only** with public-constant sizing and the statement's cast gives 0.83656% / 0.83709% at 8,192³ (FADD 8.00 /
  8.376), matching §14's 0.8366% / 0.8371%.
  - U's removal stays in the chain-only credit, because it is clean-up, not forming.
  - The chain-only protocol has the forming-credited one's game, since neither `G_γ` nor `GγSampled` reads the credit.
  - Its TT_OUT is the weaker one, by `../Pouw/PearlC/ChainOnlyGamma.lean`'s argument.

## Files

| File | Kind | What it holds |
| --- | --- | --- |
| `Pouw/PearlC/DeviceHot.lean` | trusted, definitions only | `HotSizing` (H_i's column scale and its cost; `publicConst c₀`, `colRms`), `creditDevHot`, `wrefDevHot`, `gammaHot`, `HotUnitAccounting`, `HotTileAccounting`, and their chain-only forms |
| `Pouw/PearlC/HotGamma.lean` | proofs, generated | the four general theorems (`pearlC{Gamma,Sampled}Hot{,ChainOnly}At`); at casts 8 and 8.72, 32 twins, 32 values per sizing rule and 16 at `HotSizing.publicConst 64`; at casts 32.06 and 16, 32 twins and 16 values at `publicConst 64` |
| `gen_hot_gamma.py` | generator | writes `HotGamma.lean` (stdlib only, exact arithmetic); a new cast or sizing rule is one line, the fixed constant is `C0`, and `ALL_RULES` names the casts with values for every rule |
| `v2-hot-pins.json` | records | the 132 pins as `audit.py --update` wrote them, and the `layers` entry for `DeviceHot` |
| `v2-hot-pins-store-print.json` | records | the same 132, printed by the store's vendored audit tool (the section "Ready for M2b") |

## Checks

These were built in the same private copy as `../` (the build section of `../README.md`). `DeviceHot` imports
`DevicePrices` and `../`'s `DevicePricesLoop`.
- `#print axioms` on the 132 pins: `[propext, Classical.choice, Quot.sound]`.
- Kernel replay of the two modules: 174 constants accepted (13:19Z).
- `audit.py --update --no-replay` over the whole copy (13:19Z): PASS, 9,985 declarations in 217 modules, 747 pins.
  - Against the 13:10Z records, the 32 twins and 16 values at casts 32.06 and 16 are new, and nothing changed.
- The 13:10Z audit (9,937 declarations, 699 pins), against the 13:04Z records: the 16 `…_publicConst64_…` values at
  casts 8 and 8.72 are new, and nothing changed.
- The 12:36Z audit (9,770 declarations, 596 pins), against the 12:30Z records:
  - the 32 value lemmas changed: the 16 column-RMS values moved, and the 16 public-constant ones now hold for any `c₀`;
  - the 36 twins and general theorems keep their statements, and their reads of `HotSizing` changed with its new field;
  - no record outside this folder changed.
