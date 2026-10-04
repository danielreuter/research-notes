---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# F1′ + F2, the Pearl-C4 base-split and flatness fix: conditional GO. I couldn't break it

30 Sep 2026, 14:00Z. Independent assessor (bc-d7d4b0d1). The fix under review is bc-a8466279's `internal/pouw/rtx-pro/theory-pearl-c4-domain.md` §6.2–6.5 (13:50Z banner), with F2 as corrected by bc-d9842080 (`internal/pouw/nvfp4-int8-flatness-break.md`, "Pinning c_L per shape", 13:35Z).

## Verdict

**GO, conditional on the int8-Strassen replay confirming c_L.**
- In every construction I tried, F1′ and F2 together charged more than the route saved, or the route didn't beat honest at all.
- **The two terms are complementary.** Flat scales, which F2's int8 route needs, come from tied near-max codes in every block, and those are the reliable codes F1′ charges.
- **Both F2's charge and F1′'s margin over the flat-scale routes rest on c_L**, which is my unmeasured add-cost model. That replay is the decider.

## What I ran

On CPU, against copies of `internal/pouw/cheap-binding/pearlc4-fix/` with a `torch` shim (`torch.special.ndtr` = `scipy.special.ndtr`), plus my scripts in this folder. The forming is bc-a8466279's vectorized Gaussian, not the exact reference.

**Reproduced first:** F1′ per MAC, exactly as §6.2 gives them:

| Family | F1′ per MAC |
|---|---|
| spike rows | 91.7% |
| narrow-cell rows | 28.9% |
| max at a fixed offset | 0.0% |

## The four open items

**2. Is sorted pairing the cheater's best layout within a block? Yes, where it matters** (`break_item2*.py`).
- **Random layouts:** I searched 300 random layouts per window, plus a hill-climb (pairwise swaps within each block, run to a local optimum) starting from dnc2's sorted, alternating layout.
- **Synthetic probability vectors:** the hill-climb gains up to +0.018 per MAC.
- **The real families:**

  | Family | Gain over dnc2's layout |
  |---|---|
  | spike rows | 0.000 (0 of 6 windows improved) |
  | narrow-cell | ≤ +0.0011 |
  | max-offset | ≤ +0.0005 |

- **Why it doesn't matter:** a tile is rejected once its debit passes 1/400. What matters is whether a profitable row can sit under that cap, not F1′'s exact value once it's above.
- **Optional:** replace the sorted layout by an exact in-block optimum.

**1. Gathering across blocks on operands flat on both sides: covered, because F1′ catches what F2 misses.**
- **F2 reads one tile-modal byte.** Split a tile's block columns into two classes, each flat at its own UE4M3 byte, and the tile's modal share is about 0.5, so F2 = 0 at every shape. The masked int8 route still runs, as one K/2 sub-GEMM per class. So F2 alone is blind to multi-class flatness.
- **F1′ covers it** (`mc_tuned.py`: two classes at 8.9ρ and 8.9ρ/1.125, one UE4M3 mantissa step apart in the same binade, both centred by one tuned row max; routes priced with the pinned c_L on K/2):

  | Tied maxima per block | Class flatness | F1′ | int8 route's saving, 8k / 16k / 32k / 64k | F2 |
  |---|---|---|---|---|
  | 1 | 0.920 / 0.918 | 2.6% | 0 at every shape | 0 |
  | 2 | 0.972 / 0.960 | 8.5% | 0 / 0 / 0.8% / 2.3% | 0 |
  | 3 | 0.976 / 0.984 | **15.7%** | 3.1% / 9.1% / 12.1% / **13.6%** | 0 |

- **More tied maxima means flatter scales and more reliable codes, so F1′ rises with the route's saving.**
  - Every construction is over the 1/400 cap. So every tile is rejected, whatever the saving.
  - F1′ also exceeds the route's saving at every shape I checked. The thinnest margin is tie = 3 at 65,536³: 15.7% against 13.6%.
- **The two-class spike rows** (14 per block, class flatness 0.998 / 0.993, F2 = 0) are charged 79.1% by F1′.
- **Checking my flatness metric:** untuned one-max rows give 0.59. bc-a8466279's 0.965 needs the row-max centring, and with it my construction reaches 0.92–0.98, consistent with theirs.
- **Recommended as cheap insurance, not a requirement:** F2 could read flatness modulo row and column-class factors (for example, the modal byte per block column within the tile, and per-row scale factors, which the int8 route absorbs for free), so the multi-class defence doesn't rest on F1′ alone.

**3. Adaptive regrouping after the salt: bounded, not closed.**
- The cheater sees the realised codes before choosing a layout. But one k-permutation is shared by a fragment's 16 rows and 8 columns (A′ and B̃ must be permuted together), so per-row packing of realised changes isn't available.
- F1′'s per-row expected saving is the cheater-favourable side of per-fragment adaptivity in every case I can argue, but I haven't measured it.
- **Measurement to add:** the realised best shared permutation for 16-row fragments on honest rows, against F1′.

**4. The exact-law replay: not run.**
- The Gaussian at σα overstates the tails (bc-a8466279's note), so p_t and S_w are overstated. That is the over-charging side for attack rows, and a coverage cost for honest ones.
- So this is a tightness and coverage check, not a soundness risk.

## F2's corrected version

- **Pinned c_L:** 0.808 / 0.707 / 0.619 / 0.542 at 8,192³ to 65,536³.
- **Break-even f\*:** 0.976 / 0.963 / 0.952 / 0.943.
- **It behaves as designed:**
  - honest tiles pay 0 at every shape;
  - the flat family (f = 0.99976) is charged 19.1–37.0%, equal to its route's saving;
  - a single-class one-max tile at 0.965 is caught from 32,768³ on.
- **The two edits** (a patch of 4 FP4 slots per side, depth capped by k/B only) are right. The depth cap errs toward the adversary, which is sound.
- **Capping S_w at 1:** the capped sum still bounds the better of the two routes.

## What the verdict rests on, and the gaps

- **c_L** (my free-merge add model): the int8-Strassen replay settles it.
  - If c_L is lower than modelled, F2's break-even moves up.
  - F1′'s margin over the multi-class route shrinks. It is already thin at tie = 3 and 65,536³, where it is 15.7% against 13.6%.
- **MXFP4:** F2 covers it (shaped rows rejected; honest F2 = 0 on 0.5B and 1B, with a thinner margin). **F1′'s honest MXFP4 coverage is unmeasured.** UE8M0 scales are flatter on honest data, so M_w is smaller and the honest F1′ charge could be higher. Measure it before MXFP4 relies on F1′.
- **Everything here is CPU work on the vectorized forming, one salt per construction.** GPU 7's stride-row rerun (every stride family rejected, controls zero; `art:fb8f7aac…`) is independent corroboration for F1′.

## Update 14:20Z: the int8-Strassen replay pins c_L. F2's formula is a sound adversary-best lower bound; use the measured leaf

**What ran** (node 2, preemptible fill `assessor-int8-strassen`, GPU 5 under `on=2-7`, 14:13–14:17Z; outputs preserved by `r20260930-141857-38a8`; code `int8_strassen_replay.cu`):
- the int8 IMMA GEMM (cuBLASLt, s8 × s8 → s32) and its batched small leaves;
- a standalone s8 pre-add and s32 merge;
- the NVFP4 dense divisor (CUTLASS 4.8 `dense128`, BF16 and FP32 words), in the same session, 3 interleaved reps.

| Shape | int8 GEMM | NVFP4 dense, BF16 words | Ratio |
|---|---|---|---|
| 8,192³ | 1.497 ms (735 TOPS) | 0.781 ms | 1.92 |
| 16,384³ | 11.53 ms (763 TOPS) | 7.150 ms | 1.61 |
| 32,768³ | 90.29 ms (779 TOPS) | 105.1 ms | 0.86 (my NVFP4 kernel falls off at this size) |

- **The leaf, taking each side's best rate:** int8 390 G MAC/s, NVFP4 704 G MAC/s, so **1.81 FP4 slots per MAC**, not the formula's 2.0.
  - W1's issue-rate ratio is exactly 2.0.
  - At whole-GEMM scale, NVFP4 reaches about 88% of its issue peak and int8 about 98%.
- **Batched leaves lose efficiency fast:** 476 TOPS at 1,024³ leaves, 124 at 256³ and 30 at 64³.
  - That is the leaf size a depth-7 recursion from 8,192 reaches.
  - A real deep recursion pays far more than the leaf term.
- **Standalone adds are bandwidth-bound:** the s8 pre-add costs about 1,440 FP4 slots per element and the s32 merge about 5,700 (8,192²), against the formula's fused 4.25 and free merges.
  - Deep Strassen must materialise Θ(n²·(7/4)^L) bytes of operands (88× the matrix at L = 8).
  - On this card that is memory-bound at every depth ≥ 2 at 8,192³.
  - So the real route costs well above c_L.

**Verdict on c_L:**
- **The formula is sound as the adversary's best:** its add terms are an idealisation no measured kernel approaches, so c_L can only be higher in practice, and F2 then over-charges.
- **One correction, the leaf.** To stay adversary-best in wall time, F2 should take the measured leaf, 1.81 slots, not 2.0:

  | Shape | c_L | Break-even f\* |
  |---|---|---|
  | 8,192³ | **0.741** | **0.968** |
  | 16,384³ | 0.649 | 0.956 |
  | 32,768³ | 0.568 | 0.946 |
  | 65,536³ | 0.497 | 0.937 |

  (With the 2.0 leaf these are 0.808 / 0.707 / 0.619 / 0.542 and 0.976 / 0.963 / 0.952 / 0.943.)

**Effect on the GO: none.**
- The relevant test is the 1/400 reject, not charge against saving. Every multi-class flat construction above has F1′ ≥ 2.6% (tie = 1, where the route doesn't pay), so it's rejected outright.
- With the measured leaf, tie = 3's route saving at ≥ 32,768³ rises to about 19–20%, above its 15.7% F1′ charge, but that tile is still over the cap by 60×.
- A single-class tile between f = 0.968 and 0.976 now has a small route saving the 2.0-leaf F2 misses. The only flat single-class rows there need tied maxima, and F1′ ≥ 8% rejects them.

**So: F1′ + F2 is a GO.** The condition on c_L is met, with F2 taking leaf = 1.81.
