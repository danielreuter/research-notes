import Pouw.PearlC.DeviceV2Hot

namespace Pouw.PearlC

/-- The proposed per-row guard: the row's own `RowOK` (what `passRows` credits), and the weights' `OperandOK`. -/
def HotStartsSizedRow {Q R S : Type} (h : HotSizing) (sem : PearlCSem Q R S) (hot : HotSem Q R S) : Prop :=
  ∀ (H : Q → R) (s : S) (U : Workload) (u : ℕ) (act : Codes) (i : Fin (U.layout.shape u).m),
    let sh := U.layout.shape u
    sem.RowOK sh.m sh.k act i → sem.OperandOK sh.n sh.k (U.weight (U.layout.wid u)) →
    let e : ℤ := (((hot.starts H s U u act i) >>> 23) % 256 : ℕ) - 127
    let t := hot.rowScale sh.k (wordsVal sh.m sh.k act i)
    let v := 512 * h.colMeanSq (sem.unitChain H s U u act).2 * t ^ 2
    (4 : ℚ) ^ e ≤ v ∧ v < 4 ^ (e + 1)

/-- The staged guard is exactly the per-row form asked for at 16:15Z. -/
theorem hotStartsSized_eq_row {Q R S : Type} (h : HotSizing) (sem : PearlCSem Q R S) (hot : HotSem Q R S) :
    HotStartsSized h sem hot ↔ HotStartsSizedRow h sem hot := Iff.rfl

end Pouw.PearlC

#print axioms Pouw.PearlC.hotStartsSized_eq_row
