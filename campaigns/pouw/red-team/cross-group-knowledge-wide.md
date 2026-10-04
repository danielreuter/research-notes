---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `cross-group-knowledge-wide/pearl-c`: B, and the wide residue is almost empty

30 Sep 2026, 08:45Z. Independent assessor (bc-d7d4b0d1). This row carries only cross-group sets spanning three or more promotion groups. The verifier debits the narrow ones, spanning two groups, by a pair replay. The table owner asked for a census of the set spans.

**The census** (`cross_group_span_sm120.py`, `r20260930-083156-165c`; k = 8,192, G = 4, the bit-exact sm_120 atom, census s5 forming, 16 words per family). Per word, from the honest state:
- **N,** what a narrow debit flags: lone skips, P1's within-group joint flags, and every atom of a jointly skippable pair spanning two groups (neither atom alone). The pair test replays the two group sums and the FP32 promotion fold.
- **S,** the census's greedy joint set.
- **The wide residue S \ N,** what the narrower conjecture still carries.

| Family | Greedy set | Narrow debit N | Wide residue (share of atoms) | Wide share of the greedy set |
|---|---|---|---|---|
| gaussian | 0.05% | 0.05% | 0 | 0 |
| outliers-first | 1.1% | 1.4% | 0 | 0 |
| spikes-first | 1.5% | 1.8% | 0 | 0 |
| aligned-spikes-r32 | 3.2% | 4.6% | 0.024% (max 0.39% per word) | 0.45% |
| aligned-spikes-r48 | 6.0% | 10.0% | 0 | 0 |
| aligned-spikes-pm1-r48 | 7.2% | 11.2% | 0 | 0 |

**What it shows:**
- More than 99.5% of the greedy's cross-group atoms are covered by a two-group debit. Pairs dominate: the greedy packs pairs by construction, and the singles it adds afterwards turn out to be pair-covered too.
- So the wide conjecture carries at most 0.024% of atoms here, a hundredth of γ₀.
- **The price is the debit:** the pair replay flags 0.05% of atoms on Gaussian inputs, 1.4–1.8% on outlier and spike families, and 4.6–11% on aligned spikes. Units of the last kind then exceed the 1/400 cap and are rejected, a coverage cost for spiky inputs. Real activations are about 0.002% (the row's own figure), so it costs them nothing.
- The replay's own cost is bounded by the row: about 2,000 pairs of groups per word at k = 8,192.

**Rating: B** (CPU bit-exact).
- It is weaker than `cross-group-knowledge/pearl-c` (B, 0 fragment-wide), since it asserts less.
- Its residue is measured near zero, so the narrower conjecture is worth having: it moves almost all of the carried hole into the replay.
- **↓:** 16 words per family, at k = 8,192 only. The residue is a greedy lower bound, so wider sets the greedy doesn't reach aren't counted.
