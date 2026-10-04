---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# Review request: v1-hot's price twins (`price-twins-lean/v1-hot/`, 100 pins)

30 Sep 2026, 14:45Z. From bc-876ca543 to bc-22298e90, for statement review; the pous root (bc-b729c175) sends it.
Everything here is staged: nothing is pinned, and no file outside `internal/pouw/price-twins-lean/v1-hot/` changed.

**Answered: GO on all 100 and the 10 definitions** (`../statement-review-v1-hot.md`). The rulings on the points below:
- Point 7: the published chain-only figure is 0.95930% (FADD 8.00).
- Point 2: the fold stays as written.
- An as-written (32.06) figure takes the 8.00 column in both readings.

v1-hot stays staged until Daniel decides.

**What to read:**
- **The statements:** `review-request-statements.txt`, beside this file. It holds what `audit.py --update` recorded:
  the 100 pins' signatures, and the 10 new definitions as they are now.
- **The definitions:** `Pouw/PearlC/DeviceHotRev1.lean`. The proofs are in `Pouw/PearlC/HotRev1Gamma.lean`, which
  `gen_v1hot_gamma.py` generates.
- **The records:** `v1-hot-pins.json`.
- **The values and the comparison with v1:** `README.md`.
- **The design and credit rule:** `internal/pouw/ttout-restatements.md` §9 (bc-b58c6093, 14:40Z).

**The build.** It is the same private copy as the earlier packets.
- The whole-copy audit (14:37Z, `--update --no-replay`) passes: 10,119 declarations in 221 modules and 853 pins, with
  only `propext`, `Classical.choice` and `Quot.sound`.
- A kernel replay of the two new modules accepted 123 constants.
- The only new records are these 100 pins and the 10 definitions they read. No existing record changed, including
  v2-hot's 132, since v1-hot's definitions are in a module of their own.

## The pins

| Set | Pins | What each says | Hypotheses |
| --- | --- | --- | --- |
| general theorems | 4 | TT_OUT (or `TTOutTile`) at any `P` meeting v1-hot's accounting at `d` gives `G_γ` (or `GγSampled`) at `gammaHotRev1 d h c ρ s`, or at `gammaHotRev1ChainOnly …` | the accounting, TT_OUT at `P`, and positivity of the credit (or the chain-only worst case) and of `W_ref` |
| twins | 64 | v1 under rev1 at the cap 1/400, at any `d` with `G = 4` and `Prices.sm120` or `Prices.sm120Loop`, casts 8, 8.72, 32.06 and 16, forming credited and chain-only, per unit and per tile, 8,192³ and 16,384³, for every sizing rule `h` | `hG`, `hp`, the accounting at `P`, and TT_OUT at `P`. Positivity is discharged in each twin |
| values | 32 | `gammaHotRev1{,ChainOnly} d (HotSizing.publicConst 64) c (1/400) sh = <exact>` at each twin's record, cast and shape | `hG : d.G = 4`, `hp` |

The general theorems are v2-hot's four, which you GO'd, with v1-hot's definitions substituted, and have the same
proofs. The twins have v2-hot's form, with `G = 4` and the cap 1/400 in place of `G = 0` and 1/1,000.

## What to check

1. **The credit against §9's rule.** `creditDevRev1Hot = creditDevRev1 + add·m·n`.
   - The first promotion stays excluded (`firstAddDev`), because the total starts at +0, so T_1 = S_1 exactly.
   - U's removal, one add per word, is credited.
   - Numerically this is `creditDev` at G = 4, since the removal restores the add rev1 drops.
2. **The fold.** `hotFoldDev = add·m·(k/(32·G) − 1)`, which is `k/128 − 1` adds per row at G = 4. It is in `W_ref`
   only.
   - I wrote it with `d.G` rather than 128, so that it reads the record's group.
   - It is only used at G = 4. At G = 0 it would be `−add·m`, since `k/0 = 0` in ℚ, but no pin reads it there.
   - Please say if you'd rather it be hardcoded.
3. **`W_ref`.** `wrefDevRev1Hot = creditDevRev1Hot + qa·m·k + c·m·k + hotFoldDev + h.cost`. It reads the same `h` as the
   record's H_{i,g} exponent, as in v2-hot (your note 3).
4. **The accounting props.** `HotRev1UnitAccounting`, `HotRev1TileAccounting` and their chain-only forms mirror
   v2-hot's.
   - Their credit bound is `(1 − ρ)·creditDevRev1Hot`, or chain-only `creditDevRev1HotChainOnly − ρ·creditDevRev1Hot`,
     under the cap `debit ≤ ρ·creditDevRev1Hot`.
   - The rev lane's `devSm120v1hot` should meet them by one lemma.
5. **The chain-only reading.** `creditDevRev1HotChainOnly = creditDevRev1Hot − fs·m·k`, which keeps the removal, with
   the cap on the full credit, as in v2-hot's.
6. **The values.** The 32 recompute from `gen_v1hot_gamma.py`'s `gamma`, and they reproduce all six of §9's figures:
   - forming credited: 0.51176% and 0.50564% at 8.376, and 0.51124% at 8.00;
   - chain-only: 0.95861% and 0.73161% at 8.376, and 0.95930% at 8.00.

   §9's exact `29245398169/5714672265625` is the value at 8,192³ and 8.376.
7. **The published chain-only figure.** By the two-price rule it is 0.95930% (FADD 8.00), not §9's quoted 0.95861%
   (8.376), since 8.00 is the larger chain-only at every cast, as for v1. Please confirm.
8. **The comparison with v1.** v1-hot is 0.00003–0.00071 points above v1 at the same cast.
   - My reading is that the fold's `W_ref`-only cost raises γ, and the credited removal's normalization lowers it.
   - I've worded it "equal to v1 within 0.001 points", per your §5.

## What merge still needs (not in this request)

- **The rev lane:** the record `devSm120v1hot`, its accounting lemma under one `h`, and the chain-only `_of_ttOut`.
- **The assessor:** a rating for `tt-out/pearl-c-sm120-v1-hot` that names both FP32 prices and `publicConst 64`.
- **The version's open lemma,** `no-aligned-exact-region/sm120-v1-hot` (§9).
