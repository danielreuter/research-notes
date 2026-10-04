---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `tt-out-chain/pearl-c-sm120`: B at rev1's credit; the measured cast puts its γ at the 1% line

30 Sep 2026, 08:55Z. Independent assessor (bc-d7d4b0d1). The row is TT_OUT with the credit's salted forming term removed (f_s = 40 at sm_120 prices: the noise atom at 32, the cast at 8). It is weaker, since its credit is pointwise smaller.

**Its credit** is the original `tt-out/pearl-c-sm120`'s, less forming, so the free first promotion is still in it: D at the literal credit, B at rev1's. The table owner's queue lists it "at `-rev1`'s credit", and that is what I rate.

**Skipping or fusing the cast or the noise atom:**
- **Under this row it can't matter:** forming isn't credited, so a program that saved on it would violate nothing.
- **Under the forming-credited rev1 rows it doesn't pay:**
  - The noise atom is an m × k × 32 GEMM at 1 unit per MAC, with no cheaper exact engine (NVFP4 limbs ≥ 3.1×).
  - The cast can't fuse into the MMA: `mma.sync` writes FP32, and `F2FP` is its own instruction.
  - The elements whose code the noise can't change are P3's salt-dead debit.

**The cast's price**, pooled from GPU 0 (bc-e6a46970; `r20260930-063213-c94a`, `r20260930-063827-e4c6`, locked-2100): `F2FP` alone costs 7.7–8.0 units per code. It shares a half-rate pipe with integer instructions, so a quantizer that packs four codes per word with one `PRMT` pays 12.0–12.3 per code. Interpolating the row's two points (0.959% at 8, 1.225% at 32), γ at 8,192³ is 0.95–0.96% with the cast alone and **about 1.01%** with the packing. The line carries γ ≤ 1% only if the honest kernel packs its codes without an extra integer op per word. That is a γ fact for the panel line, not the row's truth.

**Rating: B at rev1's credit** (CPU bit-exact, measured prices). **For the panel:** chain-only γ at 8,192³ sits at 0.95–1.01% on the measured cast.
