import Pouw.PearlC.V2HotCharged
import Pouw.PearlC.HotGamma

open Pouw.PearlC Pouw.PearlC.Assumptions

example : deltaHot sh8192 = some (2003 / 640000) := by
  rw [deltaHot_of_le sh8192 (by norm_num [sh8192]) (by norm_num [sh8192])]; norm_num [sh8192]
example : deltaHot ⟨8192, 8192, 16384⟩ = none := deltaHot_eq_none _ (Or.inl (by norm_num))
example : deltaHot ⟨8192, 8192, 65536⟩ = none := deltaHot_eq_none _ (Or.inl (by norm_num))
example : deltaHot sh16384 = none := deltaHot_eq_none _ (Or.inl (by norm_num [sh16384]))
example (m : ℕ) : deltaHot ⟨m, 8192, 8193⟩ = none := deltaHot_eq_none _ (Or.inl (by norm_num))
example (m : ℕ) : deltaHot ⟨m, 8193, 8192⟩ = none := deltaHot_eq_none _ (Or.inr (by norm_num))
