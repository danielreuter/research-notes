import FlockSoundness.Audit.Stratified
import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
# Harm bounds (design note §12.2's `Hstar`, §12.3's allocation)

* `IsHarmBound L h δ H`: **`harm_bound`'s specification** (`verity.proofs.profile.Stratified.harm_bound`, "an upper
  bound on `sum_{u in B} harm(u)` over the wrong-unit sets `B` with `escape >= delta`"). The Python function computes
  one by a greedy fill in floating point; this file does not prove that implementation, it states what it must return.
* `harmOpt L h δ`: the exact optimum, §12.2's `H*(δ)`, as a finite maximum (the empty set included, so it is `≥ 0`).
  `harmOpt_isHarmBound` and `harmOpt_le`: it is the least harm bound.
* `escape_lt_of_harm_gt`: a set whose harm exceeds a harm bound escapes with probability below `δ`.
* `stratified_isHarmBound`: **a closed-form harm bound for `main`'s stratified law.** If every stratum is proved whole
  or satisfies `N_s · hmax_s ≤ c · k_s`, then `c · ln(1/δ)` is a harm bound at `δ`. With `c = εW / ln(1/δ)` that is
  §12.3's harm-proportional sizing: `k_s ≥ ln(1/δ) · N_s · hmax_s / (εW)` gives `H*(δ) ≤ εW`. It rests on
  `stratified_escape_le_exp`, `escape ≤ exp(−∑_s k_s m_s / N_s)`, from `main`'s `stratified_escape` and
  `choose_sub_mul_pow_le`.
-/

namespace PouwAccountable

open FlockSoundness.Audit Finset
open scoped ENNReal

variable {n : ℕ}

/-- **`harm_bound`'s specification**: every wrong-unit set that escapes with probability at least `δ` has harm at most
`H`. -/
def IsHarmBound (L : Law n) (h : Fin n → ℝ) (δ : ℝ≥0∞) (H : ℝ) : Prop :=
  ∀ B : Finset (Fin n), δ ≤ L.escape B → ∑ u ∈ B, h u ≤ H

/-- **The exact optimum `H*(δ)`**: the largest harm of a set escaping with probability at least `δ` (and at least the
empty set's harm, 0). -/
noncomputable def harmOpt (L : Law n) (h : Fin n → ℝ) (δ : ℝ≥0∞) : ℝ :=
  (insert ∅ ((univ : Finset (Finset (Fin n))).filter fun B => δ ≤ L.escape B)).sup' (insert_nonempty _ _)
    fun B => ∑ u ∈ B, h u

theorem harmOpt_isHarmBound (L : Law n) (h : Fin n → ℝ) (δ : ℝ≥0∞) : IsHarmBound L h δ (harmOpt L h δ) :=
  fun B hB => le_sup' (fun B => ∑ u ∈ B, h u) (mem_insert_of_mem (mem_filter.2 ⟨mem_univ B, hB⟩))

/-- **`H*(δ)` is the least harm bound** (for `δ ≤ 1`, when the empty set escapes with probability `1 ≥ δ`). -/
theorem harmOpt_le (L : Law n) (h : Fin n → ℝ) {δ : ℝ≥0∞} (hδ : δ ≤ 1) {H : ℝ} (hH : IsHarmBound L h δ H) :
    harmOpt L h δ ≤ H := by
  refine sup'_le _ _ fun B hB => ?_
  rcases mem_insert.1 hB with rfl | hB
  · simpa using hH ∅ (by rw [L.escape_empty]; exact hδ)
  · exact hH B (mem_filter.1 hB).2

/-- A set whose harm exceeds a harm bound escapes with probability below `δ`. -/
theorem escape_lt_of_harm_gt {L : Law n} {h : Fin n → ℝ} {δ : ℝ≥0∞} {H : ℝ} (hH : IsHarmBound L h δ H)
    {B : Finset (Fin n)} (hB : H < ∑ u ∈ B, h u) : L.escape B < δ :=
  lt_of_not_ge fun h' => absurd (hH B h') (not_le.2 hB)

/-! ## A closed-form harm bound for the stratified law -/

/-- One stratum's hypergeometric escape is at most `exp(−k·m/N)`. -/
theorem choose_ratio_le_exp {N M k : ℕ} (hk : k ≤ N) (hM : M ≤ N) :
    ((N - M).choose k : ℝ) / (N.choose k : ℝ) ≤ Real.exp (-((k : ℝ) * M / N)) := by
  rcases Nat.eq_zero_or_pos N with rfl | hN
  · obtain rfl : k = 0 := by omega
    obtain rfl : M = 0 := by omega
    simp
  · have hC : (0 : ℝ) < N.choose k := by exact_mod_cast Nat.choose_pos hk
    have hNr : (0 : ℝ) < N := by exact_mod_cast hN
    have keyR : ((N - M).choose k : ℝ) * (N : ℝ) ^ M ≤ (N.choose k : ℝ) * ((N - k : ℕ) : ℝ) ^ M := by
      exact_mod_cast Law.choose_sub_mul_pow_le N k M hM
    have h1 : ((N - M).choose k : ℝ) / (N.choose k : ℝ) ≤ (((N - k : ℕ) : ℝ) / N) ^ M := by
      rw [div_pow, div_le_div_iff₀ hC (pow_pos hNr M)]
      linarith [keyR]
    have h2 : ((N - k : ℕ) : ℝ) / N = -((k : ℝ) / N) + 1 := by
      rw [Nat.cast_sub hk]
      field_simp
      ring
    have h3 : (0 : ℝ) ≤ ((N - k : ℕ) : ℝ) / N := by positivity
    calc ((N - M).choose k : ℝ) / (N.choose k : ℝ) ≤ (((N - k : ℕ) : ℝ) / N) ^ M := h1
      _ ≤ (Real.exp (-((k : ℝ) / N))) ^ M := by
          apply pow_le_pow_left₀ h3
          rw [h2]
          exact Real.add_one_le_exp _
      _ = Real.exp (-((k : ℝ) * M / N)) := by
          rw [← Real.exp_nat_mul]
          congr 1
          ring

variable {m : ℕ}

theorem card_filter_le_stratum (σ : Fin n → Fin m) (B : Finset (Fin n)) (s : Fin m) :
    (B.filter (σ · = s)).card ≤ (Law.stratum σ s).card := by
  rw [Law.filter_eq_inter_stratum]
  exact card_le_card inter_subset_right

/-- **The stratified escape is at most `exp(−∑_s k_s·m_s/N_s)`**, with `m_s` the wrong units in stratum `s`. -/
theorem stratified_escape_le_exp (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (Law.stratum σ s).card)
    (B : Finset (Fin n)) :
    (Law.stratified σ k hk).escape B ≤ ENNReal.ofReal (Real.exp (-∑ s,
      ((k s : ℝ) * ((B.filter (σ · = s)).card : ℝ) / ((Law.stratum σ s).card : ℝ)))) := by
  rw [Law.stratified_escape, ← sum_neg_distrib, Real.exp_sum,
    ENNReal.ofReal_prod_of_nonneg fun s _ => (Real.exp_pos _).le]
  refine prod_le_prod fun s _ => ?_
  have hC : (0 : ℝ) < ((Law.stratum σ s).card.choose (k s) : ℝ) := by exact_mod_cast Nat.choose_pos (hk s)
  rw [show ((((Law.stratum σ s).card - (B.filter (σ · = s)).card).choose (k s) : ℕ) : ℝ≥0∞) /
      (((Law.stratum σ s).card.choose (k s) : ℕ) : ℝ≥0∞) =
      ENNReal.ofReal ((((Law.stratum σ s).card - (B.filter (σ · = s)).card).choose (k s) : ℝ) /
        ((Law.stratum σ s).card.choose (k s) : ℝ)) by
    rw [ENNReal.ofReal_div_of_pos hC, ENNReal.ofReal_natCast, ENNReal.ofReal_natCast]]
  exact ENNReal.ofReal_le_ofReal (choose_ratio_le_exp (hk s) (card_filter_le_stratum σ B s))

/-- **A closed-form harm bound for the stratified law** (§12.3's harm-proportional sizing). If every unit's harm is
at most its stratum's `hmax`, and every stratum is proved whole (`k_s = N_s`) or has `N_s · hmax_s ≤ c · k_s`, then
`c · ln(1/δ)` bounds the harm of every set escaping with probability at least `δ > 0`. -/
theorem stratified_isHarmBound (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (Law.stratum σ s).card)
    (h : Fin n → ℝ) (hmax : Fin m → ℝ) (hh : ∀ u, h u ≤ hmax (σ u)) {c : ℝ} (hc0 : 0 ≤ c)
    (hc : ∀ s, k s = (Law.stratum σ s).card ∨ ((Law.stratum σ s).card : ℝ) * hmax s ≤ c * k s)
    {δ : ℝ} (hδ : 0 < δ) :
    IsHarmBound (Law.stratified σ k hk) h (ENNReal.ofReal δ) (c * Real.log δ⁻¹) := by
  intro B hB
  have hMN := card_filter_le_stratum σ B
  -- the risk budget: ∑_s k_s m_s / N_s ≤ ln(1/δ)
  have hS : ∑ s, ((k s : ℝ) * ((B.filter (σ · = s)).card : ℝ) / ((Law.stratum σ s).card : ℝ)) ≤
      Real.log δ⁻¹ := by
    have h1 := hB.trans (stratified_escape_le_exp σ k hk B)
    rw [ENNReal.ofReal_le_ofReal_iff (Real.exp_pos _).le] at h1
    have h2 := Real.log_le_log hδ h1
    rw [Real.log_exp] at h2
    rw [Real.log_inv]
    linarith
  -- a stratum proved whole holds no wrong unit of a set that escapes with positive probability
  have hcap : ∀ s, k s = (Law.stratum σ s).card → (B.filter (σ · = s)).card = 0 := by
    intro s hks
    by_contra hM
    have hle := hMN s
    have h0 : (Law.stratified σ k hk).escape B = 0 := by
      rw [Law.stratified_escape]
      refine prod_eq_zero (mem_univ s) ?_
      rw [hks, Nat.choose_eq_zero_of_lt (by omega)]
      simp
    rw [h0, nonpos_iff_eq_zero, ENNReal.ofReal_eq_zero] at hB
    exact absurd hB (not_le.2 hδ)
  calc ∑ u ∈ B, h u = ∑ s, ∑ u ∈ B.filter (σ · = s), h u := (sum_fiberwise B σ h).symm
    _ ≤ ∑ s, ((B.filter (σ · = s)).card : ℝ) * hmax s := by
        refine sum_le_sum fun s _ => ?_
        calc ∑ u ∈ B.filter (σ · = s), h u ≤ ∑ u ∈ B.filter (σ · = s), hmax s :=
              sum_le_sum fun u hu => (mem_filter.1 hu).2 ▸ hh u
          _ = ((B.filter (σ · = s)).card : ℝ) * hmax s := by rw [sum_const, nsmul_eq_mul]
    _ ≤ ∑ s, c * ((k s : ℝ) * ((B.filter (σ · = s)).card : ℝ) / ((Law.stratum σ s).card : ℝ)) := by
        refine sum_le_sum fun s _ => ?_
        rcases hc s with hks | hks
        · rw [hcap s hks]
          simp
        · rcases Nat.eq_zero_or_pos (Law.stratum σ s).card with hN | hN
          · have : (B.filter (σ · = s)).card = 0 := Nat.le_zero.1 (hN ▸ hMN s)
            rw [this]
            simp
          · have hNr : (0 : ℝ) < (Law.stratum σ s).card := by exact_mod_cast hN
            calc ((B.filter (σ · = s)).card : ℝ) * hmax s =
                  (((B.filter (σ · = s)).card : ℝ) / (Law.stratum σ s).card) *
                    (((Law.stratum σ s).card : ℝ) * hmax s) := by
                  field_simp
              _ ≤ (((B.filter (σ · = s)).card : ℝ) / (Law.stratum σ s).card) * (c * k s) :=
                  mul_le_mul_of_nonneg_left hks (by positivity)
              _ = c * ((k s : ℝ) * ((B.filter (σ · = s)).card : ℝ) / ((Law.stratum σ s).card : ℝ)) := by
                  ring
    _ = c * ∑ s, ((k s : ℝ) * ((B.filter (σ · = s)).card : ℝ) / ((Law.stratum σ s).card : ℝ)) :=
        (mul_sum _ _ _).symm
    _ ≤ c * Real.log δ⁻¹ := mul_le_mul_of_nonneg_left hS hc0

end PouwAccountable
