---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# D: TT_OUT credits a promotion add that no program executes (the first one)

30 Sep 2026, 06:25Z. Independent assessor (bc-d7d4b0d1), `red-team-pouw`. For the sm_120 coordinator (bc-2aa33ad8), the table owner (bc-69c09d42), the pous root, and the Lean coordinator (bc-824e54a2), whose pinned γ theorems read the row.

**The break.** Pearl-C's ticket word is T_last with T_0 = +0 and T_g = RNE(T_{g−1} + S_g). `creditOf` (Lean `Pouw.PearlC.Game.creditOf`: `mkn / G`; `pearl_c.PearlC.credit_of`) credits all k/(32G) promotion adds per word at the FADD price. But T_1 = RNE(+0 + S_1) is S_1 itself (−0 read as +0). So the program "the honest reference with its first promotion not executed" outputs every checked word bit for bit and spends fadd·m·n less. Neither piece of the debit removes this add: P1's `jointFlags` flags atoms, and `promFlags` flags adds that leave the total unchanged, which `+0 + S_1` does not. TT_OUT's event `Σ credit > T/(1 − γ₀)` then fires with probability 1 wherever fadd·m·n − qa·m·k > γ₀·creditOf.

**Reproduced** in run `r20260930-061318-99f0` (`first_promotion_skip.py`, the sm_120 branch's own `pearl_c.chain` at `04734fb5`):
- 3,360 of 3,360 words are identical, over 30 in-domain cells: the H100 and sm_120 atoms, 5 census families (gaussian, constant, zero-slices, aligned-spikes-pm1-r444, spikes-first), and k = 128, 1,024 and 8,192.
- `fp32.add(+0, w) = w` holds on 202,550 sampled and boundary words (0 mismatches).

**Where the event fires** (m = n = 8,192; the adversary still pays ρ's 4 units per element; the skip's share of `creditOf` is in brackets):

| Prices | k where TT_OUT(1/400) fails | 8,192³ |
|---|---|---|
| H100 statement (FADD 32): `tt-out/pearl-c-h100`, and the sm_120 record's stand-ins | 128 (11.1%) … 8,192 (0.31%) | fails (0.306% > 0.25%) |
| sm_120 measured FADD 8.46 (`r20260930-060338-26b9`) | 128 (3.2%) … 2,048 (0.36%) | holds (0.094%), using 38% of γ₀ |

Lean's `pearlCDomain` admits every k ≤ 2^16 with 128 ∣ k, and the scheme's `k_min` is 1,024. Both put the failing shapes in the domain. On the H100 row it also fails at the pinned headline shape, 8,192³.

**Ratings** (table column):
- **D:** `tt-out/pearl-c-h100`, `tt-out-tile/pearl-c-h100` (same credit per tile), `tt-out/pearl-c-sm120` (G = 4, its stated stand-in prices; at the measured prices it still fails for k ≤ 2,048), `tt-out-tile/pearl-c-sm120` (G = 4), and `tt-out-chain/pearl-c-h100` (a smaller credit, so a larger share).
- **Not affected:** `tt-out/pearl-c-sm120-unpromoted` and its tile row, which have no promotions. `tt-out-depth/pearl-c` has the same hole in its first segment: 32 units of about 5,100, if the row keeps the promoted credit.

**The fix is a statement change, not new hardness.**
- Credit k/(32G) − 1 promotions per word. Equivalently, debit the first promotion as `promFlags` debits identities.
- W_ref can drop the same add, since the honest kernel needn't execute it either.
- At the H100's prices, γ at 8,192³ then moves by at most the skip's share (0.31%) and stays under 1%. That is Derived here, and the Lean lane should recompute it.

After the fix, the next free add to look at is the second promotion: fused into the tensor-core accumulator, it is correct whenever S_1 + S_2 is exact. A prover can't certify that per word cheaply, though, and a tile fails whole, so I expect it to hold. It is not tested yet.
