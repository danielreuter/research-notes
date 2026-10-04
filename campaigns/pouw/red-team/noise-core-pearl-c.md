---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `noise-core/pearl-c`: B for the FP8 forming (δ = 1); C for the FP4 forming (δ = 1/4), untested

30 Sep 2026, 08:15Z. Independent assessor (bc-d7d4b0d1). This row is the concrete, joint, worst-case form of Pearl's Assumption 1 at Pearl-C's parameters: no program exploits the rank-32 salted noise E′·Fᵀ, before or after the cast, to compute A′·B̃ᵀ and U cheaper than a generic product of the same codes. The evidence is in [the Assumption-1 note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/quantized-noise-assumption.md), on Pearl-C's own in-domain forming (census s5, the bit-exact sm_120 atom; `r20260930-074918-eab3`, `r20260930-075641-9b96`).

**The FP8 forming.** Families: gaussian, rank-1, constant, in-span-FA, and the noise-dominated spikes-first, zero-slices and sparse10, at k = 1,024–16,384.
- **Before the cast:** D = α·x + E′·Fᵀ has rank rank(X) + 32, so its product is cheap through its factors.
- **After the cast:** it matches no ticket word, and it is off by about 0.1–6% relative.
- **The split.** A′ = D + R turns the product into D's low-rank terms plus R_A·R_Bᵀ, and R is dense: the cast is exact on ≤ 0.4% of elements. R carries 17–18 significant bits with signal and 8–12 on noise-dominated inputs, so its product costs ≥ 2.00 per useful MAC in FP16 and ≥ 10 in NVFP4 (4.5–6.8 E2M1 limbs per 16-block). That is at least twice the honest product.
- **Reuse of F across units:** within a job only F's Gram is shared, and it gives only the approximate predictor.
- **Structure across salts:** codes repeat at chance rate (1.3–1.5%) and 32-code slices never repeat.
- **Caching by quantization class:** lookups cost 16–66 against the tensor core's 1.
- **U** is C̃ plus a rank-64 BF16 clean-up, so it adds no algebraic route of its own beyond C̃.

**The FP4 forming** (Pearl-C4, δ = 1/4, E2M1 codes under per-block scales) was not tested on its own forming, since there is no Pearl-C4 replay in code. What there is: an NVFP4-style model of the cast on noise alone keeps 91.8% of the energy in rank 32, and its cast is never exact. That is indirect evidence, and the coarser grid makes a narrow R more likely there than at FP8.

**Rating.**
- **FP8 lines (`pearl-c-sm120-v1` to `-v3`): B** (about 0.5 CPU-h on the bit-exact atom; measured prices).
- **FP4 line: C** (a model only). The falsifier is the same split on Pearl-C4's own forming: R's density and its E2M1 limbs per block.
- The row takes the lower of the two, since it states both.
