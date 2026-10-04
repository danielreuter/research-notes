---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out/pearl-c-sm120-unpromoted-hot` (v2-hot): B. The hot start closes the chain start per word, even when H is mis-sized

30 Sep 2026, 11:45Z. Independent assessor (bc-d7d4b0d1). The design is `theory-pearl-c-sm120.md` §14.1 (bc-3006c44a).
- **The start:** each row's accumulator begins at H_i. Its sign and mantissa come from row i's E_A sub-domain. Its exponent follows a public rule that puts |H_i| near the chain's accumulator at atom t₀, from the row's ρ and the job's largest column RMS.
- **The output:** U = fl(C̃ − H_i), credited as forced clean-up.

## The attack: mis-size H_i with salt-free statistics

- **The loophole to test:** the rule reads only ρ (every 8th position) and a column RMS, both of which a row can steer.
- **The measurement** (`v2hot_start_sm120.py`, the census's bit-exact sm_120 unpromoted step): per word, whether every step of atoms [0, w) is exact, for w = 4, 8, 14. H_i is calibrated so the rule is right on the census's gaussian rows; the reference point is the plain chain's mid-chain windows [16, 16 + w), where the region lemma already holds. 64 × 64 words per cell, 2 repetitions, k = 8,192, all rows in the domain.

| Rows | Plain start, [0, w) | **Hot start, [0, w)** | Plain, mid-chain [16, 16 + w) | H_i against the real accumulator |
|---|---|---|---|---|
| gaussian (census) | 97–98 / 92–94 / 85% | **78–79 / 67 / 56%** | 92–93 / 83–85 / 72–73% | calibrated |
| off-sample-heavy: every 8th position N(0,1), the rest ±U(4, 6.5)ρ | 94–96 / 88 / 75–80% | **22–23 / 13–14 / 9%** | 89 / 79–80 / 60–64% | about 8× too small |
| early-light: the first 16 atoms at 1/64 | 98–99 / 93–94 / 85% | **78–83 / 65–69 / 53–55%** | 86–87 / 76–77 / 63–65% | far too big |

- **In every family, the hot start's early windows are less exact per word than the plain chain's own mid-chain windows,** where no aligned region pays (the census, from atom 16 on). So "the first atoms truncate as mid-chain ones do" holds, including when the rule mis-sizes H_i in either direction.
- **Why H too small doesn't help the adversary:** H's random full mantissa is truncated as soon as the accumulator outgrows it.
- **Why H too large doesn't help either:** the small early products fall below H's window.
- **What stays open:** alignment across words, which per-word rates can't settle. That is node 2's aligned-exact census on the hot chain, as the row says, and it moves this to a closed chain start.

## Rating

**`tt-out/pearl-c-sm120-unpromoted-hot` with its cap-1,000 and tile twins: B** (CPU, bit-exact). It is v2's cap-1,000 row (B), with the chain-start gap closed per word against a mis-sized hot start.
- **The FADD for U** is forced (U depends on the hot chain's rounding) and credited, so γ doesn't move: 0.362%, and chain-only 0.8366–0.8371% at 8,192³.
- **Falsifier (↓):** an aligned exact region on the hot chain's first atoms at a paying shape, which the node-2 census would show.
