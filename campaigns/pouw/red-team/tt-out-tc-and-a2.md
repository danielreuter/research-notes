---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out-tc/pearl-c-sm120`: B at rev1's credit (D at the original); `a2/sm120`: C

30 Sep 2026, 08:55Z. Independent assessor (bc-d7d4b0d1).

**`tt-out-tc/pearl-c-sm120`** is TT_OUT restricted to one class of programs: straight-line sm_120 MMA of every kind, shape, precision and sparsity; FP32 and INT32 arithmetic; free oblivious moves. No bit tricks on FP words, no tables, no branching.

**It is stated on the D-rated credit.** The row says "`tt-out/pearl-c-sm120` for the programs of one class". The free first promotion is itself a program of this class: the honest one with one FADD left out. So the row is **D at its literal credit** ([first-promotion note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/first-promotion-overcredit.md)) and needs `-rev1`'s credit, as the table owner's queue already assumes.

**At rev1's credit, every route of the class that I ran or priced** (measured prices on the RTX PRO 6000):
- **Other MMA precisions and sparsity** (`r20260930-060338-26b9`, `-071827-bcfb`):
  - FP8 with FP16 accumulate, int8 and E2M1 through `f8f6f4`: 1.00, not cheaper;
  - FP16/BF16 2.00, TF32 4.00, int4 emulated at 10.2, NVFP4 0.50;
  - 2:4-sparse FP8: the dense rate per useful product, so a split into two 2:4 halves only breaks even.
- **Limb emulation** (`r20260930-055203-10e8`): int8 limbs ≥ 4.9× the chain, NVFP4 limbs ≥ 3.1×, 0 one-limb blocks.
- **Strassen and Winograd at any level:** at most 3 levels fit a 128-deep group, and the best is 1.80× the chain.
- **Dropping promotion adds:** ≤ 11% of words survive dropping them all, and no tile does (the census).
- **Fusing promotions into the accumulator:** correct only with an oracle; 0 of 63–127 tile-groups certifiable (`r20260930-071537-652b`).
- **Joint atom skips:** 0 fragment-wide on every unit inside the cap, for v1 and v2 (`r20260930-071529-f334`, `-075758-b6ee`).
- **Splitting the rank-32 noise off:** ≥ 2× (`r20260930-074918-eab3`).

**Rating: B at rev1's credit** (0.05 GPU-h on the card and about 5 CPU-h on the bit-exact atom). The class's search found nothing.

**`a2/sm120`** is the other half: every real program is matched on the checked words by a class program at most γ₂ more expensive, so this row carries only bit-level and table routes. What bounds those routes on this card, measured:
- lookups at 16.2 (`PRMT`) to ≥ 32 (shared memory; 66 with random indices);
- bit operations on FP32 words at 16 (LOP3, PRMT, IMAD), against 1.00 per MAC on the tensor core;
- I2F at 32 (`r20260930-062627-063a`).

So a bit-level route must replace a tensor-core MAC with fewer than 1/16 of an op to pay. No such route is known, but none was searched for either.

**Rating: C**, the same class as NCP's `a2/m4090` (an idealized-model claim). The falsifier is a bit-level or table algorithm for the FP8 chain's words at under 1 unit per MAC.
