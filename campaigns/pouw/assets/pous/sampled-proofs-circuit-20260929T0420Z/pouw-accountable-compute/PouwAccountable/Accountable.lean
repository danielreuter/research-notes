import PouwAccountable.Closure
import PouwAccountable.HarmBound
import PouwAccountable.Assumptions

/-!
# Accountable compute (design note §12.2 (2) and (3))

Every theorem here is `main`'s one-stage profile (`audit_profile`, which holds for every law) applied to one family of
wrong-unit sets. The committed transcript is fixed at registration (`Analysis.committedOf`), and the closure, the work
and the harms are parameters fixed before the strategy, which is how A1 and A3 enter.

* `audit_damage` (**width-abstract**): for any damage `D` of the wrong-unit set that a harm `h` covers, and any harm
  bound `H` of the law at `δ`, `Pr[accept ∧ H < D(wrong)] ≤ δ + ε_ks + δ_link`. Free compute and exfiltration are two
  instances, with the same draw: `D` the unsound work, or the observable bits (`exfiltration`), whose harm depends on
  whether Z is a tile output or certified by narrow units. Neither choice enters any other statement.
* `audit_strata`: §12.2 (2) as the note first stated it, for any law (harm-weighted strip and node strata), with each
  unit's harm `harm cl w`.
* `audit_closure`: the closure-draw form. For any law that draws at least the closure of a tile draw, the tile law's
  harm bound with each tile's work as its harm bounds the unsound work.
* `accountable_compute`: **the conclusion.** Tiles drawn by `main`'s stratified law with harm-proportional sizes,
  each proved with its closure, plus any other draws: `Pr[accept ∧ verified work < (1 − ε)·W] ≤ δ + ε_ks + δ_link`.
* `compute_used` (§12.2 (3)): with PoUW's per-tile count statement (A8, with the key's hash assumptions A10), anchored
  inputs (A9) and no call index registered twice (A11) as named hypotheses, the online cost is at least
  `(1 − γ)(W − H)` except with probability `a + δin + δidx + ηTT + εcr`; `compute_used_audit` composes it with
  `accountable_compute`.
-/

namespace PouwAccountable

open FlockSoundness FlockSoundness.Audit FlockSoundness.Game Finset
open scoped ENNReal

variable {n nT : ℕ} {L : Law n} {Reg : Type} {session : Finset (Fin n) → Reg → Game Bool} {εks δlink : ℝ≥0∞}

/-- **Accountability for any covered damage** (width-abstract). -/
theorem audit_damage (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (D : Finset (Fin n) → ℝ) (h : Fin n → ℝ) (hcov : ∀ B, D B ≤ ∑ u ∈ B, h u) {δ : ℝ≥0∞} {H : ℝ}
    (hH : IsHarmBound L h δ H) (σ' : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ H < D (A.wrong (A.committedOf σ'))) (audit L Reg session) σ' ≤
      δ + εks + δlink := by
  refine (audit_profile A hks hlink (fun B => H < D B) σ').trans ?_
  gcongr
  exact iSup₂_le fun B hB => (escape_lt_of_harm_gt hH (hB.trans_le (hcov B))).le

/-- **The exfiltration bound from the same draw**: `hb u` is the number of `u`'s output bits that can reach an
observable output, which depends on the partition's width choices and on nothing else here. -/
theorem exfiltration (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (hb : Fin n → ℝ) {δ : ℝ≥0∞} {H : ℝ} (hH : IsHarmBound L hb δ H) (σ' : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ H < ∑ u ∈ A.wrong (A.committedOf σ'), hb u) (audit L Reg session) σ' ≤
      δ + εks + δlink :=
  audit_damage A hks hlink (fun B => ∑ u ∈ B, hb u) hb (fun _ => le_rfl) hH σ'

/-- **§12.2 (2) with harm-weighted strata**: any law, each unit charged the work of the tiles whose credit depends on
it. -/
theorem audit_strata (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (cl : Fin nT → Finset (Fin n)) {w : Fin nT → ℝ} (hw : ∀ t, 0 ≤ w t) {δ : ℝ≥0∞} {H : ℝ}
    (hH : IsHarmBound L (harm cl w) δ H) (σ' : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ H < unsoundWork cl w (A.wrong (A.committedOf σ'))) (audit L Reg session) σ' ≤
      δ + εks + δlink :=
  audit_damage A hks hlink (unsoundWork cl w) (harm cl w) (unsoundWork_le_harm cl hw) hH σ'

/-- **§12.2 (2) with closure draws**: for any law whose escapes are at most the closure draw's, a harm bound of the
tile law, with each tile's work as its harm, bounds the unsound work. -/
theorem audit_closure (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ)
    (hdom : ∀ B, L.escape B ≤ (closureLaw Lt cl).escape B) {δ : ℝ≥0∞} {H : ℝ} (hH : IsHarmBound Lt w δ H)
    (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (σ' : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ H < unsoundWork cl w (A.wrong (A.committedOf σ'))) (audit L Reg session) σ' ≤
      δ + εks + δlink := by
  refine (audit_profile A hks hlink (fun B => H < unsoundWork cl w B) σ').trans ?_
  gcongr
  refine iSup₂_le fun B hB => (hdom B).trans ?_
  rw [closureLaw_escape]
  exact (escape_lt_of_harm_gt hH hB).le

variable {mT : ℕ}

/-- **Accountable compute** (the conclusion). Tiles are drawn by `main`'s stratified law over tile strata `σT`, each
stratum proved whole or sized by harm (`N_s · wmax_s · ln(1/δ) ≤ ε · W · k_s`, with `wmax_s` the largest work of a
tile in it), each drawn tile proved with its closure, plus any other draws (`hdom`, e.g. `both`). Then an accepted
audit's verified work falls below `(1 − ε)·W` with probability at most `δ + ε_ks + δ_link`. -/
theorem accountable_compute (σT : Fin nT → Fin mT) (kT : Fin mT → ℕ) (hkT : ∀ s, kT s ≤ (Law.stratum σT s).card)
    (cl : Fin nT → Finset (Fin n)) {w : Fin nT → ℝ} (wmax : Fin mT → ℝ) (hw0 : ∀ t, 0 ≤ w t)
    (hw : ∀ t, w t ≤ wmax (σT t)) {δ ε : ℝ} (hδ0 : 0 < δ) (hδ1 : δ < 1) (hε : 0 < ε)
    (hsize : ∀ s, kT s = (Law.stratum σT s).card ∨
      ((Law.stratum σT s).card : ℝ) * wmax s * Real.log δ⁻¹ ≤ ε * totalWork w * kT s)
    (hdom : ∀ B, L.escape B ≤ (closureLaw (Law.stratified σT kT hkT) cl).escape B)
    (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (σ' : Strategy (audit L Reg session)) :
    prob (fun o => o.1 = true ∧ soundWork cl w (A.wrong (A.committedOf σ')) < (1 - ε) * totalWork w)
      (audit L Reg session) σ' ≤ ENNReal.ofReal δ + εks + δlink := by
  have hlog : 0 < Real.log δ⁻¹ := Real.log_pos (one_lt_inv_iff₀.2 ⟨hδ0, hδ1⟩)
  have hW : 0 ≤ totalWork w := sum_nonneg fun t _ => hw0 t
  set c := ε * totalWork w / Real.log δ⁻¹ with hcdef
  have hc0 : 0 ≤ c := div_nonneg (mul_nonneg hε.le hW) hlog.le
  have hc : ∀ s, kT s = (Law.stratum σT s).card ∨ ((Law.stratum σT s).card : ℝ) * wmax s ≤ c * kT s := by
    intro s
    rcases hsize s with h | h
    · exact Or.inl h
    · refine Or.inr ?_
      rw [hcdef, div_mul_eq_mul_div, le_div_iff₀ hlog]
      exact h
  have hH := stratified_isHarmBound σT kT hkT w wmax hw hc0 hc hδ0
  have hcH : c * Real.log δ⁻¹ = ε * totalWork w := by
    rw [hcdef, div_mul_cancel₀ _ hlog.ne']
  rw [hcH] at hH
  refine le_trans (prob_mono (fun o ho => ⟨ho.1, ?_⟩) _ _)
    (audit_closure (Law.stratified σT kT hkT) cl w hdom hH A hks hlink σ')
  have := soundWork_add_unsoundWork cl w (A.wrong (A.committedOf σ'))
  linarith [ho.2]

/-- **Accountable compute for the window's law**: the closure draws of `accountable_compute`, together with an
independent draw `M` of the other strata (the integrity floor: quantizer, dequantization or narrow Z units, the rest of
the model). -/
theorem accountable_compute_floor (σT : Fin nT → Fin mT) (kT : Fin mT → ℕ)
    (hkT : ∀ s, kT s ≤ (Law.stratum σT s).card) (cl : Fin nT → Finset (Fin n)) (M : Law n) {w : Fin nT → ℝ}
    (wmax : Fin mT → ℝ) (hw0 : ∀ t, 0 ≤ w t) (hw : ∀ t, w t ≤ wmax (σT t)) {δ ε : ℝ} (hδ0 : 0 < δ) (hδ1 : δ < 1)
    (hε : 0 < ε) (hsize : ∀ s, kT s = (Law.stratum σT s).card ∨
      ((Law.stratum σT s).card : ℝ) * wmax s * Real.log δ⁻¹ ≤ ε * totalWork w * kT s)
    {session : Finset (Fin n) → Reg → Game Bool}
    (A : Analysis (both (closureLaw (Law.stratified σT kT hkT) cl) M) Reg session) (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink)
    (σ' : Strategy (audit (both (closureLaw (Law.stratified σT kT hkT) cl) M) Reg session)) :
    prob (fun o => o.1 = true ∧ soundWork cl w (A.wrong (A.committedOf σ')) < (1 - ε) * totalWork w)
      (audit (both (closureLaw (Law.stratified σT kT hkT) cl) M) Reg session) σ' ≤
      ENNReal.ofReal δ + εks + δlink :=
  accountable_compute σT kT hkT cl wmax hw0 hw hδ0 hδ1 hε hsize (fun B => both_escape_le _ M B) A hks hlink σ'

/-- **The γ step** (§12.2 (3)), in any game. If an accepted outcome has unsound work above `H` with probability at most
`a`, inputs off their anchors with at most `δin` (A9), a repeated call index with at most `δidx` (A11), and PoUW's
per-tile count statement holds on the rest (A8, A10), then an accepted outcome's online cost falls below
`(1 − γ)(W − H)` with probability at most `a + δin + δidx + (ηTT + εcr)`. -/
theorem compute_used {α : Type} (g : Game α) (s : Strategy g) (accept anchored unique : α → Prop)
    (cost unsound : α → ℝ) {W H γ : ℝ} {a δin δidx ηTT εcr : ℝ≥0∞} (hγ : γ ≤ 1)
    (h2 : prob (fun o => accept o ∧ H < unsound o) g s ≤ a) (h9 : AnchoredInputs g s accept anchored δin)
    (h11 : UniqueCallIndices g s accept unique δidx)
    (hcount : PerTileCount g s anchored unique cost (fun o => W - unsound o) γ ηTT εcr) :
    prob (fun o => accept o ∧ cost o < (1 - γ) * (W - H)) g s ≤ a + δin + δidx + (ηTT + εcr) := by
  refine le_trans (prob_mono (q := fun o => (((accept o ∧ H < unsound o) ∨ (accept o ∧ ¬ anchored o)) ∨
      (accept o ∧ ¬ unique o)) ∨ (anchored o ∧ unique o ∧ cost o < (1 - γ) * (W - unsound o)))
    (fun o ho => ?_) g s) ?_
  · by_cases hu : H < unsound o
    · exact Or.inl (Or.inl (Or.inl ⟨ho.1, hu⟩))
    by_cases ha : anchored o
    · by_cases hq : unique o
      · refine Or.inr ⟨ha, hq, lt_of_lt_of_le ho.2 ?_⟩
        exact mul_le_mul_of_nonneg_left (by linarith [not_lt.1 hu]) (by linarith)
      · exact Or.inl (Or.inr ⟨ho.1, hq⟩)
    · exact Or.inl (Or.inl (Or.inr ⟨ho.1, ha⟩))
  · refine (prob_or_le _ _ g s).trans (add_le_add ((prob_or_le _ _ g s).trans (add_le_add
      ((prob_or_le _ _ g s).trans (add_le_add h2 h9)) h11)) hcount)

/-- **Accountable compute with γ** (§12.2 (3) on the audit): with A9, A11 and PoUW's per-tile count statement for the
verified work of the committed transcript, an accepted audit's online cost falls below `(1 − γ)(1 − ε)·W` with
probability at most `δ + ε_ks + δ_link + δin + δidx + (ηTT + εcr)`. -/
theorem compute_used_audit (σT : Fin nT → Fin mT) (kT : Fin mT → ℕ) (hkT : ∀ s, kT s ≤ (Law.stratum σT s).card)
    (cl : Fin nT → Finset (Fin n)) {w : Fin nT → ℝ} (wmax : Fin mT → ℝ) (hw0 : ∀ t, 0 ≤ w t)
    (hw : ∀ t, w t ≤ wmax (σT t)) {δ ε γ : ℝ} (hδ0 : 0 < δ) (hδ1 : δ < 1) (hε : 0 < ε) (hγ : γ ≤ 1)
    (hsize : ∀ s, kT s = (Law.stratum σT s).card ∨
      ((Law.stratum σT s).card : ℝ) * wmax s * Real.log δ⁻¹ ≤ ε * totalWork w * kT s)
    (hdom : ∀ B, L.escape B ≤ (closureLaw (Law.stratified σT kT hkT) cl).escape B)
    (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (σ' : Strategy (audit L Reg session)) (anchored unique : Bool × Finset (Fin n) → Prop)
    (cost : Bool × Finset (Fin n) → ℝ) {δin δidx ηTT εcr : ℝ≥0∞}
    (h9 : AnchoredInputs (audit L Reg session) σ' (fun o => o.1 = true) anchored δin)
    (h11 : UniqueCallIndices (audit L Reg session) σ' (fun o => o.1 = true) unique δidx)
    (hcount : PerTileCount (audit L Reg session) σ' anchored unique cost
      (fun _ => soundWork cl w (A.wrong (A.committedOf σ'))) γ ηTT εcr) :
    prob (fun o => o.1 = true ∧ cost o < (1 - γ) * ((1 - ε) * totalWork w)) (audit L Reg session) σ' ≤
      ENNReal.ofReal δ + εks + δlink + δin + δidx + (ηTT + εcr) := by
  set X := A.wrong (A.committedOf σ')
  have hsplit : soundWork cl w X = totalWork w - unsoundWork cl w X := by
    linarith [soundWork_add_unsoundWork cl w X]
  have h2 : prob (fun o => o.1 = true ∧ ε * totalWork w < unsoundWork cl w X) (audit L Reg session) σ' ≤
      ENNReal.ofReal δ + εks + δlink := by
    refine le_trans (prob_mono (fun o ho => ⟨ho.1, ?_⟩) _ _)
      (accountable_compute σT kT hkT cl wmax hw0 hw hδ0 hδ1 hε hsize hdom A hks hlink σ')
    linarith [ho.2, hsplit]
  have hcount' : PerTileCount (audit L Reg session) σ' anchored unique cost
      (fun _ => totalWork w - unsoundWork cl w X) γ ηTT εcr := by
    unfold PerTileCount at hcount ⊢
    simpa only [hsplit] using hcount
  have := compute_used (audit L Reg session) σ' (fun o => o.1 = true) anchored unique cost
    (fun _ => unsoundWork cl w X) (W := totalWork w) (H := ε * totalWork w) hγ h2 h9 h11 hcount'
  refine le_trans (prob_mono (fun o ho => ⟨ho.1, ?_⟩) _ _) this
  have : (1 - ε) * totalWork w = totalWork w - ε * totalWork w := by ring
  rw [← this]
  exact ho.2

end PouwAccountable
