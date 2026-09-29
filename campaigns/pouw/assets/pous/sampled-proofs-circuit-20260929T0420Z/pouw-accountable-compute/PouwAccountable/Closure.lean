import PouwAccountable.Charging

/-!
# Closure draws (design note §12.3)

The verifier draws tiles by a law on tiles (by work: `main`'s `Law.stratified` over the tile strata), and proves each
drawn tile together with every unit in its closure (its X and Y strips and its X strip's path nodes, each once).

* `closureLaw Lt cl`: that draw, as a law on the window's units. `mem_closureLaw_draw`: a unit is proved exactly when
  a drawn tile's closure holds it; node units have no stratum and are never drawn on their own.
* `closureLaw_escape`: **its escape is the tile law's escape of the unsound tiles**,
  `(closureLaw Lt cl).escape B = Lt.escape (unsoundTiles cl B)`. So no strip or node stratum, and no harm weighting,
  is needed: the tile law's own harm bound, with each tile's work as its harm, bounds the unsound work.
* `both L M`: two independent draws, proving the union (closure draws plus the integrity floor's draws of the other
  strata, the quantizer, dequantization or narrow Z units and the rest of the model). `both_escape_le`: drawing more
  only lowers every escape, so every bound for `L` holds for `both L M`.
-/

namespace PouwAccountable

open FlockSoundness FlockSoundness.Audit FlockSoundness.Game Finset
open scoped ENNReal

variable {n nT : ℕ}

/-- **Closure draws**: draw tiles by `Lt`, and prove each drawn tile's closure. -/
def closureLaw (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) : Law n where
  Ω := Lt.Ω
  draw ω := (Lt.draw ω).biUnion cl

/-- **What the closure draw proves**: a unit is proved exactly when some drawn tile's closure holds it. A node unit
beneath no drawn tile is never proved, and has no stratum of its own. -/
theorem mem_closureLaw_draw (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) (ω : (closureLaw Lt cl).Ω) (u : Fin n) :
    u ∈ (closureLaw Lt cl).draw ω ↔ ∃ t ∈ Lt.draw ω, u ∈ cl t :=
  mem_biUnion

/-- **The closure draw's escape** is the tile law's escape of the unsound tiles. -/
theorem closureLaw_escape (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) (B : Finset (Fin n)) :
    (closureLaw Lt cl).escape B = Lt.escape (unsoundTiles cl B) := by
  show prCoin (fun ω : Lt.Ω => Disjoint ((Lt.draw ω).biUnion cl) B) =
    prCoin (fun ω : Lt.Ω => Disjoint (Lt.draw ω) (unsoundTiles cl B))
  congr 1
  funext ω
  apply propext
  rw [disjoint_biUnion_left, disjoint_left]
  constructor
  · intro h t ht htU
    exact (mem_filter.1 htU).2 (h t ht)
  · intro h t ht
    by_contra hc
    exact h ht (mem_filter.2 ⟨mem_univ t, hc⟩)

/-- Two independent draws, proving the union of what each draws. -/
def both (L M : Law n) : Law n where
  Ω := L.Ω × M.Ω
  draw ω := L.draw ω.1 ∪ M.draw ω.2

/-- A uniform pair's first coordinate is uniform. -/
theorem prCoin_fst {α β : Type} [Fintype α] [Fintype β] [Nonempty β] (p : α → Prop) :
    prCoin (fun ω : α × β => p ω.1) = prCoin p := by
  classical
  rw [prCoin_eq_card, prCoin_eq_card]
  have h : (univ.filter fun ω : α × β => p ω.1) = (univ.filter p) ×ˢ (univ : Finset β) := by
    ext ⟨a, b⟩
    simp
  rw [h, card_product, Fintype.card_prod, card_univ, Nat.cast_mul, Nat.cast_mul]
  exact ENNReal.mul_div_mul_right _ _ (by exact_mod_cast Fintype.card_ne_zero) (ENNReal.natCast_ne_top _)

/-- **Drawing more only lowers the escape.** -/
theorem both_escape_le (L M : Law n) (B : Finset (Fin n)) : (both L M).escape B ≤ L.escape B := by
  show prCoin (fun ω : L.Ω × M.Ω => Disjoint (L.draw ω.1 ∪ M.draw ω.2) B) ≤
    prCoin (fun ω : L.Ω => Disjoint (L.draw ω) B)
  calc prCoin (fun ω : L.Ω × M.Ω => Disjoint (L.draw ω.1 ∪ M.draw ω.2) B)
      ≤ prCoin (fun ω : L.Ω × M.Ω => Disjoint (L.draw ω.1) B) :=
        prCoin_mono fun (ω : L.Ω × M.Ω) h =>
          Disjoint.mono_left (show L.draw ω.1 ⊆ L.draw ω.1 ∪ M.draw ω.2 from subset_union_left) h
    _ = prCoin (fun ω : L.Ω => Disjoint (L.draw ω) B) := prCoin_fst (fun ω : L.Ω => Disjoint (L.draw ω) B)

end PouwAccountable
