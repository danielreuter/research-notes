---
id: 20260929T0506Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: work-proportional draw law drafted (#362); one sizing correction, one question

The new law is in draft [PR #362](https://github.com/danielreuter/verity/pull/362): law `work` in `Flock/Draw.lean`.

- **How it sizes draws:** each stratum draws `min(n_s, max(1, ⌈K·w_s·n_s/W⌉))`, using work from a table the verifier holds.
- **What's proved:** 13 new pins, with no `sorry`:
  - the work bound, (1−ε)^K at both audit layers;
  - the floor, so every non-empty stratum draws at least one unit;
  - the draw count, at most K plus the number of strata;
  - a closure seam: proving more units than were drawn never raises the chance of escape, so closure draws inherit the bounds.
- **What carries over:** the stratified law's theorems and #163's link bound, which depends on the law only through its inclusion probabilities.

**Correction: K is 27,713, not 27,712.** 0.999^27712 ≈ 2^-39.99997. Lean proves that 27,712 misses δ = 2⁻⁴⁰ at ε = 0.1% and that 27,713 meets it. Please update your sizing figures (the tile draws, and the C-Flock row count that follows from them).

**Question: is the floor per template or per unit?** The ruling says units doing no PoUW work (dequantization, the quantizer, attention) "get an integrity floor of at least one draw each". #362 reads that as at least one draw per template, meaning per stratum. A per-unit floor would prove every attention unit. Confirm the per-template reading against your design, or say it's per unit and bring that to Daniel.

Closure draws still wait for §12's red-team verdict. One_stage's U2 check doesn't handle `work` draws yet; that follows the Lean vectors once a vector generator exists, which is the one-stage pilot, still with Daniel.
