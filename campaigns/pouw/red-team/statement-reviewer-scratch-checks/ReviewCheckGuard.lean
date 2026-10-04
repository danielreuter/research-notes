import Pouw.PearlC.DeviceV2Hot

namespace Pouw.PearlC

/-- The unit-level guard: a starts' source may be changed arbitrarily on every unit whose activations fail
`OperandOK` somewhere, and `HotStartsSized` still holds. -/
theorem hotStartsSized_offOperand {Q R S : Type} (h : HotSizing) (sem : PearlCSem Q R S) (hot : HotSem Q R S)
    (starts' : (Q → R) → S → (U : Workload) → (u : ℕ) → Codes → Fin (U.layout.shape u).m → ℕ)
    (hagree : ∀ H s U u act i, sem.OperandOK (U.layout.shape u).m (U.layout.shape u).k act →
      starts' H s U u act i = hot.starts H s U u act i)
    (hS : HotStartsSized h sem hot) : HotStartsSized h sem { hot with starts := starts' } := by
  intro H s U u act i
  have := hS H s U u act i
  intro sh hA hW
  have h1 := this hA hW
  simp only [hagree H s U u act i hA]
  exact h1

/-- And a row can pass `RowOK` (so `passRows` credits it per tile) in a unit that fails `OperandOK`. -/
example {Q R S : Type} (sem : PearlCSem Q R S) (p q : ℕ) (W : Codes) (i : ℕ)
    (hrow : sem.RowOK p q W i) (hbad : ¬ sem.RowOK p q W (i + 1)) (hi1 : i + 1 < p) :
    sem.RowOK p q W i ∧ ¬ sem.OperandOK p q W := by
  refine ⟨hrow, fun hop => hbad ⟨fun l hl => hop.1 (i + 1) hi1 l hl, fun h => ?_⟩⟩
  exact hop.2 ⟨i + 1, h⟩

end Pouw.PearlC

#print axioms Pouw.PearlC.hotStartsSized_offOperand
