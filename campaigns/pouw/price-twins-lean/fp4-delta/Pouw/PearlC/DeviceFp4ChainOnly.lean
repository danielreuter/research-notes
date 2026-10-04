import Pouw.PearlC.DeviceFp4Issue

/-!
# Pearl-C4's chain-only reading at an FP4 record (the price-twins lane's file; definitions only, staged)

The forming-credit reading credits the salt-dependent forming (`fs` per activation element). The chain-only reading
credits the unit without it, as `creditChainOnly` does at the H100 and `DeviceChainOnly` does for FP8: `creditFp4` less
`fs·m·k`, less the unit's debit. The cap stays on the full credit, so a unit within it keeps at least
`creditFp4 − fs·m·k − ρ·creditFp4`, and per tile the fixed credit is that times the credited rows' share. `W_ref` and
every other field are the record's. TT_OUT at these protocols is stated in `TTOutFp4ChainOnly`.
-/

namespace Pouw.PearlC

variable {Q R S : Type}

/-- **The chain-only credit at an FP4 record**: `creditFp4` less the credited forming `fs·m·k`. -/
def creditFp4ChainOnly (d : Fp4Device) (s : Shape) : ℚ := creditFp4 d s - d.prices.fs * s.m * s.k

/-- `pearlCProtocolFp4` with the chain-only credit, less the unit's debit. -/
noncomputable def pearlCProtocolFp4ChainOnly (d : Fp4Device) (sem : Fp4Sem Q R S) (ρ : ℚ) : Protocol Q R S :=
  { pearlCProtocolFp4 d sem ρ with
    credit := fun H s U u act => ((creditFp4ChainOnly d (U.layout.shape u) - sem.unitDebit d H s U u act : ℚ) : ℝ) }

/-- `pearlCTilesFp4` with the chain-only fixed credit `(creditFp4ChainOnly − ρ·creditFp4)` times the credited rows'
share. -/
noncomputable def pearlCTilesFp4ChainOnly (d : Fp4Device) (sem : Fp4Sem Q R S) (ρ : ℚ) : TileRules Q R S :=
  { pearlCTilesFp4 d sem ρ with
    credit := fun _ _ U g act =>
      let tl := auditTiling 64 64 U.layout
      let sh := U.layout.shape (tl.unit g)
      (((creditFp4ChainOnly d sh - ρ * creditFp4 d sh) * tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) :
        ℚ) : ℝ) }

/-- **Pearl-C4's chain-only γ** at the cap `ρ`, which stays on the full credit: `1 − (399/400)/ω` with
`ω = wrefFp4/(creditFp4ChainOnly − ρ·creditFp4)`. -/
def gammaFp4ChainOnly (d : Fp4Device) (ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefFp4 d s / (creditFp4ChainOnly d s - ρ * creditFp4 d s))

end Pouw.PearlC
