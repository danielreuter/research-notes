---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-zk · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
[PR #153](https://github.com/danielreuter/verity/pull/153) (branch `cursor/flock-padded-level0-8569`, on `main`)

# The table theorem with your padded level 0 is proved; one relation to confirm against M1's lane-phase rows

**What's proved** (no `sorry`, standard axioms only, 91 of 91):
- `table_sound_pad`: the oracle-layer table theorem with M1's level 0, for any padding `t` and any `e` extra lanes per
  rep.
- `table_sound_pad_m1`: at your `8d621454` values (`q₀ = 277, 242, 229` at `m = 25, 26, 27`, `t = 2q₀`, a pair per rep),
  at most **2^-196.5 per table**. The exact values are 2^-197.2, 2^-197.0 and 2^-196.8.
- The level-0 code is `RS[2^d, 2^cols + t]`. Each extra lane costs one MCA line and one coin on the restarted claim.

**The model is M1 in the clear** (`Model/LigeritoPad.lean`). It follows your §1 order for rep `r`:
1. the lane rounds, with no message after the last coin;
2. `e^r`, then `ρ^r_1 … ρ^r_e`, then `ybar^r`;
3. the restarted claim, then the code-switch message and cap 1;
4. the level-0 row check `fold(row_q[..64]) + Σ_i ρ_i·row_q[64 + e·r + i] + Enc(c·ybar ‖ ybar)(q)`, against the
   unchanged induced basis.

The verifier computes the restarted claim itself, `s + Σ_i ρ_i·e_i`. In M1, your inner proof has to enforce that
relation, since `s` and `e` are masked. The soundness of the masked verifier is then the soundness of this model plus the
inner proof's soundness for that relation.

**One relation to confirm.** In the model, `e_i` is claimed against the whole next-stage weight: `b(r̄, ·)` together with
level 0's out-of-domain claim's weight `β₀·eq(z₀, ·)`, folded by `r̄`. That is the weight the running claim `s` carries
after the lane rounds. Your §7 writes `e^r_i = ⟨b(r̄^r, ·), R^r_i⟩`.
- **If your `b(r̄, ·)` already includes the out-of-domain term,** the two agree.
- **If it does not,** the restart `T' = s + Σ ρ_i e_i` mixes weights, and the honest prover's `T'` isn't the claim level 1
  checks. The fix is either to include the term in `e`, or to state the restart with the out-of-domain part split off.

Which does `zk_veil` do?
