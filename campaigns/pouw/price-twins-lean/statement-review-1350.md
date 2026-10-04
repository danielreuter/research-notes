---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: `review-request-1350.md` (the price-twins lane's pins since my last GOs)

From bc-22298e90, the statement reviewer, to bc-876ca543, through the pous root. 30 Sep 2026, ~14:20Z. It answers the
five points the root asked about. It relies on the request, its statements file (including the 12:36Z `--update`
printout), the three pin files as of 13:57Z, and the READMEs.

## What was already covered

| Set | Pins | Where it was GO'd |
| --- | --- | --- |
| A. FP8 chain-only at casts 32.06 and 16 | 32 | `statement-review.md`, 13:55Z delta. Every instance was checked mechanically and every γ recomputed. The larger price is 8.00 for v1 and 8.376 for v2, as for the forming-credited rows |
| C1. v2-hot at `publicConst 64`, casts 8 and 8.72 | 16 | `statement-review-v2-hot.md`, 13:55Z delta (part of the 32 values there) |
| C2. v2-hot at casts 32.06 and 16 | 48 | the same delta: 32 twins and the other 16 values |
| C3. v2-hot chain-only | 34 | `statement-review-v2-hot.md`, 13:15Z delta: 2 general theorems, 16 twins, and 16 values recomputed |
| D. FP4 beyond the four twins | 55 | `statement-review-fp4-delta-v2.md`: the 13 scale-path pins at 13:25Z, the 16 chain-only pins at 13:40Z, and Pearl-C4 v2's 26 at 13:55Z. `fp4-delta-pins.json` still has those 59 records and no others, so no FP4 pin goes beyond them. D stays held |

So point (2) is covered: C3 is in my GO. So is point (4): there is nothing in FP4 beyond the 55 I reviewed.

## (1) B: v2's chain cap against the kernel's `W_ref` (6 pins, 2 definitions): GO

- **The definitions** (`DeviceChainCapKernel.lean`). `pearlCProtocolDevChainCapK` is
  `{ pearlCProtocolDevChainCap d sem ρ with Wref := wrefDevK d c }`, and `pearlCTilesDevChainCapK` replaces `Wref` and
  `Wcred` only. The credit, `capOK` (against `ρ·chainCreditDev`) and the checks are the chain cap's.
- **The general theorems.** `pearlCGammaDevChainCapKAt` takes `wrefDevK = ω·(creditDev − ρ·chainCreditDev)`, the
  per-unit worst case under the chain cap, and the record's `TTOutPearlCDevChainCap`. `pearlCSampledDevChainCapKAt`
  takes `wrefDevK = ω·(1 − ρ)·creditDev` and `TTOutTilePearlCDevChainCap`. Both reach the kernel protocol through
  `ttOut_wref`.
- **The four instances** at `devSm120v2 Prices.sm120Loop`, `c = 8 − 8953/1000`, recomputed exactly:

  | Reading | 8,192³ | 16,384³ |
  | --- | --- | --- |
  | per unit | 0.35980% | 0.35484% |
  | per tile | 0.36218% | 0.35604% |

- **Should the per-tile γ equal the unit cap's? Yes, under the tile rule `DeviceChainCap` states, and that rule is
  sound.**
  - A good tile's credit is the fixed `(1 − ρ)·creditDev·share` of `pearlCTilesDev`. Only its admission is against
    `ρ·chainCreditDev·share`. So ω per tile is `wrefDevK/((1 − ρ)·creditDev)`, the unit cap's, whatever the admission
    rule.
  - The fixed credit never exceeds what an admitted tile earns: its debited credit is at least
    `(creditDev − ρ·chainCreditDev)·share`, which is at least `(1 − ρ)·creditDev·share`.
  - So the chain cap tightens per-tile admission and leaves the per-tile γ where the unit cap has it: 0.0024 points above
    the per-unit chain-cap γ at 8,192³. That is the conservative choice.
  - **The alternative.** A tile rule crediting `(creditDev − ρ·chainCreditDev)·share` would give the per-unit figure per
    tile too. But that is a change to the verifier's credit rule and to `TTOutTilePearlCDevChainCap`, with a re-grant.
    I don't recommend it for 0.0024 points.
- **The labels** linking the eight rounded chain-cap twins to these exact pins are right.

## (3) C4: the 34 forming-credited v2-hot pins changed at 12:36Z: re-GO

- **What the printout shows.** At the end of the statements file, 32 records changed, all value lemmas: the 16
  forming-credited `gammaHot_…` and the 16 chain-only `gammaHotChainOnly_…`. The reads that moved are `HotSizing` (it
  gained `colMeanSq`), `HotSizing.cost`, `HotSizing.publicConst` (it takes `c₀`) and `HotSizing.colRms` (its FMA at
  8.46).
- **The other 18 of the 34** (the two general theorems and the 16 twins) keep their records byte for byte, as my
  comparison of the 12:25Z and 12:43Z files showed. Only their reads of `HotSizing` moved. They quantify over any
  `h : HotSizing`, so the same statements now range over the structure that also carries H_i's column scale. That is
  the fix my note 3 asked for, and it doesn't weaken them.
- **The changed value lemmas** are the ones I recomputed at 13:15Z, all 32 at their current values.
- **So all 34 are re-GO'd as they stand**, and the v2-hot set can merge with them, subject to the conditions still open
  at 13:55Z: the rev lane's accounting lemma and `_of_ttOut`, and a TT_OUT grant naming both prices and the rule.

## (5) Why v2-hot sits 0.00003–0.00077 points under v2 at the same cast

**The lane's reading is right** (the removal sits in both the credit and `W_ref`), with one refinement: what drives
the gap is the whole surplus of `W_ref` over the credited worst case, not the cast alone.
- **The argument.** Let `W` be `W_ref` and `K` the worst-case credit per m·k, so γ = 1 − (399/400)·K/W.
  - v2-hot adds the forced removal, `a = add·n/k` per m·k, to both: `W + a`, and `K + (1 − ρ)·a`. That holds in both
    readings, since the chain-only credit keeps the removal.
  - Because W > K, adding nearly the same amount to both moves K/W toward 1, and so lowers γ. The move is about
    `a·(W − K)/W²`: proportional to the surplus `W − K`, and inversely to the size.
- **What the surplus is:**
  - forming credited: `qa + c + ρ·credit`, which grows with the cast's `c`;
  - chain-only: it also contains the forming `fs·m·k` that K leaves out, so it is large even at cast 8.
- **The recompute agrees:**

  | Casts | Reading | Gap (points) |
  | --- | --- | --- |
  | 32.06 and 16 | all rows | 0.00003–0.00077, as the request says (the maximum is chain-only at 32.06, 8.376, 8192³) |
  | 8 and 8.72 | forming credited | 0.000003–0.000021, the request's "0.00001–0.00002" |
  | 8 and 8.72 | chain-only | 0.00012–0.00050 |

  So the request's "at casts 8 and 8.72 the gap is 0.00001–0.00002" holds for the forming-credited reading only.
- **What it means.** It is a normalization effect. Crediting one more forced FADD per word dilutes a fixed surplus, so
  γ, a ratio, falls slightly. It is not evidence that v2-hot is cheaper for an adversary or harder to undercut.
  Comparisons with v2 should say "equal to within 0.001 points", not "marginally cheaper".

**Labels:** none recorded.
