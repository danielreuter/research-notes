import Pouw.PearlC.Fp4FormingCode

namespace Pouw.PearlC.Fp4Dev.DNFReview

open Pouw.PearlC Pouw.PearlC.Fp4 Pouw.PearlC.Fp4Dev

/-- The proposed rule, as the README states it. -/
def RowAdmit4New (beta : (k : ℕ) → (Fin k → ℚ) → ℚ) (k : ℕ) (x : Fin k → ℚ) : Prop :=
  0 ≤ beta k x ∧ 8 ≤ (e4m3 (beta k x)).val ∧ (e4m3 (beta k x)).val < 128

/-- **The gap.** β = −1/4096 casts to the byte 0x80, which passes the staged D-NF (`8 ≤ val`), and M4's decode reads
it as the zero scale `(0, −9)`. -/
theorem gap_byte : (e4m3 (-1 / 4096 : ℚ)).val = 128 := by decide +kernel

theorem gap_admitted : RowAdmit4 (fun _ _ => (-1 / 4096 : ℚ)) 32 (fun _ => 0) := by
  show 8 ≤ (e4m3 (-1 / 4096 : ℚ)).val
  rw [gap_byte]; norm_num

theorem gap_zero_dyadic : scaleDyadic .ue4m3 (e4m3 (-1 / 4096 : ℚ)) = some (0, -9) := by
  have h : e4m3 (-1 / 4096 : ℚ) = ⟨128, by norm_num⟩ := Fin.ext gap_byte
  rw [h]; decide +kernel

theorem gap_zero_scale : scaleValue .ue4m3 (e4m3 (-1 / 4096 : ℚ)) = some 0 := by
  simp [scaleValue, gap_zero_dyadic]

theorem gap_rejected : ¬ RowAdmit4New (fun _ _ => (-1 / 4096 : ℚ)) 32 (fun _ => 0) := by
  rintro ⟨h, -, -⟩; norm_num at h

/-- β = −1: the byte 0xB8 passes the staged rule and would read as +1.0; the new rule rejects it. -/
theorem neg_one_byte : (e4m3 (-1 : ℚ)).val = 184 := by decide +kernel

/-- A byte at least 8 and at most 126 decodes to a normal scale, mantissa at least 8, so a positive value. -/
theorem normal_byte_dec : ∀ b : Fin 256, 8 ≤ b.val → b.val ≤ 126 →
    (scaleDyadic .ue4m3 b).isSome = true ∧ 8 ≤ ((scaleDyadic .ue4m3 b).map (·.1)).getD 0 := by decide +kernel

theorem normal_byte_scale (b : Fin 256) (h8 : 8 ≤ b.val) (h126 : b.val ≤ 126) :
    ∃ m e, scaleDyadic .ue4m3 b = some (m, e) ∧ 8 ≤ m := by
  obtain ⟨hs, hm⟩ := normal_byte_dec b h8 h126
  obtain ⟨⟨m, e⟩, hd⟩ := Option.isSome_iff_exists.mp hs
  exact ⟨m, e, hd, by simpa [hd] using hm⟩

/-- The cast never gives 0x7F or 0xFF: its magnitude is at most 126. -/
theorem e4m3_val_ne (β : ℚ) : (e4m3 β).val ≠ 127 ∧ (e4m3 β).val ≠ 255 := by
  have hm : (e4m3 |β|).val ≤ 126 := CodeProofs.e4m3_val_le (abs_nonneg β)
  have hv : (e4m3 |β|).val = e4m3Mag |β| % 256 := by
    simp [e4m3, abs_abs, not_lt.mpr (abs_nonneg β)]
  rw [hv] at hm
  have hβ : (e4m3 β).val = ((if β < 0 then 128 else 0) + e4m3Mag |β|) % 256 := rfl
  rw [hβ]
  generalize e4m3Mag |β| = t at hm ⊢
  split_ifs <;> omega

/-- **The closure.** Under the new rule the row's E scale is a normal UE4M3 byte, so its value is positive, not zero. -/
theorem closed (beta : (k : ℕ) → (Fin k → ℚ) → ℚ) (k : ℕ) (x : Fin k → ℚ) (h : RowAdmit4New beta k x) :
    ∃ m e, scaleDyadic .ue4m3 (e4m3 (beta k x)) = some (m, e) ∧ 8 ≤ m := by
  obtain ⟨-, h8, h128⟩ := h
  exact normal_byte_scale _ h8 (by have := (e4m3_val_ne (beta k x)).1; omega)

/-- Either clause alone closes it: (i) because the cast never gives 0x7F, (ii) by `e4m3_val_le`. -/
theorem closed_by_i (β : ℚ) (h8 : 8 ≤ (e4m3 β).val) (h128 : (e4m3 β).val < 128) :
    ∃ m e, scaleDyadic .ue4m3 (e4m3 β) = some (m, e) ∧ 8 ≤ m :=
  normal_byte_scale _ h8 (by have := (e4m3_val_ne β).1; omega)

theorem closed_by_ii (β : ℚ) (h0 : 0 ≤ β) (h8 : 8 ≤ (e4m3 β).val) :
    ∃ m e, scaleDyadic .ue4m3 (e4m3 β) = some (m, e) ∧ 8 ≤ m :=
  normal_byte_scale _ h8 (CodeProofs.e4m3_val_le h0)

/-- The new rule implies the staged one, so it only narrows admission, and `PinnedScales`' `bnn` already gives (ii). -/
theorem new_imp_old (beta : (k : ℕ) → (Fin k → ℚ) → ℚ) (k : ℕ) (x : Fin k → ℚ) (h : RowAdmit4New beta k x) :
    RowAdmit4 beta k x := h.2.1

theorem pinned_gives_new {alpha beta : (k : ℕ) → (Fin k → ℚ) → ℚ} (hp : CodeProofs.PinnedScales alpha beta)
    (k : ℕ) (x : Fin k → ℚ) (h8 : RowAdmit4 beta k x) : RowAdmit4New beta k x :=
  ⟨hp.bnn k x, h8, by have := CodeProofs.e4m3_val_le (hp.bnn k x); omega⟩

end Pouw.PearlC.Fp4Dev.DNFReview

#print axioms Pouw.PearlC.Fp4Dev.DNFReview.gap_byte
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.gap_admitted
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.gap_zero_dyadic
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.gap_zero_scale
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.gap_rejected
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.neg_one_byte
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.normal_byte_scale
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.e4m3_val_ne
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.closed
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.closed_by_i
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.closed_by_ii
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.new_imp_old
#print axioms Pouw.PearlC.Fp4Dev.DNFReview.pinned_gives_new
