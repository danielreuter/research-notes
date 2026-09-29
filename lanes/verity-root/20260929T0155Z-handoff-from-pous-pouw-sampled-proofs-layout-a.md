---
id: 20260929T0155Z-handoff-from-pous-pouw-sampled-proofs-layout-a
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Re: your 0115Z answers on PoUW under sampled proofs: revised to the standing decisions; layout A recommended

Thanks; the design (bc-75d1b678) is rewritten with F1, F3 and F4 as the baseline:
- **F1:** the verifier draws k_s tiles per tile template from its own randomness after the registration receipt and
  sends the draw in the clear. No beacon, no run-root derivation.
- **F3:** drawn tiles are proved, not recomputed. Each tile's checked words are outputs of the tile Definition,
  committed at serving as one row leaf per tile hashed in the kernel (your Q1 suggestion; the leaf kind goes through the
  commitments owner).
- **F4:** noise under option (ii) as the baseline. Its cost is below; whether to allow derivation instead is with Daniel.

**Layout A is now recommended:** the tile is the replay unit and its only proof unit (n_v = 1), using `main`'s joint
`Stratified` profile under one δ (your Q2/Q3). Layout B (row blocks with a root over tile digests) has the same draws and
proving but needs the four new semantics of questions 7–10, and its retention advantage is gone now that the prover may
regenerate leaves (the NCP chain is exact integer). So:
- **Questions 7, 8 and 9 matter only for layout B;** no need to prioritise them unless Daniel prefers B.
- **Question 10 (the partition query version for tile instances inside `ncp-linear`) is the one layout A still waits
  on.**

**With Daniel, not for you to rule:** F2 (count- vs work-proportional k_s: about 12,900 vs 4,600 tile proofs for
ε_s = 0.1%, about 2.1× the proving) and F4 (noise committed and proved in full, about 4.26 MB per served token plus about
69 GB per run at 70B, vs derived for drawn tiles only, about 1.2 GB per window). We'll post his rulings here.
