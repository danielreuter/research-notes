import FlockSoundness.Audit.OneStage

/-!
# Two-stage audits, and their relation to one-stage

A coarse partition `Pc` is refined by a fine partition `Pf` (`Partition.Refines`). Coarse units are
the ones the prover replays, and fine units are the ones proved.

**Variant (a): every intermediate committed before a single draw.** This is the one-stage audit over
the fine partition, with the registration carrying both the coarse and the fine roots. A wrong
coarse unit contains a wrong fine unit, so the fine count curve bounds coarse counts too
(`two_stage_a_coarse`).

**Variant (b): nested sampling** (`twoStage`). Serving registers the coarse roots. The verifier
draws coarse units by `L₁`. The prover commits the interiors of the drawn units (`Int`). Then the
verifier draws, independently inside each drawn coarse unit `u`, fine units by `L₂ u`, and the
session proves them. The profile is over the coarse partition, the only one committed everywhere,
with the effective escape (`effEscape`)
$$e_{\text{eff}}(B) = \mathbb E_{S_1}\Big[\prod_{u \in B \cap S_1} \max_{v \subseteq u}
  \big(1 - \pi_{L_2 u}(v)\big)\Big].$$
Why: a drawn wrong coarse unit has a wrong fine unit under every interior the prover commits
(`Analysis₂.compose`, from `Refines.exists_wrong_fine`), and the second draw is fresh after the
interior and independent across coarse units.

* `twoStage_profile`: $\Pr[\text{accept} \wedge \text{wrong}_c(X) \in \mathcal B] \le \sup_{B \in
  \mathcal B} e_{\text{eff}}(B) + \varepsilon_{ks} + \delta_{link}$, with the two per-unit terms
  named at the fine level, as in one-stage;
* `effEscape_full`: **(b1) is one-stage over the coarse partition**: when the second stage proves
  every fine unit of each drawn coarse unit, `effEscape = L₁.escape`, with no dilution.
-/

namespace FlockSoundness.Audit

open Game
open scoped ENNReal

variable {nc nf : ℕ}

theorem prCoin_eq_one_of {C : Type} [Fintype C] [Nonempty C] {p : C → Prop} (h : ∀ c, p c) :
    prCoin p = 1 := by
  classical
  unfold prCoin
  simp only [h, ite_true]
  exact avg_const 1

/-- The fine draw: inside each drawn coarse unit `u`, the second-stage draw of `L₂ u`. -/
def fineDraw (L₁ : Law nc) (L₂ : Fin nc → Law nf) (ω₁ : L₁.Ω) (ω₂ : ∀ u, (L₂ u).Ω) :
    Finset (Fin nf) :=
  (L₁.draw ω₁).biUnion fun u => (L₂ u).draw (ω₂ u)

/-- **The two-stage audit, variant (b).** The prover registers `R`; the verifier draws coarse
units; the prover commits the drawn units' interiors `I`; the verifier draws fine units inside each
drawn coarse unit, fresh; the session proves them. Output: the verdict and both draws. -/
def twoStage (L₁ : Law nc) (L₂ : Fin nc → Law nf) (Reg : Type) (Int : Finset (Fin nc) → Type)
    (session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool) :
    Game (Bool × Finset (Fin nc) × Finset (Fin nf)) :=
  .send Reg fun R => .coin L₁.Ω fun ω₁ =>
  .send (Int (L₁.draw ω₁)) fun I => .coin (∀ u, (L₂ u).Ω) fun ω₂ =>
  (session (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) I).map
    fun ok => (ok, L₁.draw ω₁, fineDraw L₁ L₂ ω₁ ω₂)

variable {L₁ : Law nc} {L₂ : Fin nc → Law nf} {Reg : Type} {Int : Finset (Fin nc) → Type}
  {session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool}

/-- The prover's state after committing the interior `I`: its session strategy for every second
draw. -/
abbrev Cont₂ (L₁ : Law nc) (L₂ : Fin nc → Law nf) (Reg : Type) (Int : Finset (Fin nc) → Type)
    (session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool) (R : Reg)
    (ω₁ : L₁.Ω) (I : Int (L₁.draw ω₁)) :=
  ∀ ω₂ : ∀ u, (L₂ u).Ω, Strategy (session (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) I)

/-- The prover's state after registering `R`: for every coarse draw, its interior and what follows. -/
abbrev Cont₁ (L₁ : Law nc) (L₂ : Fin nc → Law nf) (Reg : Type) (Int : Finset (Fin nc) → Type)
    (session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool) (R : Reg) :=
  ∀ ω₁ : L₁.Ω, Σ I : Int (L₁.draw ω₁), Cont₂ L₁ L₂ Reg Int session R ω₁ I

/-- The registration of a two-stage strategy. -/
def reg₂ (σ : Strategy (twoStage L₁ L₂ Reg Int session)) : Reg := σ.1

/-- The prover's state after registration. -/
def cont₁ (σ : Strategy (twoStage L₁ L₂ Reg Int session)) :
    Cont₁ L₁ L₂ Reg Int session (reg₂ σ) :=
  fun ω₁ => ⟨(σ.2 ω₁).1, fun ω₂ => Strategy.ofMap _ _ ((σ.2 ω₁).2 ω₂)⟩

/-- What the analysis of a two-stage audit fixes.
* `parent`: the coarse unit each fine unit lies in;
* `committedC`: the coarse committed transcript, from the prover's state at registration;
* `committedF`: the fine committed transcript, from the coarse one and the prover's state after
  committing the interior;
* `compose`: a drawn wrong coarse unit has a wrong fine unit inside it, under every interior;
* `ksFail`, `linkFail`, `cover`: as in one-stage, at the fine level. -/
structure Analysis₂ (L₁ : Law nc) (L₂ : Fin nc → Law nf) (Reg : Type) (Int : Finset (Fin nc) → Type)
    (session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool) where
  parent : Fin nf → Fin nc
  TrC : Type
  wrongC : TrC → Finset (Fin nc)
  TrF : Type
  wrongF : TrF → Finset (Fin nf)
  committedC : (R : Reg) → Cont₁ L₁ L₂ Reg Int session R → TrC
  committedF : TrC → (R : Reg) → (ω₁ : L₁.Ω) → (I : Int (L₁.draw ω₁)) →
    Cont₂ L₁ L₂ Reg Int session R ω₁ I → TrF
  compose : ∀ X R ω₁ I τ u, u ∈ L₁.draw ω₁ → u ∈ wrongC X →
    ∃ v, parent v = u ∧ v ∈ wrongF (committedF X R ω₁ I τ)
  ksFail : (S : Finset (Fin nf)) → (R : Reg) → (S₁ : Finset (Fin nc)) → (I : Int S₁) →
    Strategy (session S R S₁ I) → Fin nf → Prop
  linkFail : (S : Finset (Fin nf)) → (R : Reg) → (S₁ : Finset (Fin nc)) → (I : Int S₁) →
    Strategy (session S R S₁ I) → Fin nf → TrF → Prop
  cover : ∀ S R S₁ I (τ : Strategy (session S R S₁ I)) v Z, v ∈ wrongF Z →
    ksFail S R S₁ I τ v ∨ linkFail S R S₁ I τ v Z

namespace Analysis₂

variable (A : Analysis₂ L₁ L₂ Reg Int session)

/-- The coarse committed transcript of a two-stage strategy. -/
def committedCOf (σ : Strategy (twoStage L₁ L₂ Reg Int session)) : A.TrC :=
  A.committedC (reg₂ σ) (cont₁ σ)

/-- **Knowledge soundness at the fine level** (named hypothesis `ε_ks`), for every prover and every
rule that picks a drawn fine unit before the session's first coin. -/
def KnowledgeSound (εks : ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (c : Cont₁ L₁ L₂ Reg Int session R) (tgt : L₁.Ω → (∀ u, (L₂ u).Ω) → Option (Fin nf)),
    avg (fun ω₁ => avg fun ω₂ => prob (fun ok => ok = true ∧ ∃ v, tgt ω₁ ω₂ = some v ∧
      v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧
      A.ksFail (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1 ((c ω₁).2 ω₂) v)
      (session (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1) ((c ω₁).2 ω₂)) ≤ εks

/-- **The link term at the fine level** (named hypothesis `δ_link`): extraction of the picked fine
unit disagrees with the fine committed transcript. -/
def LinkSound (δlink : ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (c : Cont₁ L₁ L₂ Reg Int session R) (tgt : L₁.Ω → (∀ u, (L₂ u).Ω) → Option (Fin nf)),
    avg (fun ω₁ => avg fun ω₂ => prob (fun ok => ok = true ∧ ∃ v, tgt ω₁ ω₂ = some v ∧
      v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧
      A.linkFail (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1 ((c ω₁).2 ω₂) v
        (A.committedF (A.committedC R c) R ω₁ (c ω₁).1 (c ω₁).2))
      (session (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1) ((c ω₁).2 ω₂)) ≤ δlink

end Analysis₂

/-- **The effective escape** of a coarse set `B` under nested sampling: each drawn unit of `B`
escapes the second stage with the largest miss probability of a fine unit inside it. -/
noncomputable def effEscape (L₁ : Law nc) (L₂ : Fin nc → Law nf) (parent : Fin nf → Fin nc)
    (B : Finset (Fin nc)) : ℝ≥0∞ :=
  avg fun ω₁ => ∏ u ∈ B ∩ L₁.draw ω₁, ⨆ (v : Fin nf) (_ : parent v = u), (1 - (L₂ u).incl v)

/-- **The two-stage profile, variant (b)**, over the coarse partition. -/
theorem twoStage_profile (A : Analysis₂ L₁ L₂ Reg Int session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) (𝓑 : Finset (Fin nc) → Prop)
    (σ : Strategy (twoStage L₁ L₂ Reg Int session)) :
    prob (fun o => o.1 = true ∧ 𝓑 (A.wrongC (A.committedCOf σ))) (twoStage L₁ L₂ Reg Int session) σ ≤
      (⨆ (B : Finset (Fin nc)) (_ : 𝓑 B), effEscape L₁ L₂ A.parent B) + εks + δlink := by
  classical
  obtain ⟨R, c'⟩ := σ
  set c : Cont₁ L₁ L₂ Reg Int session R := cont₁ ⟨R, c'⟩
  set X := A.committedC R c
  show prob _ (twoStage L₁ L₂ Reg Int session) ⟨R, c'⟩ ≤ _
  -- the fine committed transcript after each coarse draw
  let Z : L₁.Ω → A.TrF := fun ω₁ => A.committedF X R ω₁ (c ω₁).1 (c ω₁).2
  let D : L₁.Ω → Finset (Fin nc) := fun ω₁ => A.wrongC X ∩ L₁.draw ω₁
  -- the second draw misses every wrong fine unit inside every drawn wrong coarse unit
  let Pm : L₁.Ω → ∀ u, (L₂ u).Ω → Prop := fun ω₁ u ω =>
    ∀ v, A.parent v = u → v ∈ A.wrongF (Z ω₁) → v ∉ (L₂ u).draw ω
  let tgt : L₁.Ω → (∀ u, (L₂ u).Ω) → Option (Fin nf) := fun ω₁ ω₂ =>
    if h : ∃ v, v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧ v ∈ A.wrongF (Z ω₁) then some (Classical.choose h) else none
  let sess := fun ω₁ ω₂ => session (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1
  let ksE : L₁.Ω → (∀ u, (L₂ u).Ω) → Bool → Prop := fun ω₁ ω₂ ok => ok = true ∧ ∃ v,
    tgt ω₁ ω₂ = some v ∧ v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧
    A.ksFail (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1 ((c ω₁).2 ω₂) v
  let lkE : L₁.Ω → (∀ u, (L₂ u).Ω) → Bool → Prop := fun ω₁ ω₂ ok => ok = true ∧ ∃ v,
    tgt ω₁ ω₂ = some v ∧ v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧
    A.linkFail (fineDraw L₁ L₂ ω₁ ω₂) R (L₁.draw ω₁) (c ω₁).1 ((c ω₁).2 ω₂) v (Z ω₁)
  have step : ∀ ω₁ ω₂, prob (fun ok => ok = true ∧ 𝓑 (A.wrongC X)) (sess ω₁ ω₂) ((c ω₁).2 ω₂) ≤
      (if 𝓑 (A.wrongC X) ∧ ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u) then 1 else 0) +
        prob (ksE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂) + prob (lkE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂) := by
    intro ω₁ ω₂
    by_cases hm : ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u)
    · rw [prob_and_const]
      by_cases hB : 𝓑 (A.wrongC X)
      · have e : (if 𝓑 (A.wrongC X) ∧ ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u) then (1 : ℝ≥0∞) else 0) = 1 := by
          simp only [ite_eq_left_iff]; exact fun h => absurd ⟨hB, hm⟩ h
        rw [e]
        simp only [hB, ite_true]
        exact (prob_le_one _ _ _).trans (le_add_right le_self_add)
      · simp only [hB, ite_false, false_and, zero_le]
    · push Not at hm
      obtain ⟨u, hu, hnu⟩ := hm
      obtain ⟨v, hvu, hvw, hvd⟩ : ∃ v, A.parent v = u ∧ v ∈ A.wrongF (Z ω₁) ∧ v ∈ (L₂ u).draw (ω₂ u) := by
        simpa [Pm] using hnu
      have h : ∃ v, v ∈ fineDraw L₁ L₂ ω₁ ω₂ ∧ v ∈ A.wrongF (Z ω₁) :=
        ⟨v, Finset.mem_biUnion.2 ⟨u, (Finset.mem_inter.1 hu).2, hvd⟩, hvw⟩
      have ht : tgt ω₁ ω₂ = some (Classical.choose h) := by simp only [tgt, h, dite_true]
      obtain ⟨hmem, hw⟩ := Classical.choose_spec h
      have hc := A.cover _ R _ _ ((c ω₁).2 ω₂) _ (Z ω₁) hw
      calc prob (fun ok => ok = true ∧ 𝓑 (A.wrongC X)) (sess ω₁ ω₂) ((c ω₁).2 ω₂)
          ≤ prob (fun ok => ksE ω₁ ω₂ ok ∨ lkE ω₁ ω₂ ok) (sess ω₁ ω₂) ((c ω₁).2 ω₂) :=
            prob_mono (fun ok hok => by
              rcases hc with hk | hl
              · exact Or.inl ⟨hok.1, _, ht, hmem, hk⟩
              · exact Or.inr ⟨hok.1, _, ht, hmem, hl⟩) _ _
        _ ≤ prob (ksE ω₁ ω₂) _ _ + prob (lkE ω₁ ω₂) _ _ := prob_or_le _ _ _ _
        _ ≤ _ := by rw [add_assoc]; exact le_add_left le_rfl
  -- the second draw's miss probability, inside one coarse draw
  have hmiss : ∀ ω₁, prCoin (fun ω₂ : ∀ u, (L₂ u).Ω => 𝓑 (A.wrongC X) ∧ ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u)) ≤
      if 𝓑 (A.wrongC X) then
        ∏ u ∈ A.wrongC X ∩ L₁.draw ω₁, ⨆ (v : Fin nf) (_ : A.parent v = u), (1 - (L₂ u).incl v)
      else 0 := by
    intro ω₁
    by_cases hB : 𝓑 (A.wrongC X)
    · simp only [hB, true_and, ite_true]
      rw [prCoin_pi_forall]
      refine Finset.prod_le_prod fun u hu => ?_
      obtain ⟨hw, hd⟩ := Finset.mem_inter.1 hu
      obtain ⟨v, hvu, hvw⟩ := A.compose X R ω₁ (c ω₁).1 (c ω₁).2 u hd hw
      calc prCoin (Pm ω₁ u) ≤ prCoin fun ω => v ∉ (L₂ u).draw ω :=
            prCoin_mono fun ω h => h v hvu hvw
        _ = 1 - (L₂ u).incl v := Law.prCoin_not _
        _ ≤ _ := le_iSup₂_of_le (f := fun v (_ : A.parent v = u) => 1 - (L₂ u).incl v) v hvu le_rfl
    · simp only [hB, false_and, ite_false]
      exact prCoin_false.le
  calc prob (fun o => o.1 = true ∧ 𝓑 (A.wrongC X)) (twoStage L₁ L₂ Reg Int session) ⟨R, c'⟩
      = avg fun ω₁ => avg fun ω₂ =>
          prob (fun ok => ok = true ∧ 𝓑 (A.wrongC X)) (sess ω₁ ω₂) ((c ω₁).2 ω₂) :=
        congrArg avg (funext fun ω₁ => congrArg avg (funext fun ω₂ => prob_map _ _ _ _))
    _ ≤ avg fun ω₁ => avg fun ω₂ =>
          (if 𝓑 (A.wrongC X) ∧ ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u) then 1 else 0) +
          prob (ksE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂) + prob (lkE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂) :=
        avg_mono fun ω₁ => avg_mono fun ω₂ => step ω₁ ω₂
    _ = (avg fun ω₁ => prCoin fun ω₂ : ∀ u, (L₂ u).Ω => 𝓑 (A.wrongC X) ∧ ∀ u ∈ D ω₁, Pm ω₁ u (ω₂ u)) +
          (avg fun ω₁ => avg fun ω₂ => prob (ksE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂)) +
          (avg fun ω₁ => avg fun ω₂ => prob (lkE ω₁ ω₂) (sess ω₁ ω₂) ((c ω₁).2 ω₂)) := by
        rw [← avg_add₃]
        refine congrArg avg (funext fun ω₁ => ?_)
        rw [avg_add₃, avg_ite_eq_prCoin]
    _ ≤ _ := by
        refine add_le_add (add_le_add ?_ (hks R c tgt)) (hlink R c tgt)
        refine (avg_mono hmiss).trans ?_
        by_cases hB : 𝓑 (A.wrongC X)
        · simp only [hB, ite_true]
          exact le_iSup₂_of_le (f := fun B (_ : 𝓑 B) => effEscape L₁ L₂ A.parent B) _ hB le_rfl
        · simp only [hB, ite_false]
          exact (avg_const 0).le.trans (zero_le)

/-- **The two-stage count curve**, variant (b). -/
theorem twoStage_count (A : Analysis₂ L₁ L₂ Reg Int session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) (K : ℕ)
    (σ : Strategy (twoStage L₁ L₂ Reg Int session)) :
    prob (fun o => o.1 = true ∧ K ≤ (A.wrongC (A.committedCOf σ)).card) (twoStage L₁ L₂ Reg Int session) σ ≤
      (⨆ (B : Finset (Fin nc)) (_ : K ≤ B.card), effEscape L₁ L₂ A.parent B) + εks + δlink :=
  twoStage_profile A hks hlink (fun B => K ≤ B.card) σ

/-- **(b1) is one-stage over the coarse partition.** When the second stage draws every fine unit of
each coarse unit, the effective escape is the first stage's escape. -/
theorem effEscape_full (parent : Fin nf → Fin nc) (hfull : ∀ u ω v, parent v = u → v ∈ (L₂ u).draw ω)
    (B : Finset (Fin nc)) : effEscape L₁ L₂ parent B = L₁.escape B := by
  classical
  unfold effEscape Law.escape
  rw [← avg_ite_eq_prCoin]
  refine congrArg avg (funext fun ω₁ => ?_)
  have hzero : ∀ u, (⨆ (v : Fin nf) (_ : parent v = u), (1 - (L₂ u).incl v)) = 0 := fun u =>
    le_antisymm (iSup₂_le fun v hv => by
      rw [Law.incl, prCoin_eq_one_of fun ω => hfull u ω v hv, tsub_self]) (zero_le)
  simp only [hzero]
  by_cases hd : Disjoint (L₁.draw ω₁) B
  · simp only [hd, ite_true]
    rw [Finset.inter_comm, Finset.disjoint_iff_inter_eq_empty.1 hd, Finset.prod_empty]
  · simp only [hd, ite_false]
    obtain ⟨u, hu⟩ := Finset.not_disjoint_iff_nonempty_inter.1 hd
    exact Finset.prod_eq_zero (Finset.mem_inter.2 ⟨(Finset.mem_inter.1 hu).2, (Finset.mem_inter.1 hu).1⟩) rfl

/-- **(b1)'s profile is one-stage's over the coarse partition.** -/
theorem twoStage_full_profile (A : Analysis₂ L₁ L₂ Reg Int session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (hfull : ∀ u ω v, A.parent v = u → v ∈ (L₂ u).draw ω) (𝓑 : Finset (Fin nc) → Prop)
    (σ : Strategy (twoStage L₁ L₂ Reg Int session)) :
    prob (fun o => o.1 = true ∧ 𝓑 (A.wrongC (A.committedCOf σ))) (twoStage L₁ L₂ Reg Int session) σ ≤
      (⨆ (B : Finset (Fin nc)) (_ : 𝓑 B), L₁.escape B) + εks + δlink := by
  have := twoStage_profile A hks hlink 𝓑 σ
  simp only [effEscape_full A.parent hfull] at this
  exact this

/-- **(b2) with a Bernoulli first stage, in general**: each coarse unit of `B` contributes its
Bernoulli factor at its largest second-stage miss probability, so the nested law is a one-stage
Bernoulli law thinned unit by unit. -/
theorem effEscape_bernoulli_prod {num den : ℕ} [NeZero den] (hnum : num ≤ den)
    (L₂ : Fin nc → Law nf) (parent : Fin nf → Fin nc) (B : Finset (Fin nc)) :
    effEscape (Law.bernoulli nc num den) L₂ parent B =
      ∏ u ∈ B, Law.bernFactor num den (⨆ (v : Fin nf) (_ : parent v = u), (1 - (L₂ u).incl v)) :=
  Law.bernoulli_avg_prod hnum _ B

/-! ## Over partitions -/

namespace Partition

variable {C : Circuit} {Pf : Partition C nf} {Pc : Partition C nc}

/-- **Variant (a)**: the one-stage audit over the fine partition bounds coarse counts too. -/
theorem two_stage_a_coarse (r : Refines Pf Pc) {L : Law nf} {Reg : Type}
    {session : Finset (Fin nf) → Reg → Game Bool}
    {X : (R : Reg) → Cont L Reg session R → (Fin C.N → Bool)}
    {ext : (S : Finset (Fin nf)) → (R : Reg) → Strategy (session S R) → Fin nf →
      Option (Fin C.N → Bool)} {εks δlink : ℝ≥0∞}
    (hks : (Pf.analysis X ext).KnowledgeSound εks) (hlink : (Pf.analysis X ext).LinkSound δlink)
    (K : ℕ) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ K ≤ (Pc.wrong (X (reg σ) (cont σ))).card) (audit L Reg session) σ ≤
      L.miss K + εks + δlink :=
  (prob_mono (fun _ h => ⟨h.1, h.2.trans (r.card_wrong_le fun _ _ => rfl)⟩) _ _).trans
    (audit_count (Pf.analysis X ext) hks hlink K σ)

/-- The fine transcript: the coarse committed wires from `X`, every other wire from `Y`. -/
noncomputable def extend (X Y : Fin C.N → Bool) : Fin C.N → Bool := by
  classical
  exact fun g => if g ∈ Pc.committed then X g else Y g

theorem extend_committed (X Y : Fin C.N → Bool) :
    ∀ g ∈ Pc.committed, extend (Pc := Pc) X Y g = X g := by
  classical
  intro g hg
  simp [extend, hg]

/-- **Variant (b) over a refinement.** The coarse committed transcript `X` comes from the prover's
state at registration; the interior's committed values `Yint` from its state after committing the
interior; the fine committed transcript is `X` on the coarse committed wires and `Yint` elsewhere.
Fine units are read through the extractor `ext`, as in one-stage. -/
noncomputable def Refines.analysis₂ (r : Refines Pf Pc)
    {L₁ : Law nc} {L₂ : Fin nc → Law nf} {Reg : Type} {Int : Finset (Fin nc) → Type}
    {session : Finset (Fin nf) → Reg → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool}
    (X : (R : Reg) → Cont₁ L₁ L₂ Reg Int session R → (Fin C.N → Bool))
    (Yint : (R : Reg) → (ω₁ : L₁.Ω) → (I : Int (L₁.draw ω₁)) → Cont₂ L₁ L₂ Reg Int session R ω₁ I →
      (Fin C.N → Bool))
    (ext : (S : Finset (Fin nf)) → (R : Reg) → (S₁ : Finset (Fin nc)) → (I : Int S₁) →
      Strategy (session S R S₁ I) → Fin nf → Option (Fin C.N → Bool)) :
    Analysis₂ L₁ L₂ Reg Int session where
  parent := r.parent
  TrC := Fin C.N → Bool
  wrongC := Pc.wrong
  TrF := Fin C.N → Bool
  wrongF := Pf.wrong
  committedC := X
  committedF X' R ω₁ I τ := extend (Pc := Pc) X' (Yint R ω₁ I τ)
  compose X' R ω₁ I τ u _ hu := r.exists_wrong_fine (extend_committed X' _) hu
  ksFail S R S₁ I τ v := ∀ Y, ext S R S₁ I τ v = some Y → ¬ Pf.Correct Y v
  linkFail S R S₁ I τ v Z := ∃ Y, ext S R S₁ I τ v = some Y ∧ Pf.Correct Y v ∧ ∃ g ∈ Pf.io v, Y g ≠ Z g
  cover S R S₁ I τ v Z hv := by
    by_cases h : ∃ Y, ext S R S₁ I τ v = some Y ∧ Pf.Correct Y v
    · obtain ⟨Y, hY, hc⟩ := h
      refine Or.inr ⟨Y, hY, hc, ?_⟩
      by_contra hno
      push Not at hno
      exact Pf.mem_wrong.1 hv (Pf.correct_congr (fun g hg => (hno g hg).symm) hc)
    · exact Or.inl fun Y hY hc => h ⟨Y, hY, hc⟩

/-! ### The oracle layer

The prover sends the coarse transcript, then the interior, as tables are sent at the oracle layer.
The fine transcript is `extend R I`, extraction returns it, and the link term is zero. -/

/-- **Any per-unit proof system at the fine level** (named hypothesis): if a drawn fine unit is
wrong in the fine transcript, the session accepts with probability at most `ε`. -/
def SessionSound₂ (Pf : Partition C nf) (Pc : Partition C nc) {Int : Finset (Fin nc) → Type}
    (ext : ∀ S₁, Int S₁ → (Fin C.N → Bool))
    (session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool)
    (ε : ℝ≥0∞) : Prop :=
  ∀ S R S₁ I v, v ∈ S → v ∈ Pf.wrong (extend (Pc := Pc) R (ext S₁ I)) →
    ∀ τ : Strategy (session S R S₁ I), prob (· = true) (session S R S₁ I) τ ≤ ε

/-- The oracle-layer two-stage analysis: the registration is the coarse transcript, and the
interior `I` fills in the fine one through `ext`. -/
noncomputable def Refines.oracle₂ (r : Refines Pf Pc) {L₁ : Law nc} {L₂ : Fin nc → Law nf}
    {Int : Finset (Fin nc) → Type} (ext : ∀ S₁, Int S₁ → (Fin C.N → Bool))
    (session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool) :
    Analysis₂ L₁ L₂ (Fin C.N → Bool) Int session :=
  r.analysis₂ (fun R _ => R) (fun _ ω₁ I _ => ext (L₁.draw ω₁) I)
    (fun _ R S₁ I _ _ => some (extend (Pc := Pc) R (ext S₁ I)))

theorem Refines.oracle₂_knowledgeSound (r : Refines Pf Pc) {L₁ : Law nc} {L₂ : Fin nc → Law nf}
    {Int : Finset (Fin nc) → Type} {ext : ∀ S₁, Int S₁ → (Fin C.N → Bool)}
    {session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool}
    {ε : ℝ≥0∞} (hs : SessionSound₂ Pf Pc ext session ε) :
    (r.oracle₂ (L₁ := L₁) (L₂ := L₂) ext session).KnowledgeSound ε := by
  classical
  intro R c tgt
  refine (avg_mono fun ω₁ => (avg_mono fun ω₂ => ?_).trans (avg_const _).le).trans (avg_const _).le
  rw [prob_and_const]
  split_ifs with h
  · obtain ⟨v, -, hv, hw⟩ := h
    refine hs _ R _ _ v hv (Pf.mem_wrong.2 ?_) _
    exact hw _ rfl
  · exact zero_le

theorem Refines.oracle₂_linkSound (r : Refines Pf Pc) {L₁ : Law nc} {L₂ : Fin nc → Law nf}
    {Int : Finset (Fin nc) → Type} {ext : ∀ S₁, Int S₁ → (Fin C.N → Bool)}
    {session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool} :
    (r.oracle₂ (L₁ := L₁) (L₂ := L₂) ext session).LinkSound 0 := by
  intro R c tgt
  refine le_of_eq ((congrArg avg (funext fun ω₁ => (congrArg avg (funext fun ω₂ => ?_)).trans
    (avg_const 0))).trans (avg_const 0))
  refine le_antisymm ((prob_mono (q := fun _ => False) (fun ok h => ?_) _ _).trans
    (prob_false _ _).le) (zero_le)
  obtain ⟨-, v, -, -, Y, hY, -, g, -, hne⟩ := h
  obtain rfl := Option.some.inj hY
  exact hne rfl

/-- **The two-stage profile at the oracle layer**, variant (b), from a sound fine-level session:
`Pr[accept ∧ wrong_c(R) ∈ 𝓑] ≤ sup_{B ∈ 𝓑} e_eff(B) + ε`. -/
theorem Refines.oracle₂_profile (r : Refines Pf Pc) {L₁ : Law nc} {L₂ : Fin nc → Law nf}
    {Int : Finset (Fin nc) → Type} {ext : ∀ S₁, Int S₁ → (Fin C.N → Bool)}
    {session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool}
    {ε : ℝ≥0∞} (hs : SessionSound₂ Pf Pc ext session ε) (𝓑 : Finset (Fin nc) → Prop)
    (σ : Strategy (twoStage L₁ L₂ (Fin C.N → Bool) Int session)) :
    prob (fun o => o.1 = true ∧ 𝓑 (Pc.wrong (reg₂ σ))) (twoStage L₁ L₂ _ Int session) σ ≤
      (⨆ (B : Finset (Fin nc)) (_ : 𝓑 B), effEscape L₁ L₂ r.parent B) + ε := by
  have := twoStage_profile (r.oracle₂ ext session) (r.oracle₂_knowledgeSound hs) r.oracle₂_linkSound
    𝓑 σ
  rwa [add_zero] at this

/-- **(b1) at the oracle layer is one-stage over the coarse partition**:
`Pr[accept ∧ wrong_c(R) ∈ 𝓑] ≤ sup_{B ∈ 𝓑} e_{L₁}(B) + ε`. -/
theorem Refines.oracle₂_full_profile (r : Refines Pf Pc) {L₁ : Law nc} {L₂ : Fin nc → Law nf}
    {Int : Finset (Fin nc) → Type} {ext : ∀ S₁, Int S₁ → (Fin C.N → Bool)}
    {session : Finset (Fin nf) → (Fin C.N → Bool) → (S₁ : Finset (Fin nc)) → Int S₁ → Game Bool}
    {ε : ℝ≥0∞} (hs : SessionSound₂ Pf Pc ext session ε)
    (hfull : ∀ u ω v, r.parent v = u → v ∈ (L₂ u).draw ω) (𝓑 : Finset (Fin nc) → Prop)
    (σ : Strategy (twoStage L₁ L₂ (Fin C.N → Bool) Int session)) :
    prob (fun o => o.1 = true ∧ 𝓑 (Pc.wrong (reg₂ σ))) (twoStage L₁ L₂ _ Int session) σ ≤
      (⨆ (B : Finset (Fin nc)) (_ : 𝓑 B), L₁.escape B) + ε := by
  have := r.oracle₂_profile hs 𝓑 σ
  simp only [effEscape_full r.parent hfull] at this
  exact this

end Partition

end FlockSoundness.Audit
