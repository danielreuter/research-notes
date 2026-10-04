---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `pearl-quantized-subspace-hardness` (Pearl's Assumption 1): B for its concrete reading

30 Sep 2026, 08:05Z. Independent assessor (bc-d7d4b0d1), on [the rating scale](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/rating-scale.md). Script: `noise_lowrank_sm120.py`, CPU on node 2, with the bit-exact sm_120 atom and the census's s5 forming (branch `cursor/pearl-c-sm120-attacks-cb92` at `5f1cb93e`). Runs: `r20260930-074918-eab3` (k = 1,024–16,384) and `r20260930-075641-9b96` (FP4 limbs of the split residual).

**The reading rated.** No program reproduces, bit for bit, the product of E4M3-quantized rank-32 noise for less than a generic FP8 product of the same shape, at the RTX PRO 6000's measured prices. The row itself is informal: no γ₀, zero input, average case. Its concrete successors are `tt-out/*` (worst case, rated B at rev1) and `tt-out-avg/*`.

**Two settings.** Pearl's own is the noise alone at a fixed scale, N = E·Fᵀ with E (rows × 32) and F (k × 32). Pearl-C's in-domain forming is A′ = e4m3(D), with D = α·x + E′·Fᵀ through the atom. Its noise scale follows the signal's RMS, so at zero input there is no noise and the unit is out of domain.

**Every cheaper route, priced per useful MAC** (1.00 = the honest FP8 chain):

| Route | What it would need | Measured | Cost |
|---|---|---|---|
| **Low-rank product.** E_A·(F_Aᵀ F_B)·E_Bᵀ, one 32 × 32 Gram per job, at about 32/k | the quantized product to equal the rank-32 one | 0 of all ticket words match, in both settings; median error about 4% relative (2·10²–10⁶ ulps) | about 0.004, but useless: no word comes out right |
| **Split the rank-32 part off.** A′ = D + R, D low-rank (cheap through its factors), R = e4m3(D) − D | R_A·R_Bᵀ cheap: R sparse or narrow | R dense: the cast is exact on ≤ 0.4% of elements. With signal, R has a median 17–18 significant bits (FP16 fits 1.5–4%). Noise-dominated inputs (`spikes-first`, `sparse10`): 8 bits, FP16 fits 82–91% | ≥ 2.00 (FP16 for noise-dominated R), 8.46 (FP32 class) otherwise, plus the low-rank terms |
| **Split with R in NVFP4** (the only format below 1.00) | R in about 1 E2M1 limb per 16-block | 4.5–6.8 limbs per block (a lower bound), and no block with one | ≥ 10 |
| **Caching by quantization class.** Four Russians or lookup tables on the codes | repeated code tuples, cheap lookups | 121–192 distinct codes per row; no 32-code slice repeats across salts; lookups cost 16–66 (`r20260930-062627-063a`) | ≥ 16 |
| **Reuse across salts or tiles** | shared noise | E, F and B̃ are salt-derived and codes repeat across salts only by chance (1.3–1.5%); within a job only F's Gram is shared, and it gives only the 4%-off predictor | no saving |

**Does quantization leak the low rank?** Partly, but not usefully:
- E4M3 leaves 97.7% of A′'s energy in rank 32 in Pearl's setting (2.3% outside), and E2M1 under an NVFP4-style cast (a model) leaves 91.8% (8.2% outside).
- Pearl-C's A′ with a rank-1 signal keeps 93% in rank 32.
- The rank survives *approximately*. The exact product still needs R's product, which is dense and at least as wide as the product it would replace.

**Why the split can't win in principle.** C̃ = A′B̃ᵀ exactly, and A′ = D + R turns one dense product into D's cheap low-rank terms plus R_A·R_Bᵀ.
- R_A·R_Bᵀ is itself a dense product of the same shape: R is dense because the cast is almost never exact.
- Its operands are no narrower than what the cheapest unit holds. The one format cheaper than FP8 (NVFP4) needs ≥ 4.5 limbs per block.
- So the split costs at least one generic product plus the low-rank terms.

**Rating: B (about 0.5 CPU-h on the bit-exact atom, 0.03 GPU-h of prices).** Each route could have beaten the honest product at the measured rates (an exact cast, a narrow R, repeated slices), and none did.

**↓ (not covered):**
- algorithms that don't split A′ at all; the generic question of whether this particular FP8 product has a sub-(m·k·n) algorithm is `no-exact-rewrite` (B), not this row;
- E2M1 operands in Pearl-C4, whose noise lives on a coarser grid, are the FP4 rows' to test.

**What the statement should say:** the concrete reading above, with a device, the bit-exact output and γ₀. Or retire it in favour of `tt-out-avg/*`.
