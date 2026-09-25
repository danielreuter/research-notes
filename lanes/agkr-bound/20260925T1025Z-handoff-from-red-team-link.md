# red-team-link: Link L CLEARED WITH CONDITIONS. Build it, but route (a) gets no 2^-128 Table 2 cell until C1-C4 hold (Flock's own 2^-128 profile is the long pole)

From red-team-link, 2026-09-25 10:25Z. Full report: `lanes/red-team-link/20260925T0957Z-report-red-team-link.md`.
Evidence: toy harness art:beeefd44 (16 of 16 spec and flawed negatives as expected; pod terminated 10:11Z, about $0.01).

**Verdicts.**
1. **Soundness of the mapping: HOLDS.** The integer-parity argument is correct; no attack on the protocol as written.
   - GAP F1: "Λ pinned in Σ" is not enough (the R1 pattern). The verifier must *derive* both maps, and both must be injective.
   - F2: SHA-256 needs a big-endian Λ; the doc's same-bit-order argument holds only for BLAKE3.
   - `vllm-v1` can't be linked until its mapping is final.
2. **Challenge derivation: ordering HOLDS; the field bound is a GAP.**
   - Two GF(2^128) points give 2^-246 only by Schwartz–Zippel. Folding both claims into Flock's GF(2^128) opening costs about
     2m/2^128, which is 2^-122 at m = 33, and loses the squaring (toy: batched miss 5.3 times independent).
   - Fix C1: one point over GF(2^256), or independent reductions.
   - Two BREAK-if-violated traps:
     - Flock's Fiat–Shamir seeded from root_B alone;
     - B-Ligero link points derived from HM96 coin r1. That reveals ρ before u is committed; a third coin slot is needed.
3. **Composition: GAP.** Today's whole-proof bound is about 2^-100, set by Flock.
   - Under campaign accounting (no PoW credit, ×2^60 for Fiat–Shamir), Flock needs GF(2^256) terms and interactive coins (C3).
   - B-Ligero's 2^-128.05 union has no slack for any Flock term.
4. **Checklist C1-C8 and 17 harness negatives:** §4 of the report.
   - Must-have negatives: alt_alt_bits (A-GKR's scaffold accepts it today), the unwired-chain forged block, and a VU remap.
   - Recommended for A-GKR (S1): send σ in the clear. That drops u and its second commitment; A-GKR can't host a second
     commitment anyway, since its §5.1 commits everything in W_1.

**For agkr-bound.** Build the prime side now: in-unit bits, the S1 linear constraints, the dense ℓ vector, and the negatives.
- Mind the BabyBear limit: at most 21,845 BF16 VUs per linked proof with u (40,959 with σ).
- Never range-check u as 2×16-bit limbs.
- Results are drill-down only (L) until C1 (link point field), C3 (Flock 2^-128, interactive) and C4 (chain glue: today's
  Flock runs are independent compressions, so every block is forgeable) hold.

**For b-ligero-standard-hash.** The route is additionally blocked for COMPLETE_ZK_BACKEND until Flock has ZK.
- It needs a two-tableau Ligero with a joint test.
- It needs a third HM96 coin slot.
- t must rise to make room for ε_B.

**Decision for the coordinator.** Whether to fund C3 (a Flock 2^-128 GF(2^256) interactive profile, plus a Flock red team)
before route (a) work continues beyond benchmarks. Without it, the link can't enter the filtered Table 2.
