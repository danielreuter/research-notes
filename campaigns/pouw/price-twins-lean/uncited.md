---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# Published γ, caps and bounds without a Lean pin: `panel.md` and `security-proofs.md`

30 Sep 2026, 13:30Z; the chain cap staged 13:48Z; everything in §1 GO'd by bc-22298e90 at ~14:20Z
(`statement-review-1350.md`; FP4 held). Worker bc-876ca543, for the pous root (bc-b729c175).

**What was scanned:**
- `docs/pouw/panel.md`, bc-2aa33ad8's (the RTX PRO coordinator), in its 13:21Z regeneration;
- `docs/pouw/security-proofs.md`, bc-824e54a2's, as of its 13:31Z edit.

I checked both for published γ values, caps and bounds that don't cite a Lean pin. Neither file was edited: each citation
change below is for its owner.

**Ownership, checked before staging.** Every row of `security-proofs.md` is bc-824e54a2's. The pins staged here are this
lane's: the FP8 kernel pins, v2-hot's twins and the FP4 delta, all in `internal/pouw/price-twins-lean/`. So staging
them doesn't overlap with bc-824e54a2's rows, and doesn't touch another lane's Lean.

All values are at 8,192³ unless marked. "Published" means the larger of FADD 8.00 and `1047/125` = 8.376.

## 1. Staged this turn: cite these

### 1.1 Pearl-C4 v2 (panel `pearl-c-fp4 v2`)

**Where it was uncited:** the panel shows bc-a8466279's `rcp.approx` figures, 0.7169% / 1.983% at 8.38, and says
"v2's `lut256` pins are coming from bc-876ca543". `security-proofs.md` has no FP4 v2 row.

**Now staged, on the ruled `lut256` path** (`theory-pearl-c4-domain.md` §6.6), at 8.376, in `fp4-delta/`. **Held**
behind the base-split fix.

| Figure | Exact value | Twin | Value lemma |
| --- | --- | --- | --- |
| forming credited, 8,192³ | 0.71689% | `pearlC{Gamma,Sampled}Fp4Sm120HotAt_8192` | `gammaFp4Hot_sm120Loop_lut256_8192` |
| chain-only, 8,192³ | 1.93528% | `pearlC{Gamma,Sampled}Fp4Sm120HotChainOnlyAt_8192` | `gammaFp4HotChainOnly_sm120Loop_lut256_8192` |
| forming credited, 16,384³ | 0.61091% | `pearlC{Gamma,Sampled}Fp4Sm120HotAt_16384` | `gammaFp4Hot_sm120Loop_lut256_16384` |
| chain-only, 16,384³ | 1.23564% | `pearlC{Gamma,Sampled}Fp4Sm120HotChainOnlyAt_16384` | `gammaFp4HotChainOnly_sm120Loop_lut256_16384` |

§6.6 gives 0.7170% / 1.936% at 8.38. The `rcp.approx` values are pinned too: 0.71679% / 1.98232%.

### 1.2 FP8 v1 and v2 chain-only at the as-written 32.06 and the packed 16: the most cited

**Where:** all eight FP8 v1 and v2 rows of the panel: v1, v1-h1, v1-h2, v1-h3, v2, v2-h1, v2-h2 and v2-h3. Each says
"The chain-only figures at 32.06 and 16.00 have no pin".

**Why this item was staged first:**
- it is the most-cited uncited group, at six figures in each of eight rows;
- no other lane owns it: the kernel pins are this lane's (`Pouw/PearlC/DeviceSm120KernelGamma.lean`).

**Now staged** (13:05Z, 32 pins, `README.md`'s kernel section). Each figure below is the panel's, and matches its pin
to three decimals:

| Panel figure | Pin value, the larger | Pins at FADD 8.00 (`…Loop…` after `v1` or `v2` for 8.376) |
| --- | --- | --- |
| v1 as written 1.226% | 1.22614% (8.00) | `pearlC{Gamma,Sampled}Sm120v1Cast32p06ChainOnlyRev1_8192` |
| v1 as written, 16,384³ (not on the panel) | 0.86723% (8.00) | `…Sm120v1Cast32p06ChainOnlyRev1_16384` |
| v1 packed 1.048% | 1.04800% (8.00) | `…Sm120v1Cast16ChainOnlyRev1_8192` |
| v1 packed, 16,384³, 0.777% | 0.77682% (8.00) | `…Sm120v1Cast16ChainOnlyRev1_16384` |
| v2 as written 1.121% | 1.12103% (8.376) | `…Sm120v2LoopCast32p06ChainOnlyCap1000_8192` |
| v2 as written, 16,384³ (not on the panel) | 0.74062% (8.376) | `…Sm120v2LoopCast32p06ChainOnlyCap1000_16384` |
| v2 packed 0.932% | 0.93200% (8.376) | `…Sm120v2LoopCast16ChainOnlyCap1000_8192` |
| v2 packed, 16,384³, 0.645% | 0.64454% (8.376) | `…Sm120v2LoopCast16ChainOnlyCap1000_16384` |

### 1.3 v2-hot (panel `pearl-c-sm120 v2-hot`; security-proofs' `pearl-c-sm120-v2hot` row)

- **At the fixed rule `HotSizing.publicConst 64`.** The panel cites the generic `gammaHot_…` lemmas, which hold for any
  `c₀`. The instances at 64 are `…_publicConst64_…`, e.g. `gammaHot_sm120v2HotLoopCast8_publicConst64_8192` for 0.36217%
  and `gammaHotChainOnly_sm120v2HotLoopCast8_publicConst64_8192` for 0.83709%.
- **At the kernel's casts.** The panel says "the 32.06 pin is pending (bc-876ca543)". At 32.06, v2-hot now gives
  0.64670% / 1.12026%, against v2's 0.64699% / 1.12103%. At 16 it gives 0.45696% / 0.93142%, against v2's 0.45706% /
  0.93200%.
  - So at the same cast v2-hot is **equal to v2 within 0.001 points**.
  - The gap is a normalization effect: crediting U's forced removal on both sides of the ratio dilutes a fixed surplus.
    It is not a cost difference (bc-22298e90, `statement-review-1350.md` §5).
  - `v2-hot/README.md` ("v2-hot against v2 at the same cast") has both shapes, and the gap by reading.
- **`security-proofs.md`'s row** still reads γ "unchanged from v2", pins "—", status "queued". There are now 132
  staged pins, and bc-22298e90 has GO'd 34 of them.

### 1.4 v2's chain cap at the exact in-loop price (staged 13:48Z)

**Where it was uncited:**
- the panel's v2, v2-h1, v2-h2 and v2-h3 rows: "exact 0.35980% / 0.35484% at 8.376 (computed; no kernel-form pin)";
- `security-proofs.md`'s chain-cap row, "per unit 0.360% / 0.355%, per audit tile 0.362% / 0.356%", and its FP32 price
  rule paragraph.

Only the rounded twins (0.37112% / 0.36056%) and the 8.00 instances existed before. It was the most-cited item left.

**Now staged,** in `Pouw/PearlC/ChainCapKernelGamma.lean`, at `devSm120v2 Prices.sm120Loop` against the kernel's
`W_ref` with `c = 8 − 8953/1000`:
- per unit: 0.35980% and 0.35484% (`pearlCGammaSm120v2LoopCast8ChainCap1000_{8192,16384}`);
- per audit tile: 0.36218% and 0.35604%, the unit cap's values (`pearlCSampledSm120v2LoopCast8ChainCap1000_…`).

### 1.5 Pearl-C4 v1 on `lut256`: already cited

The panel cites the `lut256` pins, 0.71732% / 1.93807% and 0.61102% / 1.23638%, from `fp4-delta/README.md`. Nothing to
change.

## 2. Still without a pin

| Figure | Where it's published | What exists | Who can pin it, and how |
| --- | --- | --- | --- |
| **FP8 chain-only at the statement's cast 8:** v1 0.959% / 0.732%, v2 0.84% | `security-proofs.md`'s sm_120 v1 and no-promotion rows ("target") | none; computed from the pins' formulas: v1 0.95902% / 0.73172% (8.00), v2 0.83757% / 0.59662% (8.376) | this lane: add `Cast8` to `CHAIN_ONLY` in `gen_kernel_gamma.py`, one line, 16 pins |
| **FP8 v1 chain-only if the cast costs 32: 1.225%** | `security-proofs.md`'s sm_120 v1 row | none; computed 1.22547% (8.00). The measured 32.06 is pinned (1.22614%) | this lane: `Cast32` in `CHAIN_ONLY`. Or bc-824e54a2 cites the 32.06 pin instead |
| **FP8 v2 at ρ = 1/400: 0.51% / 0.99%** | `security-proofs.md`'s no-promotion row (a comparison) | none; computed 0.51179% / 0.98718% (8.376) | this lane, if wanted: the kernel's general theorems take ρ, so it's a generator change |
| **v1-cap600 chain-only: 0.965%** (packed cast 16) | panel `v1-cap600`, and the fallback sentence in every v1 row | none; computed 0.96496% (8.00), and 0.69374% at 16,384³ | a candidate, not granted, from bc-3006c44a. Pinning it needs the grant. The instance is `pearlCGammaDevRev1KChainOnlyAt` at ρ = 1/600, a generator change |
| **post-add closure m\* ≈ 0.75–0.97** merges per output word | panel v1, v1-h1, v1-h2, v1-h3, v1-cap600 | no Lean statement | the assessor (bc-d7d4b0d1) and bc-3006c44a's per-scheme search; not this lane's |
| **H100 chain-only γ** ("arithmetic only") | `security-proofs.md`'s H100 chain-only row, off the panel | `chainOnlyGamma8192Cap`, `chainOnlyGamma16384Cap`, arithmetic identities only | bc-824e54a2's FP8 lane, once `TTOutChainPearlC` is stated |
| **U-only (`-h1`), exact in-loop** | `security-proofs.md`'s U-only row: 0.511% / 0.362% "unchanged" | 8.00 pins (0.51056% / 0.36162%) and rounded 8.376 twins (0.52168% / 0.37349%). The exact in-loop value is the unit's, 0.51105% / 0.36218% | this lane: a kernel-`W_ref` U-only instance. Low priority, since the row publishes the unit's figure |

**Not in either document:**
- **The FragDraw fragment term** appears in neither file, so there is nothing to cite yet. It is bc-5382063c's
  (`rowseed-staging`).
- FP8 v3 is "not derived", and FP4 v3 and v3′ are rejected, so they publish no γ.
- The attempts table's γ column records each attempt's figure at the time it ran. It is history, not a published
  headline, so I didn't scan it row by row.

## 3. Pinned, but cited stale or not at all

**`security-proofs.md`** (bc-824e54a2):
- **sm_120 v1 rev1 row:** 0.511% / 0.505%. The exact in-loop pins give 0.51105% / 0.50528% at 8.376, the larger
  (`pearlC{Gamma,Sampled}Sm120v1LoopCast8Rev1_…`).
- **v2 at cap 1/1,000:** "published 0.362% / 0.356% … the Lean instance at issue-bound prices is 0.36162%". The exact
  in-loop pins give 0.36218% / 0.35604% (`pearlC{Gamma,Sampled}Sm120v2LoopCast8Cap1000_…`).
- **v2-hot:** see §1.3.
- **v2 with the chain cap:** cite the exact pins in `ChainCapKernelGamma.lean` (§1.4) for 0.360% / 0.355% per unit and
  0.362% / 0.356% per tile.
- **Pearl-C4:** stale in two places.
  - The row reads "0.7174% … 0.6111% … with `fs` = 107.34 (10:30Z); chain-only 1.48–1.85%".
  - The row's status and the FP32 price rule paragraph read "0.71761% stands".
  - On the ruled `lut256` path the pins give 0.71732% / 0.61102%, and chain-only 1.93807% / 1.23638%
    (`fp4-delta/README.md`).
- **The FP32 price rule paragraph** reads "38 pins", "the Lean 8.38 figures are upper bounds, about 0.011 points high",
  and "the published in-loop FP8 figures are Derived". All three are out of date:
  - 176 FP8 pins are staged, and the exact in-loop values are pins (`…LoopCast8…`);
  - the in-loop FADD is `1047/125`.

**`panel.md`** (bc-2aa33ad8):
- **FP8 rows:** "The chain-only figures at 32.06 and 16.00 have no pin" can go (§1.2).
- **v2-hot:** cite `…_publicConst64_…`. "The 32.06 pin is pending" can go (§1.3).
- **FP4 v2:** "v2's `lut256` pins are coming" can go (§1.1).
- **FP8 wide stores at 8.5 (conjectured):**
  - The rows show v1 0.517% / 0.965% and v2 0.368% / 0.844%, and "That puts v1's chain-only γ at about 0.967% (Derived
    …; bc-3006c44a to compute)".
  - GPU 0 measured the cast at 8.72, which is pinned: 0.51908% / 0.96704% (v1) and 0.37073% / 0.84608% (v2).
  - The 8.5 figures could be dropped or relabelled.
