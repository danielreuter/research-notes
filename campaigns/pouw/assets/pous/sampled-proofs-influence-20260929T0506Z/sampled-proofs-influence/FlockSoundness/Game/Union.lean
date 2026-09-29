import FlockSoundness.Game.Interleave

/-!
# Union bounds and loops

The tools every phase lemma uses to add up per-coin errors:

* `LawfulMonad Game`, so that the verifier's `List.mapM` loops unfold (`List.mapM_cons`);
* `value_bind_le_of_forall`: a continuation bounded from every state bounds the composition;
* `value_or_le`, `value_exists_finset_le`: the union bound for an optimal prover, over two events
  or over a finite family (the list of codewords near the committed table, for instance);
* `value_mapM_exists_le`: in a loop that runs one step per list element, the probability that some
  step's output is bad is at most the sum of the per-step bounds;
* `value_mapM_fst`: such a loop returns one output per element, in order.
-/

namespace FlockSoundness.Game

open scoped ENNReal

variable {α β γ : Type}

instance : LawfulMonad Game :=
  LawfulMonad.mk' Game
    (id_map := fun x => by
      show x.bind (fun a => Game.ret (id a)) = x
      exact bind_ret_right x)
    (pure_bind := fun _ _ => rfl)
    (bind_assoc := fun x f g => bind_assoc x f g)

/-- A continuation bounded from every state bounds the composition. -/
theorem value_bind_le_of_forall (g : Game α) (f : α → Game β) (p : β → Prop) (ε : ℝ≥0∞)
    (h : ∀ a, value p (f a) ≤ ε) : value p (g.bind f) ≤ ε := by
  have := value_bind_le g f p (fun _ => True) ε fun a _ => h a
  simpa [value_false] using this

/-- The union bound for an optimal prover, over two events. -/
theorem value_or_le (p q : α → Prop) : ∀ g : Game α,
    value (fun a => p a ∨ q a) g ≤ value p g + value q g
  | .ret a => by
      classical
      simp only [value_ret]
      by_cases hp : p a <;> by_cases hq : q a <;> simp [hp, hq]
  | .send _ k => by
      simp only [value_send]
      exact iSup_le fun m => (value_or_le p q (k m)).trans
        (add_le_add (le_iSup (fun m => value p (k m)) m) (le_iSup (fun m => value q (k m)) m))
  | @Game.coin _ C _ _ k => by
      simp only [value_coin]
      calc ∑ c : C, (Fintype.card C : ℝ≥0∞)⁻¹ * value (fun a => p a ∨ q a) (k c)
          ≤ avg (fun c => value p (k c) + value q (k c)) := avg_mono fun c => value_or_le p q (k c)
        _ = _ := by rw [avg_add]; rfl

/-- The union bound for an optimal prover, over a finite family of events. -/
theorem value_exists_finset_le {ι : Type} (s : Finset ι) (p : ι → α → Prop) (g : Game α) :
    value (fun a => ∃ i ∈ s, p i a) g ≤ ∑ i ∈ s, value (p i) g := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [value_false]
  | insert j s hj ih =>
      rw [Finset.sum_insert hj]
      calc value (fun a => ∃ i ∈ insert j s, p i a) g
          ≤ value (fun a => p j a ∨ ∃ i ∈ s, p i a) g :=
            value_mono (fun a ⟨i, hi, hpi⟩ => by
              rcases Finset.mem_insert.1 hi with rfl | hi
              · exact Or.inl hpi
              · exact Or.inr ⟨i, hi, hpi⟩) g
        _ ≤ value (p j) g + value (fun a => ∃ i ∈ s, p i a) g := value_or_le _ _ g
        _ ≤ value (p j) g + ∑ i ∈ s, value (p i) g := add_le_add le_rfl ih

/-- In a loop with one step per list element, the probability that some step's output is bad is
at most the list's length times the per-step bound. -/
theorem value_mapM_exists_le {ι : Type} (step : ι → Game β) (bad : β → Prop) (ε : ℝ≥0∞)
    (h : ∀ i, value bad (step i) ≤ ε) :
    ∀ l : List ι, value (fun out : List β => ∃ b ∈ out, bad b) (l.mapM step) ≤ l.length * ε
  | [] => by
      classical
      rw [List.mapM_nil]
      show value _ (Game.ret []) ≤ _
      rw [value_ret]
      simp
  | i :: l => by
      rw [List.mapM_cons]
      show value _ ((step i).bind fun b => (l.mapM step).bind fun bs => Game.ret (b :: bs)) ≤ _
      refine (value_bind_le _ _ _ (fun b => ¬ bad b) (l.length * ε) fun b hb => ?_).trans ?_
      · rw [value_bind_ret]
        refine (value_mono (fun bs h' => ?_) _).trans (value_mapM_exists_le step bad ε h l)
        obtain ⟨b', hb', hbad⟩ := h'
        rcases List.mem_cons.1 hb' with rfl | hb'
        · exact absurd hbad hb
        · exact ⟨b', hb', hbad⟩
      · simp only [not_not, List.length_cons, Nat.cast_add, Nat.cast_one]
        calc value bad (step i) + l.length * ε ≤ ε + l.length * ε := add_le_add (h i) le_rfl
          _ = (l.length + 1) * ε := by ring

/-- A loop whose step returns its input (under `proj`) returns the list itself, in order: the
event that it does not has value `0`. -/
theorem value_mapM_map_ne {ι : Type} (step : ι → Game β) (proj : β → ι)
    (h : ∀ i, value (fun b => proj b ≠ i) (step i) = 0) :
    ∀ l : List ι, value (fun out : List β => out.map proj ≠ l) (l.mapM step) = 0
  | [] => by
      classical
      rw [List.mapM_nil]
      show value _ (Game.ret []) = 0
      rw [value_ret]
      simp
  | i :: l => by
      rw [List.mapM_cons]
      show value _ ((step i).bind fun b => (l.mapM step).bind fun bs => Game.ret (b :: bs)) = 0
      refine le_antisymm ((value_bind_le _ _ _ (fun b => proj b = i) 0 fun b hb => ?_).trans ?_)
        (zero_le)
      · rw [value_bind_ret]
        refine (value_mono (fun bs h' => ?_) _).trans (value_mapM_map_ne step proj h l).le
        simp only [List.map_cons, hb, ne_eq, List.cons.injEq, true_and] at h'
        exact h'
      · simp only [add_zero]
        exact (h i).le

end FlockSoundness.Game
