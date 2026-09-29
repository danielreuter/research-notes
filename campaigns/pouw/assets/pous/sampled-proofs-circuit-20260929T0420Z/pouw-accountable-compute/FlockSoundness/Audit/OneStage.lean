import FlockSoundness.Game.Prob
import FlockSoundness.Audit.Law
import FlockSoundness.Audit.Circuit

/-!
# The one-stage audit and its integrity profile

The prover registers `R` (its roots). The verifier draws units from its own randomness, by the law
`L`, after registration. One batched session proves the drawn units against `R`. The audit's output
is the verdict and the draw (`audit`).

**The committed transcript** is an analysis device: a function of the prover's state at
registration, which is its registration `R` and its session strategy for every draw (`Cont`). In
the compiled analysis it is the plurality of what the extractor recovers behind each commit string.
Because it is fixed before the draw, the draw is independent of its wrong units. Nobody computes it.

**The per-unit hypotheses** (`Analysis`) charge a drawn wrong unit to one of two failures of its
table, both named:

* `KnowledgeSound ε_ks`: the table accepts while extraction of the unit fails;
* `LinkSound δ_link`: extraction succeeds, but what it recovers differs from the committed
  transcript on the unit's wires (consistency across units).

Both are bounds over the whole audit, for every prover and every rule that picks a drawn unit before
the session's first coin (the first wrong drawn unit, in the proof). That is the form the table
theorems take once averaged over the prover's state; neither needs to hold state by state.

**The theorem** (`audit_le`): for every event `E` on the committed transcript and the draw,
$$\Pr[\text{accept} \wedge E(X, S)] \le \Pr_S[E(X, S) \wedge S \cap \mathrm{wrong}(X) = \emptyset]
  + \varepsilon_{ks} + \delta_{link}.$$
Its corollaries are the integrity profile (`audit_profile`), the count curve
`δ(K) = miss K + ε_ks + δ_link` (`audit_count`), and the drawn units (`audit_drawn`).
-/

namespace FlockSoundness.Audit

open Game
open scoped ENNReal

variable {n : ℕ}

/-- **The one-stage audit.** The prover registers `R : Reg`; the verifier draws `S` by `L`; the
session on the drawn units runs against `R`. Output: the verdict and the draw. -/
def audit (L : Law n) (Reg : Type) (session : Finset (Fin n) → Reg → Game Bool) :
    Game (Bool × Finset (Fin n)) :=
  .send Reg fun R => .coin L.Ω fun ω => (session (L.draw ω) R).map fun ok => (ok, L.draw ω)

variable {L : Law n} {Reg : Type} {session : Finset (Fin n) → Reg → Game Bool}

/-- A prover's state after registering `R`: its session strategy for every draw. -/
abbrev Cont (L : Law n) (Reg : Type) (session : Finset (Fin n) → Reg → Game Bool) (R : Reg) :=
  ∀ ω : L.Ω, Strategy (session (L.draw ω) R)

/-- The registration of an audit strategy. -/
def reg (σ : Strategy (audit L Reg session)) : Reg := σ.1

/-- The prover's state after registration. -/
def cont (σ : Strategy (audit L Reg session)) : Cont L Reg session (reg σ) :=
  fun ω => Strategy.ofMap _ _ (σ.2 ω)

/-- What the analysis of an audit fixes.
* `Tr`, `wrong`: transcripts, and the units wrong in each;
* `committed`: the committed transcript, a function of the prover's state at registration;
* `ksFail S R τ u`: extraction of drawn unit `u` from the session state `τ` fails;
* `linkFail S R τ u X`: it succeeds, but disagrees with `X` on `u`'s wires;
* `cover`: a unit wrong in `X` fails one way or the other, from every state. -/
structure Analysis (L : Law n) (Reg : Type) (session : Finset (Fin n) → Reg → Game Bool) where
  Tr : Type
  wrong : Tr → Finset (Fin n)
  committed : (R : Reg) → Cont L Reg session R → Tr
  ksFail : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → Prop
  linkFail : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → Tr → Prop
  cover : ∀ S R (τ : Strategy (session S R)) u X, u ∈ wrong X → ksFail S R τ u ∨ linkFail S R τ u X

namespace Analysis

variable (A : Analysis L Reg session)

/-- The committed transcript of an audit strategy. -/
def committedOf (σ : Strategy (audit L Reg session)) : A.Tr := A.committed (reg σ) (cont σ)

/-- **Knowledge soundness, per unit** (named hypothesis `ε_ks`): for every prover and every rule
`tgt` that picks a drawn unit before the session's first coin, the probability that the session
accepts while extraction of the picked unit fails is at most `ε_ks`. -/
def KnowledgeSound (εks : ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (τ : Cont L Reg session R) (tgt : L.Ω → Option (Fin n)),
    avg (fun ω => prob (fun ok => ok = true ∧
      ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧ A.ksFail (L.draw ω) R (τ ω) u)
      (session (L.draw ω) R) (τ ω)) ≤ εks

/-- **The link term** (named hypothesis `δ_link`): for every prover and every rule `tgt` that
picks a drawn unit before the session's first coin, the probability that the session accepts while
the picked unit's extraction disagrees with the committed transcript is at most `δ_link`. -/
def LinkSound (δlink : ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (τ : Cont L Reg session R) (tgt : L.Ω → Option (Fin n)),
    avg (fun ω => prob (fun ok => ok = true ∧
      ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧ A.linkFail (L.draw ω) R (τ ω) u (A.committed R τ))
      (session (L.draw ω) R) (τ ω)) ≤ δlink

end Analysis

theorem avg_add₃ {C : Type} [Fintype C] (f g h : C → ℝ≥0∞) :
    avg (fun c => f c + g c + h c) = avg f + avg g + avg h := by
  rw [avg_add, avg_add]

/-- **The one-stage audit bound.** For every event `E` on the committed transcript and the draw,
the audit accepts with `E` with probability at most the probability that the draw satisfies `E`
and misses every wrong unit, plus `ε_ks + δ_link`. -/
theorem audit_le (A : Analysis L Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (E : A.Tr → Finset (Fin n) → Prop)
    (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ E (A.committedOf σ) o.2) (audit L Reg session) σ ≤
      prCoin (fun ω => E (A.committedOf σ) (L.draw ω) ∧
        Disjoint (L.draw ω) (A.wrong (A.committedOf σ))) + εks + δlink := by
  classical
  obtain ⟨R, τ'⟩ := σ
  set τ : Cont L Reg session R := cont ⟨R, τ'⟩
  set X := A.committed R τ with hX
  show prob _ (audit L Reg session) ⟨R, τ'⟩ ≤
    prCoin (fun ω => E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X)) + εks + δlink
  -- the target: some wrong drawn unit, fixed by the registration and the draw
  let tgt : L.Ω → Option (Fin n) := fun ω =>
    if h : ∃ u, u ∈ L.draw ω ∧ u ∈ A.wrong X then some (Classical.choose h) else none
  let ksE : L.Ω → Bool → Prop := fun ω ok => ok = true ∧
    ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧ A.ksFail (L.draw ω) R (τ ω) u
  let lkE : L.Ω → Bool → Prop := fun ω ok => ok = true ∧
    ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧ A.linkFail (L.draw ω) R (τ ω) u X
  have step : ∀ ω, prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω) ≤
      (if E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X) then 1 else 0) +
        prob (ksE ω) (session (L.draw ω) R) (τ ω) + prob (lkE ω) (session (L.draw ω) R) (τ ω) := by
    intro ω
    by_cases hd : Disjoint (L.draw ω) (A.wrong X)
    · rw [prob_and_const]
      by_cases hE : E X (L.draw ω)
      · simp only [hE, hd, and_self, ite_true]
        exact (prob_le_one _ _ _).trans (le_add_right le_self_add)
      · simp only [hE, ite_false, false_and, zero_le]
    · have h : ∃ u, u ∈ L.draw ω ∧ u ∈ A.wrong X := by
        obtain ⟨u, hu, hu'⟩ := Finset.not_disjoint_iff.1 hd
        exact ⟨u, hu, hu'⟩
      have ht : tgt ω = some (Classical.choose h) := by simp only [tgt, h, dite_true]
      obtain ⟨hmem, hw⟩ := Classical.choose_spec h
      have hc := A.cover (L.draw ω) R (τ ω) _ X hw
      calc prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω)
          ≤ prob (fun ok => ksE ω ok ∨ lkE ω ok) (session (L.draw ω) R) (τ ω) :=
            prob_mono (fun ok hok => by
              rcases hc with hk | hl
              · exact Or.inl ⟨hok.1, _, ht, hmem, hk⟩
              · exact Or.inr ⟨hok.1, _, ht, hmem, hl⟩) _ _
        _ ≤ prob (ksE ω) _ _ + prob (lkE ω) _ _ := prob_or_le _ _ _ _
        _ ≤ _ := by rw [add_assoc]; exact le_add_left le_rfl
  calc prob (fun o => o.1 = true ∧ E X o.2) (audit L Reg session) ⟨R, τ'⟩
      = avg fun ω => prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω) := by
        exact congrArg avg (funext fun ω => prob_map _ _ _ _)
    _ ≤ avg fun ω => (if E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X) then 1 else 0) +
        prob (ksE ω) (session (L.draw ω) R) (τ ω) + prob (lkE ω) (session (L.draw ω) R) (τ ω) :=
        avg_mono step
    _ = _ := avg_add₃ _ _ _
    _ ≤ _ := add_le_add (add_le_add (avg_ite_eq_prCoin _).le (hks R τ tgt)) (hlink R τ tgt)

/-- **The one-stage integrity profile.** For every family `𝓑` of wrong-unit sets,
`Pr[accept ∧ wrong(X) ∈ 𝓑] ≤ sup_{B ∈ 𝓑} escape B + ε_ks + δ_link`. -/
theorem audit_profile (A : Analysis L Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (𝓑 : Finset (Fin n) → Prop) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ 𝓑 (A.wrong (A.committedOf σ))) (audit L Reg session) σ ≤
      (⨆ (B : Finset (Fin n)) (_ : 𝓑 B), L.escape B) + εks + δlink := by
  refine (audit_le A hks hlink (fun X _ => 𝓑 (A.wrong X)) σ).trans ?_
  gcongr
  by_cases hB : 𝓑 (A.wrong (A.committedOf σ))
  · exact (prCoin_mono fun ω h => h.2).trans (le_iSup₂_of_le (f := fun B (_ : 𝓑 B) => L.escape B)
      _ hB le_rfl)
  · exact (prCoin_mono (q := fun _ => False) fun ω h => absurd h.1 hB).trans (prCoin_false.le.trans
      (zero_le))

/-- **The count curve**: `Pr[accept ∧ at least K wrong units] ≤ miss K + ε_ks + δ_link`. -/
theorem audit_count (A : Analysis L Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (K : ℕ) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ K ≤ (A.wrong (A.committedOf σ)).card) (audit L Reg session) σ ≤
      L.miss K + εks + δlink :=
  audit_profile A hks hlink (fun B => K ≤ B.card) σ

/-- **Drawn units are correct up to `ε_ks + δ_link`**, even for a consumer who looks after the
draw. -/
theorem audit_drawn (A : Analysis L Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ ¬ Disjoint (A.wrong (A.committedOf σ)) o.2) (audit L Reg session) σ ≤
      εks + δlink := by
  refine (audit_le A hks hlink (fun X S => ¬ Disjoint (A.wrong X) S) σ).trans ?_
  have : prCoin (fun ω => ¬ Disjoint (A.wrong (A.committedOf σ)) (L.draw ω) ∧
      Disjoint (L.draw ω) (A.wrong (A.committedOf σ))) = 0 := by
    exact le_antisymm ((prCoin_mono (q := fun _ => False) fun ω h => h.1 h.2.symm).trans
      prCoin_false.le) (zero_le)
  rw [this, zero_add]

/-- **Audits in sequence.** Run `g₁`, then `g₂` from its output. If the first audit fails (`E₁`)
with probability at most `b₁` for every prover, and the second (`E₂`) with at most `b₂` from every
history, then either fails with probability at most `b₁ + b₂`. Nesting `g₂` gives the union bound
over a lifetime of audits, with every term evaluated against a prover that took part in all of them. -/
theorem audits_seq {α β : Type} (g₁ : Game α) (g₂ : α → Game β) (E₁ : α → Prop) (E₂ : β → Prop)
    (b₁ b₂ : ℝ≥0∞) (h₁ : ∀ s, prob E₁ g₁ s ≤ b₁) (h₂ : ∀ x s, prob E₂ (g₂ x) s ≤ b₂)
    (s : Strategy (g₁.bind fun x => (g₂ x).map fun y => (x, y))) :
    prob (fun o => E₁ o.1 ∨ E₂ o.2) (g₁.bind fun x => (g₂ x).map fun y => (x, y)) s ≤ b₁ + b₂ := by
  classical
  refine (prob_or_le _ _ _ _).trans (add_le_add ?_ ?_)
  · rw [prob_bind_of_const _ _ E₁ fun x t => by
      rw [prob_map]
      have := prob_and_const (fun _ => True) (E₁ x) (g₂ x) (Strategy.ofMap _ _ t)
      simp only [true_and, prob_true] at this
      rw [this]
      simp [prob]]
    exact h₁ _
  · refine (prob_bind_le _ _ (fun _ => True) b₂ (fun x _ t => by rw [prob_map]; exact h₂ x _) g₁ s).trans ?_
    rw [(le_antisymm ((prob_mono (q := fun _ => False) (fun _ h => h trivial) _ _).trans
      (prob_false _ _).le) (zero_le)), zero_add]

/-! ## Over a partition: extraction, anchors and the consumer's cone -/

namespace Partition

variable {C : Circuit} (P : Partition C n)

/-- **The audit's analysis over a partition.** `X` is the committed transcript, a function of the
prover's state at registration. `ext S R τ u` is what the extractor recovers for the drawn unit
`u` from the session state `τ`: a transcript, of which only `u`'s committed inputs and outputs
(`io u`) are read, or nothing. Extraction fails when it recovers nothing or something that does
not satisfy `u`; the link fails when it satisfies `u` but differs from `X` on `u`'s wires. -/
noncomputable def analysis (X : (R : Reg) → Cont L Reg session R → (Fin C.N → Bool))
    (ext : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n →
      Option (Fin C.N → Bool)) :
    Analysis L Reg session where
  Tr := Fin C.N → Bool
  wrong := P.wrong
  committed := X
  ksFail S R τ u := ∀ Y, ext S R τ u = some Y → ¬ P.Correct Y u
  linkFail S R τ u X := ∃ Y, ext S R τ u = some Y ∧ P.Correct Y u ∧ ∃ g ∈ P.io u, Y g ≠ X g
  cover S R τ u X hu := by
    by_cases h : ∃ Y, ext S R τ u = some Y ∧ P.Correct Y u
    · obtain ⟨Y, hY, hc⟩ := h
      refine Or.inr ⟨Y, hY, hc, ?_⟩
      by_contra hno
      push Not at hno
      exact P.mem_wrong.1 hu (P.correct_congr (fun g hg => (hno g hg).symm) hc)
    · exact Or.inl fun Y hY hc => h ⟨Y, hY, hc⟩

/-- **The input unit** (named hypothesis `δ_in`): the session accepts while the committed inputs
differ from the anchors' values `a` with probability at most `δ_in`. -/
def AnchorsSound (X : (R : Reg) → Cont L Reg session R → (Fin C.N → Bool)) (a : Fin C.N → Bool)
    (δin : ℝ≥0∞) : Prop :=
  ∀ σ : Strategy (audit L Reg session),
    prob (fun o => o.1 = true ∧ ¬ C.InputsAgree (X (reg σ) (cont σ)) a) (audit L Reg session) σ ≤ δin

variable {X : (R : Reg) → Cont L Reg session R → (Fin C.N → Bool)}
  {ext : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → Option (Fin C.N → Bool)}
  {a : Fin C.N → Bool} {εks δlink δin : ℝ≥0∞}

/-- Split an accepted event on whether the committed inputs are the anchors'. -/
theorem prob_split_inputs (X : (R : Reg) → Cont L Reg session R → (Fin C.N → Bool))
    (a : Fin C.N → Bool) (σ : Strategy (audit L Reg session)) (F : Finset (Fin n) → Prop) :
    prob (fun o => o.1 = true ∧ F o.2) (audit L Reg session) σ ≤
      prob (fun o => o.1 = true ∧ ¬ C.InputsAgree (X (reg σ) (cont σ)) a) (audit L Reg session) σ +
      prob (fun o => o.1 = true ∧ (C.InputsAgree (X (reg σ) (cont σ)) a ∧ F o.2))
        (audit L Reg session) σ :=
  (prob_mono (fun o h => by
    by_cases hi : C.InputsAgree (X (reg σ) (cont σ)) a
    · exact Or.inr ⟨h.1, hi, h.2⟩
    · exact Or.inl ⟨h.1, hi⟩) _ _).trans (prob_or_le _ _ _ _)

/-- **A consumer's value, through its cone.** For wires `T` fixed before the draw, the audit
accepts while some committed wire of `T` differs from its evaluation with probability at most the
largest miss probability of a unit in `T`'s cone, plus `ε_ks + δ_link + δ_in`. -/
theorem audit_cone (hks : (P.analysis X ext).KnowledgeSound εks)
    (hlink : (P.analysis X ext).LinkSound δlink) (hin : AnchorsSound X a δin)
    (T : Finset (Fin C.N)) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ ∃ t ∈ T, t ∈ P.committed ∧ X (reg σ) (cont σ) t ≠ C.eval a t)
        (audit L Reg session) σ ≤
      (⨆ u ∈ P.cone T, (1 - L.incl u)) + εks + δlink + δin := by
  refine (prob_split_inputs X a σ (fun _ => ∃ t ∈ T, t ∈ P.committed ∧ X (reg σ) (cont σ) t ≠ C.eval a t)).trans ?_
  rw [add_comm]
  refine add_le_add ?_ (hin σ)
  refine (audit_le (P.analysis X ext) hks hlink
    (fun Y _ => C.InputsAgree Y a ∧ ∃ t ∈ T, t ∈ P.committed ∧ Y t ≠ C.eval a t) σ).trans ?_
  gcongr
  set Y := X (reg σ) (cont σ)
  by_cases hE : C.InputsAgree Y a ∧ ∃ t ∈ T, t ∈ P.committed ∧ Y t ≠ C.eval a t
  · obtain ⟨hia, t, ht, htc, hne⟩ := hE
    have hnd : ¬ Disjoint (P.wrong Y) (P.cone T) := fun hd => hne (P.compose_cone Y a T hia hd t ht htc)
    obtain ⟨u, huw, huc⟩ := Finset.not_disjoint_iff.1 hnd
    calc prCoin (fun ω => (C.InputsAgree Y a ∧ ∃ t ∈ T, t ∈ P.committed ∧ Y t ≠ C.eval a t) ∧
          Disjoint (L.draw ω) (P.wrong Y))
        ≤ L.escape (P.wrong Y) := prCoin_mono fun ω h => h.2
      _ ≤ 1 - L.incl u := L.escape_le_of_mem huw
      _ ≤ ⨆ u ∈ P.cone T, (1 - L.incl u) :=
          le_iSup₂_of_le (f := fun u (_ : u ∈ P.cone T) => 1 - L.incl u) u huc le_rfl
  · exact (prCoin_mono (q := fun _ => False) fun ω h => hE h.1).trans (prCoin_false.le.trans (zero_le))

/-- **`j` wrong units in a cone**: for wires `T` fixed before the draw, the audit accepts with at
least `j` wrong units in `T`'s cone with probability at most the largest escape of `j` of the
cone's units, plus `ε_ks + δ_link`. -/
theorem audit_cone_count (hks : (P.analysis X ext).KnowledgeSound εks)
    (hlink : (P.analysis X ext).LinkSound δlink) (T : Finset (Fin C.N)) (j : ℕ)
    (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ j ≤ (P.wrong (X (reg σ) (cont σ)) ∩ P.cone T).card)
        (audit L Reg session) σ ≤
      (⨆ (B : Finset (Fin n)) (_ : j ≤ (B ∩ P.cone T).card), L.escape B) + εks + δlink :=
  audit_profile (P.analysis X ext) hks hlink (fun B => j ≤ (B ∩ P.cone T).card) σ

/-- **A cone the draw covered**, for wires `T S` chosen even after seeing the draw `S`: the audit
accepts with `T S`'s cone inside the draw and some committed wire of `T S` wrong with probability at
most `ε_ks + δ_link + δ_in`. -/
theorem audit_covered (hks : (P.analysis X ext).KnowledgeSound εks)
    (hlink : (P.analysis X ext).LinkSound δlink) (hin : AnchorsSound X a δin)
    (T : Finset (Fin n) → Finset (Fin C.N)) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ P.cone (T o.2) ⊆ o.2 ∧
        ∃ t ∈ T o.2, t ∈ P.committed ∧ X (reg σ) (cont σ) t ≠ C.eval a t) (audit L Reg session) σ ≤
      εks + δlink + δin := by
  refine (prob_split_inputs X a σ (fun S => P.cone (T S) ⊆ S ∧
    ∃ t ∈ T S, t ∈ P.committed ∧ X (reg σ) (cont σ) t ≠ C.eval a t)).trans ?_
  rw [add_comm]
  refine add_le_add ?_ (hin σ)
  refine (audit_le (P.analysis X ext) hks hlink (fun Y S => C.InputsAgree Y a ∧ P.cone (T S) ⊆ S ∧
    ∃ t ∈ T S, t ∈ P.committed ∧ Y t ≠ C.eval a t) σ).trans ?_
  have : prCoin (fun ω => (C.InputsAgree (X (reg σ) (cont σ)) a ∧ P.cone (T (L.draw ω)) ⊆ L.draw ω ∧
      ∃ t ∈ T (L.draw ω), t ∈ P.committed ∧ X (reg σ) (cont σ) t ≠ C.eval a t) ∧
      Disjoint (L.draw ω) (P.wrong (X (reg σ) (cont σ)))) = 0 := by
    refine le_antisymm ((prCoin_mono (q := fun _ => False) fun ω h => ?_).trans prCoin_false.le)
      (zero_le)
    obtain ⟨⟨hia, hcov, t, ht, htc, hne⟩, hd⟩ := h
    exact hne (P.compose_cone _ a _ hia (Finset.disjoint_of_subset_right hcov hd.symm) t ht htc)
  calc _ ≤ 0 + εks + δlink := add_le_add (add_le_add this.le le_rfl) le_rfl
    _ = εks + δlink := by rw [zero_add]

/-! ### The oracle layer

The prover sends the committed transcript itself, as tables are sent at the oracle layer, so the
committed transcript is the registration and extraction returns it. Knowledge soundness is then
soundness of the session (`SessionSound`), the link term is zero, and the anchors term is the
session's error on inputs other than the anchors' (`InputsSound`). -/

/-- The oracle-layer analysis: the registration is the transcript. -/
noncomputable def oracle (session : Finset (Fin n) → (Fin C.N → Bool) → Game Bool) :
    Analysis L (Fin C.N → Bool) session :=
  P.analysis (fun R _ => R) (fun _ R _ _ => some R)

/-- **Any per-unit proof system, batched** (named hypothesis): if a drawn unit is wrong, the
session accepts with probability at most `ε`, for every prover strategy. -/
def SessionSound (session : Finset (Fin n) → (Fin C.N → Bool) → Game Bool) (ε : ℝ≥0∞) : Prop :=
  ∀ S X u, u ∈ S → u ∈ P.wrong X → ∀ τ : Strategy (session S X), prob (· = true) (session S X) τ ≤ ε

/-- **The input unit, at the oracle layer** (named hypothesis): the session accepts inputs other
than the anchors' `a` with probability at most `δ`, for every prover strategy. -/
def InputsSound (session : Finset (Fin n) → (Fin C.N → Bool) → Game Bool) (a : Fin C.N → Bool)
    (δ : ℝ≥0∞) : Prop :=
  ∀ S X, ¬ C.InputsAgree X a → ∀ τ : Strategy (session S X), prob (· = true) (session S X) τ ≤ δ

variable {session' : Finset (Fin n) → (Fin C.N → Bool) → Game Bool} {ε δ : ℝ≥0∞}

theorem oracle_knowledgeSound (hs : P.SessionSound session' ε) :
    (P.oracle (L := L) session').KnowledgeSound ε := by
  intro R τ tgt
  refine (avg_mono fun ω => ?_).trans (avg_const (C := L.Ω) ε).le
  rw [show (fun ok => ok = true ∧ ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧
      (P.oracle (L := L) session').ksFail (L.draw ω) R (τ ω) u) = fun ok => ok = true ∧
      ∃ u, tgt ω = some u ∧ u ∈ L.draw ω ∧ ¬ P.Correct R u from
    funext fun ok => by simp [oracle, analysis]]
  classical
  rw [prob_and_const]
  split_ifs with h
  · obtain ⟨u, -, hu, hw⟩ := h
    exact hs _ R u hu (P.mem_wrong.2 hw) (τ ω)
  · exact zero_le

theorem oracle_linkSound : (P.oracle (L := L) session').LinkSound 0 := by
  intro R τ tgt
  refine le_of_eq ?_
  refine (congrArg avg (funext fun ω => ?_)).trans (avg_const (C := L.Ω) 0)
  refine le_antisymm ((prob_mono (q := fun _ => False) (fun ok h => ?_) _ _).trans
    (prob_false _ _).le) (zero_le)
  obtain ⟨-, u, -, -, Y, hY, -, g, -, hne⟩ := h
  obtain rfl := Option.some.inj hY
  exact hne rfl

theorem oracle_anchorsSound (hr : InputsSound session' a δ) :
    AnchorsSound (L := L) (session := session') (fun R _ => R) a δ := by
  rintro ⟨R, τ'⟩
  show prob _ (audit L _ session') ⟨R, τ'⟩ ≤ δ
  refine (avg_mono fun ω => ?_).trans (avg_const (C := L.Ω) δ).le
  rw [prob_map]
  change prob (fun ok => ok = true ∧ ¬ C.InputsAgree R a) _ _ ≤ δ
  by_cases h : C.InputsAgree R a
  · exact (prob_mono (q := fun _ => False) (fun ok hok => hok.2 h) _ _).trans
      ((prob_false _ _).le.trans (zero_le))
  · exact (prob_mono (fun ok hok => hok.1) _ _).trans (hr _ R h _)

/-- **The design's one-stage count curve, at the oracle layer**: `δ(K) = miss K + ε`. -/
theorem oracle_count (hs : P.SessionSound session' ε) (K : ℕ)
    (σ : Strategy (audit L (Fin C.N → Bool) session')) :
    prob (fun o => o.1 = true ∧ K ≤ (P.wrong (reg σ)).card) (audit L _ session') σ ≤ L.miss K + ε := by
  have := audit_count (P.oracle session') (P.oracle_knowledgeSound hs) P.oracle_linkSound K σ
  rwa [add_zero] at this

/-- **The design's one-stage profile, at the oracle layer.** -/
theorem oracle_profile (hs : P.SessionSound session' ε) (𝓑 : Finset (Fin n) → Prop)
    (σ : Strategy (audit L (Fin C.N → Bool) session')) :
    prob (fun o => o.1 = true ∧ 𝓑 (P.wrong (reg σ))) (audit L _ session') σ ≤
      (⨆ (B : Finset (Fin n)) (_ : 𝓑 B), L.escape B) + ε := by
  have := audit_profile (P.oracle session') (P.oracle_knowledgeSound hs) P.oracle_linkSound 𝓑 σ
  rwa [add_zero] at this

/-- **The design's drawn-unit bound, at the oracle layer.** -/
theorem oracle_drawn (hs : P.SessionSound session' ε) (σ : Strategy (audit L (Fin C.N → Bool) session')) :
    prob (fun o => o.1 = true ∧ ¬ Disjoint (P.wrong (reg σ)) o.2) (audit L _ session') σ ≤ ε := by
  have := audit_drawn (P.oracle session') (P.oracle_knowledgeSound hs) P.oracle_linkSound σ
  rwa [add_zero] at this

/-- **The design's cone bound, at the oracle layer.** -/
theorem oracle_cone (hs : P.SessionSound session' ε) (hr : InputsSound session' a δ)
    (T : Finset (Fin C.N)) (σ : Strategy (audit L (Fin C.N → Bool) session')) :
    prob (fun o => o.1 = true ∧ ∃ t ∈ T, t ∈ P.committed ∧ reg σ t ≠ C.eval a t)
        (audit L _ session') σ ≤ (⨆ u ∈ P.cone T, (1 - L.incl u)) + ε + δ := by
  have := P.audit_cone (P.oracle_knowledgeSound hs) P.oracle_linkSound (oracle_anchorsSound hr) T σ
  rwa [add_zero] at this

end Partition

end FlockSoundness.Audit
