import FlockSoundness.Audit.OneStage

/-!
# The one-stage audit with a randomized extractor

The knowledge extractor of a compiled table reruns the prover after its first commitment and
decodes what it saw (`Knowledge.lean`), so whether it succeeds is a probability over its reruns,
not a fact about the state. And the table theorems' bounds depend on the prover (its collision
finders' advantages). This file restates the one-stage audit for that case (`ExtractionAnalysis`),
in the joint form the table and session theorems state (agreed with lane flock-soundness):

* `ks S R τ u`: `Pr[the session accepts ∧ extraction of drawn unit u fails]`, from the session state
  `τ`, over the fresh run and the extractor's reruns;
* `link S R τ u X`: `Pr[it accepts ∧ extraction of u succeeds but differs from X on u's wires]`;
* `cover`: for a drawn unit wrong in `X`, `Pr[accept] ≤ ks + link` (every extractor outcome fails
  one way or the other).

The named hypotheses bound `ks` and `link` at the unit a rule picks before the session's first coin,
averaged over the draw (`KnowledgeSound`, `LinkSound`); the bounds are functions of the prover's
state. `extraction_audit_le` is `audit_le` in this form; the count curve is `extraction_audit_count`.
-/

namespace FlockSoundness.Audit

open Game
open scoped ENNReal

variable {n : ℕ} {L : Law n} {Reg : Type} {session : Finset (Fin n) → Reg → Game Bool}

/-- A per-unit quantity at the unit a rule picks, and zero when it picks none or an undrawn one. -/
noncomputable def atTgt (S : Finset (Fin n)) (t : Option (Fin n)) (f : Fin n → ℝ≥0∞) : ℝ≥0∞ :=
  t.elim 0 fun u => if u ∈ S then f u else 0

theorem atTgt_le {S : Finset (Fin n)} {f : Fin n → ℝ≥0∞} {c : ℝ≥0∞} (h : ∀ u ∈ S, f u ≤ c)
    (t : Option (Fin n)) : atTgt S t f ≤ c := by
  cases t with
  | none => exact zero_le
  | some u =>
    simp only [atTgt, Option.elim_some]
    split_ifs with hu
    · exact h u hu
    · exact zero_le

/-- What the analysis of an audit fixes when extraction is randomized: the committed transcript,
and for each drawn unit the joint probabilities of the two ways its table can accept while it is
wrong. -/
structure ExtractionAnalysis (L : Law n) (Reg : Type) (session : Finset (Fin n) → Reg → Game Bool)
    where
  Tr : Type
  wrong : Tr → Finset (Fin n)
  committed : (R : Reg) → Cont L Reg session R → Tr
  /-- `Pr[the session accepts ∧ extraction of u fails]` -/
  ks : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → ℝ≥0∞
  /-- `Pr[it accepts ∧ extraction of u succeeds but differs from X on u's wires]` -/
  link : (S : Finset (Fin n)) → (R : Reg) → Strategy (session S R) → Fin n → Tr → ℝ≥0∞
  cover : ∀ S R (τ : Strategy (session S R)) u X, u ∈ S → u ∈ wrong X →
    prob (· = true) (session S R) τ ≤ ks S R τ u + link S R τ u X

namespace ExtractionAnalysis

variable (A : ExtractionAnalysis L Reg session)

/-- The committed transcript of an audit strategy. -/
def committedOf (σ : Strategy (audit L Reg session)) : A.Tr := A.committed (reg σ) (cont σ)

/-- **Knowledge soundness, per unit** (named hypothesis `ε_ks`, which may depend on the prover's
state): for every prover and every rule that picks a drawn unit before the session's first coin,
the average over the draw of `Pr[accept ∧ extraction of the picked unit fails]`. -/
def KnowledgeSound (εks : (R : Reg) → Cont L Reg session R → ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (τ : Cont L Reg session R) (tgt : L.Ω → Option (Fin n)),
    avg (fun ω => atTgt (L.draw ω) (tgt ω) (A.ks (L.draw ω) R (τ ω))) ≤ εks R τ

/-- **The link term** (named hypothesis `δ_link`, which may depend on the prover's state):
likewise, with `Pr[accept ∧ extraction succeeds but disagrees with the committed transcript]`. -/
def LinkSound (δlink : (R : Reg) → Cont L Reg session R → ℝ≥0∞) : Prop :=
  ∀ (R : Reg) (τ : Cont L Reg session R) (tgt : L.Ω → Option (Fin n)),
    avg (fun ω => atTgt (L.draw ω) (tgt ω) fun u => A.link (L.draw ω) R (τ ω) u (A.committed R τ)) ≤
      δlink R τ

end ExtractionAnalysis

namespace Analysis

variable (A : Analysis L Reg session)

open Classical in
/-- **A deterministic extractor is the special case**: `ks` is `Pr[accept ∧ extraction of u
fails]`, zero or the acceptance probability, and likewise `link`. -/
noncomputable def toExtraction : ExtractionAnalysis L Reg session where
  Tr := A.Tr
  wrong := A.wrong
  committed := A.committed
  ks S R τ u := prob (fun ok => ok = true ∧ A.ksFail S R τ u) (session S R) τ
  link S R τ u X := prob (fun ok => ok = true ∧ A.linkFail S R τ u X) (session S R) τ
  cover S R τ u X _ hu :=
    (prob_mono (fun _ h => (A.cover S R τ u X hu).elim (fun hk => Or.inl ⟨h, hk⟩)
      fun hl => Or.inr ⟨h, hl⟩) _ _).trans (prob_or_le _ _ _ _)

theorem atTgt_toExtraction (S : Finset (Fin n)) (R : Reg) (τ : Strategy (session S R))
    (t : Option (Fin n)) (F : Fin n → Prop) :
    atTgt S t (fun u => prob (fun ok => ok = true ∧ F u) (session S R) τ) =
      prob (fun ok => ok = true ∧ ∃ u, t = some u ∧ u ∈ S ∧ F u) (session S R) τ := by
  classical
  rcases t with _ | u
  · simp [atTgt, prob_false]
  · by_cases hu : u ∈ S
    · simp [atTgt, hu]
    · simp [atTgt, hu, prob_false]

theorem KnowledgeSound.toExtraction {A : Analysis L Reg session} {εks : ℝ≥0∞}
    (h : A.KnowledgeSound εks) : A.toExtraction.KnowledgeSound fun _ _ => εks := fun R τ tgt =>
  le_of_eq_of_le (congrArg avg (funext fun ω =>
    atTgt_toExtraction (L.draw ω) R (τ ω) (tgt ω) (A.ksFail (L.draw ω) R (τ ω)))) (h R τ tgt)

theorem LinkSound.toExtraction {A : Analysis L Reg session} {δlink : ℝ≥0∞}
    (h : A.LinkSound δlink) : A.toExtraction.LinkSound fun _ _ => δlink := fun R τ tgt =>
  le_of_eq_of_le (congrArg avg (funext fun ω =>
    atTgt_toExtraction (L.draw ω) R (τ ω) (tgt ω)
      fun u => A.linkFail (L.draw ω) R (τ ω) u (A.committed R τ))) (h R τ tgt)

end Analysis

/-- **The one-stage audit bound, with a randomized extractor.** -/
theorem extraction_audit_le (A : ExtractionAnalysis L Reg session)
    {εks δlink : (R : Reg) → Cont L Reg session R → ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (E : A.Tr → Finset (Fin n) → Prop)
    (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ E (A.committedOf σ) o.2) (audit L Reg session) σ ≤
      prCoin (fun ω => E (A.committedOf σ) (L.draw ω) ∧
        Disjoint (L.draw ω) (A.wrong (A.committedOf σ))) +
      εks (reg σ) (cont σ) + δlink (reg σ) (cont σ) := by
  classical
  obtain ⟨R, τ'⟩ := σ
  set τ : Cont L Reg session R := cont ⟨R, τ'⟩
  set X := A.committed R τ with hX
  show prob _ (audit L Reg session) ⟨R, τ'⟩ ≤
    prCoin (fun ω => E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X)) + εks R τ + δlink R τ
  let tgt : L.Ω → Option (Fin n) := fun ω =>
    if h : ∃ u, u ∈ L.draw ω ∧ u ∈ A.wrong X then some (Classical.choose h) else none
  let ks : L.Ω → ℝ≥0∞ := fun ω => atTgt (L.draw ω) (tgt ω) (A.ks (L.draw ω) R (τ ω))
  let lk : L.Ω → ℝ≥0∞ := fun ω => atTgt (L.draw ω) (tgt ω) fun u => A.link (L.draw ω) R (τ ω) u X
  have step : ∀ ω, prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω) ≤
      (if E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X) then 1 else 0) + ks ω + lk ω := by
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
      have hc := A.cover (L.draw ω) R (τ ω) _ X hmem hw
      have hks : ks ω = A.ks (L.draw ω) R (τ ω) (Classical.choose h) := by
        simp [ks, atTgt, ht, hmem]
      have hlk : lk ω = A.link (L.draw ω) R (τ ω) (Classical.choose h) X := by
        simp [lk, atTgt, ht, hmem]
      calc prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω)
          ≤ prob (· = true) (session (L.draw ω) R) (τ ω) := prob_mono (fun ok h => h.1) _ _
        _ ≤ ks ω + lk ω := by rw [hks, hlk]; exact hc
        _ ≤ _ := by rw [add_assoc]; exact le_add_left le_rfl
  calc prob (fun o => o.1 = true ∧ E X o.2) (audit L Reg session) ⟨R, τ'⟩
      = avg fun ω => prob (fun ok => ok = true ∧ E X (L.draw ω)) (session (L.draw ω) R) (τ ω) :=
        congrArg avg (funext fun ω => prob_map _ _ _ _)
    _ ≤ avg fun ω => (if E X (L.draw ω) ∧ Disjoint (L.draw ω) (A.wrong X) then 1 else 0) +
        ks ω + lk ω := avg_mono step
    _ = _ := avg_add₃ _ _ _
    _ ≤ _ := add_le_add (add_le_add (avg_ite_eq_prCoin _).le (hks R τ tgt)) (hlink R τ tgt)

/-- **The count curve, with a randomized extractor**:
`Pr[accept ∧ at least K wrong units] ≤ miss K + ε_ks(σ) + δ_link(σ)`. -/
theorem extraction_audit_count (A : ExtractionAnalysis L Reg session)
    {εks δlink : (R : Reg) → Cont L Reg session R → ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (K : ℕ) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ K ≤ (A.wrong (A.committedOf σ)).card) (audit L Reg session) σ ≤
      L.miss K + εks (reg σ) (cont σ) + δlink (reg σ) (cont σ) := by
  refine (extraction_audit_le A hks hlink (fun X _ => K ≤ (A.wrong X).card) σ).trans ?_
  gcongr
  by_cases hB : K ≤ (A.wrong (A.committedOf σ)).card
  · exact (prCoin_mono fun ω h => h.2).trans (L.escape_le_miss hB)
  · exact (prCoin_mono (q := fun _ => False) fun ω h => absurd h.1 hB).trans
      (prCoin_false.le.trans (zero_le))

/-- **Drawn units, with a randomized extractor**, are correct up to `ε_ks(σ) + δ_link(σ)`. -/
theorem extraction_audit_drawn (A : ExtractionAnalysis L Reg session)
    {εks δlink : (R : Reg) → Cont L Reg session R → ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) (σ : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ ¬ Disjoint (A.wrong (A.committedOf σ)) o.2) (audit L Reg session) σ ≤
      εks (reg σ) (cont σ) + δlink (reg σ) (cont σ) := by
  refine (extraction_audit_le A hks hlink (fun X S => ¬ Disjoint (A.wrong X) S) σ).trans ?_
  have : prCoin (fun ω => ¬ Disjoint (A.wrong (A.committedOf σ)) (L.draw ω) ∧
      Disjoint (L.draw ω) (A.wrong (A.committedOf σ))) = 0 :=
    le_antisymm ((prCoin_mono (q := fun _ => False) fun ω h => h.1 h.2.symm).trans
      prCoin_false.le) (zero_le)
  rw [this, zero_add]

end FlockSoundness.Audit
