import FlockSoundness.Game.Prob
import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Fintype.Fin

/-!
# Draw laws

A draw law is the verifier's coin space `Ω`, uniform, and the set of units each coin draws. What a
law gives a consumer is its escape function: the probability that a draw misses a set `B` of units.

* `escape L B`: the draw is disjoint from `B`;
* `miss L K`: the largest escape over sets of at least `K` units, the sampling term of the count
  curve `δ(K) = miss K + ε`;
* `incl L u`: the probability that `u` is drawn; a single unit escapes with `1 - incl L u`
  (`escape_singleton`), and a set escapes with at most that for each of its members
  (`escape_le_of_mem`).

`subset n k` is the uniform `k`-subset of `n` units, whose escape is hypergeometric:
`C(n - |B|, k) / C(n, k)` (`subset_escape`), so its count curve is `C(n - K, k) / C(n, k)`
(`subset_miss`).
-/

namespace FlockSoundness.Audit

open Game
open scoped ENNReal

/-- A draw law over `n` units: the verifier's uniform coins, and the unit set each draws. -/
structure Law (n : ℕ) where
  Ω : Type
  [fintype : Fintype Ω]
  [nonempty : Nonempty Ω]
  draw : Ω → Finset (Fin n)

attribute [instance] Law.fintype Law.nonempty

namespace Law

variable {n : ℕ}

/-- The probability that a draw misses every unit of `B`. -/
noncomputable def escape (L : Law n) (B : Finset (Fin n)) : ℝ≥0∞ :=
  prCoin fun ω => Disjoint (L.draw ω) B

/-- The count curve's sampling term: the largest escape over sets of at least `K` units. -/
noncomputable def miss (L : Law n) (K : ℕ) : ℝ≥0∞ :=
  ⨆ (B : Finset (Fin n)) (_ : K ≤ B.card), L.escape B

/-- The inclusion probability of a unit. -/
noncomputable def incl (L : Law n) (u : Fin n) : ℝ≥0∞ :=
  prCoin fun ω => u ∈ L.draw ω

theorem prCoin_not {C : Type} [Fintype C] [Nonempty C] (p : C → Prop) :
    prCoin (fun c => ¬ p c) = 1 - prCoin p := by
  classical
  have h : prCoin p + prCoin (fun c => ¬ p c) = 1 := by
    unfold prCoin
    rw [← avg_add]
    refine (congrArg avg (funext fun c => ?_)).trans (avg_const 1)
    by_cases hc : p c <;> simp [hc]
  have hne : prCoin p ≠ ∞ := ne_top_of_le_ne_top ENNReal.one_ne_top (h ▸ le_self_add)
  exact ENNReal.eq_sub_of_add_eq hne (by rw [add_comm]; exact h)

theorem escape_le_one (L : Law n) (B : Finset (Fin n)) : L.escape B ≤ 1 := by
  classical
  unfold escape prCoin
  refine (avg_mono fun ω => ?_).trans (avg_const (C := L.Ω) 1).le
  split_ifs <;> simp

/-- Missing more units is less likely. -/
theorem escape_anti (L : Law n) {B B' : Finset (Fin n)} (h : B ⊆ B') : L.escape B' ≤ L.escape B :=
  prCoin_mono fun _ hd => hd.mono_right h

theorem escape_empty (L : Law n) : L.escape ∅ = 1 := by
  unfold escape prCoin
  simp only [Finset.disjoint_empty_right, ite_true]
  exact avg_const 1

/-- A single unit escapes exactly when it is not drawn. -/
theorem escape_singleton (L : Law n) (u : Fin n) : L.escape {u} = 1 - L.incl u := by
  unfold escape incl
  rw [← prCoin_not]
  exact congrArg prCoin (funext fun ω => propext Finset.disjoint_singleton_right)

/-- A set escapes with at most the escape of any one of its units. -/
theorem escape_le_of_mem (L : Law n) {B : Finset (Fin n)} {u : Fin n} (hu : u ∈ B) :
    L.escape B ≤ 1 - L.incl u :=
  (L.escape_anti (Finset.singleton_subset_iff.2 hu)).trans (L.escape_singleton u).le

theorem escape_le_miss (L : Law n) {K : ℕ} {B : Finset (Fin n)} (h : K ≤ B.card) :
    L.escape B ≤ L.miss K :=
  le_iSup₂_of_le (f := fun (B : Finset (Fin n)) (_ : K ≤ B.card) => L.escape B) B h le_rfl

theorem miss_le_one (L : Law n) (K : ℕ) : L.miss K ≤ 1 :=
  iSup₂_le fun B _ => L.escape_le_one B

/-- The count curve falls as `K` grows. -/
theorem miss_anti (L : Law n) {K K' : ℕ} (h : K ≤ K') : L.miss K' ≤ L.miss K :=
  iSup₂_le fun _ hB => L.escape_le_miss (h.trans hB)

/-! ## The uniform `k`-subset -/

/-- The uniform `k`-subset of `n` units. -/
def subset (n k : ℕ) (hk : k ≤ n) : Law n where
  Ω := {S : Finset (Fin n) // S.card = k}
  nonempty := by
    obtain ⟨S, -, hS⟩ := Finset.exists_subset_card_eq (s := (Finset.univ : Finset (Fin n)))
      (by simpa using hk)
    exact ⟨⟨S, hS⟩⟩
  draw := Subtype.val

theorem card_disjoint_subsets (k : ℕ) (B : Finset (Fin n)) :
    (Finset.univ.filter fun S : {S : Finset (Fin n) // S.card = k} => Disjoint S.1 B).card =
      (n - B.card).choose k := by
  classical
  rw [← Finset.card_map ⟨Subtype.val, Subtype.val_injective⟩]
  have : (Finset.univ.filter fun S : {S : Finset (Fin n) // S.card = k} => Disjoint S.1 B).map
      ⟨Subtype.val, Subtype.val_injective⟩ = Bᶜ.powersetCard k := by
    ext S
    simp only [Finset.mem_map, Finset.mem_filter, Finset.mem_univ, true_and,
      Function.Embedding.coeFn_mk, Finset.mem_powersetCard, Finset.subset_compl_iff_disjoint_right]
    constructor
    · rintro ⟨S', hS', rfl⟩
      exact ⟨hS', S'.2⟩
    · rintro ⟨hS, hk⟩
      exact ⟨⟨S, hk⟩, hS, rfl⟩
  rw [this, Finset.card_powersetCard, Finset.card_compl, Fintype.card_fin]

/-- **The hypergeometric escape.** A uniform `k`-subset misses `B` with probability
`C(n - |B|, k) / C(n, k)`. -/
theorem subset_escape {k : ℕ} (hk : k ≤ n) (B : Finset (Fin n)) :
    (subset n k hk).escape B = ((n - B.card).choose k : ℝ≥0∞) / (n.choose k : ℝ≥0∞) := by
  classical
  unfold escape
  rw [prCoin_eq_card]
  congr 1
  · exact congrArg _ (card_disjoint_subsets k B)
  · exact congrArg _ ((Fintype.card_finset_len k).trans (by rw [Fintype.card_fin]))

/-- **The uniform `k`-subset's count curve**, exactly: `miss K = C(n - K, k) / C(n, k)`. -/
theorem subset_miss {k : ℕ} (hk : k ≤ n) {K : ℕ} (hK : K ≤ n) :
    (subset n k hk).miss K = ((n - K).choose k : ℝ≥0∞) / (n.choose k : ℝ≥0∞) := by
  refine le_antisymm (iSup₂_le fun B hB => ?_) ?_
  · rw [subset_escape]
    gcongr
  · obtain ⟨B, -, hB⟩ := Finset.exists_subset_card_eq (s := (Finset.univ : Finset (Fin n)))
      (by simpa using hK)
    have := (subset n k hk).escape_le_miss (K := K) hB.ge
    rwa [subset_escape, hB] at this

/-- A uniform `k`-subset of `n` misses one given unit with probability `(n − k)/n`. -/
theorem choose_ratio {k : ℕ} (hk : k ≤ n) (hn : 1 ≤ n) :
    ((n - 1).choose k : ℝ≥0∞) / (n.choose k : ℝ≥0∞) = ((n - k : ℕ) : ℝ≥0∞) / (n : ℝ≥0∞) := by
  rw [ENNReal.div_eq_div_iff (by exact_mod_cast (show n ≠ 0 by omega)) (ENNReal.natCast_ne_top _)
    (by exact_mod_cast (Nat.choose_pos hk).ne') (ENNReal.natCast_ne_top _)]
  have := Nat.choose_mul_succ_eq (n - 1) k
  rw [show n - 1 + 1 = n by omega] at this
  rw [mul_comm]
  exact_mod_cast this

/-- `C(n − b, k)/C(n, k) ≤ ((n − k)/n)^b`, cross-multiplied. -/
theorem choose_sub_mul_pow_le (n k : ℕ) : ∀ b, b ≤ n →
    (n - b).choose k * n ^ b ≤ n.choose k * (n - k) ^ b := by
  intro b
  induction b with
  | zero => intro _; simp
  | succ b ih =>
      intro hb
      set m := n - b with hm
      have hm1 : 1 ≤ m := by omega
      have hid : (m - 1).choose k * m = m.choose k * (m - k) := by
        have := Nat.choose_mul_succ_eq (m - 1) k
        rwa [show m - 1 + 1 = m by omega] at this
      have hmk : (m - k) * n ≤ (n - k) * m := by
        rcases le_or_gt m k with h | h
        · rw [Nat.sub_eq_zero_of_le h, zero_mul]; exact Nat.zero_le _
        · have hmn : m ≤ n := by omega
          zify [h.le, (h.trans_le hmn).le]
          nlinarith
      have hih := ih (by omega)
      rw [show n - (b + 1) = m - 1 by omega]
      refine Nat.le_of_mul_le_mul_right ?_ (show 0 < m by omega)
      calc (m - 1).choose k * n ^ (b + 1) * m = (m - 1).choose k * m * n ^ b * n := by ring
        _ = m.choose k * n ^ b * ((m - k) * n) := by rw [hid]; ring
        _ ≤ n.choose k * (n - k) ^ b * ((n - k) * m) := Nat.mul_le_mul hih hmk
        _ = n.choose k * (n - k) ^ (b + 1) * m := by ring

/-- **The product bound for the uniform subset**: a set escapes with at most the product of its
units' miss probabilities, so inclusion probabilities alone give a valid bound. -/
theorem subset_escape_le_prod {k : ℕ} (hk : k ≤ n) (hn : 1 ≤ n) (B : Finset (Fin n)) :
    (subset n k hk).escape B ≤ ∏ u ∈ B, (1 - (subset n k hk).incl u) := by
  have hu : ∀ u, 1 - (subset n k hk).incl u = ((n - k : ℕ) : ℝ≥0∞) / (n : ℝ≥0∞) := by
    intro u
    rw [← escape_singleton, subset_escape, Finset.card_singleton, choose_ratio hk hn]
  rw [Finset.prod_congr rfl fun u _ => hu u, Finset.prod_const, subset_escape, div_eq_mul_inv
    (((n - k : ℕ) : ℝ≥0∞)), mul_pow, ← ENNReal.inv_pow, ← div_eq_mul_inv]
  have hc : (n.choose k : ℝ≥0∞) ≠ 0 := by exact_mod_cast (Nat.choose_pos hk).ne'
  have hp : ((n : ℝ≥0∞)) ^ B.card ≠ 0 := pow_ne_zero _ (by exact_mod_cast (show n ≠ 0 by omega))
  rw [ENNReal.div_le_iff hc (ENNReal.natCast_ne_top _), mul_comm, ← mul_div_assoc,
    ENNReal.le_div_iff_mul_le (Or.inl hp) (Or.inl (ENNReal.pow_ne_top (ENNReal.natCast_ne_top _)))]
  have := choose_sub_mul_pow_le n k B.card (by simpa using Finset.card_le_univ B)
  exact_mod_cast this

/-- **The demo's curve** (`docs/audit-protocols.md` §0.2): with 1,024 heads and 16 drawn, 590 or
more wrong heads escape with probability at most `2^-20`. -/
theorem demo_count_590 : (subset 1024 16 (by norm_num)).miss 590 ≤ ((2 : ℝ≥0∞) ^ 20)⁻¹ := by
  rw [subset_miss _ (by norm_num), ENNReal.div_le_iff (by exact_mod_cast (Nat.choose_pos
    (by norm_num : 16 ≤ 1024)).ne') (ENNReal.natCast_ne_top _), ← ENNReal.div_eq_inv_mul,
    ENNReal.le_div_iff_mul_le (Or.inl (by norm_num)) (Or.inl (by norm_num))]
  have h : (1024 - 590).choose 16 * 2 ^ 20 ≤ (1024).choose 16 := by
    rw [Nat.choose_eq_descFactorial_div_factorial, Nat.choose_eq_descFactorial_div_factorial]
    decide +kernel
  exact_mod_cast h

/-! ## Bernoulli draws -/

/-- Each unit drawn independently with probability `num / den`. -/
abbrev bernoulli (n num den : ℕ) [NeZero den] : Law n where
  Ω := Fin n → Fin den
  draw ω := Finset.univ.filter fun u => (ω u).val < num

/-- One Bernoulli coordinate's average of `a` when drawn and `1` when not. -/
noncomputable def bernFactor (num den : ℕ) (a : ℝ≥0∞) : ℝ≥0∞ :=
  ((num : ℝ≥0∞) * a + ((den - num : ℕ) : ℝ≥0∞)) / den

theorem avg_bern {num den : ℕ} [NeZero den] (h : num ≤ den) (a : ℝ≥0∞) :
    avg (fun x : Fin den => if x.val < num then a else 1) = bernFactor num den a := by
  classical
  unfold avg bernFactor
  rw [← Finset.mul_sum, Finset.sum_ite, Finset.sum_const, Finset.sum_const, Fintype.card_fin,
    ENNReal.div_eq_inv_mul]
  congr 1
  have h1 : (Finset.univ.filter fun x : Fin den => x.val < num).card = num := by
    rw [Fin.card_filter_val_lt]; omega
  have h2 : (Finset.univ.filter fun x : Fin den => ¬ x.val < num).card = den - num := by
    have := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset (Fin den)))
      (fun x : Fin den => x.val < num)
    rw [Finset.card_univ, Fintype.card_fin, h1] at this
    omega
  rw [h1, h2, nsmul_eq_mul, nsmul_eq_mul, mul_one]

/-- **Independent inclusions.** Under a Bernoulli draw, the mean of a product over the drawn units of
`B` is the product over `B` of each unit's Bernoulli factor. -/
theorem bernoulli_avg_prod {num den : ℕ} [NeZero den] (h : num ≤ den) (f : Fin n → ℝ≥0∞)
    (B : Finset (Fin n)) :
    avg (fun ω : (bernoulli n num den).Ω => ∏ u ∈ B ∩ (bernoulli n num den).draw ω, f u) =
      ∏ u ∈ B, bernFactor num den (f u) := by
  classical
  have key : ∀ ω : (bernoulli n num den).Ω, ∏ u ∈ B ∩ (bernoulli n num den).draw ω, f u =
      ∏ u, (if u ∈ B then (if (ω u).val < num then f u else 1) else 1) := by
    intro ω
    have hB : B ∩ (bernoulli n num den).draw ω = B.filter fun u => (ω u).val < num := by
      ext u; simp
    rw [hB, Finset.prod_filter, Finset.prod_ite_mem, Finset.univ_inter]
  simp only [key]
  rw [avg_pi_prod (Ω := fun _ : Fin n => Fin den)
    (fun u (x : Fin den) => if u ∈ B then (if x.val < num then f u else 1) else 1)]
  rw [← Finset.prod_filter_mul_prod_filter_not Finset.univ (· ∈ B)]
  have h1 : ∏ u ∈ Finset.univ.filter (· ∉ B),
      avg (fun x : Fin den => if u ∈ B then (if x.val < num then f u else 1) else 1) = 1 :=
    Finset.prod_eq_one fun u hu => by
      rw [Finset.mem_filter] at hu
      simp only [hu.2, ite_false]
      exact avg_const 1
  rw [h1, mul_one, Finset.filter_mem_eq_inter, Finset.univ_inter]
  refine Finset.prod_congr rfl fun u hu => ?_
  simp only [hu, ite_true]
  exact avg_bern h (f u)

/-- **The Bernoulli escape**: `((den − num)/den)^|B|`. -/
theorem bernoulli_escape {num den : ℕ} [NeZero den] (h : num ≤ den) (B : Finset (Fin n)) :
    (bernoulli n num den).escape B = bernFactor num den 0 ^ B.card := by
  classical
  rw [← Finset.prod_const, ← bernoulli_avg_prod h (fun _ => 0) B, escape, ← avg_ite_eq_prCoin]
  refine congrArg avg (funext fun ω => ?_)
  rw [Finset.prod_const, Finset.inter_comm]
  by_cases hd : Disjoint ((bernoulli n num den).draw ω) B
  · simp [hd, Finset.disjoint_iff_inter_eq_empty.1 hd]
  · have : ((bernoulli n num den).draw ω ∩ B).card ≠ 0 := by
      rw [Ne, Finset.card_eq_zero, ← Finset.disjoint_iff_inter_eq_empty]; exact hd
    simp [hd, zero_pow this]

/-! ## The uniform subset is optimal

Averaging `escape B` over a uniformly random `K`-set `B` gives `E[C(n - |S|, K)] / C(n, K)` for any
law (`avg_escape_subsets`). The map `s ↦ C(n - s, K)` is convex on `ℕ` (its drops fall,
`drop_anti`), so it lies above its supporting line at `k` (`choose_support`), and Jensen's
inequality at a mean of `k` gives `C(n - k, K)`, which is the uniform `k`-subset's value. -/

theorem avg_comm {C D : Type} [Fintype C] [Fintype D] (f : C → D → ℝ≥0∞) :
    avg (fun c => avg fun d => f c d) = avg fun d => avg fun c => f c d := by
  unfold avg
  simp only [Finset.mul_sum]
  rw [Finset.sum_comm]
  exact Finset.sum_congr rfl fun d _ => Finset.sum_congr rfl fun c _ => by ring

theorem avg_sum {C ι : Type} [Fintype C] (s : Finset ι) (f : ι → C → ℝ≥0∞) :
    avg (fun c => ∑ i ∈ s, f i c) = ∑ i ∈ s, avg (f i) := by
  unfold avg
  simp only [Finset.mul_sum]
  exact Finset.sum_comm

/-- A law's mean draw size is the sum of its inclusion probabilities. -/
theorem avg_card (L : Law n) : avg (fun ω => ((L.draw ω).card : ℝ≥0∞)) = ∑ u, L.incl u := by
  classical
  have h : ∀ ω, ((L.draw ω).card : ℝ≥0∞) = ∑ u, if u ∈ L.draw ω then (1 : ℝ≥0∞) else 0 := by
    intro ω
    rw [Finset.sum_boole, Finset.filter_mem_eq_inter, Finset.univ_inter]
  simp only [h]
  rw [avg_sum]
  exact Finset.sum_congr rfl fun u _ => avg_ite_eq_prCoin _

/-- **Averaging over `K`-sets.** For any law, the escape of a uniformly random `K`-set is the mean
of `C(n - |S|, K) / C(n, K)` over the draw `S`. -/
theorem avg_escape_subsets (M : Law n) {K : ℕ} (hK : K ≤ n) :
    avg (fun B : (subset n K hK).Ω => M.escape B.1) =
      avg fun ω => (((n - (M.draw ω).card).choose K : ℕ) : ℝ≥0∞) / (n.choose K : ℝ≥0∞) := by
  classical
  unfold escape prCoin
  rw [avg_comm]
  refine congrArg avg (funext fun ω => ?_)
  rw [← subset_escape hK (M.draw ω)]
  unfold escape prCoin
  refine congrArg avg (funext fun B => ?_)
  by_cases h : Disjoint (M.draw ω) B.1
  · simp only [subset, h, h.symm, ite_true]
  · have h' : ¬ Disjoint B.1 (M.draw ω) := fun h' => h h'.symm
    simp only [subset, h, h', ite_false]

/-- The drop of `s ↦ C(n - s, K)` at `s`. -/
def drop (n K s : ℕ) : ℕ := (n - s).choose K - (n - (s + 1)).choose K

theorem choose_eq_add_drop (n K s : ℕ) :
    (n - s).choose K = (n - (s + 1)).choose K + drop n K s := by
  have : (n - (s + 1)).choose K ≤ (n - s).choose K := Nat.choose_le_choose K (by omega)
  unfold drop
  omega

/-- **`s ↦ C(n - s, K)` is convex**: its drops fall. -/
theorem drop_anti (n K s : ℕ) : drop n K (s + 1) ≤ drop n K s := by
  rcases K with _ | K
  · simp [drop]
  · by_cases hs : s + 1 < n
    · have h1 : drop n (K + 1) s = (n - (s + 1)).choose K := by
        unfold drop
        obtain ⟨m, hm⟩ : ∃ m, n - s = m + 1 := ⟨n - s - 1, by omega⟩
        rw [hm, show n - (s + 1) = m by omega, Nat.choose_succ_succ']
        omega
      have h2 : drop n (K + 1) (s + 1) = (n - (s + 1 + 1)).choose K := by
        unfold drop
        obtain ⟨m, hm⟩ : ∃ m, n - (s + 1) = m + 1 := ⟨n - s - 2, by omega⟩
        rw [hm, show n - (s + 1 + 1) = m by omega, Nat.choose_succ_succ']
        omega
      rw [h1, h2]
      exact Nat.choose_le_choose K (by omega)
    · have : drop n (K + 1) (s + 1) = 0 := by
        unfold drop
        rw [show n - (s + 1) = 0 by omega, show n - (s + 1 + 1) = 0 by omega]
        simp
      rw [this]
      exact Nat.zero_le _

theorem drop_antitone (n K : ℕ) : Antitone (drop n K) :=
  antitone_nat_of_succ_le (drop_anti n K)

/-- **The supporting line at `k`.** -/
theorem choose_support (n K k s : ℕ) :
    (n - k).choose K + k * drop n K k ≤ (n - s).choose K + s * drop n K k := by
  set D := drop n K k
  rcases le_total k s with h | h
  · obtain ⟨t, rfl⟩ := Nat.exists_eq_add_of_le h
    induction t with
    | zero => simp
    | succ t ih =>
        have e := choose_eq_add_drop n K (k + t)
        have hd : drop n K (k + t) ≤ D := drop_antitone n K (by omega)
        have hm : (k + (t + 1)) * D = (k + t) * D + D := by ring
        rw [show k + (t + 1) = k + t + 1 by omega] at hm ⊢
        rw [hm]
        have := ih (by omega)
        omega
  · have key : ∀ t j, j + t = k → (n - k).choose K + k * D ≤ (n - j).choose K + j * D := by
      intro t
      induction t with
      | zero => intro j hj; rw [show j = k by omega]
      | succ t ih =>
          intro j hj
          have e := choose_eq_add_drop n K j
          have hd : D ≤ drop n K j := drop_antitone n K (by omega)
          have hm : (j + 1) * D = j * D + D := by ring
          have := ih (j + 1) (by omega)
          rw [hm] at this
          omega
    exact key (k - s) s (by omega)

/-- **Uniform is optimal.** No law that proves `k` units on average has a smaller count curve than
the uniform `k`-subset, at any `K`. -/
theorem subset_minimax (L : Law n) {k : ℕ} (hk : k ≤ n) (hmean : ∑ u, L.incl u = k) {K : ℕ}
    (hK : K ≤ n) : (subset n k hk).miss K ≤ L.miss K := by
  classical
  set D := drop n K k
  have hc : (n.choose K : ℝ≥0∞) ≠ 0 := by exact_mod_cast (Nat.choose_pos hK).ne'
  -- the uniform subset's count curve, read through the averaging identity
  have hU : (subset n k hk).miss K = (((n - k).choose K : ℕ) : ℝ≥0∞) / (n.choose K : ℝ≥0∞) := by
    have h1 : avg (fun B : (subset n K hK).Ω => (subset n k hk).escape B.1) = (subset n k hk).miss K := by
      rw [subset_miss hk hK]
      refine (congrArg avg (funext fun B => ?_)).trans (avg_const _)
      rw [subset_escape, B.2]
    rw [← h1, avg_escape_subsets]
    refine (congrArg avg (funext fun ω => ?_)).trans (avg_const _)
    show _ = (((n - k).choose K : ℕ) : ℝ≥0∞) / _
    have : ((subset n k hk).draw ω).card = k := ω.2
    rw [this]
  -- Jensen at the mean `k`, through the supporting line
  have hJ : (((n - k).choose K : ℕ) : ℝ≥0∞) ≤ avg fun ω => (((n - (L.draw ω).card).choose K : ℕ) : ℝ≥0∞) := by
    have hkD : (k : ℝ≥0∞) * D ≠ ⊤ := ENNReal.mul_ne_top (ENNReal.natCast_ne_top _) (ENNReal.natCast_ne_top _)
    refine ENNReal.le_of_add_le_add_right hkD ?_
    calc (((n - k).choose K : ℕ) : ℝ≥0∞) + k * D
        = avg fun _ : L.Ω => (((n - k).choose K + k * D : ℕ) : ℝ≥0∞) := by
          rw [avg_const]; push_cast; ring
      _ ≤ avg fun ω => (((n - (L.draw ω).card).choose K + (L.draw ω).card * D : ℕ) : ℝ≥0∞) :=
          avg_mono fun ω => by exact_mod_cast choose_support n K k (L.draw ω).card
      _ = (avg fun ω => (((n - (L.draw ω).card).choose K : ℕ) : ℝ≥0∞)) +
            (avg fun ω => ((L.draw ω).card : ℝ≥0∞)) * D := by
          push_cast
          rw [avg_add, avg_mul_const]
      _ = _ := by rw [avg_card, hmean]
  -- the average over `K`-sets is at most the maximum
  have hmax : avg (fun B : (subset n K hK).Ω => L.escape B.1) ≤ L.miss K :=
    (avg_mono fun B => L.escape_le_miss B.2.ge).trans (avg_const _).le
  calc (subset n k hk).miss K = (((n - k).choose K : ℕ) : ℝ≥0∞) / (n.choose K : ℝ≥0∞) := hU
    _ ≤ (avg fun ω => (((n - (L.draw ω).card).choose K : ℕ) : ℝ≥0∞)) / (n.choose K : ℝ≥0∞) := by
        gcongr
    _ = avg fun ω => (((n - (L.draw ω).card).choose K : ℕ) : ℝ≥0∞) / (n.choose K : ℝ≥0∞) := by
        simp only [div_eq_mul_inv]
        rw [avg_mul_const]
    _ = avg (fun B : (subset n K hK).Ω => L.escape B.1) := (avg_escape_subsets L hK).symm
    _ ≤ L.miss K := hmax

end Law

end FlockSoundness.Audit
