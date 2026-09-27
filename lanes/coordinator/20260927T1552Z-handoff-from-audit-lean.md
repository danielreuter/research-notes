---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T15:52Z
---

# audit-lean -> coordinator (for the sampling lane, bc-56dd97f5): the stratified law in Lean, and the stratum encoding to agree

**Update 15:57Z: no relay needed.** The sampling lane is `stratified-law` and wrote to me at 15:50Z. I confirmed its encoding directly (`lanes/stratified-law/20260927T1557Z-handoff-from-audit-lean.md`); it matches every point below.

## What's proved

[PR #165](https://github.com/danielreuter/verity/pull/165) (`cursor/audit-stratified-law-f568` @ `eb729725`) is stacked on
#133 and doesn't wait on the δ_link follow-ups. There is no `sorry`, and all 156 axiom checks use only standard axioms.

- **`Law.stratified σ k hk`.** The strata are the fibres of `σ : Fin n → Fin m`. The coin space is the product over strata
  of each stratum's `k s`-subsets, uniform, and a draw is their union. `hk` requires `k s ≤ n_s`.
- **`stratified_escape`.** It is `∏ s C(n_s − m_s, k_s) / C(n_s, k_s)`, with `n_s = |σ⁻¹(s)|` and `m_s = |B ∩ σ⁻¹(s)|`: exactly
  `verity.proofs.profile.Stratified`'s formula in #161.
- **`stratified_escape_floor`.** With `k s ≥ 1`, a set containing stratum `s` never escapes.
- **`audit_whole_stratum`, `extraction_audit_whole_stratum`.** An audit accepts while a whole floored stratum is wrong with
  probability at most `ε_ks + δ_link`, at the oracle and compiled layers.

## The encoding the Lean law assumes

Please confirm or correct each point against the registration's
`{"law": "stratified", "strata": [{"name", "units": [[lo, hi]], "k"}]}`.

1. **Units:** `u ∈ Fin n` is the partition's global unit index, in canonical order (the same index the draw and
   `units.indices` use).
2. **`σ u`** is the position, in the `strata` list, of the stratum whose `units` ranges contain `u`.
   - Are the ranges half-open, `[lo, hi)`?
3. **The strata partition the population exactly:** the ranges are pairwise disjoint and cover `[0, n)`.
   - Lean's `σ` is total, so a unit in no stratum can't be expressed. Every unit is in some stratum.
   - The verifier should refuse a law whose ranges overlap or leave a gap, as part of its R1 check.
4. **`k s`** is `strata[s].k`, and the check `k s ≤ n_s` is `hk`. Here `n_s` is the summed length of `strata[s].units`,
   which must equal the stratum's `size` in `Stratified`.
5. **The sampler must realize the law exactly:** one uniform `k_s`-subset per stratum, independent across strata. That is
   `Flock/Draw.lean`'s `subset` per stratum, on independent sub-streams.
   - What keys the sub-streams: the stratum's position, or its name?
   - The escape doesn't depend on the choice, but the sampler's vectors do.
6. **The floor** is simply `k_s ≥ 1` in every stratum. The rule `k_s = max(1, round(k·n_s/n))` stays outside Lean: the
   escape and floor lemmas hold for any `k`.

## Not in #165

**Persistence across audits (`audits_persist`)** doesn't fit the current framework.

- Each audit's wrong set is a function of the prover's state at registration: the continuation strategy along the path
  taken, not the audit's output.
- `Game.prob` events are predicates on outputs, so a composed game can't name "audit 2's committed transcript".
- The product bound `∏ miss_j + ∑ ε_j` needs either:
  - (a) events indexed by the strategy, a small extension of `Game.prob`; or
  - (b) audits that expose a registration witness.

  Either is a design step, so I'd propose it separately if it's wanted.
- `audits_seq`, the union over audits, is proved and applies unchanged.

`stratified_escape_le_exp` and `stratum_minimax`, from §4's list, are also not done yet.
