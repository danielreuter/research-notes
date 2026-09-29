import FlockSoundness.Audit.Stratified

/-!
# Harm charging and coverage (design note §12.1, §12.2 step (1))

A window's units are `Fin n`; its tiles are `Fin nT`, with work `w t` (the tile's `W_ref`). A tile's credit depends on
the units in its closure `cl t`: in PoUW (`Layout`) its own tile unit, the X strip and Y strip it reads, and the node
units on its X strip's path to D_A.

* `unsoundTiles cl B`: the tiles whose closure meets the wrong-unit set `B`; `soundWork` and `unsoundWork` split the
  total work between the tiles that are sound and those that are not (`soundWork_add_unsoundWork`).
* `harm cl w u`: the work of every tile whose closure holds `u`, what a wrong `u` spoils.
* `unsoundWork_singleton`: the charging is exact for one wrong unit.
* `unsoundWork_le_harm` (**coverage**, §12.2 (1)): `unsoundWork cl w B ≤ ∑_{u ∈ B} harm cl w u`.
* `harm_le_unsoundWork`: a wrong unit's whole harm is inside the unsound work, whether or not a draw reaches it.
* For the PoUW layout, `Layout.harm_tile`, `harm_xs`, `harm_ys` and `harm_node` restate §12.1's harm column: a wrong
  tile spoils its own work, a wrong X or Y strip the work of the tiles that read it, and a wrong node unit the work of
  the tiles whose X strip's path holds it.

Nothing here reads the tile's outputs, so it holds whether the tile outputs Z or Z moves to narrow units.
-/

namespace PouwAccountable

open Finset

variable {n nT : ℕ}

/-- The tiles whose credit depends on a unit of `B`. -/
def unsoundTiles (cl : Fin nT → Finset (Fin n)) (B : Finset (Fin n)) : Finset (Fin nT) :=
  univ.filter fun t => ¬ Disjoint (cl t) B

/-- The window's total work `W`. -/
def totalWork (w : Fin nT → ℝ) : ℝ := ∑ t, w t

/-- The work of the tiles made unsound by the wrong-unit set `B`. -/
def unsoundWork (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ) (B : Finset (Fin n)) : ℝ :=
  ∑ t ∈ unsoundTiles cl B, w t

/-- **Verified work**: the work of the sound tiles, those whose closure holds no wrong unit. -/
def soundWork (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ) (B : Finset (Fin n)) : ℝ :=
  ∑ t ∈ univ.filter (fun t => Disjoint (cl t) B), w t

theorem soundWork_add_unsoundWork (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ) (B : Finset (Fin n)) :
    soundWork cl w B + unsoundWork cl w B = totalWork w :=
  sum_filter_add_sum_filter_not univ (fun t => Disjoint (cl t) B) w

/-- **The harm of a unit**: the work of every tile whose credit depends on it. -/
def harm (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ) (u : Fin n) : ℝ :=
  ∑ t ∈ univ.filter (fun t => u ∈ cl t), w t

/-- **The charging is exact for one wrong unit.** -/
theorem unsoundWork_singleton (cl : Fin nT → Finset (Fin n)) (w : Fin nT → ℝ) (u : Fin n) :
    unsoundWork cl w {u} = harm cl w u := by
  unfold unsoundWork unsoundTiles harm
  congr 1
  ext t
  simp [disjoint_singleton_right]

/-- **Coverage** (§12.2 (1)): the work of the unsound tiles is at most the harm of the wrong units. Each unsound tile
is charged to a wrong unit of its closure; overlaps only overcount. -/
theorem unsoundWork_le_harm (cl : Fin nT → Finset (Fin n)) {w : Fin nT → ℝ} (hw : ∀ t, 0 ≤ w t)
    (B : Finset (Fin n)) : unsoundWork cl w B ≤ ∑ u ∈ B, harm cl w u := by
  classical
  unfold unsoundWork unsoundTiles harm
  simp only [sum_filter]
  rw [sum_comm]
  refine sum_le_sum fun t _ => ?_
  have hnn : ∀ u, (0 : ℝ) ≤ if u ∈ cl t then w t else 0 := fun u => by
    split_ifs
    · exact hw t
    · exact le_rfl
  split_ifs with h
  · exact sum_nonneg fun u _ => hnn u
  · obtain ⟨u, hu, huB⟩ := not_disjoint_iff.1 h
    calc w t = (if u ∈ cl t then w t else 0) := by simp [hu]
      _ ≤ ∑ u ∈ B, if u ∈ cl t then w t else 0 :=
          single_le_sum (f := fun u => if u ∈ cl t then w t else 0) (fun u _ => hnn u) huB

/-- **A wrong unit's whole harm is counted, drawn or not**: every tile whose closure holds a wrong unit is unsound. So
a wrong node unit that no draw ever reaches still has all the tiles beneath it counted in the unsound work. -/
theorem harm_le_unsoundWork (cl : Fin nT → Finset (Fin n)) {w : Fin nT → ℝ} (hw : ∀ t, 0 ≤ w t)
    {B : Finset (Fin n)} {u : Fin n} (hu : u ∈ B) : harm cl w u ≤ unsoundWork cl w B := by
  unfold harm unsoundWork unsoundTiles
  refine sum_le_sum_of_subset_of_nonneg (fun t ht => ?_) (fun t _ _ => hw t)
  rw [mem_filter] at ht ⊢
  exact ⟨ht.1, not_disjoint_iff.2 ⟨u, ht.2, hu⟩⟩

/-! ## The PoUW layout (§12.1) -/

/-- **The PoUW layout**: each tile's own unit, the X strip (`ncp-form-x`) and Y strip (`ncp-form-y`) it reads, and the
node units (`ncp-node`) on its X strip's path to D_A. -/
structure Layout (n nT : ℕ) where
  tile : Fin nT → Fin n
  xs : Fin nT → Fin n
  ys : Fin nT → Fin n
  path : Fin nT → Finset (Fin n)

namespace Layout

variable (P : Layout n nT)

/-- A tile's closure: the units the closure draw proves with it, and on which its credit depends. -/
def cl (t : Fin nT) : Finset (Fin n) := insert (P.tile t) (insert (P.xs t) (insert (P.ys t) (P.path t)))

theorem mem_cl {t : Fin nT} {u : Fin n} :
    u ∈ P.cl t ↔ u = P.tile t ∨ u = P.xs t ∨ u = P.ys t ∨ u ∈ P.path t := by
  simp [cl]

/-- **A wrong tile spoils its own work**, when tile units play no other role. -/
theorem harm_tile (w : Fin nT → ℝ) (hinj : Function.Injective P.tile) (t : Fin nT)
    (hx : ∀ t', P.xs t' ≠ P.tile t) (hy : ∀ t', P.ys t' ≠ P.tile t) (hp : ∀ t', P.tile t ∉ P.path t') :
    harm P.cl w (P.tile t) = w t := by
  unfold harm
  rw [show (univ.filter fun t' => P.tile t ∈ P.cl t') = {t} by
    ext t'
    simp only [mem_filter, mem_univ, true_and, mem_singleton, mem_cl]
    constructor
    · rintro (h | h | h | h)
      · exact (hinj h).symm
      · exact absurd h.symm (hx t')
      · exact absurd h.symm (hy t')
      · exact absurd h (hp t')
    · rintro rfl
      exact Or.inl rfl]
  exact sum_singleton _ _

/-- **A wrong X strip spoils the work of the tiles that read it**, when it plays no other role. -/
theorem harm_xs (w : Fin nT → ℝ) (x : Fin n) (ht : ∀ t, P.tile t ≠ x) (hy : ∀ t, P.ys t ≠ x)
    (hp : ∀ t, x ∉ P.path t) : harm P.cl w x = ∑ t ∈ univ.filter (fun t => P.xs t = x), w t := by
  unfold harm
  congr 1
  ext t
  simp only [mem_filter, mem_univ, true_and, mem_cl]
  constructor
  · rintro (h | h | h | h)
    · exact absurd h.symm (ht t)
    · exact h.symm
    · exact absurd h.symm (hy t)
    · exact absurd h (hp t)
  · intro h
    exact Or.inr (Or.inl h.symm)

/-- **A wrong Y strip spoils the work of the tiles that read it** (in this window), when it plays no other role. -/
theorem harm_ys (w : Fin nT → ℝ) (y : Fin n) (ht : ∀ t, P.tile t ≠ y) (hx : ∀ t, P.xs t ≠ y)
    (hp : ∀ t, y ∉ P.path t) : harm P.cl w y = ∑ t ∈ univ.filter (fun t => P.ys t = y), w t := by
  unfold harm
  congr 1
  ext t
  simp only [mem_filter, mem_univ, true_and, mem_cl]
  constructor
  · rintro (h | h | h | h)
    · exact absurd h.symm (ht t)
    · exact absurd h.symm (hx t)
    · exact h.symm
    · exact absurd h (hp t)
  · intro h
    exact Or.inr (Or.inr (Or.inl h.symm))

/-- **A wrong node unit spoils the work of the tiles whose X strip's path holds it**, when it plays no other role. -/
theorem harm_node (w : Fin nT → ℝ) (v : Fin n) (ht : ∀ t, P.tile t ≠ v) (hx : ∀ t, P.xs t ≠ v)
    (hy : ∀ t, P.ys t ≠ v) : harm P.cl w v = ∑ t ∈ univ.filter (fun t => v ∈ P.path t), w t := by
  unfold harm
  congr 1
  ext t
  simp only [mem_filter, mem_univ, true_and, mem_cl]
  constructor
  · rintro (h | h | h | h)
    · exact absurd h.symm (ht t)
    · exact absurd h.symm (hx t)
    · exact absurd h.symm (hy t)
    · exact h
  · intro h
    exact Or.inr (Or.inr (Or.inr h))

end Layout

end PouwAccountable
