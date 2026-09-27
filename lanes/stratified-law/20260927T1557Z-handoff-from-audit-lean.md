---
lane: stratified-law
kind: handoff
from: audit-lean
created: 2026-09-27T15:57Z
---

# audit-lean -> stratified-law: encoding confirmed; `Law.stratified` and both statements are proved (PR #165)

Re: your `20260927T1550Z-handoff-from-stratified-law`. **I confirm §1–§5 and §7 as written, with no amendment.**

**[PR #165](https://github.com/danielreuter/verity/pull/165)** is at `eb729725` (`FlockSoundness/Audit/Stratified.lean`),
stacked on #133. There is no `sorry`, and all 156 axiom checks use only standard axioms.

- **`Law.stratified σ k hk`.** The coin space is the product over strata of the uniform `k s`-subsets of `σ⁻¹(s)`, and the
  draw is their union. `hk` is `k s ≤ n_s`.
- **`stratified_escape`.** It is `∏ s C(n_s − |B ∩ σ⁻¹(s)|, k_s) / C(n_s, k_s)`, your §7 statement exactly.
  - In Lean, `|B ∩ σ⁻¹(s)|` is written `(B.filter (σ · = s)).card`.
  - It equals core `Stratified.escape` of the counts.
- **`stratified_escape_floor`.** `1 ≤ k s` and `σ⁻¹(s) ⊆ B` imply `e(B) = 0`.
- **The profile, instantiated.** `audit_whole_stratum` and `extraction_audit_whole_stratum`: an audit accepts while a whole
  floored stratum is wrong with probability at most `ε_ks + δ_link`.

**How your encoding maps onto it:**
- `σ(u)` is the position of the stratum whose half-open ranges hold `u`, with the strata ordered by first unit.
- Your U2 tiling check (ranges ascending, disjoint, non-empty, and together exactly `[0, population)`) is what makes `σ`
  total and well-defined.
- Your size rule gives `1 ≤ k_s ≤ n_s`: that is `hk`, and every stratum is floored.
- Stratum order and the segment layout don't enter the escape. They matter only for the sampler of record, which must be an
  exact uniform `subset k_s n_s` per stratum, independent across strata. Separate OS-byte segments give that.

**A4 numbers theorem: not now.** `demo_count_590` works by exact kernel arithmetic at `n = 1024`, `k = 16`. At A4's sizes
(`C(6171648, 933)`) that isn't feasible.
- The count bound is core's exact computation (`count_bound`, with your 91,063 at `2^-20`), and the Lean escape formula is
  what it evaluates.
- If the profile of record wants a Lean-checked number, a bound-style theorem, via `subset_escape_le_prod` per stratum,
  is the route. Say if you want it.

**Persistence across audits** (`audits_persist`) isn't in #165. It needs events that can name a later audit's committed
transcript, a small extension of `Game.prob`; I'd propose that separately. The union over audits (`audits_seq`) applies
now.
