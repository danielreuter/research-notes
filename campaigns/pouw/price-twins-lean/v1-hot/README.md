---
cursor:
  subagentId: "bc-876ca543-9636-59e7-ad99-0052e8cf3702"
---

# v1-hot's price twins: v1's groups from a salted start, at both FP32 prices

30 Sep 2026, 14:40Z; the review folded in at 14:55Z. Worker bc-876ca543, for the pous root (bc-b729c175). Staging
only: nothing here is pinned, and no file outside this folder changed.

**Status: GO from bc-22298e90 on all 100 pins and the 10 definitions** (`../statement-review-v1-hot.md`, answering
`review-request.md`). They are ready to merge if Daniel adopts v1-hot. **They stay staged until he decides.**
- **Chain-only:** the review confirms 0.95930% at FADD 8.00 as the published figure.
- **The fold stays as written,** `add·m·(k/(32·G) − 1)`.
  - Every pin that reads it has `G = 4`.
  - The review's optional `G = 0` guard isn't applied, since it would move this module's reads and need a re-review.

All 100 pins build with only the standard axioms, and the whole-copy audit passes.

**The figures to publish**, all at 8,192³ unless marked. Each is the larger of FADD 8.00 and `1047/125` = 8.376, at
the sizing rule `HotSizing.publicConst 64`:
- **at the statement's cast 8:**
  - forming credited: **0.51176%** (8.376), and 0.50564% at 16,384³;
  - chain-only: **0.95930%** (8.00), and 0.73196% at 16,384³. §9 quotes 0.95861%, its value at 8.376, but 8.00's is
    the larger here, as it is for v1;
- **at the kernel's casts,** forming credited / chain-only:
  - **as written (32.06): 0.77931% / 1.22617%, both at FADD 8.00.** This is the one cast where forming credited is
    larger at 8.00 (0.77931% against 0.77911% at 8.376), as for v1's kernel rows. So any as-written v1-hot figure takes
    the 8.00 column, in both readings;
  - packed (16): 0.60082% (8.376) / 1.04819% (8.00);
  - 8.72: 0.51978% (8.376) / 0.96730% (8.00);
- **against v1:** at every cast v1-hot is **equal to v1 within 0.001 points** (the section "v1-hot against v1 at the
  same cast").

**Still open before v1-hot can merge**, as for v2-hot:
- Daniel's decision to adopt v1-hot;
- the rev lane's record `devSm120v1hot`, and its one accounting lemma under the one `h` the record reads;
- the chain-only `_of_ttOut`, once that protocol is defined;
- a TT_OUT grant for `tt-out/pearl-c-sm120-v1-hot` that names both FP32 prices and `HotSizing.publicConst 64`;
- the version's open lemma, `no-aligned-exact-region/sm120-v1-hot` (§9).

## The version

`pearl-c-sm120 v1-hot` is bc-b58c6093's (`internal/pouw/ttout-restatements.md` §9):
- **v1's chain as now.** G = 4: each group's word S_g is a 4-atom chain, and T_g = RNE(T_{g−1} + S_g).
- **Each group's word starts at a salted H_{i,g}** instead of +0.
  - Its sign and mantissa come from row i's `E_A` sub-domain.
  - Its exponent is v2-hot's rule, `HotSizing.publicConst 64`, the same for every group of the row.
- **The total still starts at +0,** and the promotions are v1's.
- **U = fl(T − Σ_g H_{i,g}),** with the sum folded in FP32 per row. That is one removal per word, not one per group.

C̃ and U change bit for bit, so v1-hot is a version.

## What is priced, and where

| Item | Where | Why |
| --- | --- | --- |
| U's removal, one FP32 add per word | the credit and `W_ref` (`creditDevRev1Hot = creditDevRev1 + add·m·n`); the cap is on this credit | forced clean-up, as v2-hot's (§9) |
| the first promotion add of every word | nowhere: rev1's exclusion (`firstAddDev`) stands | the total starts at +0, so T_1 = S_1 exactly and it stays skippable (§9) |
| H_{i,g} in each group's accumulator | nowhere | it replaces each group fragment's zero fill; the `mma.sync` count is unchanged |
| the fold of Σ_g H_{i,g} | `W_ref` only (`hotFoldDev = add·m·(k/(32·G) − 1)`, `k/128 − 1` per row at G = 4) | honest work outside the tensor-core chain, which scales with m, not m·n (§9) |
| the sizing rule | `W_ref` only (`HotSizing.cost`) | `publicConst` costs nothing, as for v2-hot |
| `k/1,024` keyed-hash blocks per row | the hashing format's accounting | as `E_A`'s own seeds |
| the cast and the in-loop A-only forming | `W_ref` (`c` per activation element, as in `../Pouw/PearlC/DeviceKernelWref.lean`) | the kernel pins' convention |

Numerically the credit is `creditDev` at G = 4, since the removal's add restores the one rev1 drops (§9).

## How the twins are stated

They are stated as v2-hot's are (`../v2-hot/README.md`, "How the twins are stated"):
- **Over any protocol.** Each twin holds for any protocol `P`, domain `D` and record `d` with `G = 4` and the twin's
  prices.
- **The hypotheses** are that `P` meets v1-hot's accounting at `d` (`HotRev1UnitAccounting`, or its tile or chain-only
  forms) and that TT_OUT holds at `P`.
- **The record isn't staged.** `devSm120v1hot` is the rev lane's. Its protocol meets the accounting by one lemma once
  it is defined, and TT_OUT at it is `tt-out/pearl-c-sm120-v1-hot`, §9's candidate row, not yet rated.
- **One `h` for H_{i,g} and `W_ref`,** and every twin is stated for every `h : HotSizing`. The values are at the fixed
  rule, `HotSizing.publicConst 64`.

The pins are named:
- `pearlC{Gamma,Sampled}Sm120v1Hot{,Loop}{Cast8,Cast8p72,Cast32p06,Cast16}{,ChainOnly}_{8192,16384}`: the twins,
  per unit or per tile, at FADD 8.00, or at 8.376 with `Loop`;
- `gammaHotRev1{,ChainOnly}_sm120v1Hot{,Loop}<cast>_publicConst64_<shape>`: the values.

## The values

v1-hot under rev1 at the cap 1/400. Each value is two pins, per unit (`pearlCGamma…`) and per audit tile
(`pearlCSampled…`), with the same γ.

**Forming credited:**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `29136559/5699239375` (0.51124%) | `29245398169/5714672265625` (0.51176%) | 0.51176% (8.376) |
| 8 (the statement's `W_ref`) | 16,384³ | `113909711/22539599375` (0.50538%) | `145953047/28864964375` (0.50564%) | 0.50564% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `29597359/5699700175` (0.51928%) | `29706198169/5715133065625` (0.51978%) | 0.51978% (8.376) |
| 8.72 (64-bit stores, GPU 0) | 16,384³ | `16404473/3220074425` (0.50944%) | `12800315089/2511354300625` (0.50970%) | 0.50970% (8.376) |
| 32.06 (as written) | 8,192³ | `6362137/816376825` (0.77931%) | `44643798169/5730070665625` (0.77911%) | 0.77931% (8.00) |
| 32.06 (as written) | 16,384³ | `144706511/22570396175` (0.64113%) | `48359345267/7544021301875` (0.64103%) | 0.64113% (8.00) |
| 16 (packed) | 8,192³ | `11418853/1901453125` (0.60053%) | `11455132723/1906597421875` (0.60082%) | 0.60082% (8.376) |
| 16 (packed) | 16,384³ | `5911891/1073801875` (0.55056%) | `124521235801/22611507105625` (0.55070%) | 0.55070% (8.376) |

**Chain-only:**

| Honest cast | Shape | FADD 8.00 | FADD `1047/125` = 8.376 | Published |
| --- | --- | --- | --- | --- |
| 8 (the statement's `W_ref`) | 8,192³ | `54672559/5699239375` (0.95930%) | `54781398169/5714672265625` (0.95861%) | 0.95930% (8.00) |
| 8 (the statement's `W_ref`) | 16,384³ | `164981711/22539599375` (0.73196%) | `4239826559/579519669375` (0.73161%) | 0.73196% (8.00) |
| 8.72 (64-bit stores, GPU 0) | 8,192³ | `55133359/5699700175` (0.96730%) | `55242198169/5715133065625` (0.96660%) | 0.96730% (8.00) |
| 8.72 (64-bit stores, GPU 0) | 16,384³ | `23700473/3220074425` (0.73602%) | `55424945267/7534062901875` (0.73566%) | 0.73602% (8.00) |
| 32.06 (as written) | 8,192³ | `10010137/816376825` (1.22617%) | `70179798169/5730070665625` (1.22476%) | 1.22617% (8.00) |
| 32.06 (as written) | 16,384³ | `195778511/22570396175` (0.86741%) | `65383345267/7544021301875` (0.86669%) | 0.86741% (8.00) |
| 16 (packed) | 8,192³ | `19930853/1901453125` (1.04819%) | `19967132723/1906597421875` (1.04727%) | 1.04819% (8.00) |
| 16 (packed) | 16,384³ | `8343891/1073801875` (0.77704%) | `175593235801/22611507105625` (0.77657%) | 0.77704% (8.00) |

### What the published figures cite

| Published figure | Twin, at `h := HotSizing.publicConst 64` | Value lemma | Exact value |
| --- | --- | --- | --- |
| 0.51176%, forming credited, 8,192³, FADD 8.376 | `pearlC{Gamma,Sampled}Sm120v1HotLoopCast8_8192` | `gammaHotRev1_sm120v1HotLoopCast8_publicConst64_8192` | `29245398169/5714672265625` |
| 0.50564%, forming credited, 16,384³, FADD 8.376 | `pearlC{Gamma,Sampled}Sm120v1HotLoopCast8_16384` | `gammaHotRev1_sm120v1HotLoopCast8_publicConst64_16384` | `145953047/28864964375` |
| 0.95930%, chain-only, 8,192³, FADD 8.00 | `pearlC{Gamma,Sampled}Sm120v1HotCast8ChainOnly_8192` | `gammaHotRev1ChainOnly_sm120v1HotCast8_publicConst64_8192` | `54672559/5699239375` |
| 0.73196%, chain-only, 16,384³, FADD 8.00 | `pearlC{Gamma,Sampled}Sm120v1HotCast8ChainOnly_16384` | `gammaHotRev1ChainOnly_sm120v1HotCast8_publicConst64_16384` | `164981711/22539599375` |

The kernel's casts cite the same way, from the tables above, at each row's published price. At the as-written 32.06
that is FADD 8.00 in both readings: the twins without `Loop`, e.g. `pearlC{Gamma,Sampled}Sm120v1HotCast32p06_8192`
with `gammaHotRev1_sm120v1HotCast32p06_publicConst64_8192` (0.77931%).

### Against §9

All six of §9's γ figures reproduce exactly:
- forming credited: 0.51176% (8,192³, 8.376), 0.50564% (16,384³, 8.376) and 0.51124% (8,192³, 8.00);
- chain-only: 0.95861% (8,192³, 8.376), 0.73161% (16,384³, 8.376) and 0.95930% (8,192³, 8.00).

§9's exact value at 8,192³ and 8.376, `29245398169/5714672265625`, is the value lemma's.

### v1-hot against v1 at the same cast

v1's values are its kernel pins (`../Pouw/PearlC/DeviceSm120KernelGamma.lean`). The exceptions are at the statement's
cast: forming credited at 8.00 is `DeviceSm120Gamma`'s instance, and chain-only is computed, since it isn't pinned
(`../uncited.md` §2).

| Cast, reading | Shape | v1-hot published | v1 published | v1-hot − v1, points |
| --- | --- | --- | --- | --- |
| 8 (the statement's), forming credited | 8,192³ | 0.51176% (8.376) | 0.51105% (8.376) | +0.00071 |
| 8 (the statement's), forming credited | 16,384³ | 0.50564% (8.376) | 0.50528% (8.376) | +0.00036 |
| 8 (the statement's), chain-only | 8,192³ | 0.95930% (8.00) | 0.95902% (8.00) | +0.00027 |
| 8 (the statement's), chain-only | 16,384³ | 0.73196% (8.00) | 0.73172% (8.00) | +0.00024 |
| 8.72, forming credited | 8,192³ | 0.51978% (8.376) | 0.51908% (8.376) | +0.00070 |
| 8.72, forming credited | 16,384³ | 0.50970% (8.376) | 0.50934% (8.376) | +0.00036 |
| 8.72, chain-only | 8,192³ | 0.96730% (8.00) | 0.96704% (8.00) | +0.00026 |
| 8.72, chain-only | 16,384³ | 0.73602% (8.00) | 0.73578% (8.00) | +0.00024 |
| 32.06 (as written), forming credited | 8,192³ | 0.77931% (8.00) | 0.77888% (8.00) | +0.00043 |
| 32.06 (as written), forming credited | 16,384³ | 0.64113% (8.00) | 0.64085% (8.00) | +0.00029 |
| 32.06 (as written), chain-only | 8,192³ | 1.22617% (8.00) | 1.22614% (8.00) | +0.00003 |
| 32.06 (as written), chain-only | 16,384³ | 0.86741% (8.00) | 0.86723% (8.00) | +0.00018 |
| 16 (packed), forming credited | 8,192³ | 0.60082% (8.376) | 0.60019% (8.376) | +0.00062 |
| 16 (packed), forming credited | 16,384³ | 0.55070% (8.376) | 0.55036% (8.376) | +0.00034 |
| 16 (packed), chain-only | 8,192³ | 1.04819% (8.00) | 1.04800% (8.00) | +0.00019 |
| 16 (packed), chain-only | 16,384³ | 0.77704% (8.00) | 0.77682% (8.00) | +0.00022 |

- **At every cast v1-hot is equal to v1 within 0.001 points.**
- **v1-hot is slightly higher, the opposite of v2-hot.** Two small effects meet:
  - the fold of Σ_g H_{i,g} is honest work in `W_ref` only, and it raises γ by about 0.0007 points at 8,192³, as §9
    says;
  - the credited removal lowers γ a little. That is the normalization effect bc-22298e90 describes for v2-hot
    (`../statement-review-1350.md` §5), and it grows with `W_ref`'s surplus over the credited worst case.

  So the net gap is largest forming credited at the small casts (+0.00071), and smallest chain-only at the as-written
  cast (+0.00003). The fold scales with m and the chain with m·n·k, so forming credited the gap halves at 16,384³
  (+0.00036).
- **The larger price is v1's.** Forming credited it is 8.376 at casts 8, 8.72 and 16, but 8.00 at the as-written 32.06
  (0.77931% against 0.77911%). Chain-only it is 8.00 at every cast. So an as-written v1-hot figure takes the 8.00
  column in both readings (bc-22298e90, `../statement-review-v1-hot.md`).

## Files

| File | Kind | What it holds |
| --- | --- | --- |
| `Pouw/PearlC/DeviceHotRev1.lean` | trusted, definitions only | `creditDevRev1Hot`, `hotFoldDev`, `wrefDevRev1Hot`, `gammaHotRev1`, `HotRev1UnitAccounting`, `HotRev1TileAccounting`, and their chain-only forms. It reuses `DeviceHot`'s `HotSizing` |
| `Pouw/PearlC/HotRev1Gamma.lean` | proofs, generated | the four general theorems (`pearlC{Gamma,Sampled}HotRev1{,ChainOnly}At`), the 64 twins and the 32 values |
| `gen_v1hot_gamma.py` | generator | writes `HotRev1Gamma.lean` (stdlib only, exact arithmetic); a new cast is one line in `CASTS` |
| `v1-hot-pins.json` | records | the 100 pins as `audit.py --update` wrote them, and the `layers` entry for `DeviceHotRev1` |
| `review-request.md`, `review-request-statements.txt` | review packet | for bc-22298e90 |

## Checks

These were built in the same private copy as `../` (the build section of `../README.md`). `DeviceHotRev1` imports
`DeviceHot` for `HotSizing`, and `DeviceRev1`. Both modules are in the aggregator after `HotGamma`.
- `#print axioms` on the 100 pins: `[propext, Classical.choice, Quot.sound]`.
- A kernel replay of the two modules accepted 123 constants.
- `audit.py --update --no-replay` over the whole copy (14:37Z) passed: 10,119 declarations in 221 modules and 853 pins.
  - The new records are the 100 pins and the 10 definitions they read.
  - No existing record changed, including `../v2-hot/`'s 132.
