import FlockSoundness.Game.Union

/-!
# Probabilities for a fixed prover strategy

`value` bounds the optimal prover. The table theorems (`table_sound_exec`) bound `prob` for every
strategy instead, and the two differ when some branch has no strategy at all (a `send` of an empty
type), so the audit theorems are stated for every strategy too. These are the strategy-level tools
they use:

* `prob_mono`, `prob_le_one`, `prob_or_le`: monotonicity and the union bound;
* `prob_and_const`: an event conjoined with a fact fixed by the strategy;
* `Strategy.ofMap`, `prob_map`: relabelling the output (`map`) keeps the game's strategies.
-/

namespace FlockSoundness.Game

open scoped ENNReal

variable {α β : Type}

theorem prob_mono {p q : α → Prop} (h : ∀ a, p a → q a) :
    ∀ (g : Game α) (s : Strategy g), prob p g s ≤ prob q g s
  | .ret a, _ => by
      classical
      simp only [prob]
      by_cases hp : p a
      · simp [hp, h a hp]
      · simp [hp]
  | .send _ k, s => prob_mono h (k s.1) s.2
  | @Game.coin _ C _ _ k, s => Finset.sum_le_sum fun c _ => mul_le_mul_right (prob_mono h (k c) (s c)) _

theorem prob_le_one (p : α → Prop) (g : Game α) (s : Strategy g) : prob p g s ≤ 1 :=
  (prob_le_value p g s).trans (value_le_one p g)

theorem prob_false : ∀ (g : Game α) (s : Strategy g), prob (fun _ => False) g s = 0
  | .ret _, _ => by simp [prob]
  | .send _ k, s => prob_false (k s.1) s.2
  | @Game.coin _ C _ _ k, s => by simp only [prob, prob_false (k _) (s _), mul_zero, Finset.sum_const_zero]

theorem prob_coin (p : α → Prop) (C : Type) [Fintype C] [Nonempty C] (k : C → Game α)
    (s : Strategy (Game.coin C k)) :
    prob p (.coin C k) s = avg fun c => prob p (k c) (s c) := rfl

theorem prob_send (p : α → Prop) (M : Type) (k : M → Game α) (s : Strategy (Game.send M k)) :
    prob p (.send M k) s = prob p (k s.1) s.2 := rfl

/-- The union bound, for a fixed strategy. -/
theorem prob_or_le (p q : α → Prop) :
    ∀ (g : Game α) (s : Strategy g), prob (fun a => p a ∨ q a) g s ≤ prob p g s + prob q g s
  | .ret a, _ => by
      classical
      simp only [prob]
      by_cases hp : p a <;> by_cases hq : q a <;> simp [hp, hq]
  | .send _ k, s => prob_or_le p q (k s.1) s.2
  | @Game.coin _ C _ _ k, s => by
      simp only [prob_coin]
      rw [← avg_add]
      exact avg_mono fun c => prob_or_le p q (k c) (s c)

/-- An event conjoined with a fact that does not depend on the run. -/
theorem prob_and_const (p : α → Prop) (Q : Prop) [Decidable Q] (g : Game α) (s : Strategy g) :
    prob (fun a => p a ∧ Q) g s = if Q then prob p g s else 0 := by
  by_cases hQ : Q
  · simp only [hQ, and_true, ite_true]
  · simp only [hQ, and_false, ite_false, prob_false]

theorem prCoin_false {C : Type} [Fintype C] : prCoin (fun _ : C => False) = 0 := by
  simp [prCoin, avg]

theorem avg_ite_eq_prCoin {C : Type} [Fintype C] (p : C → Prop) [DecidablePred p] :
    avg (fun c => if p c then (1 : ℝ≥0∞) else 0) = prCoin p := by
  unfold prCoin
  exact congrArg avg (funext fun c => by by_cases h : p c <;> simp [h])

/-- **Independent coordinates.** Averaging a product of per-coordinate functions over a product of
uniform coins gives the product of the averages. -/
theorem avg_pi_prod {ι : Type} [Fintype ι] [DecidableEq ι] {Ω : ι → Type} [∀ i, Fintype (Ω i)]
    [∀ i, Nonempty (Ω i)] (f : ∀ i, Ω i → ℝ≥0∞) :
    avg (fun ω : ∀ i, Ω i => ∏ i, f i (ω i)) = ∏ i, avg (f i) := by
  unfold avg
  have hinv : ((Fintype.card (∀ i, Ω i) : ℝ≥0∞))⁻¹ = ∏ i, ((Fintype.card (Ω i) : ℝ≥0∞))⁻¹ := by
    rw [Fintype.card_pi, Nat.cast_prod]
    exact ENNReal.prod_inv_distrib fun i _ j _ _ => Or.inl (by exact_mod_cast Fintype.card_ne_zero)
  simp only [hinv, ← Finset.prod_mul_distrib]
  exact (Fintype.prod_sum fun i j => ((Fintype.card (Ω i) : ℝ≥0∞))⁻¹ * f i j).symm

/-- The probability that independent coordinates all satisfy their events is the product. -/
theorem prCoin_pi_forall {ι : Type} [Fintype ι] [DecidableEq ι] {Ω : ι → Type} [∀ i, Fintype (Ω i)]
    [∀ i, Nonempty (Ω i)] (D : Finset ι) (P : ∀ i, Ω i → Prop) :
    prCoin (fun ω : ∀ i, Ω i => ∀ i ∈ D, P i (ω i)) = ∏ i ∈ D, prCoin (P i) := by
  classical
  have key : (fun ω : ∀ i, Ω i => if ∀ i ∈ D, P i (ω i) then (1 : ℝ≥0∞) else 0) =
      fun ω => ∏ i, (if i ∈ D then (if P i (ω i) then 1 else 0) else 1) := by
    funext ω
    by_cases hω : ∀ i ∈ D, P i (ω i)
    · rw [ite_eq_left_iff.2 fun h => absurd hω h]
      exact (Finset.prod_eq_one fun i _ => by by_cases hi : i ∈ D <;> simp [hi, hω i]).symm
    · rw [ite_eq_right_iff.2 fun h => absurd h hω]
      push Not at hω
      obtain ⟨i, hi, hP⟩ := hω
      exact (Finset.prod_eq_zero (Finset.mem_univ i) (by simp [hi, hP])).symm
  have h1 : ∏ i ∈ Finset.univ.filter (· ∉ D),
      avg (fun c : Ω i => if i ∈ D then (if P i c then (1 : ℝ≥0∞) else 0) else 1) = 1 :=
    Finset.prod_eq_one fun i hi => by
      rw [Finset.mem_filter] at hi
      simp only [hi.2, ite_false]
      exact avg_const 1
  calc prCoin (fun ω : ∀ i, Ω i => ∀ i ∈ D, P i (ω i))
      = avg (fun ω : ∀ i, Ω i => if ∀ i ∈ D, P i (ω i) then (1 : ℝ≥0∞) else 0) :=
        (avg_ite_eq_prCoin _).symm
    _ = ∏ i, avg (fun c : Ω i => if i ∈ D then (if P i c then (1 : ℝ≥0∞) else 0) else 1) := by
        rw [key]
        exact avg_pi_prod (fun i c => if i ∈ D then (if P i c then (1 : ℝ≥0∞) else 0) else 1)
    _ = ∏ i ∈ D, prCoin (P i) := by
        rw [← Finset.prod_filter_mul_prod_filter_not Finset.univ (· ∈ D), h1, mul_one,
          Finset.filter_mem_eq_inter, Finset.univ_inter]
        refine Finset.prod_congr rfl fun i hi => ?_
        simp only [hi, ite_true]
        exact avg_ite_eq_prCoin _

/-- A strategy for the relabelled game is a strategy for the game. -/
def Strategy.ofMap (f : α → β) : (g : Game α) → Strategy (g.map f) → Strategy g
  | .ret _, _ => PUnit.unit
  | .send _ k, s => ⟨s.1, Strategy.ofMap f (k s.1) s.2⟩
  | @Game.coin _ _ _ _ k, s => fun c => Strategy.ofMap f (k c) (s c)

/-- Relabelling the output relabels the event. -/
theorem prob_map (p : β → Prop) (f : α → β) :
    ∀ (g : Game α) (s : Strategy (g.map f)),
      prob p (g.map f) s = prob (fun a => p (f a)) g (Strategy.ofMap f g s)
  | .ret _, _ => rfl
  | .send _ k, s => prob_map p f (k s.1) s.2
  | @Game.coin _ C _ _ k, s => by
      show avg (fun c => prob p ((k c).map f) (s c)) = avg fun c => prob _ (k c) _
      exact congrArg avg (funext fun c => prob_map p f (k c) (s c))

theorem prob_true : ∀ (g : Game α) (s : Strategy g), prob (fun _ => True) g s = 1
  | .ret _, _ => by simp [prob]
  | .send _ k, s => prob_true (k s.1) s.2
  | @Game.coin _ _ _ _ k, s => by
      rw [prob_coin]
      exact (congrArg avg (funext fun c => prob_true (k c) (s c))).trans (avg_const 1)

/-- A strategy for `g.bind f`, restricted to `g`. -/
def Strategy.ofBind (f : α → Game β) : (g : Game α) → Strategy (g.bind f) → Strategy g
  | .ret _, _ => PUnit.unit
  | .send _ k, s => ⟨s.1, Strategy.ofBind f (k s.1) s.2⟩
  | @Game.coin _ _ _ _ k, s => fun c => Strategy.ofBind f (k c) (s c)

/-- **Additive composition, for a fixed strategy.** If from every doomed output of `g` the
continuation succeeds with probability at most `ε₂` whatever the prover does, the composition
succeeds with at most the probability of leaving the doomed set, plus `ε₂`. -/
theorem prob_bind_le (f : α → Game β) (p : β → Prop) (D : α → Prop) (ε₂ : ℝ≥0∞)
    (hf : ∀ a, D a → ∀ t, prob p (f a) t ≤ ε₂) :
    ∀ (g : Game α) (s : Strategy (g.bind f)),
      prob p (g.bind f) s ≤ prob (fun a => ¬ D a) g (Strategy.ofBind f g s) + ε₂
  | .ret a, s => by
      classical
      show prob p (f a) s ≤ prob (fun a => ¬ D a) (.ret a) PUnit.unit + ε₂
      simp only [prob]
      by_cases hD : D a
      · simp only [hD, not_true_eq_false, ite_false, zero_add]
        exact hf a hD s
      · simp only [hD, not_false_eq_true, ite_true]
        exact (prob_le_one _ _ _).trans le_self_add
  | .send _ k, s => prob_bind_le f p D ε₂ hf (k s.1) s.2
  | @Game.coin _ C _ _ k, s => by
      show avg (fun c => prob p ((k c).bind f) (s c)) ≤
        avg (fun c => prob (fun a => ¬ D a) (k c) (Strategy.ofBind f (k c) (s c))) + ε₂
      rw [← avg_const (C := C) ε₂, ← avg_add]
      exact avg_mono fun c => prob_bind_le f p D ε₂ hf (k c) (s c)

/-- An event that the continuation settles by the first output alone. -/
theorem prob_bind_of_const (f : α → Game β) (p : β → Prop) (P : α → Prop)
    (hf : ∀ a t, prob p (f a) t = prob P (.ret a) PUnit.unit) :
    ∀ (g : Game α) (s : Strategy (g.bind f)), prob p (g.bind f) s = prob P g (Strategy.ofBind f g s)
  | .ret a, s => hf a s
  | .send _ k, s => prob_bind_of_const f p P hf (k s.1) s.2
  | @Game.coin _ _ _ _ k, s => congrArg avg (funext fun c => prob_bind_of_const f p P hf (k c) (s c))

end FlockSoundness.Game
