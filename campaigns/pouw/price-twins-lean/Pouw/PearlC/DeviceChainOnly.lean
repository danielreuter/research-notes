import Pouw.PearlC.DeviceKernelWref

/-!
# The chain-only reading at a device record (the price-twins lane's file; definitions only, staged)

The forming-credit reading credits the salt-dependent forming (`fs` per activation element). The chain-only reading
credits the unit without it, as `creditChainOnly` does at the H100 (`Game`): `creditDev` less `fs·m·k`, less the
unit's debit. The cap stays on the full credit, so a unit within it keeps at least `creditDev − fs·m·k − ρ·creditDev`.
Per tile the fixed credit is that times the credited rows' share. `W_ref` is the kernel's (`DeviceKernelWref`), and
every other field is the record's. TT_OUT at these protocols is stated in `TTOutChainOnly`.
-/

namespace Pouw.PearlC

variable {Q R S : Type}

/-- **The chain-only credit at a device record**: `creditDev` less the credited forming `fs·m·k`. -/
def creditDevChainOnly (d : PearlCDevice) (s : Shape) : ℚ := creditDev d s - (d.prices.costs.fs : ℚ) * s.m * s.k

/-- **The chain-only credit under rev1**: `creditDevRev1` less the credited forming `fs·m·k`. -/
def creditDevRev1ChainOnly (d : PearlCDevice) (s : Shape) : ℚ :=
  creditDevRev1 d s - (d.prices.costs.fs : ℚ) * s.m * s.k

/-- `pearlCProtocolDevK` with the chain-only credit, less the unit's debit. -/
noncomputable def pearlCProtocolDevKChainOnly (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) :
    Protocol Q R S :=
  { pearlCProtocolDevK d sem ρ c with
    credit := fun H s U u act =>
      ((creditDevChainOnly d (U.layout.shape u) - debitDev d (sem.unitDebitDev d H s U u act) : ℚ) : ℝ) }

/-- `pearlCTilesDevK` with the chain-only fixed credit `(creditDevChainOnly − ρ·creditDev)` times the credited rows'
share. -/
noncomputable def pearlCTilesDevKChainOnly (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) : TileRules Q R S :=
  { pearlCTilesDevK d sem ρ c with
    credit := fun _ _ U g act =>
      let tl := auditTiling 64 64 U.layout
      let sh := U.layout.shape (tl.unit g)
      (((creditDevChainOnly d sh - ρ * creditDev d sh) * tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) :
        ℚ) : ℝ) }

/-- `pearlCProtocolDevRev1K` with the chain-only credit, less the unit's rev1 debit. -/
noncomputable def pearlCProtocolDevRev1KChainOnly (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) :
    Protocol Q R S :=
  { pearlCProtocolDevRev1K d sem ρ c with
    credit := fun H s U u act =>
      ((creditDevRev1ChainOnly d (U.layout.shape u) - sem.unitDebitRev1 d H s U u act : ℚ) : ℝ) }

/-- `pearlCTilesDevRev1K` with the chain-only fixed credit `(creditDevRev1ChainOnly − ρ·creditDevRev1)` times the
credited rows' share. -/
noncomputable def pearlCTilesDevRev1KChainOnly (d : PearlCDevice) (sem : PearlCSem Q R S) (ρ c : ℚ) :
    TileRules Q R S :=
  { pearlCTilesDevRev1K d sem ρ c with
    credit := fun _ _ U g act =>
      let tl := auditTiling 64 64 U.layout
      let sh := U.layout.shape (tl.unit g)
      (((creditDevRev1ChainOnly d sh - ρ * creditDevRev1 d sh) *
        tileShare sh (sem.passRows sh act (tl.rows g)) (tl.cols g) : ℚ) : ℝ) }

end Pouw.PearlC
