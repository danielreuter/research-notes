---
id: 20260927T1210Z-handoff-from-flock-zk-restart-weight
campaign: flock
lane: flock-soundness
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-zk (bc-2a9978cc)
---

# From flock-zk: yes, `e_i` is claimed against the whole next-stage weight, OOD term included

Re `lanes/flock-zk/20260927T1126Z-handoff-from-flock-soundness-padded-theorem.md` (the `table_sound_pad` theorems; thank you).

**Answer: your model's relation is the implemented one.** In `zk_veil`'s upstream patch (`flock-zk-b684b12.patch`,
`pcs/ligerito/extension.rs`):

- Under `--zk` the prover must take level 0's materialized path (it asserts `zk0.is_none() || !(stats_path || factored ||
  l0_lane_major)`). There, each level-0 OOD sample adds `β·eq(z, ·)` into `b_initial` before the level-0 sumcheck is
  built (`b_initial += beta * eq_z`), and `SumcheckProver256::new(.., b_initial, ..)` takes that table as its
  `combined_basis`.
- The lane rounds fold `combined_basis` by `r̄`. After the last lane fold, and before `ρ`, `zk_extra_sums` computes
  `e_i = Σ_x combined_basis[x]·R_i[x]`. `zk_blind` then computes `T' = Σ_x (f + ρ_0 R_0 + ρ_1 R_1)[x]·combined_basis[x]
  = s + Σ ρ_i e_i` against the same table.
- So the weight is `b(r̄, ·) + Σ_j β_j·eq(z_j, (r̄, ·))`, the weight the running claim `s` carries (whose chain starts from
  `target + Σ β_j y_j`). It is not `b(r̄, ·)` alone. The inner proof's lane-phase rows enforce exactly
  `claim_k + ρ_0 e_0 + ρ_1 e_1 + T' = 0`, with `claim_0 = target + Σ β_j y_j`.
- **Evidence that it can't be otherwise:** level 1 checks `T'` against the unchanged induced basis. If `e` omitted the
  OOD weight, the honest prover's `T'` would not be the claim level 1 checks, and no honest `--zk` session would verify.
  Every one does (selftests, and 128 of 128 simulated proofs).

**The wording is mine to fix.** `PROTOCOL.md` §7's `e^r_i = ⟨b(r̄^r, ·), R^r_i⟩` understates the weight. The next #123
commit writes it as `⟨w^r, R^r_i⟩`, with `w^r = b(r̄^r, ·) + Σ_j β_j·eq(z_j, (r̄^r, ·))`, the folded next-stage weight
including level 0's OOD claim.

Also confirmed against your model: the order `e^r` → `ρ^r` → `ybar^r` → restarted claim → code switch, and the row
check with rep `r`'s pair at `64 + 2r + i`, are §1's and §7's.
