---
id: 20260929T0320Z-handoff-from-pous-daniel-rulings
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Daniel's rulings (PoUW under sampled proofs, Lean-first), and Round 11 acks

Re: your 0302Z note ("post his rulings here").

## Rulings

- **No recompute exception** (Daniel, 03:03Z). This answers Q10's first half.
  - Strip generation is split into its own proof units: activation strips (with their noise) and weight strips. Only a
    random sample of them is proved, like the tiles.
  - The design's recommended form uses "closure" draws. Tiles are drawn by work, and each drawn tile is proved with the
    two strips it reads, so a strip is checked in proportion to the compute it could spoil.
  - **For you as draw-law owner:** closure draws amount to a "prove what a drawn unit reads" rule. We will send it for
    review once our red team has checked §12's theorem.
- **Sizing: δ = 2⁻⁴⁰ for now, ε = 0.1%** (Daniel, 03:16Z).
  - The guarantee: with probability at least 1 − δ, an accepted window has at least 99.9% of its matmul compute
    verified.
  - The cost: about 149 T C-Flock rows per 70B window (27,712 tile draws, each with its two strips). That is about
    41 L40S-hours at 1 G AND/s, or about 600 h at the measured GEMM-template rate.
- **Lean-first protocols** (Daniel, about 03:05Z): implementations match vectors that the Lean spec generates. They do
  not call compiled Lean, and the Flock verifier is unchanged. The syncing norms are drafted, and whether a lag may sit
  on `main` is still with Daniel.
- **Still with Daniel:** the width rule (Q10's second half), where the recommendation is a named exception for tile,
  strip and tree units. Also still with him: work-proportional draw sizing, which would need a new law version in
  `Flock/Draw.lean`. We will post both rulings here.

## Acks

- **Round 11:** the coordinator's guard confirmation (lanes/pous 0305Z) is received. It launches under your 0302Z
  conditions, with C3 skipped because `capture_sample.json` is in the store.
- **`vy-pous-checks`:** guarded at $3 until 05:00Z (lanes/pous 0307Z). If the #312 and #315 recorded checks need more,
  we will ask you with a named budget.
