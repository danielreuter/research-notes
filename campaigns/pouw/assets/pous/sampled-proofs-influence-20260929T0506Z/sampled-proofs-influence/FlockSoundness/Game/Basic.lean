import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Basic.ENNReal.BigOperators
import Mathlib.Basic.ENNReal.Inv
import Mathlib.Order.CompleteLattice.Basic

/-!
# Public-coin interactions with live coins

A `Game α` is the verifier's side of a public-coin interaction, written as a program:

* `send M k`: the prover sends a message `m : M` of its choice, and the interaction continues as
  `k m`;
* `coin C k`: the verifier draws `c : C` uniformly at random, independently of everything before,
  and the interaction continues as `k c`. This is a live coin: it is drawn after every earlier
  message is fixed (in verity, the coin server draws it from the operating system after recording
  the round's digest, PROTOCOL.md §7.1);
* `ret a`: the interaction ends with the verifier's output `a`.

Messages may be anything, including whole oracles (the committed tables of the interactive oracle
proof). A deterministic prover strategy (`Strategy g`) picks a message at every `send` node as a
function of the history, which the subtree it sits in encodes. `Strategy.prob` is the exact
probability, over the verifier's uniform coins, that the output satisfies a predicate, and
`value` is the same probability for an optimal, computationally unbounded prover. A randomized
prover is a mixture of deterministic ones, so every bound on `value` bounds it too
(`prob_le_value`).
-/

namespace FlockSoundness

open scoped ENNReal

/-- The verifier's side of a public-coin interaction with live coins. -/
inductive Game (α : Type) : Type 1 where
  | ret : α → Game α
  | send (M : Type) : (M → Game α) → Game α
  | coin (C : Type) [Fintype C] [Nonempty C] : (C → Game α) → Game α

namespace Game

variable {α β γ : Type}

/-- Sequencing: run `g`, then continue with `f` applied to its output. -/
def bind : Game α → (α → Game β) → Game β
  | .ret a, f => f a
  | .send M k, f => .send M fun m => bind (k m) f
  | @Game.coin _ C iF iN k, f => @Game.coin _ C iF iN fun c => bind (k c) f

instance : Monad Game where
  pure := .ret
  bind := bind

/-- The prover sends a message of type `M`. -/
def recv (M : Type) : Game M := .send M .ret

/-- The verifier draws a uniform coin from `C`. -/
def draw (C : Type) [Fintype C] [Nonempty C] : Game C := .coin C .ret

@[simp] theorem bind_ret (a : α) (f : α → Game β) : (Game.ret a).bind f = f a := rfl

@[simp] theorem bind_send (M : Type) (k : M → Game α) (f : α → Game β) :
    (Game.send M k).bind f = .send M fun m => (k m).bind f := rfl

@[simp] theorem bind_coin (C : Type) [Fintype C] [Nonempty C] (k : C → Game α)
    (f : α → Game β) : (Game.coin C k).bind f = .coin C fun c => (k c).bind f := rfl

@[simp] theorem pure_eq (a : α) : (pure a : Game α) = .ret a := rfl

@[simp] theorem bind_eq (g : Game α) (f : α → Game β) : g >>= f = g.bind f := rfl

theorem bind_assoc (g : Game α) (f : α → Game β) (h : β → Game γ) :
    (g.bind f).bind h = g.bind fun a => (f a).bind h := by
  induction g with
  | ret a => rfl
  | send M k ih => simp only [bind_send, ih]
  | coin C k ih => simp only [bind_coin, ih]

theorem bind_ret_right (g : Game α) : g.bind .ret = g := by
  induction g with
  | ret a => rfl
  | send M k ih => simp only [bind_send, ih]
  | coin C k ih => simp only [bind_coin, ih]

/-- Relabel the output. -/
def map (f : α → β) (g : Game α) : Game β := g.bind fun a => .ret (f a)

/-! ## Strategies and probabilities -/

/-- A deterministic prover strategy: a message at every `send` node, for every history (the
history is encoded by the position in the tree, so a strategy is simply a choice at each node,
and after a coin it may depend on that coin). -/
def Strategy : Game α → Type
  | .ret _ => PUnit
  | .send _ k => (m : _) × Strategy (k m)
  | @Game.coin _ C _ _ k => (c : C) → Strategy (k c)

open Classical in
/-- The exact probability, over the verifier's independent uniform coins, that the interaction
between the verifier `g` and the prover strategy `s` ends with an output satisfying `p`. -/
noncomputable def prob (p : α → Prop) : (g : Game α) → Strategy g → ℝ≥0∞
  | .ret a, _ => if p a then 1 else 0
  | .send _ k, s => prob p (k s.1) s.2
  | @Game.coin _ C iF _ k, s => ∑ c : C, (@Fintype.card C iF : ℝ≥0∞)⁻¹ * prob p (k c) (s c)

open Classical in
/-- The same probability for an optimal, computationally unbounded prover. -/
noncomputable def value (p : α → Prop) : Game α → ℝ≥0∞
  | .ret a => if p a then 1 else 0
  | .send _ k => ⨆ m, value p (k m)
  | @Game.coin _ C iF _ k => ∑ c : C, (@Fintype.card C iF : ℝ≥0∞)⁻¹ * value p (k c)

/-- No strategy beats the optimal prover. -/
theorem prob_le_value (p : α → Prop) : ∀ (g : Game α) (s : Strategy g), prob p g s ≤ value p g
  | .ret a, _ => le_rfl
  | .send _ k, s => (prob_le_value p (k s.1) s.2).trans (le_iSup (fun m => value p (k m)) s.1)
  | @Game.coin _ C _ _ k, s =>
      Finset.sum_le_sum fun c _ => mul_le_mul_right (prob_le_value p (k c) (s c)) _

@[simp] theorem value_ret (p : α → Prop) (a : α) [Decidable (p a)] :
    value p (.ret a) = if p a then 1 else 0 := by
  simp only [value]; congr 1

@[simp] theorem value_send (p : α → Prop) (M : Type) (k : M → Game α) :
    value p (.send M k) = ⨆ m, value p (k m) := by simp only [value]

@[simp] theorem value_coin (p : α → Prop) (C : Type) [Fintype C] [Nonempty C]
    (k : C → Game α) :
    value p (.coin C k) = ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value p (k c) := by
  simp only [value]

theorem value_le_one (p : α → Prop) : ∀ g : Game α, value p g ≤ 1
  | .ret a => by classical rw [value_ret]; split_ifs <;> simp
  | .send _ k => iSup_le fun m => value_le_one p (k m)
  | @Game.coin _ C _ _ k => by
      rw [value_coin]
      calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value p (k c)
          ≤ ∑ _c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * 1 :=
            Finset.sum_le_sum fun c _ => mul_le_mul_right (value_le_one p (k c)) _
        _ = 1 := by
            simp only [mul_one, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
            exact ENNReal.mul_inv_cancel (by exact_mod_cast Fintype.card_ne_zero)
              (ENNReal.natCast_ne_top _)

theorem value_mono {p q : α → Prop} (h : ∀ a, p a → q a) : ∀ g : Game α, value p g ≤ value q g
  | .ret a => by
      classical
      simp only [value_ret]
      by_cases hp : p a
      · simp [hp, h a hp]
      · simp [hp]
  | .send _ k => iSup_mono fun m => value_mono h (k m)
  | @Game.coin _ C _ _ k => Finset.sum_le_sum fun c _ => mul_le_mul_right (value_mono h (k c)) _

/-- The uniform average over a finite type. -/
noncomputable def avg {C : Type} [Fintype C] (f : C → ℝ≥0∞) : ℝ≥0∞ :=
  ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * f c

theorem avg_const {C : Type} [Fintype C] [Nonempty C] (x : ℝ≥0∞) : avg (fun _ : C => x) = x := by
  simp only [avg, Finset.sum_const, Finset.card_univ, nsmul_eq_mul, ← mul_assoc]
  rw [ENNReal.mul_inv_cancel (by exact_mod_cast Fintype.card_ne_zero) (ENNReal.natCast_ne_top _),
    one_mul]

theorem avg_mono {C : Type} [Fintype C] {f g : C → ℝ≥0∞} (h : ∀ c, f c ≤ g c) :
    avg f ≤ avg g :=
  Finset.sum_le_sum fun c _ => mul_le_mul_right (h c) _

theorem avg_add {C : Type} [Fintype C] (f g : C → ℝ≥0∞) :
    avg (fun c => f c + g c) = avg f + avg g := by
  simp only [avg, mul_add, Finset.sum_add_distrib]

theorem avg_mul_const {C : Type} [Fintype C] (f : C → ℝ≥0∞) (x : ℝ≥0∞) :
    avg (fun c => f c * x) = avg f * x := by
  simp only [avg, ← mul_assoc, Finset.sum_mul]

open Classical in
/-- The probability that a uniform coin satisfies `p`, as an average of indicators. -/
noncomputable def prCoin {C : Type} [Fintype C] (p : C → Prop) : ℝ≥0∞ :=
  avg fun c => if p c then 1 else 0

theorem prCoin_eq_card {C : Type} [Fintype C] (p : C → Prop) [DecidablePred p] :
    prCoin p = ((Finset.univ.filter p).card : ℝ≥0∞) / Fintype.card C := by
  classical
  unfold prCoin avg
  rw [ENNReal.div_eq_inv_mul, Finset.card_filter, Nat.cast_sum, Finset.mul_sum]
  refine Finset.sum_congr rfl fun c _ => ?_
  by_cases hc : p c <;> simp [hc]

theorem prCoin_mono {C : Type} [Fintype C] {p q : C → Prop} (h : ∀ c, p c → q c) :
    prCoin p ≤ prCoin q := by
  classical
  refine avg_mono fun c => ?_
  by_cases hp : p c
  · simp [hp, h c hp]
  · simp [hp]

/-- Union bound for a uniform coin. -/
theorem prCoin_exists_le {C ι : Type} [Fintype C] (s : Finset ι) (p : ι → C → Prop) :
    prCoin (fun c => ∃ i ∈ s, p i c) ≤ ∑ i ∈ s, prCoin (p i) := by
  classical
  unfold prCoin
  refine le_trans
    (avg_mono (g := fun c => ∑ i ∈ s, if p i c then (1 : ℝ≥0∞) else 0) fun c => ?_) ?_
  · split_ifs with h
    · obtain ⟨i, hi, hpi⟩ := h
      calc (1 : ℝ≥0∞) = if p i c then 1 else 0 := by simp [hpi]
        _ ≤ ∑ i ∈ s, if p i c then (1 : ℝ≥0∞) else 0 :=
            Finset.single_le_sum (f := fun i => if p i c then (1 : ℝ≥0∞) else 0)
              (fun _ _ => zero_le) hi
    · exact zero_le
  · simp only [avg, Finset.mul_sum]
    exact Finset.sum_comm.le

/-! ## Composition -/

/-- **Additive composition.** If the first phase `g` ends in a doomed state `D` except with
probability `ε₁` (for every prover), and from every doomed state the second phase succeeds with
probability at most `ε₂`, then the composition succeeds with probability at most `ε₁ + ε₂`. This
is the union bound over phases that round-by-round soundness arguments chain. -/
theorem value_bind_le (g : Game α) (f : α → Game β) (p : β → Prop) (D : α → Prop)
    (ε₂ : ℝ≥0∞) (hf : ∀ a, D a → value p (f a) ≤ ε₂) :
    value p (g.bind f) ≤ value (fun a => ¬ D a) g + ε₂ := by
  induction g with
  | ret a =>
      classical
      simp only [bind_ret, value_ret]
      by_cases hD : D a
      · simp only [hD, not_true_eq_false, ite_false, zero_add]; exact hf a hD
      · simp only [hD, not_false_eq_true, ite_true]
        exact (value_le_one p _).trans le_self_add
  | send M k ih =>
      simp only [bind_send, value_send]
      exact iSup_le fun m => (ih m).trans (add_le_add_left (le_iSup (fun m => value (fun a => ¬ D a) (k m)) m) _)
  | coin C k ih =>
      simp only [bind_coin, value_coin]
      calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value p ((k c).bind f)
          ≤ avg (fun c => value (fun a => ¬ D a) (k c) + ε₂) := avg_mono ih
        _ = avg (fun c => value (fun a => ¬ D a) (k c)) + ε₂ := by rw [avg_add, avg_const]
        _ = _ := rfl

/-- The value of drawing a coin and ending is the probability of the event. -/
theorem value_coin_ret (p : α → Prop) (C : Type) [Fintype C] [Nonempty C] (f : C → α) :
    value p (.coin C fun c => .ret (f c)) = prCoin fun c => p (f c) := by
  classical
  simp only [value_coin, value_ret, prCoin, avg]

/-- A round-by-round step: whatever the prover sends, the coin that follows leaves the doomed
state with probability at most `ε`. -/
theorem value_round_le (p : α → Prop) (M C : Type) [Fintype C] [Nonempty C] (f : M → C → α)
    (ε : ℝ≥0∞) (h : ∀ m, prCoin (fun c => p (f m c)) ≤ ε) :
    value p (.send M fun m => .coin C fun c => .ret (f m c)) ≤ ε := by
  simp only [value_send]
  exact iSup_le fun m => by rw [value_coin_ret]; exact h m

/-- Bounding a coin step by a bound on the probability of leaving the doomed set, plus the value
from inside the doomed set. -/
theorem value_coin_le (p : α → Prop) (C : Type) [Fintype C] [Nonempty C] (k : C → Game α)
    (bad : C → Prop) (ε ε' : ℝ≥0∞) (hbad : prCoin bad ≤ ε)
    (hgood : ∀ c, ¬ bad c → value p (k c) ≤ ε') :
    value p (.coin C k) ≤ ε + ε' := by
  classical
  rw [value_coin]
  have key : ∀ c, value p (k c) ≤ (if bad c then 1 else 0) + ε' := by
    intro c
    by_cases hc : bad c
    · simp only [hc, ite_true]; exact (value_le_one p _).trans le_self_add
    · simp only [hc, ite_false, zero_add]; exact hgood c hc
  calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value p (k c)
      ≤ avg (fun c => (if bad c then (1 : ℝ≥0∞) else 0) + ε') := avg_mono key
    _ = prCoin bad + ε' := by rw [avg_add, avg_const]; rfl
    _ ≤ ε + ε' := add_le_add_left hbad _

end Game

end FlockSoundness
