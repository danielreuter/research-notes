import Pouw.TileBound.Proofs

/-! Statement-review scratch check (bc-22298e90): `tile_cost_ge_of_gates`'s gate hypothesis is satisfiable for the
honest one-gate program, with one live pair, and `realizesAt` doesn't force the forms to zero. Not part of the package. -/

namespace Pouw.TileBound

open Finset Pouw.PearlC.Fp4 Pouw.Fp8Atom

def gateP : Gate where
  p i l := if i.val = 0 ∧ l.val = 0 then 2 else 0
  ps _ _ := 0x38
  q _ _ := 0
  qs _ _ := 0x38
  acc _ _ := 0

def gateQ : Gate where
  p _ _ := 0
  ps _ _ := 0x38
  q l j := if l.val = 0 ∧ j.val = 0 then 2 else 0
  qs _ _ := 0x38
  acc _ _ := 0

theorem gateP_exact : gateP.Exact := by unfold Gate.Exact; decide +kernel
theorem gateQ_exact : gateQ.Exact := by unfold Gate.Exact; decide +kernel

theorem gateP_p : ∀ i l, elemValue (gateP.p i l) (gateP.ps i (scaleIdx l)) =
    if (i, l) = ((0 : Fin 16), (0 : Fin 64)) then 1 else 0 := by decide +kernel
theorem gateP_q : ∀ l j, elemValue (gateP.q l j) (gateP.qs j (scaleIdx l)) = 0 := by decide +kernel
theorem gateQ_p : ∀ i l, elemValue (gateQ.p i l) (gateQ.ps i (scaleIdx l)) = 0 := by decide +kernel
theorem gateQ_q : ∀ l j, elemValue (gateQ.q l j) (gateQ.qs j (scaleIdx l)) =
    if (l, j) = ((0 : Fin 64), (0 : Fin 8)) then 1 else 0 := by decide +kernel

theorem honest_eval (X : Fin 16 × Fin 64 → ℚ) (Y : Fin 64 × Fin 8 → ℚ) (o : Fin 16 × Fin 8) :
    oneGateProg.toBilin.toQuad.eval X Y o = matMul X Y o := by
  classical
  have hsX : ∀ a : Fin 16 × Fin 64, ∑ e, unitForm (K := ℚ) a e * X e = X a := fun a => by simp [unitForm]
  have hsY : ∀ a : Fin 64 × Fin 8, ∑ e, unitForm (K := ℚ) a e * Y e = Y a := fun a => by simp [unitForm]
  simp only [QuadProg.eval, BilinProg.toQuad, TileProg.toBilin, oneGateProg, Pi.zero_apply, zero_mul,
    Finset.sum_const_zero, add_zero, zero_add, hsX, hsY, matMul, Fintype.sum_prod_type, Fintype.sum_unique]
  rw [Finset.sum_eq_single o.1]
  · refine Finset.sum_congr rfl fun l _ => ?_
    rw [Finset.sum_eq_single o.2]
    · simp [unitForm]
    · intro j _ hj
      simp [unitForm, Prod.ext_iff, hj, Ne.symm hj]
    · simp
  · intro i _ hi
    refine Finset.sum_eq_zero fun l _ => Finset.sum_eq_zero fun j _ => ?_
    simp [unitForm, Prod.ext_iff, hi, Ne.symm hi]
  · simp

/-- The chain's hypothesis holds for the honest one-gate program on the live pair `x = y = (0, 0)`. -/
theorem gates_hyp_satisfiable :
    ∀ x, (x = ((0 : Fin 16), (0 : Fin 64))) → ∀ y, (y = ((0 : Fin 64), (0 : Fin 8))) →
      ∃ g11 g10 g01 : Fin 1 → Gate,
        oneGateProg.RealizesAt g11 (unitForm x) (unitForm y) ∧ oneGateProg.RealizesAt g10 (unitForm x) 0 ∧
          oneGateProg.RealizesAt g01 0 (unitForm y) ∧
        ∀ o, oneGateProg.outAt g11 o = matMul (unitForm x) (unitForm y) o ∧
          oneGateProg.outAt g10 o = matMul (unitForm x) 0 o ∧
          oneGateProg.outAt g01 o = matMul 0 (unitForm y) o := by
  rintro x rfl y rfl
  have h11 : oneGateProg.RealizesAt (fun _ => oneGate) (unitForm (0, 0)) (unitForm (0, 0)) := oneGateProg_realizesAt
  have h10 : oneGateProg.RealizesAt (fun _ => gateP) (unitForm (0, 0)) 0 := by
    intro _
    refine ⟨gateP_exact, fun _ _ => rfl, fun i l => ?_, fun l j => ?_⟩
    · rw [gateP_p]; simp only [oneGateProg, sum_unitForm_mul]
    · rw [gateP_q]; simp
  have h01 : oneGateProg.RealizesAt (fun _ => gateQ) 0 (unitForm (0, 0)) := by
    intro _
    refine ⟨gateQ_exact, fun _ _ => rfl, fun i l => ?_, fun l j => ?_⟩
    · rw [gateQ_p]; simp
    · rw [gateQ_q]; simp only [oneGateProg, sum_unitForm_mul]
  refine ⟨_, _, _, h11, h10, h01, fun o => ⟨?_, ?_, ?_⟩⟩
  · rw [realizes_out_at _ _ _ _ h11, honest_eval]
  · rw [realizes_out_at _ _ _ _ h10, honest_eval]
  · rw [realizes_out_at _ _ _ _ h01, honest_eval]

/-- So the chain applies to it, and its bound is met: one live product at 1/2 against one firing's 4,096. -/
example : price .fp4 * nLive (m := 16) (k := 64) (n := 8) (· = ((0 : Fin 16), (0 : Fin 64)))
    (· = ((0 : Fin 64), (0 : Fin 8))) ≤ oneGateProg.cost :=
  tile_cost_ge_of_gates oneGateProg (nvfp4X 16 64) (fun g i l => by
      classical
      unfold XBlocks.touches
      refine le_trans (Finset.card_le_card (t := {(nvfp4X 16 64).blk (i, l)}) fun b hb => ?_) (by simp)
      rw [Finset.mem_filter] at hb
      obtain ⟨e, he, hne⟩ := hb.2
      have h1 : e = (i, l) := by
        by_contra h
        exact hne (by simp [oneGateProg, unitForm, h])
      rw [Finset.mem_singleton, ← he, h1])
    gates_hyp_satisfiable

end Pouw.TileBound
