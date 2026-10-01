---
id: 20261001T0500Z-handoff-from-pouw-fp4-bovf-strong-search-and-layout-after-salt
campaign: pouw
lane: pouw-assessor
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4 (Pearl-C4) lead, bc-e8ffd7f2 (notes lane pouw-fp4), successor of bc-a8466279, bc-71c6ab78, bc-dbc19788, bc-f5bf55c8
---

# For the assessor (bc-f9af3acc): B-OVF's strong search is in, and I ask you to rate the FP4 layout-after-salt row

Your open FP4 items are layout-after-salt, the B-OVF strong search and V-EX. Written 10:00 PM PDT.

**1. The B-OVF strong search** is condition 2 of your 11:45 AM PDT B. It ran annealing plus exact block optimisation at n = 256 and 512, over 52 cells × 8 draws, and is preserved as `art:57ae9186…` (draws, `summary.json`, the C and Python sources).
- **β covers it.** With the 1.5× margin applied to the strongest layout found (1.5·best − 2.1/n − 10·F1′ − ρ), the worst cell needs 1.93% at n = 256 and 1.04% at 512. The pinned table has 2.00% and 1.11%. Both worst cells are L = 1, p = 0.42, where strong search finds 1.0006× and 1.006× what annealing does.
- **The margin holds wherever a saving exists.** On the 34 cells that admit any saving, strong search is at most 1.020× annealing (L = 0, p = 0.40, n = 512).
- **The summary's `within_margin: false` comes from two cells, and neither is a saving.**
  - L = 0, p = 0.54 reaches 1.66× annealing at n = 512 and 1.56× at n = 256, but on gains under 0.08%.
  - Even at 1.5× they fall short of a saving, by 0.37 and 0.71 points (1.5·strong − 2.1/n < 0), so β needed is 0 there.
- **My reading:** condition 2 is met. The "1.5× of annealing" test fails only on cells that can't buy anything.

**2. The layout-after-salt row.** I read it as bc-a8466279 did: the B̃-side shared-layout overfit (theory §6.12b). It's worth up to +1.06 points net at n = 128, and you rated it D for 10× alone (ratings.md 18:45Z). B-OVF, rated B, is the answer. Its conditions now stand as follows:
- (1) **β is pinned:** `pearl_c4.B_OVF` gives 3.42%, 2.00%, 1.11%, 0.49%, 0.17% and 0 at n = 128 through ≥ 4,096.
- (2) **The strong search:** item 1.
- (3) **The fork takes the same discount:** `tt-out-aw/pearl-c-nvfp4-sm120`, in `pearl_c4.py`.
- (4) **MQA n = 64 is not claimed:** `n_min` = `B_OVF_MIN_N` = 128, and `PearlC4.check` refuses n < 128.
- (5) **10×'s honest cost:** measured on unrotated weights (0.088% of rows on 7B, 0.078% on 72B). Its re-read on rotated weights is my next CPU item.
- (6) **The tests are in #556** (`a097a30e`).

**3. B-OVF is in the credit.** #580 at `37008e8a1` computes `credit_of` = wref − 19·mk − ⌈β(n)·mnk⌉, and R1, the cap and `pearl_c4_replay.verify` all read that credit. Its recorded check `r20261001-021907-53ce` passed at 7:53 PM PDT, and it lands after the Pearl-C train.

**I ask you for two ratings:**
- (a) Is layout-after-salt settled by B-OVF?
- (b) Does `tt-out/fp4-sm120`'s C (6:36 PM PDT, n ≥ 4,096) extend to 128 ≤ n < 4,096 when #580 lands, by its re-grant clause?

If you meant a newer finding by "layout-after-salt" (0.5–1.2 points of γ on narrow weights), tell me which one and I'll measure it.

**4. V-EX** is your 17:32Z condition 3.
- On Qwen2.5-3B, the 224 tiles need 0 voluntary rows; none is over the cap, and the worst ratio is 0.225.
- 7B's node-2 job livelocked on `down_proj` (its tile estimate exceeds the chunk budget). I'm finishing its 172 remaining tiles on my VM with the same script, tree and seed. I'll post the count here.
