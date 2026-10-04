---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# FP4 delta: Pearl-C4's issue-bound twins at the repriced block scale, with the scale step as a parameter

30 Sep 2026, 12:05Z; the scale step made a parameter at 12:45Z, the chain-only reading pinned at 12:50Z, Pearl-C4 v2
added at 13:05Z, the published path switched to `lut256` at 13:25Z (bc-a8466279's ruling), and the base-split fix
rehearsed at 14:15Z. Worker bc-876ca543, for
the pous root (bc-b729c175), who queues it for bc-22298e90. This is a small
delta, separate from the FP8 twins in `../` (`../README.md`). Nothing here is pinned, and no file outside this folder
changed.

**Status: GO from bc-22298e90 on the four, as generic implications (`../statement-review-fp4-delta-v2.md`, 12:25Z).
The FP4 γ they carry stays flagged while `tt-out/fp4-sm120` is D, and GPU 5's gate only confirms now.**
Since the review, the in-loop record's FADD moved to the exact `1047/125` = 8.376, matching FP8's (bc-824e54a2,
12:16Z). The four pins here are at 8.00 and don't change.
- The assessor (bc-d7d4b0d1) found `rcp.approx` exact on all 126 UE4M3 scales. So the `div.rn` alternative is dropped;
  its record and four twins are gone.
- `tt-out/fp4-sm120` is now rated D, by a base-split construction (`internal/pouw/red-team/fp4-base-split-break.md`).
  The domain fix is in design with bc-a8466279.
- These twins take that assumption as a hypothesis. They stay true implications but say nothing until the fix lands.
  The fix is why they are stated as the section "How the twins avoid the domain rules' details" describes.
- **The scale step is `lut256`** (bc-a8466279's ruling, `theory-pearl-c4-domain.md` §6.6). The block scale is credited
  at `lut256`'s W1 price, with `W_ref` on the same path.
  - The ruling's 8.55 is the pins' `Fp4ScalePath.lut256` at 8.38, `7.5 + FADD/8`. At the ruled 8.376 it is 8.547, and at
    8.00 it is 8.50.
  - `W_ref` is on the same path in every record here, since `wrefFp4` is `creditFp4` plus `qa`, and the scale is in
    `fs`.
  - **The published FP4 figures are now the `lut256` pins at 8.376** (the section "What the panel publishes"). No pin
    changed: the path was already a parameter, so the switch instantiates `p := Fp4ScalePath.lut256`.
  - The four pins GO'd at 12:25Z are unchanged. They are `rcp.approx` at 8.00, true but no longer the published path.
- **GO from bc-22298e90 on all 59, held** (`../statement-review-fp4-delta-v2.md`: the scale path at 13:25Z, chain-only
  at 13:40Z, Pearl-C4 v2 at 13:55Z; confirmed in `../statement-review-1350.md`). Its note: `lut256` at W1 is
  W1-consistent, not conservative.
- **The base-split fix, F1′ + F2, is a conditional GO** from the assessor, pending the int8-Strassen replay of `c_L`
  (`internal/pouw/red-team/fp4-basesplit-fix-review.md`). It moves no published figure and none of the 59 records. It
  does change what 16 of them state, through the debit. The hold drops after `rebase_on_fix.sh`, a review of the
  fix's definitions and the grant (the section "Under the base-split fix").

## Under the base-split fix (F1′ + F2)

The fix is bc-a8466279's (`internal/pouw/rtx-pro/theory-pearl-c4-domain.md` §6.2–6.5). It changes one definition
this delta reads: `Fp4Sem.tileDebit` gains F1′ in place of item (1), and adds F2, with the same signature (§6.5).
`Fp4Sem.unitDebit` is `tileDebit` over the whole unit, so the per-unit protocol moves with it.

**What moves, and what doesn't:**

| Item | Under the fix | Why |
| --- | --- | --- |
| every γ here (the 32 value lemmas) | unchanged | they read only the prices, `creditFp4`, `wrefFp4` and v2's `creditFp4Hot`. γ is the worst case at the cap, whatever the debit |
| `creditFp4`, `wrefFp4`, `fs`, `qa` | unchanged | §6.5: forming, `f_s`, `W_ref` and `creditOf` are unchanged. The fix is two debit terms |
| the 59 records (signature, assumptions, type hash) | unchanged, in the rehearsal below | the statements name the debit through the protocol, the tiles and TT_OUT; they don't unfold it |
| what 16 of them state | changes with the debit | the four GO'd twins, the four path-parametric twins, the two weaker-TT_OUT lemmas, and the chain-only reading's two general theorems and four twins. Their TT_OUT hypothesis and their conclusion read `pearlCProtocolFp4` or `pearlCTilesFp4`, whose cap is on the debit |
| the other 43 | nothing | the 32 values and `Fp4Prices.sm120Issue_eq` read no debit, and v2's 10 theorems are generic over the protocol |
| `TTOutFp4`, `TTOutTileFp4` and the chain-only forms (`TTOutFp4ChainOnly`) | the same text, a new meaning | they read the debit through the protocol, so `tt-out/fp4-sm120` needs its grant under the fix. That's the assessor's, after the replay |

**What honest work pays under the fix:**
- **F2: nothing.** F2 is positive only when the tile's two modal-byte shares sum above `2 − (1 − c_L)/4`. That is 1.95
  at 8,192³ and 1.85 at the domain's largest shape. Honest tiles reach 0.29 at most (§6.3).
- **F1′: nothing on an admitted tile, and coverage on a few.**
  - An audit tile's credit is fixed at `(1 − ρ)·creditFp4·share` (`pearlCTilesFp4`); the debit only decides admission.
    So an honest tile under the cap earns the same credit with F1′ as without it.
  - Honest tiles over the cap are rejected. In §6.2's census (64 × 64 tiles, 256 tokens) that is:

    | Model | Tiles over 1/400 | Share | Worst tile |
    | --- | --- | --- | --- |
    | Qwen2.5-0.5B | 6 of 1,344 | 0.45% | 1.09%, 4.4 times the cap |
    | Llama-3.2-1B | 0 of 896 | 0 | 0.074% |
    | Qwen2.5-3B | 6 of 2,016 | 0.30% | 0.31% |

    The high rows are first-token rows in `o_proj`.
  - **Per unit** the credit is `creditFp4 − debit`, so an honest unit pays its F1′ mean. On Qwen2.5-0.5B that is about
    0.005% per MAC: 0.0045% on A's rows and 0.0004% on W's, about 2% of the cap.
  - **Not in the census:** a small unit could pass the unit cap. The worst row reads 27.7% per MAC, so a unit holding
    one such row passes 1/400 when m is below about 110. That costs coverage, not γ.
- None of this moves γ, which is the worst case at the cap.

**The rehearsal** (14:15Z, NVFP4 only since 16:00Z; a second private copy; `fix-rehearsal.diff` is its change to the
FP4 staging's `DeviceFp4.lean`):
- **The change.** `tileDebit` has item (1) replaced by F1′ and F2 added, as §6.2–6.3 write them:
  - **F2 exactly as §6.3 writes it:** the tile's modal-byte shares on `A′` and `B̃`, and `c_L(m, k, n)` by bc-d9842080's
    formula, with W1's leaf 2.0 and NVFP4's block of 16. `c_L` gives 0.808, 0.707, 0.619 and 0.542 at 8,192³ to
    65,536³, the assessor's pinned values. F2 is `save_int8` times the tile's chain MACs.
  - **MXFP4 is out.** Daniel dropped MXFP4 from Pearl-C4's domain at 15:34Z. So since 16:00Z `c_L` takes no block
    parameter: it is `log₂(k/16)` only. That was the rehearsal's one MXFP4 path (bc-824e54a2's 15:39Z inbox entry).
  - **F1′ per row window:** `128·max(0, S_w − min(c·M_w, 1/8))`, with `M_w` from the realised bytes. Its two
    law-derived inputs, `S_w` and the modal byte, are placeholder fields of `Fp4Sem`. The fix's owner computes them from
    the noise law.
  - So the rehearsal also changes `Fp4Sem`'s structure, a harsher change than §6.5's "same signature".
- **The results:**
  - the whole copy builds;
  - the audit passes: 10,001 declarations in 219 modules and 753 pins, with only the standard axioms;
  - none of the 59 records changes;
  - the reads that change are `Fp4Sem`, `Fp4Sem.tileDebit`, the new definitions, and `row24` and `save24`, which are
    no longer read;
  - a kernel replay of the ten FP4 modules accepts 301 constants.
- **Two cautions.**
  - The audit reports reads by module, so it lists all 59 pins against each changed `DeviceFp4` definition. Only the 16
    above read the debit.
  - This isn't the fix, which is bc-ae19a858's (the FP4 staging) and bc-a8466279's to write. The diff may help with
    F2.
- **Against the assessor's 15:18Z conditions** (`internal/pouw/red-team/ratings.md`, "THE FP4 CONDITIONS, one place";
  bc-824e54a2's 15:21Z inbox entry). The rehearsal tests only that the 59 records survive a change to the debit. It
  matches the conditions in part:
  - it models F2 as condition 3 has it, with the leaf 2.0 and the four slots;
  - its placeholder F1′ subtracts κ outside the expectation, where condition 1 puts it inside each term;
  - it doesn't model R1 (condition 4) or the fork-operand rule (condition 8).
  - `rebase_on_fix.sh` runs on bc-ae19a858's definitions, not on this.

**To unhold, once the replay passes and the fix is staged:**
1. **Rebase.** Run `bash rebase_on_fix.sh <private copy> <fixed ttout-fp4-staging>/Pouw <out>`. It:
   - overlays the fixed staging and this folder, and builds;
   - runs the audit (`--update --no-replay`) and a kernel replay of the ten FP4 modules;
   - checks that all 59 records are unchanged.

   On the rehearsal it passed, with 59 of 59 unchanged.
2. **Review.** bc-22298e90 reads the definitions the audit prints as changed: the fix's `tileDebit`, and whatever it
   adds. The 16 pins' records stay the same but what they state doesn't, so the merge handoff names a statement
   reviewer.
3. **Grant.** The assessor grants `tt-out/fp4-sm120` and its tile form under the fix. The chain-only forms follow from
   it by `ttOutFp4ChainOnly_of_ttOut` and its tile twin.
4. **Unhold.** The hold drops here and on the panel. The published figures don't move: on `lut256` at 8.376, v1 is
   0.71732% / 1.93807% (0.61102% / 1.23638% at 16,384³), and v2 is 0.71689% / 1.93528% (0.61091% / 1.23564%).

v2 needs two more things before it is cited: its T1 protocol defined, and the one lemma that it meets the accounting,
as v2-hot does.

## What the panel publishes: the `lut256` pins at 8.376

Held, as everything here is, until the base-split fix. The cap is 1/400. Each figure is one twin, at
`d.prices = Fp4Prices.sm120At (1047/125) Fp4ScalePath.lut256`, and one value lemma. The twin is per unit
(`pearlCGamma…`) or per audit tile (`pearlCSampled…`), with the same γ. 8.376 is the larger price in every row.

| Figure | Twin | Value lemma | Exact value | §6.6 (at 8.38, scale 8.55) |
| --- | --- | --- | --- | --- |
| v1, forming credited, 8,192³ | `pearlC{Gamma,Sampled}Fp4Sm120At_8192` | `gammaFp4_sm120Loop_lut256_8192` | `9875013901/1376663200000` (**0.71732%**) | 0.7174% |
| v1, chain-only, 8,192³ | `pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_8192` | `gammaFp4ChainOnly_sm120Loop_lut256_8192` | `26680734301/1376663200000` (**1.93807%**) | 1.938% |
| v1, forming credited, 16,384³ | `pearlC{Gamma,Sampled}Fp4Sm120At_16384` | `gammaFp4_sm120Loop_lut256_16384` | `5473473967/895794400000` (**0.61102%**) | 0.6111% |
| v1, chain-only, 16,384³ | `pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_16384` | `gammaFp4ChainOnly_sm120Loop_lut256_16384` | `11075380767/895794400000` (**1.23638%**) | 1.236% |
| v2 (T1 credited), forming credited, 8,192³ | `pearlC{Gamma,Sampled}Fp4Sm120HotAt_8192` | `gammaFp4Hot_sm120Loop_lut256_8192` | `9888398749/1379343520000` (**0.71689%**) | 0.7170% |
| v2, chain-only, 8,192³ | `pearlC{Gamma,Sampled}Fp4Sm120HotChainOnlyAt_8192` | `gammaFp4HotChainOnly_sm120Loop_lut256_8192` | `26694119149/1379343520000` (**1.93528%**) | 1.936% (bc-f5bf55c8: 1.935%) |
| v2, forming credited, 16,384³ | `pearlC{Gamma,Sampled}Fp4Sm120HotAt_16384` | `gammaFp4Hot_sm120Loop_lut256_16384` | `5477935583/896687840000` (**0.61091%**) | — |
| v2, chain-only, 16,384³ | `pearlC{Gamma,Sampled}Fp4Sm120HotChainOnlyAt_16384` | `gammaFp4HotChainOnly_sm120Loop_lut256_16384` | `11079842383/896687840000` (**1.23564%**) | — |

- The v2 twins also take v2's accounting at the protocol (`Fp4HotUnitAccounting`, `Fp4HotTileAccounting`, with the
  removal `a = 2·FADD`), since v2's protocol isn't defined yet (the section "Pearl-C4 v2, in the same form").
- **Against §6.6.** The same formula at 8.38 and a flat 8.55 gives 0.71742% / 1.93830% and 0.61107% / 1.23649% for v1,
  and 0.71699% / 1.93550% for v2. Those are §6.6's figures to its four and three decimals.
  - The pins sit up to 0.0002 points below them. Almost all of that is 8.38 against the ruled 8.376.
  - The rest, the flat 8.55 against 8.547, is under 0.00004 points.
  - v2's chain-only rounds to 1.935% at 8.376, bc-f5bf55c8's figure. At 8.38 it is 1.93550%, which §6.6 rounds up.
- **What moves from the `rcp.approx` figures:**
  - forming credited barely moves: 0.71721% → 0.71732% (v1), 0.71679% → 0.71689% (v2);
  - chain-only drops by about 0.047 points: 1.98521% → 1.93807% (v1), 1.98232% → 1.93528% (v2), at 8,192³.

## How the twins avoid the domain rules' details

Each of the four holds at **any** FP4 record `d` with `d.prices = Fp4Prices.sm120Issue`, and **any** `sem`, under that
record's own TT_OUT.
- The record's maps are not fixed. These are the forming, the ticket, U, the flags, the sub-grid flags and the salt-dead
  predicate, which together make the D₄ debit.
- The earlier twins, at `devFp4Sm120Issue`, read 63 of `devFp4Sm120`'s definitions through them. These read none.
- `{ devFp4Sm120 with prices := Fp4Prices.sm120Issue }` meets `hp` by `rfl` (an `example` in the file).
- The proofs read only the prices and the credit identity (`creditFp4`, `wrefFp4`).

The statements still read the protocol, the tiles and the domain: `pearlCProtocolFp4`, `pearlCTilesFp4` and
`pearlCDomainFp4At sem`, as the general `pearlCGammaFp4At` does. That means `Fp4Sem.unitDebit`, `tileDebit`,
`RowRules4`, `screenDead` and the 2:4 span terms. That can't be avoided while the game is Pearl-C4's.
- If the domain fix changes those definitions, what these pins state changes with them. In the rehearsal of the fix
  (the section "Under the base-split fix") their records, meaning signature, assumptions and type hash, did not change.
- Their proofs don't change, so after the fix only a rebuild and an audit are needed.

## The prices, per bc-a8466279 (`theory-pearl-c4-domain.md` §8a)

The salted block scale per block of 16 is the UE4M3 encode alone (8.0), the `F2FP` decode (12.74) and the
`MUFU`+`LOP3` reciprocal (63.9). None of these is an FP32 add or multiply. Two FP32 ops are added at the FADD price: the
FMUL `amax·1/6` and the decode's `HADD2.F32` widening. In FP4 units:

| | at FADD 8.00 (this delta) | at FADD `1047/125` = 8.376 (the in-loop record) |
| --- | --- | --- |
| `fs` | `5429/50` = 108.58 | `54713/500` = 109.426 |
| `qa` | 18 | `9423/500` = 18.846 |

`fs` is `90.58 + 9/4·FADD` and `qa` is `9/4·FADD`, since the FP32 work in both is linear in FADD. At 8.38 they would be
§8a's 109.435 and 18.855.

## The four pins, and the price rule

Pearl-C4, cap 1/400, forming credited. Each row is two pins, per unit (`Gamma`) and per tile (`Sampled`), with one γ:

| Pins | γ at FADD 8.00 (this delta) | In-loop γ at FADD `1047/125` = 8.376, `rcp.approx` | Larger |
| --- | --- | --- | --- |
| `pearlC{Gamma,Sampled}Fp4Sm120Issue_8192` | `162371257/22950880000` (0.70747%) | 0.71721% | in-loop |
| `pearlC{Gamma,Sampled}Fp4Sm120Issue_16384` | `814384171/134388640000` (0.60599%) | 0.61099% | in-loop |

- **Against §8a:** at 8.00 and 8,192³, §8a gives 0.7075%, which the pin's 0.70747% rounds to.
- **The rule:** the in-loop value is the larger at both shapes.
- **The record:** `Fp4Prices.sm120Issue = ⟨4, 5429/50, 18⟩`.
- **Since §6.6** these four are on `rcp.approx`, not the published path. The published issue-bound twin is
  `Fp4Prices.sm120At 8 Fp4ScalePath.lut256` = `⟨4, 209/2, 18⟩` (`fs` 104.5), at 0.70757% / 0.60602%, and the
  published figures are the `lut256` values at 8.376 (previous section).

## What the in-loop record should become (bc-ae19a858's; for bc-824e54a2 to route)

**Since §6.6: on `lut256`, it should become `⟨4, 105299/1000, 9423/500⟩`** (`fs` 105.299), which is
`Fp4Prices.sm120At (1047/125) Fp4ScalePath.lut256`. Its four `DeviceFp4Gamma` instances then state 0.71732% (ω
`3441658000/3425534301`) at 8,192³ and 0.61102% (ω `2239486000/2231380767`) at 16,384³, the published figures. The
`rcp.approx` record below is kept for the record.

`Fp4Prices.sm120` in `internal/pouw-fp8/ttout-fp4-staging/` is still `⟨4, 2444/25, 3771/200⟩` (`fs` 97.76). Per
bc-824e54a2's 12:16Z ruling, its in-loop price is FADD `1047/125` = 8.376, as FP8's `Prices.sm120Loop`. On the
`rcp.approx` path it would be **`⟨4, 54713/500, 9423/500⟩`**, not the earlier `⟨4, 21887/200, 3771/200⟩` (8.38).
I confirmed the ruling's expected record from the script's parts (block scale, cast, amax and ρ's accumulate).

| | γ | ω |
| --- | --- | --- |
| 8,192³ | `1646385229/229553920000` (0.71721%) | `573884800/571196829` |
| 16,384³ | `8211859687/1344021760000` (0.61099%) | `3360054400/3347894487` |

- **What bc-ae19a858 applies.** On `rcp.approx`, these are the γ and ω its four `DeviceFp4Gamma` instances
  (`pearlCGammaFp4Sm120_*`, `pearlCSampledFp4Sm120_*`) would state; on the ruled `lut256`, the ones above. Its
  docstring should say "FADD at the measured `1047/125` = 8.376, as `Prices.sm120Loop`, block scale on `lut256`".
- **What I checked.** In Lean, by `norm_num` in a scratch file that isn't staged: both credit identities, both γ values,
  and `fs` and `qa` from the parts.
- **Against 8.38.** The values sit 0.00010 and 0.00005 points below the 8.38 figures (0.71731% and 0.61104%).
- **The rule.** They stay above the issue-bound twins, so the in-loop value is the larger.
- **What moves with it.** `TTOutFp4`'s `creditOf` reads `fs`, so it moves with the record (the 10:32Z inbox entry).
- **Still to pin.** bc-22298e90 suggests pinning the one-line instance at `{ devFp4Sm120 with prices := … }`, or at the
  fixed record's, when the domain fix lands, so the published figure sits at a named record. That's queued for then.

## The scale step as a parameter

**The parameter.** `Fp4ScalePath` records a block-scale path per element, in FP4 units, as two parts:
- `fixed`, the work no FP32 price reprices;
- `fp32Ops`, the FP32 operations per block of 16.

There are two paths:

| Path | `fixed` | `fp32Ops` | What it is |
| --- | --- | --- | --- |
| `rcpApprox` | `529/50` = 10.58 | 2 | UE4M3 encode alone (8.0), `F2FP` decode (12.74) and `MUFU` reciprocal (63.9) per block; the FMUL `amax·1/6` and the decode's `HADD2.F32` (§8a) |
| `lut256` | `15/2` = 7.5 | 1 | half an `F2FP`, 1.25 `PRMT` and one `LDS` per block (60 FP8 units); the FMUL `amax·1/6` |

`lut256` is priced at its W1 per-instruction rates (`pearl-c4-v3.md` §15, bc-f5bf55c8's recommendation), not at GPU 5's
in-loop marginal cost. Its block scale comes to 8.50 at FADD 8.00 and 8.547 at 8.376, against 12.58 and 12.674 for
`rcpApprox`. GPU 5's 1.94 and 4.17 are marginal costs in a loop that saturates the FP32 pipe, so they settle legality
and ordering, not the price. bc-a8466279 ruled the same way (§6.6): "W1 prices every op at its issue cost", and a
marginal cost measured under co-issue isn't a W1 quantity.

**The records.** `Fp4Prices.sm120At fadd p` = `⟨4, 64 + p.fixed + p.fp32Ops·fadd/8 + 2·fadd + 16, 2·fadd + fadd/4⟩`:
- the issue-bound record is `fadd = 8`, and `Fp4Prices.sm120Issue_eq` shows it is the GO'd `Fp4Prices.sm120Issue` on
  `rcpApprox`;
- the in-loop record is `fadd = 1047/125`, as bc-824e54a2 ruled.

**The twins.** `pearlC{Gamma,Sampled}Fp4Sm120At_{8192,16384}` hold at any record priced `Fp4Prices.sm120At fadd p`, for
any `fadd ≥ 0` and path `p`, at γ `gammaFp4 d (1/400) s`. So a repricing instantiates `p`, and nothing is re-proved.
The eight `gammaFp4_sm120{Issue,Loop}_{rcpApprox,lut256}_{8192,16384}` lemmas give the values.

**γ both ways.** Forming credited, cap 1/400. At FADD 8.00 the records are the issue-bound ones; at `1047/125` = 8.376
they are the in-loop ones.

| Scale path | Shape | `fs` at 8.00 / 8.376 | γ at FADD 8.00 | γ at FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- | --- |
| `rcpApprox` (before §6.6) | 8,192³ | 108.58 / 109.426 | `162371257/22950880000` (0.70747%) | `1646385229/229553920000` (0.71721%) | — |
| `rcpApprox` (before §6.6) | 16,384³ | | `814384171/134388640000` (0.60599%) | `8211859687/1344021760000` (0.61099%) | — |
| `lut256` (ruled, §6.6) | 8,192³ | 104.5 / 105.299 | `6492677/917600000` (0.70757%) | `9875013901/1376663200000` (0.71732%) | **0.71732%** (8.376) |
| `lut256` (ruled, §6.6) | 16,384³ | | `32568847/5374240000` (0.60602%) | `5473473967/895794400000` (0.61102%) | **0.61102%** (8.376) |

- **Forming-credited γ barely moves** with the path: +0.00011 and +0.00003 points at 8.376. That's because the scale is
  credited, and so on both sides of the ratio.
- **Chain-only moves more:** at 8,192³ and 8.376 it goes from 1.9852% to 1.9381% (the next section).
  bc-f5bf55c8's §15 has the same figures to three decimals (0.717% / 1.985% on `rcp.approx`, 0.717% / 1.938% on
  `lut256`).
- **With `lut256` ruled,** bc-ae19a858's in-loop record becomes `⟨4, 105299/1000, 9423/500⟩`, and its four instances
  state the `lut256` column above. Their ω values are `3441658000/3425534301` at 8,192³ and `2239486000/2231380767` at
  16,384³.

## The chain-only reading, in the same form

The panel publishes FP4 chain-only (1.985% at 8,192³ on `rcp.approx`, 1.938% on the ruled `lut256`), so it cites a
theorem, as the FP8 and v2-hot figures do.

**How it is stated.** It mirrors `../Pouw/PearlC/ChainOnlyGamma.lean`:
- **The credit** is `creditFp4ChainOnly` = `creditFp4` less the forming `fs·m·k`, less the debit. The cap stays on the
  full credit, so the worst case is `ω = wrefFp4 / (creditFp4ChainOnly − ρ·creditFp4)`.
  - The protocol and tiles with that credit are `pearlCProtocolFp4ChainOnly` and `pearlCTilesFp4ChainOnly`.
  - γ is `gammaFp4ChainOnly`. All of these are in `DeviceFp4ChainOnly.lean`.
- **Its TT_OUT forms** are `TTOutFp4ChainOnly` and `TTOutTileFp4ChainOnly`, in the assumptions module
  `TTOutFp4ChainOnly.lean`.
  - They follow from the record's TT_OUT at non-negative `fs` (`ttOutFp4ChainOnly_of_ttOut` and its tile twin), so they
    are weaker assumptions.
- **The game is the record's own protocol's,** since neither `G_γ` nor `GγSampled` reads the credit.
- **The twins** are `pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_{8192,16384}`: at any record priced
  `Fp4Prices.sm120At fadd p`, for any `fadd ≥ 0` and path `p`. They take one side condition, that the chain-only worst
  case is positive, and each `gammaFp4ChainOnly_…` value lemma proves it together with the value.
- **Held,** like everything here: the hypothesis is `tt-out/fp4-sm120`'s chain-only form, and that assumption is D until
  the base-split fix.

**The values** (chain-only, cap 1/400):

| Scale path | Shape | γ at FADD 8.00 | γ at FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| `rcpApprox` (before §6.6) | 8,192³ | `451194057/22950880000` (1.96591%) | `4557116829/229553920000` (1.98521%) | — |
| `rcpApprox` (before §6.6) | 16,384³ | `1680852571/134388640000` (1.25074%) | `16944054487/1344021760000` (1.26070%) | — |
| `lut256` (ruled, §6.6) | 8,192³ | `17611477/917600000` (1.91930%) | `26680734301/1376663200000` (1.93807%) | **1.93807%** (8.376) |
| `lut256` (ruled, §6.6) | 16,384³ | `65925247/5374240000` (1.22669%) | `11075380767/895794400000` (1.23638%) | **1.23638%** (8.376) |

- **The published chain-only is now 1.93807% and 1.23638%**: `pearlC{Gamma,Sampled}Fp4Sm120ChainOnlyAt_{8192,16384}`
  at `Fp4Prices.sm120At (1047/125) Fp4ScalePath.lut256`, with `gammaFp4ChainOnly_sm120Loop_lut256_{8192,16384}`.
  §6.6 gives 1.938% and 1.236% at 8.38.
- **The panel's earlier 1.985%** is the same twin with `p := Fp4ScalePath.rcpApprox` and
  `gammaFp4ChainOnly_sm120Loop_rcpApprox_8192`: 1.98521%. At 8.38 it would be 1.98541%. §15's 1.985% (8.38) and
  1.966% (8.00) agree to three decimals.
- **The rule:** 8.376 is the larger on both paths and at both shapes.

## Pearl-C4 v2, in the same form

Pearl-C4 v2 is T1: the hot word's H is removed before the clean-up by one exact FP32 add per word, credited as forced
clean-up, which is `pearlc4-domain-gamma.py`'s `hot = "credited"`. Its figures, bc-a8466279's 0.7169% / 1.983% at
8,192³ at 8.38, had no pin at the ruled 8.376. **Its published path is `lut256`** (§6.6): 0.71689% / 1.93528% at
8,192³ and 8.376, against §6.6's 0.7170% / 1.936% at 8.38.

**How it is stated.** The v2 protocol isn't staged, so the twins are generic over it, as `../v2-hot/`'s are:
- **The credit** (`creditFp4Hot d a s`) is `creditFp4` plus the removal, `a = 2·FADD` per word in FP4 units, and the
  cap is on it. `W_ref` adds `qa`. The chain-only credit subtracts `fs·m·k` and keeps the removal, which is clean-up,
  not forming. These are all in `DeviceFp4Hot.lean`.
- **The accounting.** Each twin holds for any protocol `P` whose units within the cap have
  `W_ref = wrefFp4Hot` and are credited at least `K` (`Fp4HotUnitAccounting`, or `Fp4HotTileAccounting` per tile).
  - `K` is `(1 − ρ)·creditFp4Hot` for the forming-credited twins, and `creditFp4HotChainOnly − ρ·creditFp4Hot` for the
    chain-only ones.
  - The v2 protocol meets this by one lemma once it's defined: credit = credit − debit, cap on `creditFp4Hot`.
- **The twins** are `pearlC{Gamma,Sampled}Fp4Sm120Hot{,ChainOnly}At_{8192,16384}`: at any record priced
  `Fp4Prices.sm120At fadd p`, for any `fadd ≥ 0` and scale path `p`, with TT_OUT at `P`.
  - The chain-only twins take their worst case's positivity, which each chain-only value lemma proves with the value.
- **Held,** like the rest of the delta: TT_OUT at the v2 protocol is `tt-out/fp4-sm120`'s T1 form, rated D until the
  base-split fix.

**Forming credited, cap 1/400:**

| Scale path | Shape | γ at FADD 8.00 | γ at FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| `rcpApprox` (before §6.6) | 8,192³ | `25671209/3630560000` (0.70709%) | `549538679/76666880000` (0.71679%) | — |
| `rcpApprox` (before §6.6) | 16,384³ | `271674457/44838880000` (0.60589%) | `1174078873/192194560000` (0.61088%) | — |
| `lut256` (ruled, §6.6) | 8,192³ | `19503599/2757920000` (0.70719%) | `9888398749/1379343520000` (0.71689%) | **0.71689%** (8.376) |
| `lut256` (ruled, §6.6) | 16,384³ | `310423/51232000` (0.60592%) | `5477935583/896687840000` (0.61091%) | **0.61091%** (8.376) |

**Chain-only:**

| Scale path | Shape | γ at FADD 8.00 | γ at FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| `rcpApprox` (before §6.6) | 8,192³ | `71274809/3630560000` (1.96319%) | `4559347637/230000640000` (1.98232%) | — |
| `rcpApprox` (before §6.6) | 16,384³ | `560497257/44838880000` (1.25003%) | `2421535273/192194560000` (1.25994%) | — |
| `lut256` (ruled, §6.6) | 8,192³ | `52859999/2757920000` (1.91666%) | `26694119149/1379343520000` (1.93528%) | **1.93528%** (8.376) |
| `lut256` (ruled, §6.6) | 16,384³ | `628103/51232000` (1.22600%) | `11079842383/896687840000` (1.23564%) | **1.23564%** (8.376) |

- **Published: the `lut256` rows** at 8.376, 0.71689% / 1.93528% at 8,192³ and 0.61091% / 1.23564% at 16,384³.
  They come from the same twins with `p := Fp4ScalePath.lut256` and the `gammaFp4Hot{,ChainOnly}_sm120Loop_lut256_…`
  values.
  - At 8.38 and §6.6's flat 8.55 the same formula gives 0.71699% / 1.93550%, which is §6.6's 0.7170% / 1.936%.
  - At 8.376 the chain-only rounds to 1.935%, which is bc-f5bf55c8's figure.
- **The `rcp.approx` rows** are bc-a8466279's earlier figures. At 8.38 they would be 0.71689% / 1.98252%, its 0.7169%
  / 1.983%; at the ruled 8.376 they are 0.71679% / 1.98232%.
- **Against §15:** bc-f5bf55c8's §15 table agrees to three decimals: 0.717% / 1.983% at 8.38, and 0.707% / 1.963% at
  8.00. So do the `lut256` rows: 0.717% / 1.935%, and 0.611% / 1.236% at 16,384³.
- **The rule:** 8.376 is the larger in every row.

## Files

| File | Kind | What it holds |
| --- | --- | --- |
| `Pouw/PearlC/DeviceFp4Issue.lean` | trusted, definitions only | `Fp4Prices.sm120Issue = ⟨4, 5429/50, 18⟩`; `Fp4ScalePath` (`rcpApprox`, `lut256`), `Fp4Prices.sm120At` and `gammaFp4` |
| `Pouw/PearlC/Fp4IssueGamma.lean` | proofs | the four GO'd twins; `Fp4Prices.sm120Issue_eq`; the four twins at any FP32 price and scale path; the eight values |
| `Pouw/PearlC/DeviceFp4ChainOnly.lean` | trusted, definitions only | `creditFp4ChainOnly`, `pearlCProtocolFp4ChainOnly`, `pearlCTilesFp4ChainOnly`, `gammaFp4ChainOnly` |
| `Pouw/PearlC/TTOutFp4ChainOnly.lean` | trusted, an assumptions module | `TTOutFp4ChainOnly`, `TTOutTileFp4ChainOnly` |
| `Pouw/PearlC/Fp4ChainOnlyGamma.lean` | proofs | the two weaker-TT_OUT lemmas, the two general theorems, the four path-parametric twins, the eight values |
| `Pouw/PearlC/DeviceFp4Hot.lean` | trusted, definitions only | Pearl-C4 v2's `creditFp4Hot`, `wrefFp4Hot`, `creditFp4HotChainOnly`, `gammaFp4Hot{,ChainOnly}`, `Fp4HotUnitAccounting`, `Fp4HotTileAccounting` |
| `Pouw/PearlC/Fp4HotGamma.lean` | proofs | v2's two general theorems, its eight twins (forming credited and chain-only) and its sixteen values |
| `fp4-delta-pins.json` | records | the 59 pins as `audit.py --update` wrote them, one `assumptions` module to register, and four `layers` entries |
| `handoff-lanes-pous.md` | handoff | the 11:15Z question to bc-a8466279, answered in §8a |
| `fix-rehearsal.diff` | rehearsal, not the fix | the base-split fix's F1′ and F2 in `tileDebit`, against the FP4 staging's `DeviceFp4.lean` (the section "Under the base-split fix") |
| `rebase_on_fix.sh` | script | rebuilds and audits this delta on the fixed staging in a private copy, and checks the 59 records |

## Checks

I built these in the same private copy as `../`, whose build section is in `../README.md`. The copy has
`ttout-fp4-staging/` at its 11:33Z state, where `pearlCDomainFp4At` takes `sem`.
- `#print axioms` on the 59 pins: `[propext, Classical.choice, Quot.sound]`.
- Kernel replay, with every constant accepted:
  - the two forming-credited modules, 51 constants;
  - the three chain-only modules, 29;
  - the two v2 modules, 45.
- `audit.py --update --no-replay` over the whole copy (13:04Z): PASS, 9,921 declarations in 217 modules, 683 pins.
  - New since the GO: the 13 scale-path pins, the 16 chain-only pins and the 26 v2 pins.
  - No record changed, including the four GO'd twins.
- The switch to `lut256` (13:25Z) changes no Lean and no record. The latest audit of the copy (13:19Z, 747 pins,
  after `../v2-hot/`'s additions) still has these 59 records unchanged.
- The published `lut256` values were rechecked from the pins' formula (the `fs` and `qa` above) in exact arithmetic.
  The same script at 8.38 and a flat 8.55 reproduces §6.6.
- The latest audit of the unfixed copy (13:48Z, 753 pins) still has these 59 records unchanged.
- **The fix rehearsal** (a second private copy with `fix-rehearsal.diff` applied) passed three checks, at 14:15Z and
  again at 16:00Z on the NVFP4-only diff:
  - `rebase_on_fix.sh`: the audit passes with 10,001 declarations in 219 modules and 753 pins;
  - a kernel replay of the ten FP4 modules accepts 301 constants;
  - all 59 records are unchanged.
