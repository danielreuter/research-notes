import Pouw.TileBound.WinogradStrassen

namespace Pouw.TileBound

/-- The 10:35Z signature follows from the strengthened one, at NVFP4's blocks. -/
example (m n : ℕ) (h : 7 * (m + n) < m * n) :
    ∃ P : SlotProg ℚ (2 * m) 4 (2 * n) (Fin 7 × ((Fin m × Fin n) ⊕ (Fin m ⊕ Fin n))),
      P.toQuadProg.CrossOn (fun _ => True) (fun _ => True) ∧
      P.Representable (nvfp4X (2 * m) 4) (nvfp4Y 4 (2 * n)) ∧ (∀ t, P.fmt t = .int8) ∧
      P.cost < price .fp4 * nLive (m := 2 * m) (k := 4) (n := 2 * n) (fun _ => True) (fun _ => True) := by
  obtain ⟨P, h1, h2, h3, h4⟩ := int8_winograd_strassen_beats m n h
  exact ⟨P, h1, h2 _ _, h3, h4⟩

/-- And at single-entry blocks, the finest partition, so the pin bounds each input's entries by int8's 10. -/
example : ∃ P : SlotProg ℚ (2 * 16) 4 (2 * 16) (Fin 7 × ((Fin 16 × Fin 16) ⊕ (Fin 16 ⊕ Fin 16))),
    P.Representable (⟨id, fun _ _ h => by rw [id, id] at h; rw [h]⟩ : XBlocks (2 * 16) 4 (Fin (2 * 16) × Fin 4))
      (⟨id, fun _ _ h => by rw [id, id] at h; rw [h]⟩ : YBlocks 4 (2 * 16) (Fin 4 × Fin (2 * 16))) := by
  obtain ⟨P, _, h2, _, _⟩ := int8_winograd_strassen_beats_32
  exact ⟨P, h2 _ _⟩

end Pouw.TileBound
