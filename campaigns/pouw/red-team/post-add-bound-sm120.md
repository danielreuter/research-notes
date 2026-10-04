---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `post-add-bound/sm120`: C. The count's premise misses a free mechanism, though the conclusion has a wide margin

30 Sep 2026, 10:55Z. Independent assessor (bc-d7d4b0d1). The row is bc-b58c6093's (`ttout-restatements.md` §7, with the catalogue `cheap-binding/fmm-ranks.json`). Over the fast-matmul catalogue, a 128-deep E4M3 group rewrites at 0.929× of honest if FP32 post-adds are free, and at ≥ 1.067× if each costs 8 units. v1's tensor-core closure (every rewrite with K ≤ 128 costs ≥ 1.067) rests on the priced form.

## The bound as stated

- **The claim:** a scheme ⟨p, q, r; R⟩ has nnz(W) ≥ pqr output coefficients (rank q per output block).
- **What it counts as free:** each product accumulates into one output block in place, through the MMA's accumulator.
- **The conclusion:** a level needs at least pqr − R further FP32 block additions, q(1 − ρ) per output word, each priced at 8 units.

## What sm_120 actually gives for free

**Seeding.** `mma.sync` reads its accumulator C from any register and writes D to another. So a value (one product, or a partial sum of several) can seed any number of later chains at no cost, with no FP32 add and no recomputation.

**What that changes.**
- A product can serve several outputs through a shared prefix.
- The free operations are "add one product to any existing value", not "one output per product".
- "nnz(W) − R adds" follows from the first premise, not the second, so it is not a derived lower bound on sm_120.

**Example, Strassen–Winograd ⟨2,2,2; 7⟩:**
- Its outputs, as product sets: C11 = {1, 2}, C12 = {1, 6, 5, 3}, C21 = {1, 6, 7, −4}, C22 = {1, 6, 7, 5}.
- Textbook form: 7 block post-adds.
- With prefix seeding and 7 MMAs: 2.
  - The chains are 1 → 2 (C11), 1 → 6 → 7 → −4 (C21, with nodes {1, 6} and {1, 6, 7}), and 5 → 3.
  - Then C12 = {1, 6} + {5, 3} and C22 = {1, 6, 7} + {5}.
- That is still ≥ the bound's 1, so this scheme doesn't break it. But the count's argument doesn't cover programs like this one.

**Exactness isn't a new constraint.** Seeding is exact wherever in-place accumulation is: on the exact regions a rewrite needs, every partial sum is exact, so the order and grouping of the sums don't matter.

## Does the conclusion survive? Probably, with a wide margin, but it isn't proved

- **What a break would need at w = 4 atoms (K = 128).** The free family's best shapes cost 0.996–0.999 per honest MAC. A rewrite there beats honest only if its FP32 merges cost at most about 0.004 per honest MAC: at most about 0.064 merges per output word (0.004 · 128 / 8).
- **What even the smallest case gives.**
  - Every level of a scheme with R < pqr needs merges.
  - For ⟨2,2,2⟩, a zero-merge program (the outputs as nodes of one forest of chains) would need seven products whose sums realize the four blocks. The rank constraints on the blocks' differences rule out the forests I tried.
  - At one merge per four blocks and per level, and with the several levels the deep compositions need, the count stays well above 0.064 per word.
- **What would settle it:** a bound on merges in the accumulate-and-merge model (each product added once to any existing value, values reusable, merges priced), or an exact per-scheme search over the catalogue's small formats.

## Rating

**C** for the row as stated: the derivation doesn't hold on sm_120's `mma.sync`.
- **What the statement should say:** the free operations are adding a product to any existing value, with values reusable. The count has to be re-proved in that model, or checked per scheme.
- **The conclusion** (K ≤ 128 closes) probably survives. It needs merges ≤ about 0.064 per output word to fail.
- **Falsifier (↓):** a catalogue scheme whose outputs form a forest of shared chains, with few merges per level, at K ≤ 128.
- **Other routes to cheaper post-adds don't exist on this card:**
  - FP32 adds cost 8.0–8.46 per add (FADD, FFMA);
  - `add.f32x2` is two FADDs;
  - IADD3 on fixed point is about 8 per add, before conversions;
  - BF16, FP16 and TF32 MMA adds round FP32;
  - L2 reductions are far slower than FADD per add.

Seeding is the only near-free mechanism, and it is the one the count misses.
