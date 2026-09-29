import FlockSoundness.Audit.Extraction

/-!
# The stratified draw law

The strata are the units a map `σ : Fin n → Fin m` assigns to each `s`, for example one stratum per template. The
stratified law draws an independent uniform `k s`-subset inside each stratum (`Law.stratified`,
`docs/sampling-strategies.md` §1, §4).

* `stratified_escape`: a set `B` with `m_s` units in stratum `s` escapes with the product of hypergeometrics
  `∏ s C(n_s − m_s, k_s) / C(n_s, k_s)`. It depends only on the counts, as `verity.proofs.profile.Stratified` computes
  it. The uniform `k`-subset is the case of one stratum.
* `stratified_escape_floor`: **a floor catches its whole stratum**. With `1 ≤ k s`, a set containing stratum `s` never
  escapes.
* The one-stage profile theorems hold for every law, so they instantiate here. `audit_whole_stratum` (oracle layer) and
  `extraction_audit_whole_stratum` (compiled layer): an audit accepts while a whole floored stratum is wrong with
  probability at most the per-unit terms.
-/

namespace FlockSoundness.Audit

open Game Finset
open scoped ENNReal

namespace Law

variable {n m : ℕ}

/-- Stratum `s` of the assignment `σ`: the units it assigns to `s`. -/
def stratum (σ : Fin n → Fin m) (s : Fin m) : Finset (Fin n) := univ.filter (σ · = s)

theorem mem_stratum {σ : Fin n → Fin m} {s : Fin m} {u : Fin n} : u ∈ stratum σ s ↔ σ u = s := by
  simp [stratum]

/-- **Independent uniform subsets inside the strata of `σ`**, `k s` of stratum `s`. -/
def stratified (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (stratum σ s).card) : Law n where
  Ω := (s : Fin m) → ((stratum σ s).powersetCard (k s))
  nonempty := ⟨fun s => ⟨_, (Finset.powersetCard_nonempty.2 (hk s)).choose_spec⟩⟩
  draw ω := univ.biUnion fun s => (ω s).1

theorem card_coe_filter {α : Type} (P : Finset α) (q : α → Prop) [DecidablePred q] :
    (univ.filter fun x : P => q x.1).card = (P.filter q).card := by
  rw [← Finset.card_map ⟨Subtype.val, Subtype.val_injective⟩]
  congr 1
  ext x
  simp [and_comm]

/-- A coin uniform over the elements of `P`: `q` holds with probability `|P.filter q| / |P|`. -/
theorem prCoin_coe {α : Type} (P : Finset α) [Nonempty P] (q : α → Prop) [DecidablePred q] :
    prCoin (fun x : P => q x.1) = ((P.filter q).card : ℝ≥0∞) / P.card := by
  rw [prCoin_eq_card, card_coe_filter, Fintype.card_coe]

/-- The `k`-subsets of `T` that miss `B`: `C(|T| − |B ∩ T|, k)` of them. -/
theorem card_powersetCard_disjoint (T B : Finset (Fin n)) (k : ℕ) :
    ((T.powersetCard k).filter fun S => Disjoint S B).card = (T.card - (B ∩ T).card).choose k := by
  have h : (T.powersetCard k).filter (fun S => Disjoint S B) = (T \ B).powersetCard k := by
    ext S
    simp only [mem_filter, mem_powersetCard, subset_sdiff]
    tauto
  rw [h, card_powersetCard]
  congr 1
  rw [show T \ B = T \ (B ∩ T) by ext; simp, card_sdiff_of_subset inter_subset_right]

theorem filter_eq_inter_stratum (σ : Fin n → Fin m) (s : Fin m) (B : Finset (Fin n)) :
    B.filter (σ · = s) = B ∩ stratum σ s := by
  ext u
  simp [stratum]

/-- **The stratified escape**: the product over strata of the hypergeometric escape of the stratum's count,
`∏ s C(n_s − m_s, k_s) / C(n_s, k_s)` with `n_s = |stratum s|` and `m_s = |B ∩ stratum s|`. -/
theorem stratified_escape (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (stratum σ s).card)
    (B : Finset (Fin n)) :
    (stratified σ k hk).escape B =
      ∏ s, (((stratum σ s).card - (B.filter (σ · = s)).card).choose (k s) : ℝ≥0∞) /
        ((stratum σ s).card.choose (k s) : ℝ≥0∞) := by
  classical
  unfold escape
  have hd : (fun ω : (stratified σ k hk).Ω => Disjoint ((stratified σ k hk).draw ω) B) =
      fun ω => ∀ s ∈ (univ : Finset (Fin m)), Disjoint (ω s).1 B := by
    funext ω
    exact propext (Finset.disjoint_biUnion_left univ (fun s => (ω s).1) B)
  rw [hd]
  have : ∀ s, Nonempty ((stratum σ s).powersetCard (k s)) :=
    fun s => ⟨⟨_, (Finset.powersetCard_nonempty.2 (hk s)).choose_spec⟩⟩
  refine (prCoin_pi_forall (Ω := fun s => ((stratum σ s).powersetCard (k s))) univ
    (fun s S => Disjoint S.1 B)).trans ?_
  refine Finset.prod_congr rfl fun s _ => ?_
  classical
  refine (prCoin_coe ((stratum σ s).powersetCard (k s)) (fun S => Disjoint S B)).trans ?_
  rw [card_powersetCard_disjoint, card_powersetCard, filter_eq_inter_stratum]

/-- **A floor catches its whole stratum**: with `1 ≤ k s`, a set containing stratum `s` never escapes. -/
theorem stratified_escape_floor (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (stratum σ s).card)
    (s : Fin m) (h : 1 ≤ k s) {B : Finset (Fin n)} (hB : stratum σ s ⊆ B) :
    (stratified σ k hk).escape B = 0 := by
  rw [stratified_escape]
  refine Finset.prod_eq_zero (mem_univ s) ?_
  have hc : (B.filter (σ · = s)).card = (stratum σ s).card := by
    rw [filter_eq_inter_stratum, inter_eq_right.2 hB]
  rw [hc, Nat.sub_self, Nat.choose_eq_zero_of_lt (by omega)]
  simp

end Law

section Audits

variable {n m : ℕ} {σ : Fin n → Fin m} {k : Fin m → ℕ} {hk : ∀ s, k s ≤ (Law.stratum σ s).card}
  {Reg : Type} {session : Finset (Fin n) → Reg → Game Bool}

/-- **A wholly wrong floored stratum is caught** (oracle layer): the audit accepts while every unit of stratum `s`
is wrong with probability at most `ε_ks + δ_link`. -/
theorem audit_whole_stratum (A : Analysis (Law.stratified σ k hk) Reg session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) (s : Fin m) (h : 1 ≤ k s)
    (σ' : Strategy (audit (Law.stratified σ k hk) Reg session)) :
    prob (fun o => o.1 = true ∧ Law.stratum σ s ⊆ A.wrong (A.committedOf σ'))
        (audit (Law.stratified σ k hk) Reg session) σ' ≤ εks + δlink := by
  refine (audit_profile A hks hlink (fun B => Law.stratum σ s ⊆ B) σ').trans ?_
  have h0 : (⨆ (B : Finset (Fin n)) (_ : Law.stratum σ s ⊆ B), (Law.stratified σ k hk).escape B) = 0 :=
    le_antisymm (iSup₂_le fun B hB => (Law.stratified_escape_floor σ k hk s h hB).le) (zero_le)
  rw [h0, zero_add]

/-- **A wholly wrong floored stratum is caught** (compiled layer, randomized extractor): at most
`ε_ks(σ) + δ_link(σ)`. -/
theorem extraction_audit_whole_stratum (A : ExtractionAnalysis (Law.stratified σ k hk) Reg session)
    {εks δlink : (R : Reg) → Cont (Law.stratified σ k hk) Reg session R → ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) (s : Fin m) (h : 1 ≤ k s)
    (σ' : Strategy (audit (Law.stratified σ k hk) Reg session)) :
    prob (fun o => o.1 = true ∧ Law.stratum σ s ⊆ A.wrong (A.committedOf σ'))
        (audit (Law.stratified σ k hk) Reg session) σ' ≤ εks (reg σ') (cont σ') + δlink (reg σ') (cont σ') := by
  refine (extraction_audit_le A hks hlink (fun X _ => Law.stratum σ s ⊆ A.wrong X) σ').trans ?_
  have h0 : prCoin (fun ω => Law.stratum σ s ⊆ A.wrong (A.committedOf σ') ∧
      Disjoint ((Law.stratified σ k hk).draw ω) (A.wrong (A.committedOf σ'))) = 0 := by
    by_cases hB : Law.stratum σ s ⊆ A.wrong (A.committedOf σ')
    · exact le_antisymm ((prCoin_mono fun ω h => h.2).trans
        (Law.stratified_escape_floor σ k hk s h hB).le) (zero_le)
    · exact le_antisymm ((prCoin_mono (q := fun _ => False) fun ω h => hB h.1).trans prCoin_false.le) (zero_le)
  rw [h0, zero_add]

end Audits

end FlockSoundness.Audit
