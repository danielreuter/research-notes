import FlockSoundness.Game.Basic

/-!
# Two interactions run concurrently

`interleave g₁ g₂` runs two interactions side by side, with the prover choosing at every step
which one advances next, adaptively. This is how the two reps of a Flock table run on the live
coin server: each rep is its own stream, the server draws a stream's coins when that stream's
round arrives, and the prover may interleave the streams in any order (PROTOCOL.md §5.3, S15).
The verifier accepts only if both interactions accept.

`value_interleave_le` is the repetition theorem: against an optimal, unbounded prover, the
probability that both interactions accept is at most the product of the two values, whatever the
schedule. With a sound single rep, two reps on independent live coins therefore square the error.
-/

namespace FlockSoundness

open scoped ENNReal

namespace Game

variable {α β : Type}

/-- The concurrent run once the first interaction's next step is fixed: `adv₁ g₂` advances the
first interaction by one node while the second is at `g₂`, and `fin₁ b` finishes the first
interaction alone once the second has ended with `b`. Recursion is on the second interaction. -/
def interleaveWith (adv₁ : Game β → Game (α × β)) (fin₁ : β → Game (α × β)) :
    Game β → Game (α × β)
  | .ret b => fin₁ b
  | .send M k => .send Bool fun first =>
      if first then adv₁ (.send M k) else .send M fun m => interleaveWith adv₁ fin₁ (k m)
  | @Game.coin _ C iF iN k => .send Bool fun first =>
      if first then adv₁ (@Game.coin _ C iF iN k)
      else @Game.coin _ C iF iN fun c => interleaveWith adv₁ fin₁ (k c)

/-- Run two interactions concurrently; at every step the prover chooses which one advances. -/
def interleave : Game α → Game β → Game (α × β)
  | .ret a => fun g₂ => g₂.map fun b => (a, b)
  | .send M k => interleaveWith (fun g₂ => .send M fun m => interleave (k m) g₂)
      (fun b => (Game.send M k).map fun a => (a, b))
  | @Game.coin _ C iF iN k => interleaveWith
      (fun g₂ => @Game.coin _ C iF iN fun c => interleave (k c) g₂)
      (fun b => (@Game.coin _ C iF iN k).map fun a => (a, b))

theorem value_map (p : β → Prop) (f : α → β) : ∀ g : Game α,
    value p (g.map f) = value (fun a => p (f a)) g
  | .ret a => by classical simp [map]
  | .send M k => by
      simp only [map, bind_send, value_send]
      exact iSup_congr fun m => value_map p f (k m)
  | @Game.coin _ C _ _ k => by
      simp only [map, bind_coin, value_coin]
      exact Finset.sum_congr rfl fun c _ => by rw [← value_map p f (k c)]; rfl

theorem value_bind_ret (p : β → Prop) (f : α → β) (g : Game α) :
    value p (g.bind fun a => .ret (f a)) = value (fun a => p (f a)) g :=
  value_map p f g

theorem value_congr {p q : α → Prop} (h : ∀ a, p a ↔ q a) (g : Game α) :
    value p g = value q g :=
  le_antisymm (value_mono (fun a => (h a).1) g) (value_mono (fun a => (h a).2) g)

theorem value_false : ∀ g : Game α, value (fun _ => False) g = 0
  | .ret a => by simp
  | .send M k => by
      rw [value_send]
      exact le_antisymm (iSup_le fun m => (value_false (k m)).le) zero_le
  | @Game.coin _ C _ _ k => by
      rw [value_coin]
      exact Finset.sum_eq_zero fun c _ => by rw [value_false (k c), mul_zero]

open Classical in
theorem value_const_and (P : Prop) (q : β → Prop) (g : Game β) :
    value (fun b => P ∧ q b) g = (if P then 1 else 0) * value q g := by
  by_cases hP : P
  · simp only [hP, true_and, ite_true, one_mul]
  · simp only [hP, false_and, ite_false, zero_mul]; exact value_false g

open Classical in
theorem value_and_const (p : α → Prop) (Q : Prop) (g : Game α) :
    value (fun a => p a ∧ Q) g = value p g * (if Q then 1 else 0) := by
  by_cases hQ : Q
  · simp only [hQ, and_true, ite_true, mul_one]
  · simp only [hQ, and_false, ite_false, mul_zero]; exact value_false g

theorem value_interleaveWith_le (p : α → Prop) (q : β → Prop)
    (adv₁ : Game β → Game (α × β)) (fin₁ : β → Game (α × β)) (v₁ : ℝ≥0∞)
    (hadv : ∀ g₂, value (fun x => p x.1 ∧ q x.2) (adv₁ g₂) ≤ v₁ * value q g₂)
    (hfin : ∀ b, value (fun x => p x.1 ∧ q x.2) (fin₁ b) ≤ v₁ * value q (.ret b)) :
    ∀ g₂ : Game β, value (fun x => p x.1 ∧ q x.2) (interleaveWith adv₁ fin₁ g₂) ≤
      v₁ * value q g₂
  | .ret b => hfin b
  | .send M k => by
      simp only [interleaveWith, value_send]
      refine iSup_le fun first => ?_
      cases first
      · simp only [Bool.false_eq_true, ite_false, value_send]
        rw [ENNReal.mul_iSup]
        exact iSup_mono fun m => value_interleaveWith_le p q adv₁ fin₁ v₁ hadv hfin (k m)
      · simp only [ite_true]
        exact hadv _
  | @Game.coin _ C _ _ k => by
      simp only [interleaveWith, value_send]
      refine iSup_le fun first => ?_
      cases first
      · simp only [Bool.false_eq_true, ite_false, value_coin]
        calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ *
              value (fun x => p x.1 ∧ q x.2) (interleaveWith adv₁ fin₁ (k c))
            ≤ ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * (v₁ * value q (k c)) :=
              Finset.sum_le_sum fun c _ => mul_le_mul_right
                (value_interleaveWith_le p q adv₁ fin₁ v₁ hadv hfin (k c)) _
          _ = v₁ * ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value q (k c) := by
              rw [Finset.mul_sum]
              exact Finset.sum_congr rfl fun c _ => by ring
      · simp only [ite_true]
        exact hadv _

/-- **Repetition on independent live coins.** Whatever schedule the prover chooses, the
probability that both concurrent interactions accept is at most the product of their values. -/
theorem value_interleave_le (p : α → Prop) (q : β → Prop) :
    ∀ (g₁ : Game α) (g₂ : Game β),
      value (fun x => p x.1 ∧ q x.2) (interleave g₁ g₂) ≤ value p g₁ * value q g₂
  | .ret a, g₂ => by
      classical
      simp only [interleave, value_map, value_ret]
      exact (value_const_and (p a) q g₂).le
  | .send M k, g₂ => by
      refine value_interleaveWith_le p q _ _ _ (fun g₂ => ?_) (fun b => ?_) g₂
      · simp only [value_send]
        rw [ENNReal.iSup_mul]
        exact iSup_mono fun m => value_interleave_le p q (k m) g₂
      · classical
        rw [value_map, value_ret]
        exact (value_and_const p (q b) (.send M k)).le
  | @Game.coin _ C _ _ k, g₂ => by
      refine value_interleaveWith_le p q _ _ _ (fun g₂ => ?_) (fun b => ?_) g₂
      · simp only [value_coin]
        calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ *
              value (fun x => p x.1 ∧ q x.2) (interleave (k c) g₂)
            ≤ ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * (value p (k c) * value q g₂) :=
              Finset.sum_le_sum fun c _ =>
                mul_le_mul_right (value_interleave_le p q (k c) g₂) _
          _ = (∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value p (k c)) * value q g₂ := by
              rw [Finset.sum_mul]
              exact Finset.sum_congr rfl fun c _ => by ring
      · classical
        rw [value_map, value_ret]
        exact (value_and_const p (q b) (@Game.coin _ C _ _ k)).le

end Game

end FlockSoundness
