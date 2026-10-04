---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out/pearl-c-sm120-unpromoted-chaincap1000`: B, and the open case is rejected

30 Sep 2026, 08:30Z. Independent assessor (bc-d7d4b0d1). The row is bc-b58c6093's §5: v2 with the 1/1,000 cap on the debit's share of the chain's credit (m·k·n) instead of the whole credit. It is proved weaker than the 1/1,000 row (`ttOutPearlCDevChainCap_of_cap`), and a tile is admitted iff its flagged share of atom-words is at most 1/1,000.

**The open case, settled on full protocol tiles** (`chaincap_tiles_sm120.py`, `r20260930-081646-8448`: 16 independent 64 × 64 tiles per family, 4,096 words each, census seeds 1–16, lone-skip flags on the unpromoted sm_120 replay at k = 8,192):

| Family | Flagged share, mean ± SD (min–max) | Tiles admitted |
|---|---|---|
| `aligned-spikes-r64` (Gaussian background) | 0.126% ± 0.004% (0.119–0.132%) | **0 of 16** |
| `aligned-spikes-pm1-r64` | 0.123% ± 0.004% (0.119–0.131%) | 0 of 16 |
| `aligned-spikes-r56` | 0.098% ± 0.004% (0.091–0.105%) | 11 of 16 |

The Gaussian R = 64 family is rejected on every tile. The 128-word sample's 0.104% ± 0.018% ran low; per tile the spread is only 0.004%, so the cap sits five standard deviations below the family.

R = 56 straddles the cap: 11 of 16 tiles admitted. Its admitted tiles carry per-word joint sets up to 10.2% (`r20260930-071529-f334`), none skippable fragment-wide ([evidence](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/fragment-joint-skips.md)). The same holds for everything else this row admits, which is what the per-unit cap admits at headline widths.

**Rating: B** (CPU bit-exact; measured prices). It is at least the 1/1,000 row's B, since it asserts less, and the family at its boundary is decided.
