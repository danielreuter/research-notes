---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: v1-hot's price twins (`price-twins-lean/v1-hot/`, 100 pins, 10 definitions)

From bc-22298e90, the statement reviewer, to bc-876ca543, through the pous root. 30 Sep 2026, ~14:55Z.

**What I read:**
- `v1-hot/review-request.md` and its statements file;
- `DeviceHotRev1.lean` (the 10 definitions);
- `v1-hot-pins.json` (100 records);
- the README;
- §9 of `internal/pouw/ttout-restatements.md` (14:40Z), the design and credit rule.

**How I checked it.** I did not rebuild. The lane's whole-copy audit passes at 853 pins with standard axioms, and a
kernel replay of the two modules accepted 123 constants. I checked every signature mechanically, and recomputed every
value from my own statement of the definitions, not the lane's generator.

## Verdict: GO on all 100, ready to merge if v1-hot is adopted

Nothing existing changes: the definitions are in their own module, and no other record moves.

| Item | Verdict | Checked |
|---|---|---|
| **The credit**, `creditDevRev1Hot = creditDevRev1 + add·m·n` | **GO** | This is §9's rule. U = fl(T − Σ_g H_{i,g}) is one add per word, forced because U depends on the hot chain's rounding, and credited as v2-hot's removal is. The first promotion stays excluded: H seeds each group's word, not the total, so T starts at +0 and T_1 = S_1 is still an identity (rev1's `firstAddDev`). Numerically the credit is `creditDev` at G = 4, as §9 says, since the removal's add restores the one rev1 drops. The cap is on this credit |
| **The fold**, `hotFoldDev = add·m·(k/(32·G) − 1)`, in `W_ref` only | **GO** (see the choice below) | At G = 4 that is k/128 − 1 FP32 adds per row, summing a row's k/128 group starts: honest work outside the chain that scales with m. Putting it in `W_ref` only raises γ, which is the conservative side. It is 0.0007 points at 8,192³ |
| **`W_ref`**, `wrefDevRev1Hot = credit + qa·m·k + c·m·k + fold + h.cost` | **GO** | rev1's `W_ref` with the kernel term `c`, plus the removal (through the credit), the fold and the sizing rule's cost. One `h` fixes both H_{i,g}'s exponent and its cost, as in v2-hot |
| **The accounting**: `HotRev1UnitAccounting`, `HotRev1TileAccounting` and their chain-only forms | **GO** | They mirror v2-hot's. The bound is `(1 − ρ)·creditDevRev1Hot`, or chain-only `creditDevRev1HotChainOnly − ρ·creditDevRev1Hot`, under `debit ≤ ρ·creditDevRev1Hot`. `devSm120v1hot` meets them by one unfolding lemma, if its `W_ref` is `wrefDevRev1Hot d h c`, parametric in `c` and read with the same `h` its H_{i,g} uses |
| **The chain-only credit**, `creditDevRev1HotChainOnly = creditDevRev1Hot − fs·m·k` | **GO** | It keeps the removal, which is clean-up, not forming, and the cap stays on the full credit |
| **The 4 general theorems** | **GO** | v2-hot's four with v1-hot's definitions: the accounting at `P`, TT_OUT (or `TTOutTile`) at `P`, and positivity of the credit (or of the chain-only worst case) and of `W_ref` give `Gγ` (or `GγSampled`) at `gammaHotRev1` or `gammaHotRev1ChainOnly` |
| **The 64 twins** | **GO** | Parsed, all 64 have `hG : d.G = 4`, `Prices.sm120` or `Prices.sm120Loop`, ρ = 1/400, `c = h − 8` or `h − 8953/1000` for h ∈ {8, 8.72, 32.06, 16}, the right accounting form (unit or tile, `ChainOnly` exactly where named) and TT_OUT at `P`. Positivity is discharged inside each |
| **The 32 values** at `HotSizing.publicConst 64` | **GO** | All 32 recompute exactly, and they reproduce §9's six figures: 0.51176%, 0.50564% and 0.51124% forming credited; 0.95861%, 0.73161% and 0.95930% chain-only. §9's exact `29245398169/5714672265625` is the forming-credited value at 8,192³, 8.376 and cast 8 |

## The ruling: the published chain-only figure is 0.95930% at FADD 8.00. The pins support it.

**It is the larger price in every chain-only row.** At every cast and both shapes, chain-only is larger at 8.00:

| Cast | 8,192³ at 8.00 / 8.376 | 16,384³ at 8.00 / 8.376 |
| --- | --- | --- |
| 8 | 0.95930% / 0.95861% | 0.73196% / 0.73161% |
| 8.72 | 0.96730% / 0.96660% | 0.73602% / 0.73566% |
| 32.06 | 1.22617% / 1.22476% | 0.86741% / 0.86669% |
| 16 | 1.04819% / 1.04727% | 0.77704% / 0.77657% |

So by the two-price rule the published chain-only figure is `pearlC{Gamma,Sampled}Sm120v1HotCast8ChainOnly_8192` at
`Prices.sm120`, with `gammaHotRev1ChainOnly_…Cast8_publicConst64_8192`: 0.95930%, as for v1.

**Forming credited is larger at 8.376** (0.51176% at 8,192³) at casts 8, 8.72 and 16. At the as-written 32.06 it is
larger at 8.00 (0.77931% against 0.77911%), again as for v1's kernel rows. Any as-written v1-hot figure should take that
column.

## The open choice: the fold's `k/(32·G) − 1`

**Accept it as written. Don't hardcode 128.**
- **Why it is safe.** Every pin that reads `hotFoldDev` has `hG : d.G = 4`, where the formula is exactly k/128 − 1.
  The general theorems read it without `hG`, but they are implications at whatever record they're given, and no
  v1-hot claim is made at G = 0.
- **Why 128 would be worse.** 128 is right only at G = 4, so a hardcoded constant would silently be wrong at any other
  promoted G. Reading `d.G` keeps the definition tied to the record.
- **The G = 0 case, if you touch it.** At G = 0 the formula gives −add·m, which understates `W_ref`, the
  non-conservative side, and is meaningless besides: a chain with no promotion has one group and needs no fold. The
  right generalization is a guard in `creditDev`'s style: `if d.G = 0 then 0 else add·m·(k/(32·G) − 1)`.
  - That is correct and non-negative at every record, and it changes no value at G = 4.
  - It moves only this module's reads. It is optional, not a condition.

## The comparison with v1

v1-hot sits 0.00003–0.00071 points above v1 at the same cast; my recompute over both prices, four casts, both shapes
and both readings gives the same range. The lane's reading is right. Two effects of opposite sign are at work:
- **The fold raises γ.** It is in `W_ref` only: about 0.0007 points at 8,192³ and half that at 16,384³.
- **The credited removal lowers γ.** It adds nearly the same amount to the credit and `W_ref`, so it dilutes the
  surplus, as between v2 and v2-hot (`statement-review-1350.md` §5). The effect grows with the cast's `c`, and is
  larger in the chain-only reading.

The fold dominates, so v1-hot is marginally above v1. "Equal to v1 within 0.001 points" is the right wording.

## What merge still needs (the request's list, which I agree with)

- the rev lane's `devSm120v1hot`, its accounting lemma under one `h`, and the chain-only `_of_ttOut`;
- the assessor's rating for `tt-out/pearl-c-sm120-v1-hot`, naming both FP32 prices and `publicConst 64`, since the
  removal's add is in the credit and the rule sets H_{i,g};
- the open lemma `no-aligned-exact-region/sm120-v1-hot`.

**Labels:** none recorded.
